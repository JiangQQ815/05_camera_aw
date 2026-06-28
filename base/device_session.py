"""
设备会话管理 - 支持多设备连接和调度
pytest fixture 直接注入，无需单例

atx-agent 死亡问题处理:
- atx-agent 可能在任何输入操作时静默死亡
- HTTP 连接 127.0.0.1:37333 时抛出 ReadTimeout（默认60秒）
- 所有设备操作都配置了超时，避免测试线程阻塞
参考: https://github.com/openatx/uiautomator2/issues/224
"""
import uiautomator2 as u2
import logging
import time
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from requests.exceptions import ReadTimeout, ConnectTimeout

logger = logging.getLogger("DeviceSession")

# 设备操作超时配置（秒）
DEFAULT_CONNECT_TIMEOUT = 10  # 连接 atx-agent 超时
DEFAULT_OPERATION_TIMEOUT = 5  # 一般操作超时
DEFAULT_ATX_AGENT_DEAD_TIMEOUT = 3  # atx-agent 疑似死亡时的快速失败超时


class DeviceStatus(Enum):
    """设备状态"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class DeviceInfo:
    """设备信息"""
    serial: str
    name: str = ""
    status: DeviceStatus = DeviceStatus.AVAILABLE
    current_task: Optional[str] = None
    last_used: float = field(default_factory=time.time)
    total_cases: int = 0
    pass_cases: int = 0
    fail_cases: int = 0

    def __post_init__(self):
        if not self.name:
            self.name = self.serial


class DeviceSession:
    """
    设备会话管理器

    作为 pytest fixture 注入，无需单例
    支持多设备并行测试
    """

    def __init__(self):
        self._devices: Dict[str, DeviceInfo] = {}
        self._drivers: Dict[str, u2.Device] = {}
        self._test_sessions: Dict[str, Dict] = {}  # session_id -> test session data
        logger.info("DeviceSession 初始化")

    def connect_all_devices(self) -> List[DeviceInfo]:
        """自动连接所有已连接的ADB设备"""
        import subprocess

        logger.info("正在扫描可用设备...")

        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split("\n")[1:]
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        serial = parts[0]
                        status = parts[1].strip()
                        if status == "device":
                            self.add_device(serial)

        except Exception as e:
            logger.error(f"扫描设备失败: {e}")

        return list(self._devices.values())

    def add_device(
        self,
        serial: str,
        max_retries: int = 3,
        operation_timeout: float = DEFAULT_OPERATION_TIMEOUT,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    ) -> DeviceInfo:
        """
        添加设备（带 atx-agent 死亡处理）

        Args:
            serial: 设备序列号
            max_retries: 最大重试次数
            operation_timeout: 操作超时时间（秒）
            connect_timeout: 连接超时时间（秒）
        """
        if serial in self._devices:
            logger.info(f"设备已存在: {serial}")
            return self._devices[serial]

        last_error: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"正在连接设备: {serial} (尝试 {attempt}/{max_retries})")

                # 配置 uiautomator2 超时参数，避免 60 秒阻塞
                driver = u2.connect(serial)
                driver.timeout = operation_timeout  # 全局操作超时

                info = driver.info
                device_name = info.get("deviceName", serial)

                device_info = DeviceInfo(serial=serial, name=device_name)
                self._devices[serial] = device_info
                self._drivers[serial] = driver

                logger.info(f"设备连接成功: {serial} ({device_name})")
                return device_info

            except (ReadTimeout, ConnectTimeout) as e:
                last_error = e
                logger.warning(
                    f"设备连接超时 (atx-agent 可能死亡, 尝试 {attempt}/{max_retries}): "
                    f"{serial}, error: {e}"
                )
                if attempt < max_retries:
                    time.sleep(1 * attempt)  # 指数退避
                    continue

            except Exception as e:
                last_error = e
                logger.error(f"设备连接失败: {serial}, error: {e}")
                if attempt < max_retries:
                    time.sleep(1 * attempt)
                    continue
                break

        # 所有重试都失败
        device_info = DeviceInfo(serial=serial, status=DeviceStatus.ERROR)
        self._devices[serial] = device_info
        if last_error:
            logger.error(f"设备 {serial} 在 {max_retries} 次重试后仍然失败: {last_error}")
        return device_info

    def reconnect_device(self, serial: str) -> bool:
        """
        重新连接设备（用于 atx-agent 死亡后恢复）

        Returns:
            bool: 重新连接是否成功
        """
        if serial not in self._devices:
            logger.warning(f"设备不存在，无法重连: {serial}")
            return False

        logger.info(f"尝试重新连接设备: {serial}")

        # 移除旧连接
        old_driver = self._drivers.get(serial)
        if old_driver:
            try:
                # 尝试优雅关闭
                if hasattr(old_driver, 'shell'):
                    old_driver.shell(["exit"])
            except Exception:
                pass  # 忽略关闭错误

        # 重新添加设备
        device_info = self.add_device(serial)
        if device_info.status == DeviceStatus.AVAILABLE:
            logger.info(f"设备重连成功: {serial}")
            return True

        logger.error(f"设备重连失败: {serial}")
        return False

    def is_agent_alive(self, serial: str) -> bool:
        """
        检查 atx-agent 是否存活

        Returns:
            bool: agent 是否正常运行
        """
        driver = self._drivers.get(serial)
        if not driver:
            return False

        try:
            driver.info  # 轻量级检查
            return True
        except Exception:
            return False

    def remove_device(self, serial: str):
        """移除设备"""
        if serial in self._drivers:
            del self._drivers[serial]
        if serial in self._devices:
            del self._devices[serial]
        logger.info(f"设备已移除: {serial}")

    def get_device(self, serial: str) -> Optional[DeviceInfo]:
        """获取设备信息"""
        return self._devices.get(serial)

    def get_driver(self, serial: str) -> Optional[u2.Device]:
        """获取设备驱动"""
        return self._drivers.get(serial)

    def get_available_devices(self) -> List[DeviceInfo]:
        """获取所有可用设备"""
        return [d for d in self._devices.values()
                 if d.status == DeviceStatus.AVAILABLE]

    def get_all_devices(self) -> List[DeviceInfo]:
        """获取所有设备"""
        return list(self._devices.values())

    def allocate_device(self, task_name: str = "") -> Optional[DeviceInfo]:
        """分配一个可用设备"""
        available = self.get_available_devices()
        if not available:
            logger.warning("没有可用的设备")
            return None

        device = min(available, key=lambda d: d.last_used)
        device.status = DeviceStatus.BUSY
        device.current_task = task_name
        device.last_used = time.time()

        logger.info(f"设备已分配: {device.serial} -> {task_name}")
        return device

    def release_device(self, serial: str):
        """释放设备"""
        if serial in self._devices:
            device = self._devices[serial]
            device.status = DeviceStatus.AVAILABLE
            device.current_task = None
            logger.info(f"设备已释放: {serial}")

    def update_stats(self, serial: str, passed: bool = True):
        """更新设备统计"""
        if serial in self._devices:
            device = self._devices[serial]
            device.total_cases += 1
            if passed:
                device.pass_cases += 1
            else:
                device.fail_cases += 1

    def print_status(self):
        """打印所有设备状态"""
        logger.info("=" * 60)
        logger.info("设备状态总览")
        logger.info("=" * 60)

        for device in self._devices.values():
            success_rate = (device.pass_cases / device.total_cases * 100) if device.total_cases > 0 else 0
            logger.info(
                f"[{device.serial}] {device.name} | "
                f"状态: {device.status.value} | "
                f"任务: {device.current_task or '无'} | "
                f"用例: {device.total_cases} (通过: {device.pass_cases}, 失败: {device.fail_cases}) | "
                f"成功率: {success_rate:.1f}%"
            )

        logger.info("=" * 60)


# ============================================
# pytest fixtures
# ============================================

def create_device_session() -> DeviceSession:
    """创建设备会话（供 fixture 调用）"""
    return DeviceSession()

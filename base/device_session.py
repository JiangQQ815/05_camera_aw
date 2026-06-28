"""
设备会话管理 - 支持多设备连接和调度
pytest fixture 直接注入，无需单例
"""
import uiautomator2 as u2
import logging
import time
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("DeviceSession")


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

    def add_device(self, serial: str) -> DeviceInfo:
        """添加设备"""
        if serial in self._devices:
            logger.info(f"设备已存在: {serial}")
            return self._devices[serial]

        try:
            logger.info(f"正在连接设备: {serial}")
            driver = u2.connect(serial)
            info = driver.info
            device_name = info.get("deviceName", serial)

            device_info = DeviceInfo(serial=serial, name=device_name)
            self._devices[serial] = device_info
            self._drivers[serial] = driver

            logger.info(f"设备连接成功: {serial} ({device_name})")
            return device_info

        except Exception as e:
            logger.error(f"设备连接失败: {serial}, error: {e}")
            device_info = DeviceInfo(serial=serial, status=DeviceStatus.ERROR)
            self._devices[serial] = device_info
            return device_info

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

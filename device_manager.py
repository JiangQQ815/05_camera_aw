"""
设备管理器 - 管理多设备连接和调度

为 run_tests.py 提供设备管理功能，支持:
- 多设备并行测试
- 设备状态跟踪
- 用例分发

注意: 此模块已被 base/device_session.py 替代，
新代码应使用 DeviceSession 类
"""
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("DeviceManager")


class DeviceStatus(Enum):
    """设备状态"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class DeviceStats:
    """设备统计信息"""
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    last_used: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return (self.passed_cases / self.total_cases) * 100


class DeviceManager:
    """
    设备管理器（单例）

    管理设备连接、状态和统计信息
    """

    _instance: Optional['DeviceManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._drivers: Dict[str, 'u2.Device'] = {}
        self._stats: Dict[str, DeviceStats] = {}
        self._status: Dict[str, DeviceStatus] = {}
        self._initialized = True
        logger.info("DeviceManager 初始化")

    def add_device(self, serial: str) -> 'Device':
        """添加设备"""
        import uiautomator2 as u2

        if serial in self._drivers:
            logger.info(f"设备已存在: {serial}")
            return self._drivers[serial]

        try:
            logger.info(f"正在连接设备: {serial}")
            driver = u2.connect(serial)
            device_info = driver.info
            device_name = device_info.get("deviceName", serial)

            self._drivers[serial] = driver
            self._stats[serial] = DeviceStats()
            self._status[serial] = DeviceStatus.AVAILABLE

            logger.info(f"设备连接成功: {serial} ({device_name})")
            return driver

        except Exception as e:
            logger.error(f"设备连接失败: {serial}, error: {e}")
            self._status[serial] = DeviceStatus.ERROR
            raise

    def get_device(self, serial: str) -> Optional['u2.Device']:
        """获取设备驱动"""
        return self._drivers.get(serial)

    def get_all_devices(self) -> List[str]:
        """获取所有已连接设备序列号"""
        return list(self._drivers.keys())

    def get_available_devices(self) -> List[str]:
        """获取所有可用设备"""
        return [
            serial for serial, status in self._status.items()
            if status == DeviceStatus.AVAILABLE
        ]

    def allocate_device(self, task_name: str = "") -> Optional[str]:
        """
        分配一个可用设备

        Returns:
            设备序列号，如果没有可用设备返回 None
        """
        available = self.get_available_devices()
        if not available:
            logger.warning("没有可用的设备")
            return None

        # 选择最久未使用的设备
        device = min(
            available,
            key=lambda s: self._stats[s].last_used if s in self._stats else 0
        )

        self._status[device] = DeviceStatus.BUSY
        self._stats[device].last_used = time.time()

        logger.info(f"设备已分配: {device} -> {task_name}")
        return device

    def release_device(self, serial: str):
        """释放设备"""
        if serial in self._status:
            self._status[serial] = DeviceStatus.AVAILABLE
            logger.info(f"设备已释放: {serial}")

    def update_device_stats(self, serial: str, passed: bool = True):
        """更新设备统计信息"""
        if serial not in self._stats:
            self._stats[serial] = DeviceStats()

        stats = self._stats[serial]
        stats.total_cases += 1
        if passed:
            stats.passed_cases += 1
        else:
            stats.failed_cases += 1

    def get_device_stats(self, serial: str) -> Optional[DeviceStats]:
        """获取设备统计信息"""
        return self._stats.get(serial)

    def print_status(self):
        """打印所有设备状态"""
        logger.info("=" * 60)
        logger.info("设备状态总览")
        logger.info("=" * 60)

        for serial in self._drivers.keys():
            stats = self._stats.get(serial, DeviceStats())
            status = self._status.get(serial, DeviceStatus.OFFLINE)
            driver = self._drivers.get(serial)

            device_name = "Unknown"
            if driver and hasattr(driver, 'info') and driver.info:
                device_name = driver.info.get('deviceName', 'Unknown')

            logger.info(
                f"[{serial}] {device_name} | "
                f"状态: {status.value} | "
                f"用例: {stats.total_cases} "
                f"(通过: {stats.passed_cases}, 失败: {stats.failed_cases}) | "
                f"成功率: {stats.success_rate:.1f}%"
            )

        logger.info("=" * 60)

    def cleanup(self):
        """清理所有设备连接"""
        for serial in list(self._drivers.keys()):
            try:
                if hasattr(self._drivers[serial], 'app_stop'):
                    self._drivers[serial].app_stop("com.android.camera")
            except Exception as e:
                logger.warning(f"清理设备 {serial} 失败: {e}")

        self._drivers.clear()
        self._stats.clear()
        self._status.clear()
        logger.info("设备管理器已清理")


# 全局单例实例
_device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """获取设备管理器单例"""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


# 兼容旧接口 - 直接导出单例
@property
def device_manager() -> DeviceManager:
    """设备管理器单例（兼容旧接口）"""
    return get_device_manager()


# 为方便使用，也直接实例化
device_manager = get_device_manager()

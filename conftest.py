"""
Pytest Fixtures - 相机自动化测试
"""
import pytest
import uiautomator2 as u2
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def device(serial=None):
    """
    初始化 uiautomator2 设备连接
    :param serial: 设备序列号，默认 None 自动选择第一个
    """
    logger.info("正在连接设备...")
    d = u2.connect(serial)
    logger.info(f"设备连接成功: {d.info.get('deviceName', 'Unknown')}")
    yield d
    logger.info("测试结束，清理设备连接...")


@pytest.fixture(scope="function")
def camera_app(device):
    """
    启动相机应用并在测试后关闭
    """
    logger.info("启动相机应用...")
    device.app_stop("com.android.camera")
    time.sleep(0.5)
    device.app_start("com.android.camera")
    time.sleep(2)  # 等待相机完全启动

    yield device

    logger.info("测试完成，返回相机主界面...")
    device.app_stop("com.android.camera")


@pytest.fixture(scope="function")
def camera_aw(camera_app):
    """
    初始化 CameraAutomationAW 实例
    """
    from base.camera_aw import CameraAutomationAW
    return CameraAutomationAW(camera_app)

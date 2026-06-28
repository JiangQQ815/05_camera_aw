"""
Pytest配置文件 - 支持pytest-xdist多进程并行
使用方法: pytest --forked -k "test_photo"
"""
import pytest
import uiautomator2 as u2
import logging
import time
import os

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """pytest配置钩子"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "device(serial): 指定设备序列号"
    )
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试"
    )
    config.addinivalue_line(
        "markers", "photo: 拍照测试"
    )
    config.addinivalue_line(
        "markers", "video: 录像测试"
    )


@pytest.fixture(scope="session")
def device_info(request):
    """
    获取命令行指定的设备序列号
    """
    serial = request.config.getoption("--device-serial", default=None)
    return serial


@pytest.fixture(scope="session")
def u2_driver(device_info):
    """
    创建uiautomator2驱动
    """
    if device_info:
        driver = u2.connect(device_info)
    else:
        driver = u2.connect()

    yield driver

    # 清理
    try:
        driver.app_stop("com.android.camera")
    except:
        pass


@pytest.fixture(scope="function")
def camera_ready(u2_driver):
    """
    确保相机应用正常运行
    """
    logger.info("准备相机应用...")
    u2_driver.app_stop("com.huawei.camera")
    time.sleep(0.5)
    u2_driver.app_start("com.huawei.camera")
    time.sleep(2)

    yield u2_driver

    # 测试后清理
    try:
        u2_driver.app_stop("com.android.camera")
    except:
        pass


def pytest_collection_modifyitems(config, items):
    """
    修改测试用例收集
    - 根据worker ID分配设备
    """
    if not hasattr(config, 'workerinput'):
        # 主进程，不处理
        return

    # 获取当前worker ID
    worker_id = config.workerinput['workerid']

    # 从已连接的设备中分配
    import subprocess
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.strip().split("\n")[1:]
    devices = []
    for line in lines:
        if line.strip() and "device" in line:
            serial = line.split("\t")[0].strip()
            devices.append(serial)

    if not devices:
        logger.warning("没有可用设备")
        return

    # 按worker数量分配
    worker_count = len(config.workerinput)
    worker_index = int(worker_id.replace("gw", "") or 0)

    if worker_index < len(devices):
        target_device = devices[worker_index]
        logger.info(f"Worker {worker_id} 分配设备: {target_device}")

        # 为每个用例添加设备标记
        for item in items:
            item.user_properties.append(("device", target_device))


def pytest_report_header(config):
    """添加测试报告头"""
    devices_info = []
    try:
        import subprocess
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split("\n")[1:]
        for line in lines:
            if line.strip() and "device" in line:
                serial = line.split("\t")[0].strip()
                devices_info.append(serial)
    except:
        pass

    return [f"可用设备: {', '.join(devices_info) if devices_info else '无'}"]

"""
Pytest Fixtures - 多设备版本
支持多设备并行/分布执行测试
"""
import pytest
import uiautomator2 as u2
import logging
import time
import os
from typing import Optional, Dict, List

from device_manager import device_manager, DeviceInfo, DeviceStatus
from base.camera_aw import CameraAutomationAW

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--devices",
        action="store",
        default=None,
        help="指定设备序列号，逗号分隔，如: 'ABC123,DEF456'"
    )
    parser.addoption(
        "--device-serial",
        action="store",
        default=None,
        help="指定单个设备序列号"
    )
    parser.addoption(
        "--distribute",
        action="store_true",
        default=False,
        help="启用用例分发模式"
    )


@pytest.fixture(scope="session")
def all_devices(request):
    """
    获取所有已连接设备
    """
    logger.info("=" * 60)
    logger.info("初始化多设备环境")
    logger.info("=" * 60)

    # 获取命令行指定的设备
    devices_arg = request.config.getoption("--devices")
    device_serial_arg = request.config.getoption("--device-serial")

    devices = []

    if device_serial_arg:
        # 单个指定设备
        device_info = device_manager.add_device(device_serial_arg)
        devices.append(device_info)
    elif devices_arg:
        # 逗号分隔的多个设备
        serials = [s.strip() for s in devices_arg.split(",")]
        for serial in serials:
            device_info = device_manager.add_device(serial)
            devices.append(device_info)
    else:
        # 自动扫描所有设备
        devices = device_manager.connect_all_devices()

    if not devices:
        pytest.exit("没有找到可用设备！请连接设备后重试。")

    logger.info(f"共发现 {len(devices)} 个设备:")
    for d in devices:
        logger.info(f"  - {d.serial} ({d.name})")

    yield devices

    # 清理
    logger.info("=" * 60)
    logger.info("测试结束，打印设备统计")
    logger.info("=" * 60)
    device_manager.print_status()


@pytest.fixture(scope="function")
def multi_device_camera(all_devices):
    """
    多设备相机fixture - 返回所有设备
    """
    connected_devices = []

    for device_info in all_devices:
        if device_info.status != DeviceStatus.ERROR:
            try:
                driver = device_manager.get_driver(device_info.serial)
                connected_devices.append({
                    "info": device_info,
                    "driver": driver,
                    "aw": CameraAutomationAW(driver)
                })
            except Exception as e:
                logger.error(f"初始化设备失败 {device_info.serial}: {e}")

    return connected_devices


def get_cases_for_device(device_serial: str, all_cases: List[Dict]) -> List[Dict]:
    """
    根据设备分配用例
    :param device_serial: 设备序列号
    :param all_cases: 所有用例
    :return: 分配给该设备的用例
    """
    # 按 case_id 的 hash 值分配，实现均匀分布
    device_hash = hash(device_serial)
    assigned = []

    for i, case in enumerate(all_cases):
        if hash(case.get("case_id", str(i))) % len(all_devices := [device_serial]) == device_hash % 1:
            assigned.append(case)

    # 简化：直接按索引分配
    assigned = []
    for i, case in enumerate(all_cases):
        case_with_idx = case.copy()
        case_with_idx["_device_index"] = i % len([d.serial for d in device_manager.get_all_devices()])
        assigned.append(case_with_idx)

    return assigned


# ============================================
# 单设备模式的兼容接口
# ============================================

@pytest.fixture(scope="session")
def device(all_devices):
    """
    单设备兼容fixture - 默认使用第一个设备
    """
    if not all_devices:
        pytest.exit("没有可用设备")

    first_device = all_devices[0]
    logger.info(f"使用默认设备: {first_device.serial}")

    driver = device_manager.get_driver(first_device.serial)
    yield driver

    logger.info("设备连接已关闭")


@pytest.fixture(scope="function")
def camera_app(device):
    """
    启动相机应用
    """
    logger.info("启动相机应用...")
    device.app_stop("com.android.camera")
    time.sleep(0.5)
    device.app_start("com.android.camera")
    time.sleep(2)

    yield device

    logger.info("返回相机主界面...")
    device.app_stop("com.android.camera")


@pytest.fixture(scope="function")
def camera_aw(camera_app):
    """
    初始化 CameraAutomationAW 实例
    """
    return CameraAutomationAW(camera_app)


# ============================================
# 多设备并行执行辅助
# ============================================

def distribute_cases_to_devices(devices: List[DeviceInfo], cases: List[Dict]) -> Dict[str, List[Dict]]:
    """
    将用例均匀分发到多个设备
    :param devices: 设备列表
    :param cases: 用例列表
    :return: {device_serial: [cases]}
    """
    distribution = {d.serial: [] for d in devices}

    for i, case in enumerate(cases):
        target_device = devices[i % len(devices)]
        case_with_device = case.copy()
        case_with_device["_target_device"] = target_device.serial
        distribution[target_device.serial].append(case_with_device)

    return distribution


def run_on_device(device_serial: str, cases: List[Dict]) -> Dict:
    """
    在指定设备上运行用例
    :param device_serial: 设备序列号
    :param cases: 用例列表
    :return: 运行结果
    """
    results = {
        "device": device_serial,
        "total": len(cases),
        "passed": 0,
        "failed": 0,
        "cases": []
    }

    try:
        driver = device_manager.get_driver(device_serial)
        if not driver:
            logger.error(f"设备未连接: {device_serial}")
            return results

        cam = CameraAutomationAW(driver)

        for case in cases:
            try:
                logger.info(f"[{device_serial}] 执行用例: {case.get('case_id')}")

                # 执行用例
                cam.switch_camera_lens(case.get("facing", "后置"))
                cam.switch_to_mode(case.get("mode", "拍照"))

                for option, val in case.get("settings", {}).items():
                    cam.set_camera_setting(option, val)

                action = case.get("action")
                if action == "photo":
                    cam.take_photo()
                elif action == "video":
                    cam.start_video_recording()
                    cam.stop_video_recording(case.get("video_duration", 3))

                time.sleep(1)

                if cam.verify_thumbnail_updated() and not cam.check_camera_crash():
                    results["passed"] += 1
                    logger.info(f"[{device_serial}] ✓ {case.get('case_id')} 通过")
                else:
                    results["failed"] += 1
                    logger.error(f"[{device_serial}] ✗ {case.get('case_id')} 失败")

            except Exception as e:
                results["failed"] += 1
                logger.error(f"[{device_serial}] ✗ {case.get('case_id')} 异常: {e}")

            device_manager.update_device_stats(device_serial, passed=(results["failed"] == 0))

    except Exception as e:
        logger.error(f"设备执行异常 {device_serial}: {e}")

    return results

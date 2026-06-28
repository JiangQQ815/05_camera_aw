#!/usr/bin/env python
"""
多设备相机测试运行器
支持:
- 自动发现多设备
- 用例分发到不同设备
- 并行/串行执行
- 结果汇总

使用方法:
    python run_tests.py                           # 自动发现设备执行
    python run_tests.py --devices ABC123,DEF456    # 指定设备
    python run_tests.py --mode smoke               # 冒烟测试
    python run_tests.py --mode photo              # 拍照测试
    python run_tests.py --parallel                # 并行执行
"""
import argparse
import subprocess
import sys
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """测试结果"""
    device: str
    case_id: str
    status: str  # PASSED, FAILED, ERROR
    message: str = ""


def get_connected_devices() -> List[str]:
    """获取所有连接的设备"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split("\n")[1:]
        devices = []
        for line in lines:
            if line.strip() and "device" in line:
                serial = line.split("\t")[0].strip()
                devices.append(serial)
        return devices
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return []


def run_tests_on_device(
    device_serial: str,
    test_cases: List[Dict],
    report_dir: str
) -> List[TestResult]:
    """
    在指定设备上运行测试用例
    """
    results = []

    logger.info(f"[{device_serial}] 初始化设备...")
    try:
        # 导入必要的模块
        sys.path.insert(0, os.path.dirname(__file__))
        from device_manager import device_manager

        device_info = device_manager.add_device(device_serial)
        driver = device_manager.get_driver(device_serial)

        if not driver:
            logger.error(f"[{device_serial}] 设备连接失败")
            return results

        from base.camera_aw import CameraAutomationAW
        cam = CameraAutomationAW(driver)

        logger.info(f"[{device_serial}] 开始执行 {len(test_cases)} 个用例")

        for case in test_cases:
            case_id = case.get("case_id", "UNKNOWN")
            try:
                logger.info(f"[{device_serial}] 执行: {case_id}")

                # 执行测试
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

                # 验证
                if cam.verify_thumbnail_updated() and not cam.check_camera_crash():
                    results.append(TestResult(
                        device=device_serial,
                        case_id=case_id,
                        status="PASSED"
                    ))
                    logger.info(f"[{device_serial}] ✓ {case_id} PASSED")
                else:
                    results.append(TestResult(
                        device=device_serial,
                        case_id=case_id,
                        status="FAILED",
                        message="验证失败"
                    ))
                    logger.error(f"[{device_serial}] ✗ {case_id} FAILED")

                device_manager.update_device_stats(device_serial, passed=True)

            except Exception as e:
                results.append(TestResult(
                    device=device_serial,
                    case_id=case_id,
                    status="ERROR",
                    message=str(e)
                ))
                logger.error(f"[{device_serial}] ✗ {case_id} ERROR: {e}")
                device_manager.update_device_stats(device_serial, passed=False)

        # 清理
        driver.app_stop("com.android.camera")
        device_manager.release_device(device_serial)

    except Exception as e:
        logger.error(f"[{device_serial}] 执行异常: {e}")

    return results


def distribute_cases(cases: List[Dict], devices: List[str]) -> Dict[str, List[Dict]]:
    """将用例均匀分发到多个设备"""
    distribution = {d: [] for d in devices}

    for i, case in enumerate(cases):
        target_device = devices[i % len(devices)]
        distribution[target_device].append(case)

    return distribution


def print_summary(results: List[TestResult], duration: float):
    """打印测试汇总"""
    passed = sum(1 for r in results if r.status == "PASSED")
    failed = sum(1 for r in results if r.status == "FAILED")
    errors = sum(1 for r in results if r.status == "ERROR")
    total = len(results)

    logger.info("=" * 60)
    logger.info("测试汇总")
    logger.info("=" * 60)
    logger.info(f"总用例数: {total}")
    logger.info(f"通过: {passed} ({passed/total*100:.1f}%)" if total > 0 else "通过: 0")
    logger.info(f"失败: {failed}")
    logger.info(f"错误: {errors}")
    logger.info(f"耗时: {duration:.1f}秒")
    logger.info("=" * 60)

    # 按设备汇总
    devices = set(r.device for r in results)
    for device in devices:
        device_results = [r for r in results if r.device == device]
        d_passed = sum(1 for r in device_results if r.status == "PASSED")
        d_total = len(device_results)
        logger.info(f"  {device}: {d_passed}/{d_total} 通过")


def main():
    parser = argparse.ArgumentParser(description="多设备相机测试运行器")
    parser.add_argument(
        "--devices",
        type=str,
        help="指定设备序列号，逗号分隔"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="smoke",
        choices=["smoke", "photo", "video", "night", "pro", "all"],
        help="测试模式"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行执行模式"
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="报告输出目录"
    )

    args = parser.parse_args()

    # 创建报告目录
    report_dir = args.report
    if not report_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(os.path.dirname(__file__), "reports", f"run_{timestamp}")

    os.makedirs(report_dir, exist_ok=True)
    logger.info(f"报告目录: {report_dir}")

    # 获取设备
    devices = []
    if args.devices:
        devices = [d.strip() for d in args.devices.split(",")]
    else:
        devices = get_connected_devices()

    if not devices:
        logger.error("没有找到可用设备！")
        sys.exit(1)

    logger.info(f"使用设备: {devices}")

    # 加载测试用例
    from config.test_data import (
        QUICK_TEST_CASES,
        PHOTO_MODE_CASES,
        VIDEO_MODE_CASES,
        NIGHT_MODE_CASES,
        PRO_MODE_CASES,
        ALL_TEST_CASES
    )

    case_map = {
        "smoke": QUICK_TEST_CASES,
        "photo": PHOTO_MODE_CASES,
        "video": VIDEO_MODE_CASES,
        "night": NIGHT_MODE_CASES,
        "pro": PRO_MODE_CASES,
        "all": ALL_TEST_CASES
    }

    test_cases = case_map.get(args.mode, QUICK_TEST_CASES)
    logger.info(f"加载 {len(test_cases)} 个测试用例")

    # 分发用例到设备
    distribution = distribute_cases(test_cases, devices)
    for device, cases in distribution.items():
        logger.info(f"  {device}: {len(cases)} 个用例")

    # 开始测试
    start_time = time.time()
    all_results = []

    if args.parallel:
        # 并行执行
        import threading
        threads = []

        for device, cases in distribution.items():
            if cases:
                t = threading.Thread(
                    target=lambda d, c: all_results.extend(
                        run_tests_on_device(d, c, report_dir)
                    ),
                    args=(device, cases)
                )
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

    else:
        # 串行执行
        for device, cases in distribution.items():
            if cases:
                results = run_tests_on_device(device, cases, report_dir)
                all_results.extend(results)

    duration = time.time() - start_time

    # 打印汇总
    print_summary(all_results, duration)

    # 保存结果
    result_file = os.path.join(report_dir, "results.txt")
    with open(result_file, "w", encoding="utf-8") as f:
        for r in all_results:
            f.write(f"[{r.device}] {r.case_id}: {r.status}\n")

    logger.info(f"结果已保存: {result_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
测试执行器 - 相机自动化测试的标准化执行流程
将6步测试流程封装为可复用模块
"""
import time
import logging
from dataclasses import dataclass
from typing import Optional

from base.camera_aw import CameraAutomationAW, CameraAWError


@dataclass
class TestResult:
    """测试执行结果"""
    case_id: str
    title: str
    passed: bool
    error_message: Optional[str] = None
    duration: float = 0.0

    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        msg = f"[{self.case_id}] {self.title}: {status}"
        if self.error_message:
            msg += f" - {self.error_message}"
        return msg


class CameraTestExecutor:
    """
    相机测试执行器

    封装标准的6步测试流程:
    Step 0: 环境检查 - 防止相机崩溃残留
    Step 1: 切换镜头（前置/后置）
    Step 2: 切换相机模式
    Step 3: 配置参数设置
    Step 4: 执行拍摄动作
    Step 5: 结果校验
    """

    def __init__(self, cam: CameraAutomationAW):
        """
        初始化执行器
        :param cam: CameraAutomationAW 实例
        """
        self.cam = cam
        self.logger = logging.getLogger("CameraTestExecutor")

    def execute(self, case: dict) -> TestResult:
        """
        执行单个测试用例
        :param case: 测试用例数据字典
        :return: TestResult 执行结果
        """
        start_time = time.time()
        case_id = case.get("case_id", "UNKNOWN")
        title = case.get("title", "")

        self.logger.info(f"[{case_id}] 开始执行: {title}")

        try:
            # Step 0: 环境检查
            self._step0_environment_check()

            # Step 1: 切换镜头
            self._step1_switch_lens(case.get("facing", "后置"))

            # Step 2: 切换模式
            self._step2_switch_mode(case.get("mode", "拍照"))

            # Step 3: 配置设置
            self._step3_configure_settings(case.get("settings", {}))

            # Step 4: 执行动作
            self._step4_execute_action(case)

            # Step 5: 验证结果
            self._step5_verify_result()

            duration = time.time() - start_time
            self.logger.info(f"[{case_id}] ✓ 通过 (耗时: {duration:.1f}s)")

            return TestResult(
                case_id=case_id,
                title=title,
                passed=True,
                duration=duration
            )

        except CameraAWError as e:
            duration = time.time() - start_time
            self.logger.error(f"[{case_id}] ✗ AW错误: {e}")
            return TestResult(
                case_id=case_id,
                title=title,
                passed=False,
                error_message=f"AW错误: {e}",
                duration=duration
            )

        except AssertionError as e:
            duration = time.time() - start_time
            self.logger.error(f"[{case_id}] ✗ 断言失败: {e}")
            return TestResult(
                case_id=case_id,
                title=title,
                passed=False,
                error_message=str(e),
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"[{case_id}] ✗ 异常: {e}")
            return TestResult(
                case_id=case_id,
                title=title,
                passed=False,
                error_message=f"异常: {e}",
                duration=duration
            )

    # ============================================
    # Step 0: 环境检查
    # ============================================

    def _step0_environment_check(self):
        """Step 0: 检查相机状态，防止崩溃残留"""
        if self.cam.check_camera_crash():
            self.logger.warning("检测到相机崩溃残留，尝试恢复...")
            self.cam.return_to_main界面()

        assert not self.cam.check_camera_crash(), "相机已崩溃"
        self.logger.debug("环境检查通过")

    # ============================================
    # Step 1: 切换镜头
    # ============================================

    def _step1_switch_lens(self, facing: str):
        """Step 1: 切换前后置摄像头"""
        self.cam.switch_camera_lens(facing)
        self.logger.debug(f"镜头切换完成: {facing}")

    # ============================================
    # Step 2: 切换模式
    # ============================================

    def _step2_switch_mode(self, mode: str):
        """Step 2: 切换相机模式"""
        self.cam.switch_to_mode(mode)
        self.logger.debug(f"模式切换完成: {mode}")

    # ============================================
    # Step 3: 配置设置
    # ============================================

    def _step3_configure_settings(self, settings: dict):
        """Step 3: 配置各种参数设置"""
        for option, value in settings.items():
            self.cam.set_camera_setting(option, value)
        self.logger.debug(f"参数配置完成: {settings}")

    # ============================================
    # Step 4: 执行动作
    # ============================================

    def _step4_execute_action(self, case: dict):
        """Step 4: 执行拍摄动作"""
        action = case.get("action")

        if action == "photo":
            self.cam.take_photo()
            self.logger.debug("拍照完成")

        elif action == "video":
            duration = case.get("video_duration", 3)
            self.cam.start_video_recording()
            self.cam.stop_video_recording(expect_duration=duration)
            self.logger.debug(f"录像完成 (时长: {duration}s)")

        elif action == "panorama":
            self.cam.start_panorama_capture()
            self.logger.debug("全景拍摄完成")

        else:
            raise CameraAWError(f"未知动作类型: {action}")

    # ============================================
    # Step 5: 验证结果
    # ============================================

    def _step5_verify_result(self):
        """Step 5: 验证测试结果"""
        # 等待文件保存
        time.sleep(1)

        # 验证缩略图更新
        assert self.cam.verify_thumbnail_updated(), \
            "缩略图未更新，可能拍摄未成功"

        # 验证相机未崩溃
        assert not self.cam.check_camera_crash(), \
            "相机发生崩溃"

        self.logger.debug("结果验证通过")

"""
CameraTestExecutor 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from base.test_executor import CameraTestExecutor, TestResult, CameraAWError
from base.camera_aw import CameraAutomationAW


class TestCameraTestExecutor:
    """CameraTestExecutor 测试套件"""

    @pytest.fixture
    def mock_cam(self, mock_driver):
        """创建 mock CameraAutomationAW"""
        cam = Mock(spec=CameraAutomationAW)
        cam.d = mock_driver
        cam.check_camera_crash = Mock(return_value=False)
        cam.switch_camera_lens = Mock()
        cam.switch_to_mode = Mock()
        cam.set_camera_setting = Mock()
        cam.take_photo = Mock()
        cam.start_video_recording = Mock()
        cam.stop_video_recording = Mock()
        cam.start_panorama_capture = Mock()
        cam.verify_thumbnail_updated = Mock(return_value=True)
        cam.return_to_main界面 = Mock()
        return cam

    @pytest.fixture
    def executor(self, mock_cam):
        """创建 CameraTestExecutor 实例"""
        return CameraTestExecutor(mock_cam)

    # ====== 正常流程测试 ======

    def test_execute_photo_success(self, executor, mock_cam, sample_photo_case):
        """测试拍照用例成功"""
        result = executor.execute(sample_photo_case)

        assert result.passed is True
        assert result.case_id == "PHOTO_001"
        assert result.duration > 0

    def test_execute_video_success(self, executor, mock_cam, sample_video_case):
        """测试录像用例成功"""
        result = executor.execute(sample_video_case)

        assert result.passed is True
        assert result.case_id == "VIDEO_001"
        mock_cam.start_video_recording.assert_called_once()
        mock_cam.stop_video_recording.assert_called_once_with(expect_duration=3)

    def test_execute_panorama(self, executor, mock_cam):
        """测试全景拍摄用例"""
        case = {
            "case_id": "PANO_001",
            "title": "全景拍摄",
            "facing": "后置",
            "mode": "全景",
            "settings": {},
            "action": "panorama"
        }
        result = executor.execute(case)

        assert result.passed is True
        mock_cam.start_panorama_capture.assert_called_once()

    # ====== 步骤测试 ======

    def test_step0_environment_check_recovery(self, executor, mock_cam):
        """Step 0: 相机崩溃时恢复"""
        mock_cam.check_camera_crash.return_value = True

        # 应该能恢复，不会抛异常
        executor._step0_environment_check()

        mock_cam.return_to_main界面.assert_called_once()

    def test_step0_environment_check_clear(self, executor, mock_cam):
        """Step 0: 相机正常"""
        mock_cam.check_camera_crash.return_value = False

        executor._step0_environment_check()

        # return_to_main界面 不应被调用
        mock_cam.return_to_main界面.assert_not_called()

    def test_step1_switch_lens(self, executor, mock_cam):
        """Step 1: 切换镜头"""
        executor._step1_switch_lens("前置")

        mock_cam.switch_camera_lens.assert_called_once_with("前置")

    def test_step2_switch_mode(self, executor, mock_cam):
        """Step 2: 切换模式"""
        executor._step2_switch_mode("夜景")

        mock_cam.switch_to_mode.assert_called_once_with("夜景")

    def test_step3_configure_settings(self, executor, mock_cam):
        """Step 3: 配置设置"""
        settings = {"闪光灯": "自动", "HDR": "开启"}

        executor._step3_configure_settings(settings)

        mock_cam.set_camera_setting.assert_any_call("闪光灯", "自动")
        mock_cam.set_camera_setting.assert_any_call("HDR", "开启")

    def test_step4_execute_photo(self, executor, mock_cam, sample_photo_case):
        """Step 4: 执行拍照"""
        executor._step4_execute_action(sample_photo_case)

        mock_cam.take_photo.assert_called_once()

    def test_step4_execute_video(self, executor, mock_cam, sample_video_case):
        """Step 4: 执行录像"""
        executor._step4_execute_action(sample_video_case)

        mock_cam.start_video_recording.assert_called_once()
        mock_cam.stop_video_recording.assert_called_once()

    def test_step5_verify_result_success(self, executor, mock_cam):
        """Step 5: 验证成功"""
        mock_cam.verify_thumbnail_updated.return_value = True
        mock_cam.check_camera_crash.return_value = False

        # 不应抛出异常
        executor._step5_verify_result()

    def test_step5_verify_thumbnail_failed(self, executor, mock_cam):
        """Step 5: 缩略图未更新"""
        mock_cam.verify_thumbnail_updated.return_value = False

        with pytest.raises(AssertionError, match="缩略图未更新"):
            executor._step5_verify_result()

    # ====== 异常处理测试 ======

    def test_execute_camera_aw_error(self, executor, mock_cam, sample_photo_case):
        """CameraAWError 捕获"""
        mock_cam.switch_camera_lens.side_effect = CameraAWError("切换镜头失败")

        result = executor.execute(sample_photo_case)

        assert result.passed is False
        assert "AW错误" in result.error_message
        assert "切换镜头失败" in result.error_message

    def test_execute_assertion_error(self, executor, mock_cam, sample_photo_case):
        """AssertionError 捕获"""
        mock_cam.verify_thumbnail_updated.side_effect = AssertionError("缩略图未更新")

        result = executor.execute(sample_photo_case)

        assert result.passed is False
        assert "断言失败" in result.error_message
        assert "缩略图未更新" in result.error_message

    def test_execute_generic_error(self, executor, mock_cam, sample_photo_case):
        """通用异常捕获"""
        mock_cam.switch_camera_lens.side_effect = Exception("未知错误")

        result = executor.execute(sample_photo_case)

        assert result.passed is False
        assert "异常" in result.error_message

    # ====== 参数化测试 ======

    @pytest.mark.parametrize("facing", ["后置", "前置"])
    def test_switch_lens_param(self, executor, mock_cam, facing):
        """参数化测试：切换不同镜头"""
        case = {
            "case_id": f"LENS_{facing}",
            "title": f"切换{facing}镜头",
            "facing": facing,
            "mode": "拍照",
            "settings": {},
            "action": "photo"
        }

        result = executor.execute(case)

        assert result.passed is True
        mock_cam.switch_camera_lens.assert_called_with(facing)

    @pytest.mark.parametrize("mode,action", [
        ("拍照", "photo"),
        ("录像", "video"),
        ("全景", "panorama"),
    ])
    def test_execute_modes_param(self, executor, mock_cam, mode, action):
        """参数化测试：不同模式"""
        case = {
            "case_id": f"MODE_{mode}",
            "title": f"{mode}模式测试",
            "facing": "后置",
            "mode": mode,
            "settings": {},
            "action": action
        }

        result = executor.execute(case)

        assert result.passed is True

    # ====== TestResult 测试 ======

    def test_test_result_str_pass(self):
        """TestResult 字符串表示 - 通过"""
        result = TestResult(
            case_id="TEST_001",
            title="测试用例",
            passed=True,
            duration=1.5
        )

        assert "PASS" in str(result)
        assert "TEST_001" in str(result)

    def test_test_result_str_fail(self):
        """TestResult 字符串表示 - 失败"""
        result = TestResult(
            case_id="TEST_002",
            title="测试用例",
            passed=False,
            error_message="断言失败",
            duration=0.5
        )

        assert "FAIL" in str(result)
        assert "断言失败" in str(result)
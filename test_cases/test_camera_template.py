"""
相机自动化测试用例 - 模板化设计
所有测试用例通过参数化驱动，只需修改 test_data 即可扩展
"""
import pytest
import logging

from base.camera_aw import CameraAutomationAW
from base.test_executor import CameraTestExecutor
from config.test_data import (
    ALL_TEST_CASES,
    QUICK_TEST_CASES,
    PHOTO_MODE_CASES,
    VIDEO_MODE_CASES,
    PORTRAIT_MODE_CASES,
    NIGHT_MODE_CASES,
    PRO_MODE_CASES,
    COMBO_CASES,
)

logger = logging.getLogger(__name__)


class TestCameraTemplate:
    """相机模板化测试用例"""

    @pytest.fixture
    def executor(self, camera_aw: CameraAutomationAW) -> CameraTestExecutor:
        """提供 CameraTestExecutor 实例"""
        return CameraTestExecutor(camera_aw)

    @pytest.mark.parametrize("case", QUICK_TEST_CASES, ids=lambda x: x["case_id"])
    def test_quick_smoke(self, executor: CameraTestExecutor, case):
        """快速冒烟测试 - 验证核心功能"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", PHOTO_MODE_CASES, ids=lambda x: x["case_id"])
    def test_photo_mode(self, executor: CameraTestExecutor, case):
        """拍照模式测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", VIDEO_MODE_CASES, ids=lambda x: x["case_id"])
    def test_video_mode(self, executor: CameraTestExecutor, case):
        """录像模式测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", PORTRAIT_MODE_CASES, ids=lambda x: x["case_id"])
    def test_portrait_mode(self, executor: CameraTestExecutor, case):
        """人像模式测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", NIGHT_MODE_CASES, ids=lambda x: x["case_id"])
    def test_night_mode(self, executor: CameraTestExecutor, case):
        """夜景模式测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", PRO_MODE_CASES, ids=lambda x: x["case_id"])
    def test_pro_mode(self, executor: CameraTestExecutor, case):
        """专业模式测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"

    @pytest.mark.parametrize("case", COMBO_CASES, ids=lambda x: x["case_id"])
    def test_combo_settings(self, executor: CameraTestExecutor, case):
        """组合设置测试"""
        result = executor.execute(case)
        assert result.passed, f"用例失败: {result.error_message}"


class TestCameraAll:
    """运行所有测试用例"""

    @pytest.fixture
    def executor(self, camera_aw: CameraAutomationAW) -> CameraTestExecutor:
        """提供 CameraTestExecutor 实例"""
        return CameraTestExecutor(camera_aw)

    @pytest.mark.parametrize("case", ALL_TEST_CASES, ids=lambda x: x["case_id"])
    def test_all_modes(self, executor: CameraTestExecutor, case):
        """运行所有模式的测试用例"""
        result = executor.execute(case)
        assert result.passed, f"{result.case_id}: {result.error_message}"

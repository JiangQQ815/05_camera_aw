"""
MediaVerifier 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from base.media_verifier import MediaVerifier, VerificationResult


def make_mock_element(exists=True):
    """创建 Mock UI 元素，exists() 返回布尔值"""
    elem = Mock()
    elem.exists = Mock(return_value=exists)
    elem.wait = Mock(return_value=exists)
    elem.click = Mock(return_value=True)
    elem.get_text = Mock(return_value="")
    return elem


class TestMediaVerifier:
    """MediaVerifier 测试套件"""

    @pytest.fixture
    def mock_driver(self):
        """创建 mock driver"""
        d = Mock()
        d.shell = Mock(return_value="")
        return d

    @pytest.fixture
    def verifier(self, mock_driver):
        """创建 MediaVerifier 实例"""
        return MediaVerifier(mock_driver)

    # ====== verify_photo_saved 测试 ======

    def test_verify_photo_saved_success(self, verifier, mock_driver):
        """照片验证成功"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/test.jpg",
            "15000",
        ])
        result = verifier.verify_photo_saved(min_size_kb=10)
        assert result.success is True

    def test_verify_photo_saved_file_too_small(self, verifier, mock_driver):
        """文件过小"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/small.jpg",
            "5000",
        ])
        result = verifier.verify_photo_saved(min_size_kb=10)
        assert result.success is False
        assert "文件过小" in result.error

    def test_verify_photo_saved_no_file(self, verifier, mock_driver):
        """未找到照片文件"""
        mock_driver.shell = Mock(return_value="")
        result = verifier.verify_photo_saved()
        assert result.success is False
        assert "未找到照片文件" in result.error

    def test_verify_photo_saved_jpeg_extension(self, verifier, mock_driver):
        """jpeg 扩展名"""
        mock_driver.shell = Mock(side_effect=[
            "",
            "/sdcard/DCIM/Camera/test.jpeg",
            "20000",
        ])
        result = verifier.verify_photo_saved(min_size_kb=10)
        assert result.success is True

    def test_verify_photo_saved_exception(self, verifier, mock_driver):
        """异常处理"""
        mock_driver.shell = Mock(side_effect=Exception("Device error"))
        result = verifier.verify_photo_saved()
        assert result.success is False

    # ====== verify_video_saved 测试 ======

    def test_verify_video_saved_success(self, verifier, mock_driver):
        """视频验证成功"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/test.mp4",
            "5000000",
            "3.5",
        ])
        result = verifier.verify_video_saved(min_duration_sec=1.0)
        assert result.success is True
        assert result.duration == 3.5

    def test_verify_video_saved_duration_too_short(self, verifier, mock_driver):
        """视频时长不足"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/short.mp4",
            "1000000",
            "0.5",
        ])
        result = verifier.verify_video_saved(min_duration_sec=1.0)
        assert result.success is False
        assert "视频过短" in result.error

    def test_verify_video_saved_no_file(self, verifier, mock_driver):
        """未找到视频文件"""
        mock_driver.shell = Mock(return_value="")
        result = verifier.verify_video_saved()
        assert result.success is False
        assert "未找到视频文件" in result.error

    def test_verify_video_saved_ffprobe_unavailable(self, verifier, mock_driver):
        """ffprobe 不可用"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/test.mp4",
            "5000000",
            "",
        ])
        result = verifier.verify_video_saved(min_duration_sec=1.0)
        assert result.success is True

    # ====== 内部方法测试 ======

    def test_find_dcim_path_success(self, verifier, mock_driver):
        """找到 DCIM 路径"""
        mock_driver.shell = Mock(return_value="Camera")
        path = verifier._find_dcim_path()
        assert path == "/sdcard/DCIM/Camera"

    def test_find_dcim_path_default(self, verifier, mock_driver):
        """默认 DCIM 路径"""
        mock_driver.shell = Mock(return_value="")
        path = verifier._find_dcim_path()
        assert path == MediaVerifier.DCIM_PATHS[0]

    def test_get_latest_file_success(self, verifier, mock_driver):
        """获取最新文件成功"""
        mock_driver.shell = Mock(side_effect=[
            "/sdcard/DCIM/Camera/latest.jpg",
            "12345",
        ])
        result = verifier._get_latest_file("/sdcard/DCIM/Camera", "jpg")
        assert result is not None
        assert result[0] == "/sdcard/DCIM/Camera/latest.jpg"

    def test_get_latest_file_not_found(self, verifier, mock_driver):
        """获取最新文件失败"""
        mock_driver.shell = Mock(return_value="")
        result = verifier._get_latest_file("/sdcard/DCIM/Camera", "jpg")
        assert result is None

    # ====== 工厂函数测试 ======

    def test_create_media_verifier(self, mock_driver):
        """工厂函数"""
        from base.media_verifier import create_media_verifier
        verifier = create_media_verifier(mock_driver)
        assert isinstance(verifier, MediaVerifier)


class TestVerificationResult:
    """VerificationResult 数据类测试"""

    def test_success_result(self):
        result = VerificationResult(success=True, file_path="/path/file.jpg", file_size=15000)
        assert result.success is True
        assert result.file_path == "/path/file.jpg"

    def test_failure_result(self):
        result = VerificationResult(success=False, error="File not found")
        assert result.success is False
        assert result.error == "File not found"

    def test_video_result_with_duration(self):
        result = VerificationResult(success=True, file_path="/path/video.mp4", file_size=5000000, duration=5.5)
        assert result.duration == 5.5

    def test_default_values(self):
        result = VerificationResult(success=True)
        assert result.file_path is None
        assert result.file_size == 0
        assert result.duration is None
        assert result.error is None
"""
CameraAutomationAW 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from base.camera_aw import CameraAutomationAW, CameraAWError


def make_mock_element(exists=True, text=""):
    """创建 Mock UI 元素，exists() 返回布尔值"""
    elem = Mock()
    elem.exists = Mock(return_value=exists)
    elem.wait = Mock(return_value=exists)
    elem.click = Mock(return_value=True)
    elem.get_text = Mock(return_value=text)
    elem.long_click = Mock(return_value=True)
    return elem


class TestCameraAutomationAW:
    """CameraAutomationAW 测试套件"""

    @pytest.fixture
    def mock_driver(self):
        """创建 mock driver"""
        d = Mock()
        d.info = {"deviceName": "test_device", "serial": "test_serial"}
        d.resource_id = MagicMock(side_effect=lambda rid: make_mock_element(False))
        d.xpath = MagicMock(side_effect=lambda xpath: make_mock_element(False))
        d.swipe = Mock()
        d(text=MagicMock(side_effect=lambda t: make_mock_element(False)))
        d.app_stop = Mock()
        d.app_start = Mock()
        return d

    @pytest.fixture
    def cam(self, mock_driver):
        """创建 CameraAutomationAW 实例"""
        return CameraAutomationAW(mock_driver)

    # ====== 初始化测试 ======

    def test_init(self, cam, mock_driver):
        """初始化"""
        assert cam.d == mock_driver
        assert cam._current_facing == "后置"
        assert cam._current_mode == "拍照"
        assert cam._settings_handler is None

    def test_settings_property(self, cam):
        """settings 属性延迟创建"""
        settings = cam.settings
        assert settings is not None
        assert cam._settings_handler is not None

    # ====== 基础操作测试 ======

    def test_find_element_exists(self, cam, mock_driver):
        """元素存在"""
        mock_driver.resource_id = MagicMock(return_value=make_mock_element(True))
        result = cam._find_element({"resource_id": "test_id"})
        assert result is True

    def test_find_element_not_exists(self, cam, mock_driver):
        """元素不存在"""
        result = cam._find_element({"resource_id": "nonexistent"})
        assert result is False

    def test_find_element_no_locator(self, cam, mock_driver):
        """无定位符"""
        result = cam._find_element({})
        assert result is False

    def test_click_element(self, cam, mock_driver):
        """点击元素"""
        elem = make_mock_element(True)
        mock_driver.resource_id = MagicMock(return_value=elem)
        result = cam._click_element({"resource_id": "test_id"})
        assert result is True

    def test_long_click_element(self, cam, mock_driver):
        """长按元素"""
        elem = make_mock_element(True)
        mock_driver.resource_id = MagicMock(return_value=elem)
        result = cam._long_click_element({"resource_id": "test_id"}, duration=2.0)
        assert result is True

    def test_swipe(self, cam, mock_driver):
        """滑动屏幕"""
        cam._swipe(100, 200, 300, 400, duration=0.5)
        mock_driver.swipe.assert_called_once_with(100, 200, 300, 400, duration=0.5)

    def test_get_element_text(self, cam, mock_driver):
        """获取元素文本"""
        elem = make_mock_element(True, "Test Text")
        mock_driver.resource_id = MagicMock(return_value=elem)
        text = cam._get_element_text({"resource_id": "test_id"})
        assert text == "Test Text"

    # ====== 切换镜头测试 ======

    def test_switch_camera_lens_same(self, cam, mock_driver):
        """切换到相同镜头"""
        cam._current_facing = "后置"
        cam.switch_camera_lens("后置")
        mock_driver.resource_id.assert_not_called()

    def test_switch_camera_lens_to_front(self, cam, mock_driver):
        """切换到前置镜头"""
        cam._click_element = Mock()
        cam.switch_camera_lens("前置")
        assert cam._current_facing == "前置"

    def test_switch_camera_lens_to_back(self, cam, mock_driver):
        """切换到后置镜头"""
        cam._current_facing = "前置"
        cam._click_element = Mock()
        cam.switch_camera_lens("后置")
        assert cam._current_facing == "后置"

    def test_switch_camera_lens_error(self, cam, mock_driver):
        """切换镜头失败"""
        cam._click_element = Mock(side_effect=Exception("Click failed"))
        with pytest.raises(CameraAWError):
            cam.switch_camera_lens("前置")

    # ====== 切换模式测试 ======

    def test_switch_to_mode_same(self, cam, mock_driver):
        """切换到相同模式"""
        cam._current_mode = "拍照"
        cam._click_element = Mock()
        cam.switch_to_mode("拍照")
        assert cam._click_element.call_count == 0

    def test_switch_to_mode_photo(self, cam, mock_driver):
        """切换到拍照模式"""
        cam._click_element = Mock()
        cam._is_mode_in_more = Mock(return_value=False)
        cam.switch_to_mode("拍照")
        assert cam._current_mode == "拍照"

    def test_switch_to_mode_video(self, cam, mock_driver):
        """切换到录像模式"""
        cam._click_element = Mock()
        cam._is_mode_in_more = Mock(return_value=False)
        cam.switch_to_mode("录像")
        assert cam._current_mode == "录像"

    def test_switch_to_mode_unsupported(self, cam, mock_driver):
        """不支持的模式"""
        with pytest.raises(CameraAWError, match="不支持的模式"):
            cam.switch_to_mode("不支持的模式")

    def test_switch_to_mode_in_more(self, cam, mock_driver):
        """模式在更多里面"""
        cam._click_element = Mock()
        cam._is_mode_in_more = Mock(return_value=True)
        cam.switch_to_mode("夜景")
        assert cam._click_element.call_count == 2

    def test_get_mode_locator(self, cam):
        """获取模式定位符"""
        locator = cam._get_mode_locator("夜景")
        assert locator is not None

    def test_get_mode_locator_unsupported(self, cam):
        """不支持的模式定位符"""
        locator = cam._get_mode_locator("不支持")
        assert locator is None

    def test_is_mode_in_more_true(self, cam, mock_driver):
        """模式在更多里"""
        cam._find_element = Mock(return_value=False)
        result = cam._is_mode_in_more("夜景")
        assert result is True

    def test_is_mode_in_more_false(self, cam, mock_driver):
        """模式不在更多里"""
        cam._find_element = Mock(return_value=True)
        result = cam._is_mode_in_more("拍照")
        assert result is False

    # ====== 设置参数测试 ======

    def test_set_camera_setting_flash(self, cam, mock_driver):
        """设置闪光灯"""
        cam._settings_handler = Mock()
        cam.settings.set_flash = Mock()
        cam.set_camera_setting("闪光灯", "自动")
        cam._settings_handler.set_flash.assert_called_once_with("自动")

    def test_set_camera_setting_hdr(self, cam, mock_driver):
        """设置 HDR"""
        cam._settings_handler = Mock()
        cam.set_camera_setting("HDR", "开启")
        cam._settings_handler.set_hdr.assert_called_once_with("开启")

    def test_set_camera_setting_unknown(self, cam, mock_driver):
        """未知设置项"""
        cam._settings_handler = Mock()
        cam.set_camera_setting("未知设置", "值")

    # ====== 快门操作测试 ======

    def test_click_shutter(self, cam, mock_driver):
        """点击快门"""
        cam._click_element = Mock()
        cam.click_shutter()
        cam._click_element.assert_called_once()

    def test_take_photo(self, cam, mock_driver):
        """拍照"""
        cam.click_shutter = Mock()
        cam.take_photo(post_wait=1)
        cam.click_shutter.assert_called_once()

    def test_take_photo_night_mode_extra_wait(self, cam, mock_driver):
        """夜景模式额外等待"""
        cam._current_mode = "夜景"
        cam.click_shutter = Mock()
        import time
        start = time.time()
        cam.take_photo(post_wait=1)
        duration = time.time() - start
        assert duration >= 3  # 1 + 2 extra

    def test_start_video_recording(self, cam, mock_driver):
        """开始录像"""
        cam._click_element = Mock()
        cam._find_element = Mock(return_value=True)
        cam.start_video_recording()
        cam._click_element.assert_called()

    def test_start_video_recording_failed(self, cam, mock_driver):
        """开始录像失败"""
        cam._click_element = Mock()
        cam._find_element = Mock(return_value=False)
        with pytest.raises(CameraAWError, match="录像未正常开始"):
            cam.start_video_recording()

    def test_stop_video_recording(self, cam, mock_driver):
        """停止录像"""
        cam._click_element = Mock()
        cam.stop_video_recording(expect_duration=3)
        cam._click_element.assert_called()

    def test_start_panorama_capture(self, cam, mock_driver):
        """开始全景拍摄"""
        cam.click_shutter = Mock()
        cam.start_panorama_capture()
        assert cam.click_shutter.call_count == 2

    # ====== 结果校验测试 ======

    def test_verify_thumbnail_updated_true(self, cam, mock_driver):
        """缩略图已更新"""
        cam._find_element = Mock(return_value=True)
        result = cam.verify_thumbnail_updated()
        assert result is True

    def test_verify_thumbnail_updated_false(self, cam, mock_driver):
        """缩略图未更新"""
        cam._find_element = Mock(return_value=False)
        result = cam.verify_thumbnail_updated()
        assert result is False

    def test_check_camera_crash_true(self, cam, mock_driver):
        """检测到崩溃"""
        cam._find_element = Mock(return_value=True)
        cam._click_element = Mock()
        result = cam.check_camera_crash()
        assert result is True
        cam._click_element.assert_called()

    def test_check_camera_crash_false(self, cam, mock_driver):
        """无崩溃"""
        cam._find_element = Mock(return_value=False)
        result = cam.check_camera_crash()
        assert result is False

    def test_check_camera_anr_true(self, cam, mock_driver):
        """检测到 ANR"""
        elem = make_mock_element(True)
        mock_driver.textContains = MagicMock(return_value=elem)
        result = cam.check_camera_anr()
        assert result is True

    def test_check_camera_anr_false(self, cam, mock_driver):
        """无 ANR"""
        mock_driver.textContains = MagicMock(return_value=make_mock_element(False))
        result = cam.check_camera_anr()
        assert result is False

    # ====== 辅助操作测试 ======

    def test_open_gallery(self, cam, mock_driver):
        """打开相册"""
        cam._click_element = Mock()
        cam.open_gallery()
        cam._click_element.assert_called()

    def test_close_gallery(self, cam, mock_driver):
        """关闭相册"""
        cam._click_element = Mock()
        cam.close_gallery()
        cam._click_element.assert_called()

    def test_return_to_main_interface(self, cam, mock_driver):
        """返回主界面"""
        call_count = [0]
        def fake_find(locator, timeout=1):
            call_count[0] += 1
            return call_count[0] <= 2
        cam._find_element = Mock(side_effect=fake_find)
        cam._click_element = Mock()
        cam.return_to_main界面()
        assert cam._find_element.call_count >= 2

    def test_switch_to_video_shutter(self, cam, mock_driver):
        """切换到录像快门"""
        cam._click_element = Mock()
        cam.switch_to_video_shutter()
        cam._click_element.assert_called()

    def test_get_current_facing(self, cam):
        """获取当前镜头"""
        assert cam.get_current_facing() == "后置"

    def test_get_current_mode(self, cam):
        """获取当前模式"""
        assert cam.get_current_mode() == "拍照"


class TestCameraAWError:
    """CameraAWError 异常测试"""

    def test_camera_aw_error(self):
        """异常创建"""
        error = CameraAWError("测试错误")
        assert str(error) == "测试错误"
        assert isinstance(error, Exception)
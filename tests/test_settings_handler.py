"""
SettingsHandler 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from base.settings_handler import SettingsHandler


def make_mock_element(exists=True):
    """创建 Mock UI 元素，exists() 返回布尔值"""
    elem = Mock()
    elem.exists = Mock(return_value=exists)
    elem.wait = Mock(return_value=exists)
    elem.click = Mock(return_value=True)
    elem.get_text = Mock(return_value="")
    elem.long_click = Mock(return_value=True)
    return elem


class TestSettingsHandler:
    """SettingsHandler 测试套件"""

    @pytest.fixture
    def mock_driver(self):
        """创建 mock driver"""
        d = Mock()
        d.resource_id = MagicMock(side_effect=lambda rid: make_mock_element(False))
        d.xpath = MagicMock(side_effect=lambda xpath: make_mock_element(False))
        d(text=MagicMock(side_effect=lambda t: make_mock_element(False)))
        d.app_stop = Mock()
        d.app_start = Mock()
        d.swipe = Mock()
        return d

    @pytest.fixture
    def handler(self, mock_driver):
        """创建 SettingsHandler 实例"""
        return SettingsHandler(mock_driver)

    # ====== 初始化测试 ======

    def test_init(self, handler, mock_driver):
        """初始化"""
        assert handler.d == mock_driver
        assert handler._is_settings_open is False

    def test_find_element_exists(self, handler, mock_driver):
        """元素存在"""
        mock_driver.resource_id = MagicMock(return_value=make_mock_element(True))
        result = handler._find_element({"resource_id": "test_id"})
        assert result is True

    def test_find_element_not_exists(self, handler, mock_driver):
        """元素不存在"""
        result = handler._find_element({"resource_id": "nonexistent"})
        assert result is False

    def test_find_element_no_locator(self, handler, mock_driver):
        """无定位符"""
        result = handler._find_element({})
        assert result is False

    def test_click_element_resource_id(self, handler, mock_driver):
        """点击 resource_id 元素"""
        elem = make_mock_element(True)
        mock_driver.resource_id = MagicMock(return_value=elem)
        result = handler._click_element({"resource_id": "test_id"})
        assert result is True

    def test_click_element_xpath(self, handler, mock_driver):
        """点击 xpath 元素"""
        elem = make_mock_element(True)
        mock_driver.xpath = MagicMock(return_value=elem)
        result = handler._click_element({"xpath": "//test"})
        assert result is True

    def test_click_element_no_locator(self, handler, mock_driver):
        """无定位符点击"""
        result = handler._click_element({})
        assert result is False

    # ====== open/close 测试 ======

    def test_open_settings(self, handler, mock_driver):
        """打开设置"""
        elem = make_mock_element(True)
        mock_driver.resource_id = MagicMock(return_value=elem)
        handler.open()
        assert handler._is_settings_open is True

    def test_close_settings(self, handler, mock_driver):
        """关闭设置"""
        handler._is_settings_open = True
        elem = make_mock_element(True)
        mock_driver.resource_id = MagicMock(return_value=elem)
        handler.close()
        assert handler._is_settings_open is False

    # ====== 设置方法测试 ======

    def test_set_flash_auto(self, handler, mock_driver):
        """设置闪光灯自动"""
        handler._click_element = Mock()
        handler.set_flash("自动")
        assert handler._click_element.called

    def test_set_flash_on(self, handler, mock_driver):
        """设置闪光灯开启"""
        handler._click_element = Mock()
        handler.set_flash("开启")
        assert handler._click_element.called

    def test_set_flash_off(self, handler, mock_driver):
        """设置闪光灯关闭"""
        handler._click_element = Mock()
        handler.set_flash("关闭")
        assert handler._click_element.called

    def test_set_hdr(self, handler, mock_driver):
        """设置 HDR"""
        handler._click_element = Mock()
        handler.set_hdr("开启")
        assert handler._click_element.called

    def test_set_aspect_ratio(self, handler, mock_driver):
        """设置画幅比例"""
        handler._click_element = Mock()
        mock_driver(text=MagicMock(return_value=make_mock_element(True)))
        handler.set_aspect_ratio("4:3")
        assert handler._click_element.called

    def test_set_timer_off(self, handler, mock_driver):
        """设置定时关闭"""
        handler._click_element = Mock()
        handler.set_timer("关闭")
        assert handler._click_element.called

    def test_set_timer_3s(self, handler, mock_driver):
        """设置定时3秒"""
        handler._click_element = Mock()
        handler.set_timer("3秒")
        assert handler._click_element.called

    def test_set_timer_10s(self, handler, mock_driver):
        """设置定时10秒"""
        handler._click_element = Mock()
        handler.set_timer("10秒")
        assert handler._click_element.called

    def test_set_ai(self, handler, mock_driver):
        """设置 AI"""
        handler._find_element = Mock(return_value=True)
        handler._click_element = Mock()
        handler.set_ai("开启")

    def test_set_watermark(self, handler, mock_driver):
        """设置水印"""
        handler._click_element = Mock()
        handler.set_watermark("开启")
        assert handler._click_element.called

    def test_set_beauty(self, handler, mock_driver):
        """设置美颜"""
        handler._click_element = Mock()
        handler.set_beauty("开启")
        assert handler._click_element.called

    def test_set_iso(self, handler, mock_driver):
        """设置 ISO"""
        handler._click_element = Mock()
        mock_driver(text=MagicMock(return_value=make_mock_element(True)))
        handler.set_iso("自动")
        assert handler._click_element.called

    def test_set_white_balance(self, handler, mock_driver):
        """设置白平衡"""
        handler._click_element = Mock()
        mock_driver(text=MagicMock(return_value=make_mock_element(True)))
        handler.set_white_balance("自动")
        assert handler._click_element.called

    def test_set_af(self, handler, mock_driver):
        """设置对焦模式"""
        handler._click_element = Mock()
        mock_driver(text=MagicMock(return_value=make_mock_element(True)))
        handler.set_af("自动")
        assert handler._click_element.called

    def test_set_ev(self, handler, mock_driver):
        """设置曝光补偿"""
        handler._click_element = Mock()
        handler.set_ev("+1")
        assert handler._click_element.called

    # ====== 异常处理测试 ======

    def test_click_element_exception(self, handler, mock_driver):
        """点击异常"""
        elem = Mock()
        elem.exists = Mock(return_value=True)
        elem.click = Mock(side_effect=Exception("Click failed"))
        mock_driver.resource_id = MagicMock(return_value=elem)
        with pytest.raises(Exception):
            handler._click_element({"resource_id": "test_id"})

    # ====== 工厂函数测试 ======

    def test_create_settings_handler(self, mock_driver):
        """工厂函数"""
        from base.settings_handler import create_settings_handler
        handler = create_settings_handler(mock_driver)
        assert isinstance(handler, SettingsHandler)
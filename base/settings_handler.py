"""
设置处理器 - 相机参数设置适配器
将各种相机设置操作封装为统一的接口
"""
import time
import logging
from typing import Protocol, Dict, Any

from config.locators import *


class SettingsHandlerProtocol(Protocol):
    """设置处理器接口"""
    def open(self) -> None: ...
    def close(self) -> None: ...
    def set_flash(self, value: str) -> None: ...
    def set_hdr(self, value: str) -> None: ...
    def set_aspect_ratio(self, value: str) -> None: ...
    def set_timer(self, value: str) -> None: ...
    def set_ai(self, value: str) -> None: ...
    def set_watermark(self, value: str) -> None: ...
    def set_beauty(self, value: str) -> None: ...
    def set_iso(self, value: str) -> None: ...
    def set_white_balance(self, value: str) -> None: ...
    def set_af(self, value: str) -> None: ...
    def set_ev(self, value: str) -> None: ...


class SettingsHandler:
    """
    设置处理器实现

    封装所有相机参数设置操作，提供统一接口
    """

    def __init__(self, driver):
        """
        初始化设置处理器
        :param driver: uiautomator2 的 d 对象
        """
        self.d = driver
        self.logger = logging.getLogger("SettingsHandler")
        self._is_settings_open = False

    # ============================================
    # 基础操作
    # ============================================

    def _find_element(self, locator: Dict, timeout: float = 5) -> bool:
        """查找元素是否存在"""
        try:
            if locator.get("resource_id"):
                self.d(resource_id=locator["resource_id"]).wait(timeout=timeout)
                return self.d(resource_id=locator["resource_id"]).exists()
            elif locator.get("xpath"):
                self.d.xpath(locator["xpath"]).wait(timeout=timeout)
                return self.d.xpath(locator["xpath"]).exists()
            return False
        except Exception:
            return False

    def _click_element(self, locator: Dict, timeout: float = 5) -> bool:
        """点击元素"""
        try:
            if locator.get("resource_id"):
                self.d(resource_id=locator["resource_id"]).click(timeout=timeout)
                return True
            elif locator.get("xpath"):
                self.d.xpath(locator["xpath"]).click(timeout=timeout)
                return True
            return False
        except Exception as e:
            self.logger.error(f"点击元素失败: {locator.get('desc', 'unknown')}, error: {e}")
            raise

    def _open_settings_if_needed(self):
        """打开设置菜单（如果当前不在设置界面）"""
        if self._is_settings_open:
            return
        if not self._find_element(SETTING_ICON, timeout=1):
            return
        self._click_element(SETTING_ICON)
        time.sleep(0.5)
        self._is_settings_open = True

    def _close_settings(self):
        """关闭设置菜单"""
        if not self._is_settings_open:
            return
        try:
            if self._find_element(BACK_BUTTON, timeout=1):
                self._click_element(BACK_BUTTON)
            elif self._find_element(CLOSE_BUTTON, timeout=1):
                self._click_element(CLOSE_BUTTON)
            time.sleep(0.3)
            self._is_settings_open = False
        except:
            pass

    def open(self):
        """显式打开设置菜单"""
        self._click_element(SETTING_ICON)
        time.sleep(0.5)
        self._is_settings_open = True

    def close(self):
        """关闭设置菜单"""
        self._close_settings()

    # ============================================
    # 设置方法
    # ============================================

    def set_flash(self, value: str):
        """设置闪光灯: 自动/开启/关闭"""
        self._click_element(SETTING_FLASH)
        time.sleep(0.3)

        flash_options = {
            "自动": SETTING_FLASH_AUTO,
            "开启": SETTING_FLASH_ON,
            "关闭": SETTING_FLASH_OFF,
        }

        option = flash_options.get(value)
        if option:
            self._click_element(option)
            self.logger.info(f"闪光灯设置为: {value}")
        time.sleep(0.3)

    def set_hdr(self, value: str):
        """设置HDR"""
        self._click_element(SETTING_HDR)
        time.sleep(0.3)
        self.logger.info(f"HDR设置为: {value}")
        time.sleep(0.3)

    def set_aspect_ratio(self, value: str):
        """设置画幅比例: 4:3/16:9/1:1"""
        self._click_element(SETTING_ASPECT_RATIO)
        time.sleep(0.3)

        aspect_options = {
            "4:3": {"text": "4:3"},
            "16:9": {"text": "16:9"},
            "1:1": {"text": "1:1"},
        }

        option = aspect_options.get(value)
        if option:
            self.d(text=option["text"]).click()
            self.logger.info(f"画幅设置为: {value}")
        time.sleep(0.3)

    def set_timer(self, value: str):
        """设置定时: 关闭/3秒/10秒"""
        self._click_element(SETTING_TIMER)
        time.sleep(0.3)

        timer_options = {
            "关闭": SETTING_TIMER_OFF,
            "3秒": SETTING_TIMER_3S,
            "10秒": SETTING_TIMER_10S,
        }

        option = timer_options.get(value)
        if option:
            self._click_element(option)
            self.logger.info(f"定时设置为: {value}")
        time.sleep(0.3)

    def set_ai(self, value: str):
        """设置AI摄影大师: 开启/关闭"""
        if self._find_element(SETTING_AI, timeout=1):
            current_state = self._get_ai_state()
            if (value == "开启" and not current_state) or (value == "关闭" and current_state):
                self._click_element(SETTING_AI)
        self.logger.info(f"AI设置为: {value}")

    def _get_ai_state(self) -> bool:
        """获取AI当前状态"""
        try:
            ai_element = self.d(resource_id=SETTING_AI["resource_id"])
            return False
        except:
            return False

    def set_watermark(self, value: str):
        """设置水印"""
        self._click_element(SETTING_WATERMARK)
        time.sleep(0.3)
        self.logger.info(f"水印设置为: {value}")

    def set_beauty(self, value: str):
        """设置美颜"""
        self._click_element(SETTING_BEAUTY)
        time.sleep(0.3)
        self.logger.info(f"美颜级别设置为: {value}")

    def set_iso(self, value: str):
        """设置ISO: 自动/100/200/400/800/1600/3200"""
        self._click_element(SETTING_ISO)
        time.sleep(0.3)

        iso_options = ["自动", "100", "200", "400", "800", "1600", "3200"]
        if value in iso_options:
            self.d(text=value).click()
            self.logger.info(f"ISO设置为: {value}")
        time.sleep(0.3)

    def set_white_balance(self, value: str):
        """设置白平衡: 自动/白炽灯/日光/阴天/荧光灯"""
        self._click_element(SETTING_WB)
        time.sleep(0.3)

        wb_options = ["自动", "白炽灯", "日光", "阴天", "荧光灯"]
        if value in wb_options:
            self.d(text=value).click()
            self.logger.info(f"白平衡设置为: {value}")
        time.sleep(0.3)

    def set_af(self, value: str):
        """设置对焦模式: 自动/手动"""
        self._click_element(SETTING_AF)
        time.sleep(0.3)

        af_options = ["自动", "手动"]
        if value in af_options:
            self.d(text=value).click()
            self.logger.info(f"对焦模式设置为: {value}")
        time.sleep(0.3)

    def set_ev(self, value: str):
        """设置曝光补偿"""
        self._click_element(SETTING_EV)
        time.sleep(0.3)
        self.logger.info(f"EV设置为: {value}")
        time.sleep(0.3)


# ============================================
# 默认设置处理器工厂
# ============================================

def create_settings_handler(driver) -> SettingsHandler:
    """创建设置处理器实例"""
    return SettingsHandler(driver)

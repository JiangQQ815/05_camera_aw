"""
设置处理器 - 相机参数设置适配器
将各种相机设置操作封装为统一的接口
"""
import time
import logging
from typing import Protocol, Dict, Any, Optional

from config.locators import *
from base.ui_element import UIElementOperations


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


class SettingsHandler(UIElementOperations):
    """
    设置处理器实现

    封装所有相机参数设置操作，提供统一接口

    注意: _is_settings_open 状态追踪是最佳努力机制，
    可能因 atx-agent 死亡或相机崩溃而失去同步。
    使用 try/finally 确保操作后状态重置。
    """

    SETTINGS_ENTRIES = [
        SETTING_FLASH, SETTING_HDR, SETTING_ASPECT_RATIO, SETTING_TIMER,
        SETTING_AI, SETTING_WATERMARK, SETTING_BEAUTY, SETTING_ISO,
        SETTING_WB, SETTING_AF, SETTING_EV
    ]

    def __init__(self, driver):
        """
        初始化设置处理器
        :param driver: uiautomator2 的 d 对象
        """
        self.d = driver
        super().__init__()
        self.logger = logging.getLogger("SettingsHandler")
        self._is_settings_open = False

    def _verify_settings_open(self) -> bool:
        """
        验证设置菜单是否真正打开（检测状态同步失败）

        Returns:
            bool: 设置菜单是否打开
        """
        # 检查设置菜单中的任一元素是否存在
        for entry in self.SETTINGS_ENTRIES:
            if self._find_element(entry, timeout=0.5):
                return True
        return False

    def _sync_settings_state(self) -> bool:
        """
        同步设置状态

        Returns:
            bool: 当前设置菜单是否打开
        """
        actual_state = self._verify_settings_open()
        if self._is_settings_open and not actual_state:
            self.logger.warning("检测到设置状态不同步: 状态为打开但实际已关闭")
            self._is_settings_open = False
        elif not self._is_settings_open and actual_state:
            self.logger.warning("检测到设置状态不同步: 状态为关闭但实际已打开")
            self._is_settings_open = True
        return actual_state

    def _open_settings_if_needed(self):
        """打开设置菜单（如果当前不在设置界面）"""
        if self._sync_settings_state():
            return  # 已经打开

        if not self._find_element(SETTING_ICON, timeout=1):
            return

        try:
            self._click_element(SETTING_ICON)
            time.sleep(0.5)
            self._is_settings_open = self._verify_settings_open()
        except Exception as e:
            self.logger.error(f"打开设置菜单失败: {e}")
            self._is_settings_open = self._verify_settings_open()
            raise

    def _close_settings(self):
        """关闭设置菜单"""
        if not self._sync_settings_state():
            return

        try:
            if self._find_element(BACK_BUTTON, timeout=1):
                self._click_element(BACK_BUTTON)
            elif self._find_element(CLOSE_BUTTON, timeout=1):
                self._click_element(CLOSE_BUTTON)
            time.sleep(0.3)
        except Exception as e:
            self.logger.warning(f"关闭设置菜单时出错: {e}")
        finally:
            # 无论成功与否，验证实际状态
            self._is_settings_open = self._verify_settings_open()

    def open(self):
        """显式打开设置菜单"""
        self._click_element(SETTING_ICON)
        time.sleep(0.5)
        self._is_settings_open = self._verify_settings_open()

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
            "4:3": {"text": "4:3", "desc": "画幅4:3"},
            "16:9": {"text": "16:9", "desc": "画幅16:9"},
            "1:1": {"text": "1:1", "desc": "画幅1:1"},
        }

        option = aspect_options.get(value)
        if option:
            # 使用带重试机制的点击（避免 atx-agent 死亡导致失败）
            self._click_element({"text": option["text"], "desc": option["desc"]})
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
        """
        获取AI摄影大师当前状态

        通过检查元素的 selected 属性或 content-desc 判断是否开启

        Returns:
            bool: AI 是否已开启
        """
        try:
            ai_element = self.d(resourceId=SETTING_AI["resource_id"])
            # 尝试获取 selected 状态（ToggleButton 的选中状态）
            if hasattr(ai_element, 'selected'):
                return bool(ai_element.selected)
            # 备选：检查 content-desc 是否包含 "开启" 或 "on"
            info = ai_element.info
            if info:
                content_desc = info.get('contentDescription', '') or ''
                text = info.get('text', '') or ''
                return '开' in content_desc or 'on' in content_desc.lower() or '开启' in text
            return False
        except Exception as e:
            self.logger.debug(f"获取AI状态失败: {e}")
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
            # 使用带重试机制的点击（避免 atx-agent 死亡导致失败）
            self._click_element({"text": value, "desc": f"ISO_{value}"})
            self.logger.info(f"ISO设置为: {value}")
        time.sleep(0.3)

    def set_white_balance(self, value: str):
        """设置白平衡: 自动/白炽灯/日光/阴天/荧光灯"""
        self._click_element(SETTING_WB)
        time.sleep(0.3)

        wb_options = ["自动", "白炽灯", "日光", "阴天", "荧光灯"]
        if value in wb_options:
            # 使用带重试机制的点击（避免 atx-agent 死亡导致失败）
            self._click_element({"text": value, "desc": f"WB_{value}"})
            self.logger.info(f"白平衡设置为: {value}")
        time.sleep(0.3)

    def set_af(self, value: str):
        """设置对焦模式: 自动/手动"""
        self._click_element(SETTING_AF)
        time.sleep(0.3)

        af_options = ["自动", "手动"]
        if value in af_options:
            # 使用带重试机制的点击（避免 atx-agent 死亡导致失败）
            self._click_element({"text": value, "desc": f"AF_{value}"})
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

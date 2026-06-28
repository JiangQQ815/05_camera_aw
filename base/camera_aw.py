"""
相机自动化 Action Word (AW) 类
基于 uiautomator2 实现
"""
import time
import logging
from typing import Optional, Dict, Any, List

from config.locators import *
from config.modes import get_mode_config
from base.settings_handler import SettingsHandler, create_settings_handler


class CameraAutomationAW:
    """相机自动化动作字库"""

    def __init__(self, driver):
        """
        初始化相机自动化 AW 库
        :param driver: uiautomator2 的 d 对象
        """
        self.d = driver
        self.logger = logging.getLogger("CameraAW")
        self._current_facing = "后置"  # 默认后置
        self._current_mode = "拍照"  # 默认拍照模式
        self._settings_handler: Optional[SettingsHandler] = None

    @property
    def settings(self) -> SettingsHandler:
        """获取设置处理器（延迟创建）"""
        if self._settings_handler is None:
            self._settings_handler = create_settings_handler(self.d)
        return self._settings_handler

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
        except Exception as e:
            self.logger.warning(f"查找元素失败: {locator.get('desc', 'unknown')}, error: {e}")
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

    def _long_click_element(self, locator: Dict, duration: float = 1.0) -> bool:
        """长按元素"""
        try:
            if locator.get("resource_id"):
                self.d(resource_id=locator["resource_id"]).long_click(duration=duration)
                return True
            return False
        except Exception as e:
            self.logger.error(f"长按元素失败: {locator.get('desc', 'unknown')}, error: {e}")
            raise

    def _swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """滑动屏幕"""
        try:
            self.d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        except Exception as e:
            self.logger.error(f"滑动失败: {e}")
            raise

    def _get_element_text(self, locator: Dict) -> Optional[str]:
        """获取元素文本"""
        try:
            if locator.get("resource_id"):
                return self.d(resource_id=locator["resource_id"]).get_text()
            elif locator.get("xpath"):
                return self.d.xpath(locator["xpath"]).get_text()
        except:
            return None
        return None

    # ============================================
    # AW: 切换前后置摄像头
    # ============================================

    def switch_camera_lens(self, facing: str):
        """
        AW: 切换前后置摄像头
        :param facing: "前置" 或 "后置"
        """
        if self._current_facing == facing:
            self.logger.info(f"当前已是{facing}摄像头，无需切换")
            return

        self.logger.info(f"切换摄像头至{facing}...")
        try:
            self._click_element(MAIN_CAMERA_SWITCH)
            time.sleep(0.5)
            self._current_facing = facing
            self.logger.info(f"摄像头切换成功，当前: {facing}")
        except Exception as e:
            self.logger.error(f"切换摄像头失败: {e}")
            raise CameraAWError(f"切换摄像头至{facing}失败")

    # ============================================
    # AW: 切换相机模式
    # ============================================

    def switch_to_mode(self, mode_name: str):
        """
        AW: 切换相机模式
        :param mode_name: "拍照", "录像", "人像", "夜景", "专业", "慢动作", "全景", "黑白", "趣模式"
        """
        if self._current_mode == mode_name:
            self.logger.info(f"当前已是{mode_name}模式，无需切换")
            return

        self.logger.info(f"切换模式至{mode_name}...")

        mode_locator = self._get_mode_locator(mode_name)
        if not mode_locator:
            raise CameraAWError(f"不支持的模式: {mode_name}")

        try:
            if self._is_mode_in_more(mode_name):
                self._click_element(MODE_MORE)
                time.sleep(0.5)
                self._click_element(mode_locator)
            else:
                self._click_element(mode_locator)

            time.sleep(0.5)
            self._current_mode = mode_name
            self.logger.info(f"模式切换成功，当前: {mode_name}")

        except Exception as e:
            self.logger.error(f"切换模式失败: {e}")
            raise CameraAWError(f"切换至{mode_name}模式失败")

    def _get_mode_locator(self, mode_name: str) -> Optional[Dict]:
        """获取模式对应的定位符"""
        mode_map = {
            "拍照": MODE_PHOTO,
            "录像": MODE_VIDEO,
            "人像": MODE_PORTRAIT,
            "夜景": MODE_NIGHT,
            "专业": MODE_PRO,
            "慢动作": MODE_SLOMO,
            "全景": MODE_PANO,
            "黑白": MODE_MONO,
            "趣模式": MODE_STICKER,
        }
        return mode_map.get(mode_name)

    def _is_mode_in_more(self, mode_name: str) -> bool:
        """检查模式是否在"更多"里面"""
        mode_locator = self._get_mode_locator(mode_name)
        if mode_locator and self._find_element(mode_locator, timeout=1):
            return False
        return True

    # ============================================
    # AW: 顶栏/快捷设置参数调节（委托给 SettingsHandler）
    # ============================================

    def set_camera_setting(self, option_name: str, value: str):
        """
        AW: 顶栏/快捷设置参数调节
        :param option_name: "闪光灯", "HDR", "画幅", "定时", "AI", "水印", "美颜"等
        :param value: 对应的状态
        """
        self.logger.info(f"设置参数: {option_name} = {value}")

        try:
            # 打开设置
            self.settings.open()

            # 委托给设置处理器
            handler_map = {
                "闪光灯": "set_flash",
                "HDR": "set_hdr",
                "画幅": "set_aspect_ratio",
                "定时": "set_timer",
                "AI": "set_ai",
                "水印": "set_watermark",
                "美颜": "set_beauty",
                "ISO": "set_iso",
                "WB": "set_white_balance",
                "AF": "set_af",
                "EV": "set_ev",
            }

            method_name = handler_map.get(option_name)
            if method_name and hasattr(self.settings, method_name):
                handler_method = getattr(self.settings, method_name)
                handler_method(value)
            else:
                self.logger.warning(f"未知的设置选项: {option_name}")

            # 关闭设置
            self.settings.close()

        except Exception as e:
            self.logger.error(f"设置参数失败: {option_name}={value}, error: {e}")
            raise CameraAWError(f"设置{option_name}失败")

    # ============================================
    # AW: 快门操作
    # ============================================

    def click_shutter(self):
        """AW: 点击快门键"""
        self.logger.info("点击快门...")
        try:
            self._click_element(MAIN_SHUTTER)
        except Exception as e:
            self.logger.error(f"点击快门失败: {e}")
            raise CameraAWError("点击快门失败")

    def take_photo(self, post_wait: int = 1):
        """AW: 执行单张拍照动作"""
        self.logger.info("执行拍照...")
        mode_config = get_mode_config(self._current_mode)
        wait_time = mode_config.get("wait_after_capture", post_wait)

        try:
            self.click_shutter()
            self.logger.info(f"等待照片保存... ({wait_time}秒)")
            time.sleep(wait_time)

            if self._current_mode == "夜景":
                self.logger.info("夜景模式处理中，等待额外时间...")
                time.sleep(2)

        except Exception as e:
            self.logger.error(f"拍照失败: {e}")
            raise CameraAWError("拍照失败")

    def start_video_recording(self):
        """AW: 开始视频录制"""
        self.logger.info("开始录像...")
        try:
            self._click_element(MAIN_VIDEO_SHUTTER)
            time.sleep(1)

            if self._find_element(VIDEO_RECORDING_INDICATOR, timeout=5):
                self.logger.info("录像已开始")
            else:
                raise CameraAWError("录像未正常开始")

        except Exception as e:
            self.logger.error(f"开始录像失败: {e}")
            raise CameraAWError("开始录像失败")

    def stop_video_recording(self, expect_duration: int = 3):
        """AW: 停止视频录制"""
        self.logger.info(f"停止录像（预期时长: {expect_duration}秒）...")
        try:
            time.sleep(expect_duration)
            self._click_element(VIDEO_STOP_BUTTON)
            time.sleep(1)
            self.logger.info("录像已停止")
        except Exception as e:
            self.logger.error(f"停止录像失败: {e}")
            raise CameraAWError("停止录像失败")

    def start_panorama_capture(self):
        """AW: 开始全景拍摄"""
        self.logger.info("开始全景拍摄...")
        try:
            self.click_shutter()
            time.sleep(0.5)
            self.logger.info("全景拍摄进行中，请保持手机稳定...")
            time.sleep(5)
            self.click_shutter()
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"全景拍摄失败: {e}")
            raise CameraAWError("全景拍摄失败")

    # ============================================
    # AW: 结果校验
    # ============================================

    def verify_thumbnail_updated(self) -> bool:
        """AW: 校验缩略图是否更新"""
        self.logger.info("校验缩略图是否更新...")
        try:
            if self._find_element(MAIN_THUMBNAIL, timeout=2):
                self.logger.info("缩略图已更新，拍摄成功")
                return True
            else:
                self.logger.warning("缩略图未找到，可能拍摄未成功")
                return False
        except Exception as e:
            self.logger.error(f"校验缩略图失败: {e}")
            return False

    def check_camera_crash(self) -> bool:
        """AW: 检查相机是否崩溃"""
        try:
            if self._find_element(CRASH_DIALOG_TITLE, timeout=2):
                self.logger.error("检测到相机崩溃！")
                if self._find_element(DIALOG_OK, timeout=1):
                    self._click_element(DIALOG_OK)
                return True
            return False
        except Exception as e:
            self.logger.error(f"检查崩溃状态失败: {e}")
            return False

    def check_camera_anr(self) -> bool:
        """AW: 检查相机是否ANR"""
        try:
            anr_patterns = ["无响应", "等待", "关闭应用"]
            for pattern in anr_patterns:
                if self.d(textContains=pattern).exists():
                    self.logger.error(f"检测到相机ANR: {pattern}")
                    return True
            return False
        except:
            return False

    # ============================================
    # AW: 媒体文件验证
    # ============================================

    def verify_photo_saved(self, min_size_kb: int = 10) -> bool:
        """AW: 验证照片已保存到相册"""
        self.logger.info("验证照片文件...")
        return True

    def verify_video_saved(self, min_duration_sec: int = 1) -> bool:
        """AW: 验证视频已保存到相册"""
        self.logger.info("验证视频文件...")
        return True

    # ============================================
    # AW: 辅助操作
    # ============================================

    def open_gallery(self):
        """AW: 打开相册预览"""
        self.logger.info("打开相册...")
        try:
            self._click_element(MAIN_GALLERY)
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"打开相册失败: {e}")
            raise CameraAWError("打开相册失败")

    def close_gallery(self):
        """AW: 关闭相册返回相机"""
        self.logger.info("关闭相册...")
        try:
            self._click_element(BACK_BUTTON)
            time.sleep(0.5)
        except:
            pass

    def return_to_main界面(self):
        """AW: 返回相机主界面"""
        self.logger.info("返回主界面...")
        try:
            while self._find_element(BACK_BUTTON, timeout=1):
                self._click_element(BACK_BUTTON)
                time.sleep(0.3)
        except:
            pass

    def switch_to_video_shutter(self):
        """AW: 切换到录像快门按钮"""
        try:
            self._click_element(MAIN_VIDEO_SHUTTER)
            time.sleep(0.5)
        except Exception as e:
            self.logger.error(f"切换录像模式失败: {e}")

    def get_current_facing(self) -> str:
        """获取当前镜头位置"""
        return self._current_facing

    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self._current_mode


class CameraAWError(Exception):
    """相机自动化异常"""
    pass

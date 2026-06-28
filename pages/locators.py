"""
相机页面元素定位符 - 按页面/区域组织
每个页面/区域有自己的定位符集合
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Locator:
    """定位符"""
    desc: str
    resource_id: str = ""
    xpath: str = ""
    text: str = ""

    def to_dict(self) -> Dict:
        result = {"desc": self.desc}
        if self.resource_id:
            result["resource_id"] = self.resource_id
        if self.xpath:
            result["xpath"] = self.xpath
        if self.text:
            result["text"] = self.text
        return result


# ============================================
# MainPage - 主界面
# ============================================
class MainPage:
    """主界面定位符"""

    SHUTTER = Locator(
        desc="快门按钮",
        resource_id="com.android.camera:id/shutter_button"
    )

    VIDEO_SHUTTER = Locator(
        desc="录像按钮",
        resource_id="com.android.camera:id/video_shutter_button"
    )

    CAMERA_SWITCH = Locator(
        desc="前后置切换按钮",
        resource_id="com.android.camera:id/front_back_switcher"
    )

    THUMBNAIL = Locator(
        desc="右下角缩略图",
        resource_id="com.android.camera:id/thumbnail"
    )

    GALLERY = Locator(
        desc="相册入口",
        resource_id="com.android.camera:id/gallery_thumbnail"
    )


# ============================================
# SettingsPage - 设置界面
# ============================================
class SettingsPage:
    """设置界面定位符"""

    SETTING_ICON = Locator(
        desc="设置图标",
        resource_id="com.android.camera:id/settings"
    )

    FLASH = Locator(
        desc="闪光灯设置",
        text="闪光灯"
    )

    FLASH_AUTO = Locator(
        desc="闪光灯自动",
        text="自动"
    )

    FLASH_ON = Locator(
        desc="闪光灯开启",
        text="开启"
    )

    FLASH_OFF = Locator(
        desc="闪光灯关闭",
        text="关闭"
    )

    AI = Locator(
        desc="AI摄影大师",
        resource_id="com.android.camera:id/ai_master"
    )

    HDR = Locator(
        desc="HDR设置",
        text="HDR"
    )

    ASPECT_RATIO = Locator(
        desc="画幅比例",
        text="画幅比例"
    )

    TIMER = Locator(
        desc="定时拍照",
        text="定时"
    )

    TIMER_OFF = Locator(
        desc="定时关闭",
        text="关闭"
    )

    TIMER_3S = Locator(
        desc="定时3秒",
        text="3秒"
    )

    TIMER_10S = Locator(
        desc="定时10秒",
        text="10秒"
    )

    WATERMARK = Locator(
        desc="水印开关",
        resource_id="com.android.camera:id/watermark"
    )

    BEAUTY = Locator(
        desc="美颜",
        resource_id="com.android.camera:id/beauty_level"
    )


# ============================================
# ProSettingsPage - 专业模式设置
# ============================================
class ProSettingsPage:
    """专业模式设置定位符"""

    ISO = Locator(
        desc="ISO感光度",
        text="ISO"
    )

    WHITE_BALANCE = Locator(
        desc="白平衡",
        text="WB"
    )

    AUTO_FOCUS = Locator(
        desc="对焦模式",
        text="AF"
    )

    EXPOSURE_VALUE = Locator(
        desc="曝光补偿",
        text="EV"
    )


# ============================================
# ModePanel - 模式选择面板
# ============================================
class ModePanel:
    """模式选择面板定位符"""

    PHOTO = Locator(
        desc="拍照模式",
        text="拍照"
    )

    VIDEO = Locator(
        desc="录像模式",
        text="录像"
    )

    PORTRAIT = Locator(
        desc="人像模式",
        text="人像"
    )

    NIGHT = Locator(
        desc="夜景模式",
        text="夜景"
    )

    PRO = Locator(
        desc="专业模式",
        text="专业"
    )

    SLOMO = Locator(
        desc="慢动作模式",
        text="慢动作"
    )

    PANO = Locator(
        desc="全景模式",
        text="全景"
    )

    MONO = Locator(
        desc="黑白模式",
        text="黑白"
    )

    STICKER = Locator(
        desc="趣模式",
        text="趣模式"
    )

    MORE = Locator(
        desc="更多模式入口",
        text="更多"
    )


# ============================================
# VideoPage - 录像相关
# ============================================
class VideoPage:
    """录像相关定位符"""

    RECORDING_INDICATOR = Locator(
        desc="录像计时器指示器",
        resource_id="com.android.camera:id/recording_time"
    )

    STOP_BUTTON = Locator(
        desc="录像停止按钮",
        resource_id="com.android.camera:id/stop_recording"
    )


# ============================================
# Dialogs - 弹窗
# ============================================
class Dialogs:
    """通用弹窗定位符"""

    OK = Locator(
        desc="确定按钮",
        text="确定"
    )

    CANCEL = Locator(
        desc="取消按钮",
        text="取消"
    )

    CLOSE = Locator(
        desc="关闭按钮",
        resource_id="com.android.camera:id/dialog_close"
    )

    CRASH_TITLE = Locator(
        desc="崩溃提示标题",
        text="相机已停止运行"
    )


# ============================================
# Navigation - 导航
# ============================================
class Navigation:
    """导航相关定位符"""

    BACK = Locator(
        desc="返回按钮",
        resource_id="com.android.camera:id/back"
    )

    CLOSE = Locator(
        desc="关闭按钮",
        resource_id="com.android.camera:id/close"
    )


# ============================================
# 兼容性别名（导出原名方便迁移）
# ============================================
# Main
MAIN_SHUTTER = MainPage.SHUTTER
MAIN_VIDEO_SHUTTER = MainPage.VIDEO_SHUTTER
MAIN_CAMERA_SWITCH = MainPage.CAMERA_SWITCH
MAIN_THUMBNAIL = MainPage.THUMBNAIL
MAIN_GALLERY = MainPage.GALLERY

# Settings
SETTING_ICON = SettingsPage.SETTING_ICON
SETTING_FLASH = SettingsPage.FLASH
SETTING_FLASH_AUTO = SettingsPage.FLASH_AUTO
SETTING_FLASH_ON = SettingsPage.FLASH_ON
SETTING_FLASH_OFF = SettingsPage.FLASH_OFF
SETTING_AI = SettingsPage.AI
SETTING_HDR = SettingsPage.HDR
SETTING_ASPECT_RATIO = SettingsPage.ASPECT_RATIO
SETTING_TIMER = SettingsPage.TIMER
SETTING_TIMER_OFF = SettingsPage.TIMER_OFF
SETTING_TIMER_3S = SettingsPage.TIMER_3S
SETTING_TIMER_10S = SettingsPage.TIMER_10S
SETTING_WATERMARK = SettingsPage.WATERMARK
SETTING_BEAUTY = SettingsPage.BEAUTY

# Pro
SETTING_ISO = ProSettingsPage.ISO
SETTING_WB = ProSettingsPage.WHITE_BALANCE
SETTING_AF = ProSettingsPage.AUTO_FOCUS
SETTING_EV = ProSettingsPage.EXPOSURE_VALUE

# Modes
MODE_PHOTO = ModePanel.PHOTO
MODE_VIDEO = ModePanel.VIDEO
MODE_PORTRAIT = ModePanel.PORTRAIT
MODE_NIGHT = ModePanel.NIGHT
MODE_PRO = ModePanel.PRO
MODE_SLOMO = ModePanel.SLOMO
MODE_PANO = ModePanel.PANO
MODE_MONO = ModePanel.MONO
MODE_STICKER = ModePanel.STICKER
MODE_MORE = ModePanel.MORE

# Video
VIDEO_RECORDING_INDICATOR = VideoPage.RECORDING_INDICATOR
VIDEO_STOP_BUTTON = VideoPage.STOP_BUTTON

# Dialogs
DIALOG_OK = Dialogs.OK
DIALOG_CANCEL = Dialogs.CANCEL
DIALOG_CLOSE = Dialogs.CLOSE
CRASH_DIALOG_TITLE = Dialogs.CRASH_TITLE

# Navigation
BACK_BUTTON = Navigation.BACK
CLOSE_BUTTON = Navigation.CLOSE

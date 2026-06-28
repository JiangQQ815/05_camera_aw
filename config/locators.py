"""
相机 UI 元素定位符配置
支持各厂商 Android 系统的相机应用

各厂商定位符需要根据实际设备修改:
- 华为: com.huawei.camera
- 小米: com.xiaomi.miui.camera
- OPPO: com.oppo.camera
- vivo: com.vivo.camera
"""

# ============================================
# 主界面元素 - 快门和基础控件
# ============================================
MAIN_SHUTTER = {
    "desc": "快门按钮",
    "resource_id": "com.huawei.camera:id/shutter_button",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/shutter_button']",
    "type": "click"
}

MAIN_VIDEO_SHUTTER = {
    "desc": "录像按钮",
    "resource_id": "com.huawei.camera:id/video_shutter_button",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/video_shutter_button']",
    "type": "click"
}

MAIN_CAMERA_SWITCH = {
    "desc": "前后置切换按钮",
    "resource_id": "com.huawei.camera:id/front_back_switcher",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/front_back_switcher']",
    "type": "click"
}

MAIN_THUMBNAIL = {
    "desc": "右下角缩略图",
    "resource_id": "com.huawei.camera:id/thumbnail",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/thumbnail']",
    "type": "exists"
}

MAIN_GALLERY = {
    "desc": "相册入口",
    "resource_id": "com.huawei.camera:id/gallery_thumbnail",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/gallery_thumbnail']",
    "type": "click"
}

# ============================================
# 模式滑块相关
# ============================================
MODE_SLIDER = {
    "desc": "模式选择滑块",
    "resource_id": "com.huawei.camera:id/mode_slider",
    "xpath": "//android.widget.HorizontalScrollView[@resource-id='com.huawei.camera:id/mode_slider']",
    "type": "scroll"
}

MODE_PHOTO = {
    "desc": "拍照模式",
    "text": "拍照",
    "resource_id": "com.huawei.camera:id/photo_mode",
    "xpath": "//android.widget.TextView[@text='拍照']",
    "type": "click"
}

MODE_VIDEO = {
    "desc": "录像模式",
    "text": "录像",
    "resource_id": "com.huawei.camera:id/video_mode",
    "xpath": "//android.widget.TextView[@text='录像']",
    "type": "click"
}

MODE_PORTRAIT = {
    "desc": "人像模式",
    "text": "人像",
    "resource_id": "com.huawei.camera:id/portrait_mode",
    "xpath": "//android.widget.TextView[@text='人像']",
    "type": "click"
}

MODE_NIGHT = {
    "desc": "夜景模式",
    "text": "夜景",
    "resource_id": "com.huawei.camera:id/night_mode",
    "xpath": "//android.widget.TextView[@text='夜景']",
    "type": "click"
}

MODE_PRO = {
    "desc": "专业模式",
    "text": "专业",
    "resource_id": "com.huawei.camera:id/pro_mode",
    "xpath": "//android.widget.TextView[@text='专业']",
    "type": "click"
}

MODE_SLOMO = {
    "desc": "慢动作模式",
    "text": "慢动作",
    "resource_id": "com.huawei.camera:id/slomo_mode",
    "xpath": "//android.widget.TextView[@text='慢动作']",
    "type": "click"
}

MODE_PANO = {
    "desc": "全景模式",
    "text": "全景",
    "resource_id": "com.huawei.camera:id/pano_mode",
    "xpath": "//android.widget.TextView[@text='全景']",
    "type": "click"
}

MODE_MONO = {
    "desc": "黑白模式",
    "text": "黑白",
    "resource_id": "com.huawei.camera:id/mono_mode",
    "xpath": "//android.widget.TextView[@text='黑白']",
    "type": "click"
}

MODE_STICKER = {
    "desc": "趣模式/贴纸",
    "text": "趣模式",
    "resource_id": "com.huawei.camera:id/sticker_mode",
    "xpath": "//android.widget.TextView[@text='趣模式']",
    "type": "click"
}

MODE_MORE = {
    "desc": "更多模式入口",
    "text": "更多",
    "resource_id": "com.huawei.camera:id/more_mode",
    "xpath": "//android.widget.TextView[@text='更多']",
    "type": "click"
}

# ============================================
# 设置相关
# ============================================
SETTING_ICON = {
    "desc": "设置图标",
    "resource_id": "com.huawei.camera:id/settings",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/settings']",
    "type": "click"
}

SETTING_FLASH = {
    "desc": "闪光灯设置",
    "text": "闪光灯",
    "resource_id": "com.huawei.camera:id/flash_setting",
    "xpath": "//android.widget.TextView[@text='闪光灯']",
    "type": "click"
}

SETTING_FLASH_AUTO = {
    "desc": "闪光灯自动",
    "text": "自动",
    "xpath": "//android.widget.CheckedTextView[@text='自动']",
    "type": "click"
}

SETTING_FLASH_ON = {
    "desc": "闪光灯开启",
    "text": "开启",
    "xpath": "//android.widget.CheckedTextView[@text='开启']",
    "type": "click"
}

SETTING_FLASH_OFF = {
    "desc": "闪光灯关闭",
    "text": "关闭",
    "xpath": "//android.widget.CheckedTextView[@text='关闭']",
    "type": "click"
}

SETTING_AI = {
    "desc": "AI摄影大师",
    "resource_id": "com.huawei.camera:id/ai_master",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/ai_master']",
    "type": "toggle"
}

SETTING_HDR = {
    "desc": "HDR设置",
    "text": "HDR",
    "resource_id": "com.huawei.camera:id/hdr_setting",
    "xpath": "//android.widget.TextView[@text='HDR']",
    "type": "click"
}

SETTING_VIDEO_QUALITY = {
    "desc": "视频质量/分辨率",
    "text": "视频分辨率",
    "resource_id": "com.huawei.camera:id/video_quality",
    "xpath": "//android.widget.TextView[@text='视频分辨率']",
    "type": "click"
}

SETTING_ASPECT_RATIO = {
    "desc": "画幅比例",
    "text": "画幅比例",
    "resource_id": "com.huawei.camera:id/aspect_ratio",
    "xpath": "//android.widget.TextView[@text='画幅比例']",
    "type": "click"
}

SETTING_TIMER = {
    "desc": "定时拍照",
    "text": "定时",
    "resource_id": "com.huawei.camera:id/timer_setting",
    "xpath": "//android.widget.TextView[@text='定时']",
    "type": "click"
}

SETTING_TIMER_OFF = {
    "desc": "定时关闭",
    "text": "关闭",
    "xpath": "//android.widget.CheckedTextView[@text='关闭']",
    "type": "click"
}

SETTING_TIMER_3S = {
    "desc": "定时3秒",
    "text": "3秒",
    "xpath": "//android.widget.CheckedTextView[@text='3秒']",
    "type": "click"
}

SETTING_TIMER_10S = {
    "desc": "定时10秒",
    "text": "10秒",
    "xpath": "//android.widget.CheckedTextView[@text='10秒']",
    "type": "click"
}

SETTING_VIVID = {
    "desc": "鲜艳模式",
    "resource_id": "com.huawei.camera:id/vivid_color",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/vivid_color']",
    "type": "toggle"
}

SETTING_MONOCHROME = {
    "desc": "单色",
    "resource_id": "com.huawei.camera:id/monochrome_effect",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/monochrome_effect']",
    "type": "toggle"
}

SETTING_BEAUTY = {
    "desc": "美颜",
    "resource_id": "com.huawei.camera:id/beauty_level",
    "xpath": "//android.widget.ImageView[@resource-id='com.huawei.camera:id/beauty_level']",
    "type": "slider"
}

SETTING_WATERMARK = {
    "desc": "水印",
    "text": "自动水印",
    "resource_id": "com.huawei.camera:id/watermark",
    "xpath": "//android.widget.Switch[@resource-id='com.huawei.camera:id/watermark']",
    "type": "toggle"
}

SETTING_GRID = {
    "desc": "参考线/网格",
    "text": "参考线",
    "resource_id": "com.huawei.camera:id/grid_line",
    "xpath": "//android.widget.TextView[@text='参考线']",
    "type": "click"
}

SETTING_SATURATION = {
    "desc": "饱和度",
    "text": "饱和度",
    "resource_id": "com.huawei.camera:id/saturation",
    "xpath": "//android.widget.TextView[@text='饱和度']",
    "type": "slider"
}

SETTING_CONTRAST = {
    "desc": "对比度",
    "text": "对比度",
    "resource_id": "com.huawei.camera:id/contrast",
    "xpath": "//android.widget.TextView[@text='对比度']",
    "type": "slider"
}

SETTING_SHARPNESS = {
    "desc": "锐度",
    "text": "锐度",
    "resource_id": "com.huawei.camera:id/sharpness",
    "xpath": "//android.widget.TextView[@text='锐度']",
    "type": "slider"
}

SETTING_ISO = {
    "desc": "ISO感光度(专业模式)",
    "text": "ISO",
    "resource_id": "com.huawei.camera:id/iso",
    "xpath": "//android.widget.TextView[@text='ISO']",
    "type": "click"
}

SETTING_WB = {
    "desc": "白平衡(专业模式)",
    "text": "WB",
    "resource_id": "com.huawei.camera:id/white_balance",
    "xpath": "//android.widget.TextView[@text='WB']",
    "type": "click"
}

SETTING_AF = {
    "desc": "对焦模式(专业模式)",
    "text": "AF",
    "resource_id": "com.huawei.camera:id/auto_focus",
    "xpath": "//android.widget.TextView[@text='AF']",
    "type": "click"
}

SETTING_EV = {
    "desc": "曝光补偿(专业模式)",
    "text": "EV",
    "resource_id": "com.huawei.camera:id/exposure_value",
    "xpath": "//android.widget.TextView[@text='EV']",
    "type": "slider"
}

# ============================================
# 视频录制相关
# ============================================
VIDEO_RECORDING_INDICATOR = {
    "desc": "录像计时器指示器",
    "resource_id": "com.huawei.camera:id/recording_time",
    "xpath": "//android.widget.TextView[@resource-id='com.huawei.camera:id/recording_time']",
    "type": "exists"
}

VIDEO_STOP_BUTTON = {
    "desc": "录像停止按钮",
    "resource_id": "com.huawei.camera:id/stop_recording",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/stop_recording']",
    "type": "click"
}

# ============================================
# 弹窗处理
# ============================================
DIALOG_OK = {
    "desc": "确定按钮",
    "text": "确定",
    "xpath": "//android.widget.Button[@text='确定']",
    "type": "click"
}

DIALOG_CANCEL = {
    "desc": "取消按钮",
    "text": "取消",
    "xpath": "//android.widget.Button[@text='取消']",
    "type": "click"
}

DIALOG_CLOSE = {
    "desc": "关闭按钮",
    "resource_id": "com.huawei.camera:id/dialog_close",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/dialog_close']",
    "type": "click"
}

CRASH_DIALOG_TITLE = {
    "desc": "崩溃提示标题",
    "text": "相机已停止运行",
    "xpath": "//android.widget.TextView[@text='相机已停止运行']",
    "type": "exists"
}

# ============================================
# 返回和导航
# ============================================
BACK_BUTTON = {
    "desc": "返回按钮",
    "resource_id": "com.huawei.camera:id/back",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/back']",
    "type": "click"
}

CLOSE_BUTTON = {
    "desc": "关闭按钮",
    "resource_id": "com.huawei.camera:id/close",
    "xpath": "//android.widget.ImageButton[@resource-id='com.huawei.camera:id/close']",
    "type": "click"
}

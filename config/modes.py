"""
相机模式配置
定义所有支持的相机模式
"""

CAMERA_MODES = {
    "拍照": {
        "name": "photo",
        "desc": "标准拍照模式",
        "shutter_type": "photo",
        "settings_available": ["闪光灯", "HDR", "AI", "定时", "画幅", "水印", "参考线"]
    },
    "录像": {
        "name": "video",
        "desc": "标准录像模式",
        "shutter_type": "video",
        "settings_available": ["闪光灯", "视频分辨率", "视频质量"]
    },
    "人像": {
        "name": "portrait",
        "desc": "人像模式",
        "shutter_type": "photo",
        "settings_available": ["美颜", "闪光灯", "定时"]
    },
    "夜景": {
        "name": "night",
        "desc": "夜景模式",
        "shutter_type": "photo",
        "settings_available": ["闪光灯", "定时"],
        "wait_after_capture": 3  # 夜景模式需要更长的处理时间
    },
    "专业": {
        "name": "pro",
        "desc": "专业拍照模式",
        "shutter_type": "photo",
        "settings_available": ["ISO", "WB", "AF", "EV", "闪光灯", "定时"],
        "additional_settings": {
            "ISO": ["自动", "100", "200", "400", "800", "1600", "3200"],
            "WB": ["自动", "白炽灯", "日光", "阴天", "荧光灯", "自定义"],
            "AF": ["自动", "手动"],
            "EV": ["-3", "-2", "-1", "0", "+1", "+2", "+3"]
        }
    },
    "慢动作": {
        "name": "slomo",
        "desc": "慢动作录像模式",
        "shutter_type": "video",
        "settings_available": ["慢动作倍速"]
    },
    "全景": {
        "name": "pano",
        "desc": "全景拍摄模式",
        "shutter_type": "panoramic",
        "settings_available": ["定时"]
    },
    "黑白": {
        "name": "mono",
        "desc": "黑白模式",
        "shutter_type": "photo",
        "settings_available": ["单色"]
    },
    "趣模式": {
        "name": "sticker",
        "desc": "趣模式/贴纸",
        "shutter_type": "photo",
        "settings_available": ["贴纸选择"]
    }
}


def get_mode_config(mode_name):
    """
    获取指定模式的配置信息
    :param mode_name: 模式名称，如 "拍照"、"夜景" 等
    :return: 模式配置字典
    """
    return CAMERA_MODES.get(mode_name, {})


def get_all_modes():
    """
    获取所有支持的模式列表
    :return: 模式名称列表
    """
    return list(CAMERA_MODES.keys())


def get_modes_by_facing(facing):
    """
    获取指定镜头支持的所有模式
    :param facing: "前置" 或 "后置"
    :return: 支持的模式列表
    """
    if facing == "前置":
        return ["拍照", "录像", "人像", "趣模式"]
    else:  # 后置
        return ["拍照", "录像", "人像", "夜景", "专业", "慢动作", "全景", "黑白", "趣模式"]

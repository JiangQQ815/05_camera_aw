"""
相机测试数据配置
所有测试用例的数据驱动配置
"""

# ============================================
# 拍照模式测试数据
# ============================================
PHOTO_MODE_CASES = [
    {
        "case_id": "PHOTO_001",
        "title": "后置-拍照-默认设置",
        "facing": "后置",
        "mode": "拍照",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_002",
        "title": "后置-拍照-闪光灯开启",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"闪光灯": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_003",
        "title": "后置-拍照-闪光灯自动",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"闪光灯": "自动"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_004",
        "title": "后置-拍照-闪光灯关闭",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"闪光灯": "关闭"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_005",
        "title": "后置-拍照-HDR开启",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"HDR": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_006",
        "title": "后置-拍照-定时3秒",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"定时": "3秒"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_007",
        "title": "后置-拍照-定时10秒",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"定时": "10秒"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_008",
        "title": "后置-拍照-画幅16:9",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"画幅": "16:9"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_009",
        "title": "后置-拍照-画幅1:1",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"画幅": "1:1"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_010",
        "title": "后置-拍照-AI开启",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"AI": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_011",
        "title": "后置-拍照-水印开启",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"水印": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_012",
        "title": "前置-拍照-默认设置",
        "facing": "前置",
        "mode": "拍照",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_013",
        "title": "前置-拍照-美颜开启",
        "facing": "前置",
        "mode": "拍照",
        "settings": {"美颜": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PHOTO_014",
        "title": "前置-拍照-定时3秒",
        "facing": "前置",
        "mode": "拍照",
        "settings": {"定时": "3秒"},
        "action": "photo"
    },
]

# ============================================
# 录像模式测试数据
# ============================================
VIDEO_MODE_CASES = [
    {
        "case_id": "VIDEO_001",
        "title": "后置-录像-默认设置",
        "facing": "后置",
        "mode": "录像",
        "settings": {},
        "action": "video",
        "video_duration": 5
    },
    {
        "case_id": "VIDEO_002",
        "title": "后置-录像-闪光灯开启",
        "facing": "后置",
        "mode": "录像",
        "settings": {"闪光灯": "开启"},
        "action": "video",
        "video_duration": 5
    },
    {
        "case_id": "VIDEO_003",
        "title": "后置-录像-闪光灯关闭",
        "facing": "后置",
        "mode": "录像",
        "settings": {"闪光灯": "关闭"},
        "action": "video",
        "video_duration": 5
    },
    {
        "case_id": "VIDEO_004",
        "title": "前置-录像-默认设置",
        "facing": "前置",
        "mode": "录像",
        "settings": {},
        "action": "video",
        "video_duration": 5
    },
]

# ============================================
# 人像模式测试数据
# ============================================
PORTRAIT_MODE_CASES = [
    {
        "case_id": "PORTRAIT_001",
        "title": "后置-人像-默认设置",
        "facing": "后置",
        "mode": "人像",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "PORTRAIT_002",
        "title": "后置-人像-美颜开启",
        "facing": "后置",
        "mode": "人像",
        "settings": {"美颜": "开启"},
        "action": "photo"
    },
    {
        "case_id": "PORTRAIT_003",
        "title": "前置-人像-默认设置",
        "facing": "前置",
        "mode": "人像",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "PORTRAIT_004",
        "title": "前置-人像-美颜开启",
        "facing": "前置",
        "mode": "人像",
        "settings": {"美颜": "开启"},
        "action": "photo"
    },
]

# ============================================
# 夜景模式测试数据
# ============================================
NIGHT_MODE_CASES = [
    {
        "case_id": "NIGHT_001",
        "title": "后置-夜景-默认设置",
        "facing": "后置",
        "mode": "夜景",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "NIGHT_002",
        "title": "后置-夜景-闪光灯自动",
        "facing": "后置",
        "mode": "夜景",
        "settings": {"闪光灯": "自动"},
        "action": "photo"
    },
    {
        "case_id": "NIGHT_003",
        "title": "后置-夜景-定时3秒",
        "facing": "后置",
        "mode": "夜景",
        "settings": {"定时": "3秒"},
        "action": "photo"
    },
]

# ============================================
# 专业模式测试数据
# ============================================
PRO_MODE_CASES = [
    {
        "case_id": "PRO_001",
        "title": "后置-专业-默认设置",
        "facing": "后置",
        "mode": "专业",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "PRO_002",
        "title": "后置-专业-ISO_100",
        "facing": "后置",
        "mode": "专业",
        "settings": {"ISO": "100"},
        "action": "photo"
    },
    {
        "case_id": "PRO_003",
        "title": "后置-专业-ISO_自动",
        "facing": "后置",
        "mode": "专业",
        "settings": {"ISO": "自动"},
        "action": "photo"
    },
    {
        "case_id": "PRO_004",
        "title": "后置-专业-白平衡日光",
        "facing": "后置",
        "mode": "专业",
        "settings": {"WB": "日光"},
        "action": "photo"
    },
    {
        "case_id": "PRO_005",
        "title": "后置-专业-白平衡自动",
        "facing": "后置",
        "mode": "专业",
        "settings": {"WB": "自动"},
        "action": "photo"
    },
    {
        "case_id": "PRO_006",
        "title": "后置-专业-对焦自动",
        "facing": "后置",
        "mode": "专业",
        "settings": {"AF": "自动"},
        "action": "photo"
    },
    {
        "case_id": "PRO_007",
        "title": "后置-专业-对焦手动",
        "facing": "后置",
        "mode": "专业",
        "settings": {"AF": "手动"},
        "action": "photo"
    },
    {
        "case_id": "PRO_008",
        "title": "后置-专业-EV_0",
        "facing": "后置",
        "mode": "专业",
        "settings": {"EV": "0"},
        "action": "photo"
    },
    {
        "case_id": "PRO_009",
        "title": "后置-专业-EV_+1",
        "facing": "后置",
        "mode": "专业",
        "settings": {"EV": "+1"},
        "action": "photo"
    },
]

# ============================================
# 慢动作模式测试数据
# ============================================
SLOMO_MODE_CASES = [
    {
        "case_id": "SLOMO_001",
        "title": "后置-慢动作-默认设置",
        "facing": "后置",
        "mode": "慢动作",
        "settings": {},
        "action": "video",
        "video_duration": 5
    },
]

# ============================================
# 全景模式测试数据
# ============================================
PANO_MODE_CASES = [
    {
        "case_id": "PANO_001",
        "title": "后置-全景-默认设置",
        "facing": "后置",
        "mode": "全景",
        "settings": {},
        "action": "panorama"
    },
    {
        "case_id": "PANO_002",
        "title": "后置-全景-定时3秒",
        "facing": "后置",
        "mode": "全景",
        "settings": {"定时": "3秒"},
        "action": "panorama"
    },
]

# ============================================
# 黑白模式测试数据
# ============================================
MONO_MODE_CASES = [
    {
        "case_id": "MONO_001",
        "title": "后置-黑白-默认设置",
        "facing": "后置",
        "mode": "黑白",
        "settings": {},
        "action": "photo"
    },
]

# ============================================
# 趣模式测试数据
# ============================================
STICKER_MODE_CASES = [
    {
        "case_id": "STICKER_001",
        "title": "前置-趣模式-默认设置",
        "facing": "前置",
        "mode": "趣模式",
        "settings": {},
        "action": "photo"
    },
]

# ============================================
# 组合测试数据（多设置组合）
# ============================================
COMBO_CASES = [
    {
        "case_id": "COMBO_001",
        "title": "后置-拍照-闪光灯开启-HDR自动-AI开启",
        "facing": "后置",
        "mode": "拍照",
        "settings": {"闪光灯": "开启", "HDR": "开启", "AI": "开启"},
        "action": "photo"
    },
    {
        "case_id": "COMBO_002",
        "title": "前置-拍照-美颜开启-定时3秒",
        "facing": "前置",
        "mode": "拍照",
        "settings": {"美颜": "开启", "定时": "3秒"},
        "action": "photo"
    },
    {
        "case_id": "COMBO_003",
        "title": "后置-专业-ISO_400-白平衡日光-EV_0",
        "facing": "后置",
        "mode": "专业",
        "settings": {"ISO": "400", "WB": "日光", "EV": "0"},
        "action": "photo"
    },
]

# ============================================
# 汇总所有测试数据
# ============================================
ALL_TEST_CASES = (
    PHOTO_MODE_CASES
    + VIDEO_MODE_CASES
    + PORTRAIT_MODE_CASES
    + NIGHT_MODE_CASES
    + PRO_MODE_CASES
    + SLOMO_MODE_CASES
    + PANO_MODE_CASES
    + MONO_MODE_CASES
    + STICKER_MODE_CASES
    + COMBO_CASES
)


# ============================================
# 快速选择测试集
# ============================================
QUICK_TEST_CASES = [
    # 快速冒烟测试
    {
        "case_id": "SMOKE_001",
        "title": "后置-拍照-默认",
        "facing": "后置",
        "mode": "拍照",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "SMOKE_002",
        "title": "前置-拍照-默认",
        "facing": "前置",
        "mode": "拍照",
        "settings": {},
        "action": "photo"
    },
    {
        "case_id": "SMOKE_003",
        "title": "后置-录像-5秒",
        "facing": "后置",
        "mode": "录像",
        "settings": {},
        "action": "video",
        "video_duration": 5
    },
    {
        "case_id": "SMOKE_004",
        "title": "后置-夜景-默认",
        "facing": "后置",
        "mode": "夜景",
        "settings": {},
        "action": "photo"
    },
]

RESOLUTION_TEST_CASES = [
    # 分辨率相关测试
    {
        "case_id": "RES_001",
        "title": "后置-拍照-视频分辨率-4K",
        "facing": "后置",
        "mode": "录像",
        "settings": {"视频分辨率": "4K"},
        "action": "video",
        "video_duration": 5
    },
    {
        "case_id": "RES_002",
        "title": "后置-拍照-视频分辨率-1080p",
        "facing": "后置",
        "mode": "录像",
        "settings": {"视频分辨率": "1080p"},
        "action": "video",
        "video_duration": 5
    },
]

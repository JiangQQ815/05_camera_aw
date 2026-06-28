# 相机自动化测试框架

基于关键字驱动（Action Word）的 Android 相机 UI 自动化测试框架，支持**多设备并行执行**。

## 项目结构

```
05_camera_aw/
├── base/
│   └── camera_aw.py           # 核心 AW 类
├── config/
│   ├── locators.py            # 相机 UI 定位符
│   ├── modes.py               # 相机模式配置
│   └── test_data.py           # 测试用例数据
├── test_cases/
│   └── test_camera_template.py # 模板化测试用例
├── conftest.py                # Pytest fixtures (单设备)
├── conftest_multi.py          # Pytest fixtures (多设备)
├── conftest_xdist.py          # Pytest-xdist 并行支持
├── device_manager.py          # 多设备管理器
├── run_tests.py               # Python 多设备运行器
├── run_multi_device.bat       # 多设备批量执行 (Windows)
├── run_parallel.bat           # 并行分发执行 (Windows)
├── requirements.txt
└── README.md
```

## 功能特性

- ✅ **关键字驱动 (Action Word)** - 封装相机操作为独立方法
- ✅ **数据驱动** - 测试用例通过配置字典定义，易于扩展
- ✅ **模板化设计** - 用例主体固定，只需修改参数
- ✅ **通用相机支持** - 支持所有模式和设置
- ✅ **多设备支持** - 支持多设备并行/串行执行
- ✅ **详细日志** - 完整的日志记录和问题追踪

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化设备

```bash
# 连接设备（确保USB调试已开启）
python -m uiautomator2 init
```

### 3. 运行测试

```bash
# 单设备冒烟测试
python run_tests.py --mode smoke

# 多设备并行执行
python run_tests.py --mode photo --parallel

# 指定设备执行
python run_tests.py --devices ABC123,DEF456 --mode all
```

---

## 多设备使用指南

### 方案一：使用 BAT 脚本（推荐 Windows 用户）

```batch
# 方式1: 主菜单交互
run_multi_device.bat

# 方式2: 快速冒烟测试
run_smoke_all_devices.bat

# 方式3: 自动分发并行执行
run_parallel.bat
```

### 方案二：使用 Python 运行器

```bash
# 查看帮助
python run_tests.py --help

# 自动发现所有设备执行
python run_tests.py --mode smoke

# 指定设备列表
python run_tests.py --devices "ABC123,DEF456,XYZ789" --mode photo

# 并行执行
python run_tests.py --mode video --parallel
```

### 方案三：使用 Pytest 直接调用

```bash
# 单设备
pytest test_cases/ -v --device-serial=ABC123

# 多设备
pytest test_cases/ -v --devices=ABC123,DEF456

# 并行执行（需安装 pytest-xdist）
pip install pytest-xdist
pytest test_cases/ -v -n 3 --distribute
```

---

## 支持的相机模式

| 模式 | 说明 | 支持前置 | 支持后置 |
|------|------|---------|---------|
| 拍照 | 标准拍照 | ✅ | ✅ |
| 录像 | 标准录像 | ✅ | ✅ |
| 人像 | 人像模式 | ✅ | ✅ |
| 夜景 | 夜景拍摄 | ❌ | ✅ |
| 专业 | 专业模式（ISO/WB/AF/EV） | ❌ | ✅ |
| 慢动作 | 慢动作录像 | ❌ | ✅ |
| 全景 | 全景拍摄 | ❌ | ✅ |
| 黑白 | 黑白模式 | ❌ | ✅ |
| 趣模式 | 贴纸/趣AR | ✅ | ❌ |

## 支持的设置参数

| 设置项 | 适用模式 | 可选值 |
|--------|---------|-------|
| 闪光灯 | 拍照/录像/夜景/人像 | 自动/开启/关闭 |
| HDR | 拍照 | 开启/关闭 |
| AI | 拍照 | 开启/关闭 |
| 定时 | 拍照/人像/夜景/全景 | 关闭/3秒/10秒 |
| 画幅 | 拍照 | 4:3/16:9/1:1 |
| 水印 | 拍照 | 开启/关闭 |
| 美颜 | 拍照/人像 | 开启/关闭 |
| ISO | 专业模式 | 自动/100/200/400/800/1600/3200 |
| WB | 专业模式 | 自动/白炽灯/日光/阴天/荧光灯 |
| AF | 专业模式 | 自动/手动 |
| EV | 专业模式 | -3/-2/-1/0/+1/+2/+3 |

---

## 多设备架构说明

### 设备管理器 (device_manager.py)

```python
from device_manager import device_manager

# 连接所有设备
device_manager.connect_all_devices()

# 获取可用设备
available = device_manager.get_available_devices()

# 分配设备
device = device_manager.allocate_device("test_task_1")

# 释放设备
device_manager.release_device(device.serial)
```

### 用例分发策略

```
设备A: [Case_001, Case_004, Case_007, ...]
设备B: [Case_002, Case_005, Case_008, ...]
设备C: [Case_003, Case_006, Case_009, ...]

# 循环分配，确保均匀分布
```

### 执行模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 串行 | 所有设备顺序执行相同用例 | 验证所有设备一致性 |
| 并行 | 用例分发到多设备 | 加速测试执行 |
| 单设备 | 指定单一设备执行 | 调试特定设备问题 |

---

## 常见问题

### 1. 元素定位失败

不同机型 UI 可能有差异，修改 `config/locators.py` 中的定位符。

### 2. 多设备连接问题

```bash
# 检查设备连接
adb devices

# 重启ADB服务
adb kill-server
adb start-server
```

### 3. 并行执行冲突

多个设备同时操作可能导致资源冲突，确保：
- 每个设备运行不同的用例
- 用例之间无依赖关系

---

## 高级用法

### 自定义测试数据

在 `config/test_data.py` 中添加新的测试用例：

```python
MY_CUSTOM_CASES = [
    {
        "case_id": "MY_001",
        "title": "自定义夜景测试",
        "facing": "后置",
        "mode": "夜景",
        "settings": {"闪光灯": "自动"},
        "action": "photo"
    },
]
```

### 自定义设备分配

修改 `device_manager.py` 中的分配策略，实现按设备特性分配用例：

```python
def allocate_device(self, task_name: str, device_requirements: dict = None):
    # 按设备能力分配
    # 例如：前置镜头用例只分配给有前置相机的设备
    ...
```

---

## License

MIT

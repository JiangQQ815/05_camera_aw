# 05_camera_aw 改进规范

## 1. 概述与目标

本项目是一个基于关键字驱动（Action Word）的 Android 相机 UI 自动化测试框架。当前缺少单元测试覆盖，代码中存在的 stub 实现需要完善。

**本次改进目标：**
- 为 base 模块编写完整单元测试（覆盖率 ≥ 80%）
- 重构 stub 实现（MediaVerifier.verify_photo_saved / verify_video_saved）
- 代码审查与简化
- 确保多设备场景可测试

---

## 2. 验收标准

### 2.1 测试覆盖

| 模块 | 目标覆盖率 | 说明 |
|------|-----------|------|
| base/camera_aw.py | 70% | AW 方法 |
| base/test_executor.py | 90% | 执行器核心逻辑 |
| base/device_session.py | 85% | 设备会话管理 |
| base/media_verifier.py | 80% | 媒体验证逻辑 |
| base/settings_handler.py | 75% | 设置处理器 |
| pages/locators.py | 90% | 定位符无逻辑，覆盖类定义即可 |
| config/modes.py | 90% | 模式配置 |

### 2.2 重构验收

- [ ] MediaVerifier.verify_photo_saved 实现完整逻辑（连接 real device 或 mock）
- [ ] MediaVerifier.verify_video_saved 实现完整逻辑
- [ ] CameraAutomationAW.verify_photo_saved 调用 MediaVerifier
- [ ] CameraAutomationAW.verify_video_saved 调用 MediaVerifier

### 2.3 代码质量

- [ ] 无 `pass` stub（除真正的 no-op 动作）
- [ ] 所有 public 方法有 docstring
- [ ] 错误处理完整，无 bare except
- [ ] 类型注解完整（至少函数签名）

---

## 3. 模块结构

### 3.1 现有模块

```
05_camera_aw/
├── base/
│   ├── camera_aw.py          # AW 类，相机操作封装
│   ├── test_executor.py      # 6步测试执行器
│   ├── device_session.py     # 多设备会话管理
│   ├── media_verifier.py     # 媒体文件验证（stub）
│   └── settings_handler.py   # 设置参数处理器
├── config/
│   ├── locators.py           # UI 定位符（按页面组织）
│   ├── modes.py              # 相机模式配置
│   └── test_data.py          # 测试用例数据
├── pages/
│   └── locators.py           # 页面级定位符（pages 包）
├── test_cases/
│   └── test_camera_template.py  # pytest 参数化用例
└── conftest.py               # pytest fixtures
```

### 3.2 测试模块（新）

```
tests/                        # 新增单元测试目录
├── __init__.py
├── conftest.py               # 测试共享 fixtures
├── test_camera_aw.py         # CameraAutomationAW 单元测试
├── test_executor.py          # CameraTestExecutor 单元测试
├── test_device_session.py    # DeviceSession 单元测试
├── test_media_verifier.py    # MediaVerifier 单元测试
└── test_settings_handler.py  # SettingsHandler 单元测试
```

---

## 4. 功能详情

### 4.1 MediaVerifier 完善

**当前状态：** verify_photo_saved / verify_video_saved 是 stub，直接返回 True。

**目标实现：**
- 扫描 DCIM 目录获取最新文件
- 验证文件大小（最小阈值）
- 视频需验证时长（ffprobe）
- 返回 VerificationResult

**接口：**
```python
@dataclass
class VerificationResult:
    success: bool
    file_path: Optional[str] = None
    file_size: int = 0
    duration: Optional[float] = None
    error: Optional[str] = None
```

### 4.2 CameraAutomationAW 集成

将 verify_photo_saved / verify_video_saved 从 stub 改为调用 MediaVerifier：
```python
def verify_photo_saved(self, min_size_kb: int = 10) -> bool:
    result = self._media_verifier.verify_photo_saved(min_size_kb)
    return result.success
```

### 4.3 DeviceSession 设备分配

支持按任务名分配设备，最小使用时间优先：
```python
def allocate_device(self, task_name: str = "") -> Optional[DeviceInfo]:
    # 选择 last_used 最早的可用设备
```

---

## 5. 测试策略

### 5.1 测试隔离

- **单元测试：** 使用 mock uiautomator2 driver，不依赖真机
- **集成测试：** 使用 conftest.py 的 real device fixtures
- **测试数据：** 使用 config.test_data 中的用例结构

### 5.2 Mock 策略

使用 `unittest.mock` Mock uiautomator2 driver：
```python
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_driver():
    d = Mock()
    d.info = {"deviceName": "test_device"}
    d.shell = Mock(return_value="")
    d(resource_id=...).exists = Mock(return_value=False)
    return d
```

### 5.3 参数化测试

对 CameraTestExecutor.execute 使用参数化测试，覆盖各种 case 组合。

---

## 6. 代码简化清单

### 6.1 CameraAWError 异常

统一异常类，替代散落的 raise。

### 6.2 Locator 去重

pages/locators.py 和 config/locators.py 有重复：
- 合并到 config/locators.py
- pages/locators.py 作为兼容性别名

### 6.3 SettingsHandler 方法简化

每个 set_* 方法有重复的 time.sleep()，考虑抽取通用方法。

---

## 7. 文件变更计划

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| tests/ | 新增 | 单元测试目录 |
| tests/conftest.py | 新增 | 测试 fixtures |
| tests/test_camera_aw.py | 新增 | AW 类测试 |
| tests/test_executor.py | 新增 | 执行器测试 |
| tests/test_device_session.py | 新增 | 设备会话测试 |
| tests/test_media_verifier.py | 新增 | 媒体验证测试 |
| tests/test_settings_handler.py | 新增 | 设置处理器测试 |
| base/camera_aw.py | 重构 | 调用 MediaVerifier |
| base/media_verifier.py | 重构 | 完善 stub 实现 |
| config/locators.py | 重构 | 合并 pages/locators.py |
| pages/locators.py | 重构 | 变为兼容层 |
| conftest.py | 重构 | 添加测试辅助 fixture |

---

## 8. 暂不考虑

以下内容不在本次范围内：

- E2E 测试（需要真机）
- CI/CD 集成
- 性能基准测试
- 文档更新（README 后续单独处理）
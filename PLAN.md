# 05_camera_aw 改进计划

基于 SPEC.md 的任务分解。

---

## Phase 1: 测试基础设施

### Task 1.1: 创建 tests 目录结构
- [ ] 创建 `tests/__init__.py`
- [ ] 创建 `tests/conftest.py`，包含 mock driver fixture
- [ ] 创建 `tests/test_camera_aw.py`
- [ ] 创建 `tests/test_executor.py`
- [ ] 创建 `tests/test_device_session.py`
- [ ] 创建 `tests/test_media_verifier.py`
- [ ] 创建 `tests/test_settings_handler.py`

**验收标准：**
- pytest 可发现所有测试文件
- mock fixture 可正常注入

---

## Phase 2: MediaVerifier 重构

### Task 2.1: 完善 MediaVerifier 实现
- [ ] 补全 verify_photo_saved 逻辑（扫描 DCIM、验证大小）
- [ ] 补全 verify_video_saved 逻辑（扫描 DCIM、验证时长）
- [ ] 添加异常处理（设备连接失败等）

**依赖：** Task 1.1

**验收标准：**
- 无 `return True` stub
- 返回 VerificationResult

### Task 2.2: CameraAutomationAW 集成 MediaVerifier
- [ ] CameraAutomationAW 添加 _media_verifier 属性
- [ ] verify_photo_saved 调用 MediaVerifier
- [ ] verify_video_saved 调用 MediaVerifier

**依赖：** Task 2.1

**验收标准：**
- AW 方法返回 bool
- 集成测试通过

---

## Phase 3: 单元测试编写

### Task 3.1: test_executor.py 单元测试
- [ ] 测试 execute 正常流程
- [ ] 测试 CameraAWError 捕获
- [ ] 测试 AssertionError 捕获
- [ ] 测试各 Step 方法
- [ ] 参数化测试多种 case

**验收标准：** 覆盖率 ≥ 90%

### Task 3.2: test_device_session.py 单元测试
- [ ] 测试 connect_all_devices
- [ ] 测试 add_device / remove_device
- [ ] 测试 allocate_device / release_device
- [ ] 测试设备统计更新
- [ ] 测试多设备场景

**验收标准：** 覆盖率 ≥ 85%

### Task 3.3: test_media_verifier.py 单元测试
- [ ] 测试 verify_photo_saved 成功
- [ ] 测试 verify_photo_saved 文件过小
- [ ] 测试 verify_photo_saved 未找到文件
- [ ] 测试 verify_video_saved 成功
- [ ] 测试 verify_video_saved 时长不足

**验收标准：** 覆盖率 ≥ 80%

### Task 3.4: test_settings_handler.py 单元测试
- [ ] 测试 open / close
- [ ] 测试 set_flash / set_hdr / set_timer 等
- [ ] 测试异常处理

**验收标准：** 覆盖率 ≥ 75%

### Task 3.5: test_camera_aw.py 单元测试
- [ ] 测试 switch_camera_lens
- [ ] 测试 switch_to_mode
- [ ] 测试 set_camera_setting
- [ ] 测试快门操作
- [ ] 测试结果校验

**验收标准：** 覆盖率 ≥ 70%

---

## Phase 4: 代码简化

### Task 4.1: 合并 locators
- [ ] 将 pages/locators.py 别名合并到 config/locators.py
- [ ] pages/locators.py 变为兼容层（仅 import）

### Task 4.2: 统一异常处理
- [ ] 确认 CameraAWError 被正确使用
- [ ] 移除 bare except

---

## Phase 5: 代码审查

### Task 5.1: 全面代码审查
- [ ] 审查 test_executor.py
- [ ] 审查 device_session.py
- [ ] 审查 media_verifier.py
- [ ] 审查 settings_handler.py
- [ ] 审查 camera_aw.py

**问题分级：**
- CRITICAL: 阻塞，必须修复
- HIGH: 重要，优先修复
- MEDIUM: 建议，择机修复

---

## Phase 6: 运行验证

### Task 6.1: 运行所有测试
- [ ] pytest tests/ -v
- [ ] 覆盖率报告 pytest --cov

### Task 6.2: Git 提交
- [ ] 提交 Phase 1-5 的所有变更
- [ ] commit message 遵循规范

---

## 任务依赖图

```
Task 1.1 ──▶ Task 2.1 ──▶ Task 2.2
  │                          │
  │                          ▼
  │                    Task 3.5 (部分依赖)
  │
  ▼
Task 3.1 ──────────────────▶ Task 3.2 ──▶ Task 3.3 ──▶ Task 3.4
                                              │
                                              ▼
                                            Task 5.1
                                              │
                                              ▼
                                            Task 6.1 ──▶ Task 6.2
```

---

## 执行顺序

1. Phase 1: 测试基础设施（Task 1.1）
2. Phase 2: MediaVerifier 重构（Task 2.1 → 2.2）
3. Phase 3: 单元测试（3.1 → 3.2 → 3.3 → 3.4 → 3.5）
4. Phase 4: 代码简化
5. Phase 5: 代码审查
6. Phase 6: 运行验证
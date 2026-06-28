"""
base包初始化

核心模块:
- camera_aw: 相机自动化 Action Word 类
- device_session: 设备会话管理
- media_verifier: 媒体文件验证
- settings_handler: 相机参数设置处理器
- test_executor: 测试执行器
- ui_element: UI元素操作基类（带 atx-agent 死亡重试机制）
- retry_handler: 重试处理器（处理 uiautomator2 atx-agent 静默死亡）
"""
from base.camera_aw import CameraAutomationAW, CameraAWError
from base.device_session import DeviceSession, DeviceStatus, DeviceInfo
from base.media_verifier import MediaVerifier, VerificationResult
from base.settings_handler import SettingsHandler, create_settings_handler
from base.test_executor import CameraTestExecutor, TestResult
from base.ui_element import UIElementOperations
from base.retry_handler import (
    RetryExhaustedError,
    DeviceConnectionError,
    with_retry,
    should_retry_on_connection_error,
)

__all__ = [
    # Camera AW
    'CameraAutomationAW',
    'CameraAWError',
    # Device Session
    'DeviceSession',
    'DeviceStatus',
    'DeviceInfo',
    # Media Verifier
    'MediaVerifier',
    'VerificationResult',
    # Settings Handler
    'SettingsHandler',
    'create_settings_handler',
    # Test Executor
    'CameraTestExecutor',
    'TestResult',
    # UI Element
    'UIElementOperations',
    # Retry Handler
    'RetryExhaustedError',
    'DeviceConnectionError',
    'with_retry',
    'should_retry_on_connection_error',
]

"""
测试共享 fixtures - 提供 mock uiautomator2 driver
tests/ 目录专用，不依赖项目根 conftest.py
"""
import sys
import os

# 确保只加载 tests 目录下的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass


@dataclass
class MockDeviceInfo:
    """Mock 设备信息"""
    deviceName: str = "test_device"
    serial: str = "test_serial_123"


class MockShellResult:
    """Mock shell 命令结果"""
    def __init__(self, output: str = ""):
        self._output = output

    def strip(self):
        return self._output.strip()

    def __str__(self):
        return self._output

    def __call__(self, *args, **kwargs):
        return self._output


def make_mock_element(exists: bool = True, text: str = ""):
    """创建 Mock UI 元素"""
    elem = Mock()
    elem.exists = Mock(return_value=exists)
    elem.wait = Mock(return_value=exists)
    elem.click = Mock(return_value=True)
    elem.get_text = Mock(return_value=text)
    elem.long_click = Mock(return_value=True)
    return elem


@pytest.fixture
def mock_driver():
    """
    创建 mock uiautomator2 driver
    可配置返回行为
    """
    d = Mock()

    # 设备信息
    d.info = {
        "deviceName": "test_device",
        "serial": "test_serial_123"
    }

    # 默认 shell 返回空
    d.shell = Mock(return_value="")

    # 默认元素不存在
    d.resource_id = MagicMock(side_effect=lambda rid: make_mock_element(False))
    d.xpath = MagicMock(side_effect=lambda xpath: make_mock_element(False))
    d(text=MagicMock(side_effect=lambda t: make_mock_element(False)))

    # 模拟 app 操作
    d.app_stop = Mock()
    d.app_start = Mock()

    # 模拟 swipe
    d.swipe = Mock()

    # 模拟 textContains
    d(textContains=MagicMock(side_effect=lambda t: make_mock_element(False)))

    return d


@pytest.fixture
def mock_driver_with_elements(mock_driver):
    """
    mock driver，配置部分元素存在
    """
    mock_driver.resource_id = MagicMock(side_effect=lambda rid: make_mock_element(exists=True))
    mock_driver.shell = Mock(return_value="/sdcard/DCIM/Camera/test.jpg\n5000")
    return mock_driver


@pytest.fixture
def mock_device_info():
    """Mock DeviceInfo"""
    return MockDeviceInfo(
        deviceName="test_device",
        serial="test_serial_123"
    )


@pytest.fixture
def sample_photo_case():
    """标准拍照测试用例"""
    return {
        "case_id": "PHOTO_001",
        "title": "后置摄像头拍照",
        "facing": "后置",
        "mode": "拍照",
        "settings": {},
        "action": "photo"
    }


@pytest.fixture
def sample_video_case():
    """标准录像测试用例"""
    return {
        "case_id": "VIDEO_001",
        "title": "后置摄像头录像",
        "facing": "后置",
        "mode": "录像",
        "settings": {},
        "action": "video",
        "video_duration": 3
    }
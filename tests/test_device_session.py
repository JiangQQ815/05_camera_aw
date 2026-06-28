"""
DeviceSession 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import time

# Mock uiautomator2 before importing device_session
import sys
sys.modules['uiautomator2'] = Mock()

from base.device_session import DeviceSession, DeviceInfo, DeviceStatus


class TestDeviceSession:
    """DeviceSession 测试套件"""

    @pytest.fixture
    def session(self):
        """创建 DeviceSession 实例"""
        return DeviceSession()

    @pytest.fixture
    def mock_u2_connect(self):
        """Mock uiautomator2.connect"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "mock_device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            yield mock_driver

    # ====== 设备连接测试 ======

    def test_connect_all_devices_empty(self, session):
        """无设备连接"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="List of devices attached\n")
            devices = session.connect_all_devices()
            assert devices == []

    def test_add_device_success(self, session):
        """成功添加设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            device_info = session.add_device("test_serial")
            assert device_info.serial == "test_serial"
            assert device_info.status == DeviceStatus.AVAILABLE

    def test_add_device_already_exists(self, session):
        """设备已存在"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            session.add_device("test_serial")
            # u2.connect 只应调用一次
            assert len(session.get_all_devices()) == 1

    def test_add_device_connection_failed(self, session):
        """设备连接失败"""
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(side_effect=Exception("Connection failed")))}):
            device_info = session.add_device("test_serial")
            assert device_info.status == DeviceStatus.ERROR

    def test_remove_device(self, session):
        """移除设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            session.remove_device("test_serial")
            assert session.get_device("test_serial") is None

    # ====== 设备查询测试 ======

    def test_get_device_exists(self, session):
        """获取已存在的设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            device = session.get_device("test_serial")
            assert device is not None
            assert device.serial == "test_serial"

    def test_get_device_not_exists(self, session):
        """获取不存在的设备"""
        device = session.get_device("nonexistent")
        assert device is None

    def test_get_available_devices(self, session):
        """获取可用设备列表"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("device1")
            session.add_device("device2")
            session.allocate_device("task1")
            available = session.get_available_devices()
            assert len(available) == 1

    def test_get_all_devices(self, session):
        """获取所有设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("device1")
            session.add_device("device2")
            assert len(session.get_all_devices()) == 2

    # ====== 设备分配测试 ======

    def test_allocate_device_success(self, session):
        """成功分配设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            device = session.allocate_device("test_task")
            assert device is not None
            assert device.status == DeviceStatus.BUSY
            assert device.current_task == "test_task"

    def test_allocate_device_no_available(self, session):
        """无可用设备"""
        device = session.allocate_device("test_task")
        assert device is None

    def test_release_device(self, session):
        """释放设备"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            session.allocate_device("test_task")
            session.release_device("test_serial")
            device = session.get_device("test_serial")
            assert device.status == DeviceStatus.AVAILABLE
            assert device.current_task is None

    # ====== 统计测试 ======

    def test_update_stats_pass(self, session):
        """更新通过统计"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            session.update_stats("test_serial", passed=True)
            device = session.get_device("test_serial")
            assert device.total_cases == 1
            assert device.pass_cases == 1
            assert device.fail_cases == 0

    def test_update_stats_fail(self, session):
        """更新失败统计"""
        mock_driver = Mock()
        mock_driver.info = {"deviceName": "Test Device"}
        with patch.dict('sys.modules', {'uiautomator2': Mock(connect=Mock(return_value=mock_driver))}):
            session.add_device("test_serial")
            session.update_stats("test_serial", passed=False)
            device = session.get_device("test_serial")
            assert device.total_cases == 1
            assert device.pass_cases == 0
            assert device.fail_cases == 1

    # ====== 工厂函数测试 ======

    def test_create_device_session(self):
        """工厂函数"""
        from base.device_session import create_device_session
        session = create_device_session()
        assert isinstance(session, DeviceSession)


class TestDeviceInfo:
    """DeviceInfo 测试"""

    def test_device_info_default_name(self):
        info = DeviceInfo(serial="test123")
        assert info.name == "test123"

    def test_device_info_custom_name(self):
        info = DeviceInfo(serial="test123", name="My Device")
        assert info.name == "My Device"

    def test_device_info_default_status(self):
        info = DeviceInfo(serial="test123")
        assert info.status == DeviceStatus.AVAILABLE


class TestDeviceStatus:
    """DeviceStatus 枚举测试"""

    def test_device_status_values(self):
        assert DeviceStatus.AVAILABLE.value == "available"
        assert DeviceStatus.BUSY.value == "busy"
        assert DeviceStatus.OFFLINE.value == "offline"
        assert DeviceStatus.ERROR.value == "error"
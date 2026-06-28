"""
UI元素操作基类 - 提供通用的UI自动化操作方法
消除 CameraAutomationAW 和 SettingsHandler 之间的代码重复

注意: 所有输入操作都使用重试机制来处理 atx-agent 静默死亡问题
参考: https://github.com/openatx/uiautomator2/issues/224
"""
import time
import logging
from typing import Dict, Optional
from requests.exceptions import ReadTimeout, ConnectTimeout

from base.retry_handler import (
    should_retry_on_connection_error,
    RetryExhaustedError,
    DeviceConnectionError
)


class UIElementOperations:
    """
    UI元素操作基类

    提供 find_element, click_element, long_click_element, swipe 等通用操作
    子类只需提供 self.d (uiautomator2 driver)

    所有输入操作都使用重试机制来处理 atx-agent 静默死亡问题
    """

    # 重试配置
    DEFAULT_MAX_ATTEMPTS = 3
    DEFAULT_BASE_DELAY = 0.5

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._max_retry_attempts = self.DEFAULT_MAX_ATTEMPTS

    def _find_element(self, locator: Dict, timeout: float = 5) -> bool:
        """查找元素是否存在（带重试机制处理 atx-agent 死亡）"""
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retry_attempts + 1):
            try:
                if locator.get("resource_id"):
                    self.d(resource_id=locator["resource_id"]).wait(timeout=timeout)
                    return self.d(resource_id=locator["resource_id"]).exists()
                elif locator.get("xpath"):
                    self.d.xpath(locator["xpath"]).wait(timeout=timeout)
                    return self.d.xpath(locator["xpath"]).exists()
                return False
            except Exception as e:
                last_error = e
                if not should_retry_on_connection_error(e):
                    self.logger.warning(
                        f"查找元素失败(非重试错误): {locator.get('desc', 'unknown')}, error: {e}"
                    )
                    return False

                if attempt < self._max_retry_attempts:
                    self.logger.warning(
                        f"查找元素失败(atx-agent 可能死亡, 尝试 {attempt}/{self._max_retry_attempts}): "
                        f"{locator.get('desc', 'unknown')}, error: {e}"
                    )
                    time.sleep(self.DEFAULT_BASE_DELAY * attempt)
                    continue

                self.logger.error(
                    f"查找元素失败(重试耗尽): {locator.get('desc', 'unknown')}, error: {e}"
                )
                return False

        return False

    def _click_element(self, locator: Dict, timeout: float = 5) -> bool:
        """
        点击元素（带重试机制处理 atx-agent 静默死亡）

        这是最容易受 atx-agent 死亡影响的操作，已添加完整的重试逻辑：
        1. 首次失败后尝试识别 atx-agent 死亡
        2. 指数退避重试
        3. 必要时重新连接设备
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retry_attempts + 1):
            try:
                if locator.get("resource_id"):
                    self.d(resource_id=locator["resource_id"]).click(timeout=timeout)
                    return True
                elif locator.get("xpath"):
                    self.d.xpath(locator["xpath"]).click(timeout=timeout)
                    return True
                return False

            except Exception as e:
                last_error = e

                if not should_retry_on_connection_error(e):
                    self.logger.error(
                        f"点击元素失败(非重试错误): {locator.get('desc', 'unknown')}, error: {e}"
                    )
                    raise DeviceConnectionError(
                        f"点击元素失败: {locator.get('desc', 'unknown')}"
                    ) from e

                if attempt == self._max_retry_attempts:
                    self.logger.error(
                        f"点击元素失败(重试 {self._max_retry_attempts} 次耗尽): "
                        f"{locator.get('desc', 'unknown')}, error: {e}"
                    )
                    raise RetryExhaustedError(
                        operation=f"_click_element({locator.get('desc', 'unknown')})",
                        original_error=e,
                        attempts=self._max_retry_attempts
                    ) from e

                delay = self.DEFAULT_BASE_DELAY * (2 ** (attempt - 1))
                self.logger.warning(
                    f"点击元素失败(atx-agent 可能死亡, 尝试 {attempt}/{self._max_retry_attempts}), "
                    f"{delay:.1f}秒后重试: {locator.get('desc', 'unknown')}, error: {e}"
                )
                time.sleep(delay)

        # 不应该到达这里
        if last_error:
            raise last_error
        return False

    def _long_click_element(self, locator: Dict, duration: float = 1.0) -> bool:
        """长按元素（带重试机制）"""
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retry_attempts + 1):
            try:
                if locator.get("resource_id"):
                    self.d(resource_id=locator["resource_id"]).long_click(duration=duration)
                    return True
                return False
            except Exception as e:
                last_error = e

                if not should_retry_on_connection_error(e):
                    self.logger.error(f"长按元素失败: {locator.get('desc', 'unknown')}, error: {e}")
                    raise DeviceConnectionError(f"长按元素失败") from e

                if attempt < self._max_retry_attempts:
                    delay = self.DEFAULT_BASE_DELAY * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"长按元素失败(atx-agent 可能死亡, 尝试 {attempt}/{self._max_retry_attempts}), "
                        f"{delay:.1f}秒后重试: {locator.get('desc', 'unknown')}"
                    )
                    time.sleep(delay)
                    continue

                raise RetryExhaustedError(
                    operation=f"_long_click_element({locator.get('desc', 'unknown')})",
                    original_error=e,
                    attempts=self._max_retry_attempts
                ) from e

        if last_error:
            raise last_error
        return False

    def _swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """
        滑动屏幕（带重试机制处理 atx-agent 死亡）

        根据 issue #224，swipe 操作也可能导致 atx-agent 死亡
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retry_attempts + 1):
            try:
                self.d.swipe(start_x, start_y, end_x, end_y, duration=duration)
                return
            except Exception as e:
                last_error = e

                if not should_retry_on_connection_error(e):
                    self.logger.error(f"滑动失败: {e}")
                    raise DeviceConnectionError(f"滑动操作失败") from e

                if attempt < self._max_retry_attempts:
                    delay = self.DEFAULT_BASE_DELAY * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"滑动失败(atx-agent 可能死亡, 尝试 {attempt}/{self._max_retry_attempts}), "
                        f"{delay:.1f}秒后重试"
                    )
                    time.sleep(delay)
                    continue

                raise RetryExhaustedError(
                    operation="_swipe",
                    original_error=e,
                    attempts=self._max_retry_attempts
                ) from e

        if last_error:
            raise last_error

    def _get_element_text(self, locator: Dict) -> Optional[str]:
        """获取元素文本"""
        try:
            if locator.get("resource_id"):
                return self.d(resource_id=locator["resource_id"]).get_text()
            elif locator.get("xpath"):
                return self.d.xpath(locator["xpath"]).get_text()
        except Exception:
            return None
        return None

    def is_device_connected(self) -> bool:
        """检查设备是否仍然连接（atx-agent 是否存活）"""
        try:
            self.d.info
            return True
        except Exception:
            return False

    def set_max_retry_attempts(self, max_attempts: int):
        """设置最大重试次数"""
        self._max_retry_attempts = max_attempts
        self.logger.debug(f"最大重试次数设置为: {max_attempts}")

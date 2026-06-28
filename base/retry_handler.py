"""
重试处理器 - 处理 uiautomator2 atx-agent 进程死亡问题

atx-agent 可能在任何输入操作(tap/click/swipe)时静默死亡，
在 HTTP 连接 127.0.0.1:37333 时抛出 ReadTimeout 异常。

参考: https://github.com/openatx/uiautomator2/issues/224
"""
import time
import logging
from functools import wraps
from typing import Callable, Optional, TypeVar, Any
from requests.exceptions import ReadTimeout, ConnectTimeout

logger = logging.getLogger("RetryHandler")

T = TypeVar('T')


class DeviceConnectionError(Exception):
    """设备连接错误（atx-agent 可能已死亡）"""
    pass


class RetryExhaustedError(Exception):
    """重试次数耗尽"""
    def __init__(self, operation: str, original_error: Exception, attempts: int):
        self.operation = operation
        self.original_error = original_error
        self.attempts = attempts
        super().__init__(
            f"操作 '{operation}' 在 {attempts} 次重试后失败: {original_error}"
        )


def should_retry_on_connection_error(exc: Exception) -> bool:
    """
    判断是否应该重试连接错误
    atx-agent 死亡时通常会抛出 ReadTimeout 或 ConnectTimeout
    """
    if isinstance(exc, (ReadTimeout, ConnectTimeout)):
        return True
    # 检查异常消息中是否包含连接错误
    error_msg = str(exc).lower()
    connection_errors = [
        "readtimeout",
        "connecttimeout",
        "connection refused",
        "connection reset",
        "broken pipe",
        "atx-agent",
        "127.0.0.1:37333"
    ]
    return any(err in error_msg for err in connection_errors)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exponential_base: float = 2.0,
    reconnect: bool = True
):
    """
    带重试的装饰器，用于包装可能因 atx-agent 死亡而失败的操作

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数退避基数
        reconnect: 是否在重试前尝试重新连接

    Example:
        @with_retry(max_attempts=3)
        def click_element(self, locator):
            return self.d(resource_id=locator["resource_id"]).click()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 获取 driver 引用用于重连（self.d 或 args[0].d）
            self_or_driver = args[0] if args else None
            driver = None

            if hasattr(self_or_driver, 'd'):
                driver = self_or_driver.d
            elif hasattr(self_or_driver, 'device'):  # some wrappers use 'device'
                driver = self_or_driver.device

            last_error: Optional[Exception] = None
            operation_name = func.__name__

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e

                    if not should_retry_on_connection_error(e):
                        # 非连接错误，直接抛出
                        logger.warning(
                            f"[{operation_name}] 非重试错误，直接抛出: {e}"
                        )
                        raise

                    if attempt == max_attempts:
                        logger.error(
                            f"[{operation_name}] 重试 {max_attempts} 次后失败: {e}"
                        )
                        raise RetryExhaustedError(
                            operation=operation_name,
                            original_error=e,
                            attempts=max_attempts
                        ) from e

                    # 计算延迟（指数退避）
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"[{operation_name}] atx-agent 可能死亡 (尝试 {attempt}/{max_attempts}), "
                        f"{delay:.1f}秒后重试... 错误: {e}"
                    )

                    if reconnect and driver is not None:
                        _attempt_reconnect(driver)

                    time.sleep(delay)

            # 不应该到达这里，但以防万一
            if last_error:
                raise last_error
            raise RetryExhaustedError(
                operation=operation_name,
                original_error=Exception("未知错误"),
                attempts=max_attempts
            )

        return wrapper
    return decorator


def _attempt_reconnect(driver, max_retries: int = 2):
    """
    尝试重新连接 atx-agent

    Args:
        driver: uiautomator2 driver
        max_retries: 最大重连尝试次数
    """
    import uiautomator2 as u2

    for i in range(max_retries):
        try:
            serial = driver.serial if hasattr(driver, 'serial') else None
            logger.info(f"尝试重新连接设备: {serial}")

            # 重新连接
            new_driver = u2.connect(serial)
            # 验证连接
            new_driver.info
            logger.info("重新连接成功")
            return True
        except Exception as e:
            logger.warning(f"重连尝试 {i+1}/{max_retries} 失败: {e}")
            time.sleep(1)

    logger.error("重新连接失败")
    return False


class RetryableOperations:
    """
    可重试操作的混入类

    使用方式:
        class MyCameraOps(RetryableOperations):
            def __init__(self, driver):
                self.d = driver
                self._setup_retry_methods()

            def _setup_retry_methods(self):
                # 将需要重试的方法包装
                self._retry_click = self._make_retry(self._raw_click)
                self._retry_swipe = self._make_retry(self._raw_swipe)

            def _raw_click(self, locator):
                if locator.get("resource_id"):
                    self.d(resource_id=locator["resource_id"]).click()
                elif locator.get("xpath"):
                    self.d.xpath(locator["xpath"]).click()

            def click_element(self, locator):
                return self._retry_click(locator)
    """

    def __init__(self):
        self._retry_config = {
            'max_attempts': 3,
            'base_delay': 0.5,
            'max_delay': 5.0,
            'reconnect': True
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def _make_retry(self, operation: Callable[..., Any]) -> Callable[..., Any]:
        """将操作包装为可重试版本"""
        @with_retry(**self._retry_config)
        def retry_wrapper(*args, **kwargs):
            return operation(*args, **kwargs)
        return retry_wrapper

    def set_retry_config(
        self,
        max_attempts: Optional[int] = None,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None
    ):
        """更新重试配置"""
        if max_attempts is not None:
            self._retry_config['max_attempts'] = max_attempts
        if base_delay is not None:
            self._retry_config['base_delay'] = base_delay
        if max_delay is not None:
            self._retry_config['max_delay'] = max_delay

    def is_agent_alive(self) -> bool:
        """检查 atx-agent 是否存活"""
        try:
            if hasattr(self, 'd') and hasattr(self.d, 'info'):
                self.d.info
                return True
        except Exception:
            pass
        return False

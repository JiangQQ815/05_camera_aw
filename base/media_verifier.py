"""
媒体文件验证器 - 验证照片和视频是否正确保存
"""
import os
import time
import logging
import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class VerificationResult:
    """验证结果"""
    success: bool
    file_path: Optional[str] = None
    file_size: int = 0
    duration: Optional[float] = None
    error: Optional[str] = None


class MediaVerifier:
    """
    媒体文件验证器

    检查DCIM目录下的最新文件，验证照片/视频是否正确保存
    """

    # 常见的相机存储路径
    DCIM_PATHS = [
        "/sdcard/DCIM/Camera",
        "/sdcard/DCIM/100ANDRO",
        "/storage/emulated/0/DCIM/Camera",
    ]

    def __init__(self, device_driver):
        """
        初始化验证器
        :param device_driver: uiautomator2 driver
        """
        self.d = device_driver
        self.logger = logging.getLogger("MediaVerifier")

    def _find_dcim_path(self) -> Optional[str]:
        """查找DCIM目录"""
        for path in self.DCIM_PATHS:
            if self.d.shell(f"ls {path}").strip():
                return path
        return self.DCIM_PATHS[0]  # 返回默认路径

    def _get_latest_file(self, directory: str, extension: str) -> Optional[tuple]:
        """
        获取目录中最新文件
        :return: (文件路径, 修改时间) 或 None
        """
        try:
            result = self.d.shell(f"ls -t {directory}/*.{extension} 2>/dev/null | head -1")
            if result.strip():
                file_path = result.strip()
                size_result = self.d.shell(f"stat -c %s {file_path} 2>/dev/null || wc -c < {file_path}")
                size = int(size_result.strip() or "0")
                return (file_path, size)
        except Exception as e:
            self.logger.debug(f"获取最新文件失败: {e}")
        return None

    def verify_photo_saved(self, min_size_kb: int = 10) -> VerificationResult:
        """
        验证照片已保存到DCIM
        :param min_size_kb: 最小文件大小(KB)
        :return: VerificationResult
        """
        self.logger.info("验证照片文件...")

        try:
            dcim = self._find_dcim_path()
            self.logger.debug(f"检查目录: {dcim}")

            latest = self._get_latest_file(dcim, "jpg")
            if not latest:
                latest = self._get_latest_file(dcim, "jpeg")
            if not latest:
                latest = self._get_latest_file(dcim, "png")

            if not latest:
                return VerificationResult(
                    success=False,
                    error="未找到照片文件"
                )

            file_path, size = latest
            size_kb = size // 1024

            if size_kb < min_size_kb:
                return VerificationResult(
                    success=False,
                    file_path=file_path,
                    file_size=size_kb,
                    error=f"文件过小 ({size_kb}KB < {min_size_kb}KB)"
                )

            self.logger.info(f"照片验证通过: {file_path} ({size_kb}KB)")
            return VerificationResult(
                success=True,
                file_path=file_path,
                file_size=size_kb
            )

        except Exception as e:
            self.logger.error(f"照片验证异常: {e}")
            return VerificationResult(
                success=False,
                error=str(e)
            )

    def verify_video_saved(self, min_duration_sec: float = 1.0) -> VerificationResult:
        """
        验证视频已保存到DCIM
        :param min_duration_sec: 最小视频时长(秒)
        :return: VerificationResult
        """
        self.logger.info("验证视频文件...")

        try:
            dcim = self._find_dcim_path()
            self.logger.debug(f"检查目录: {dcim}")

            latest = self._get_latest_file(dcim, "mp4")
            if not latest:
                latest = self._get_latest_file(dcim, "3gp")

            if not latest:
                return VerificationResult(
                    success=False,
                    error="未找到视频文件"
                )

            file_path, size = latest

            # 尝试获取视频时长（如果ffprobe可用）
            duration = None
            try:
                probe_result = self.d.shell(
                    f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
                )
                if probe_result.strip():
                    duration = float(probe_result.strip())
                    if duration < min_duration_sec:
                        return VerificationResult(
                            success=False,
                            file_path=file_path,
                            file_size=size,
                            duration=duration,
                            error=f"视频过短 ({duration:.1f}s < {min_duration_sec}s)"
                        )
            except:
                pass  # ffprobe不可用时跳过时长验证

            size_mb = size // (1024 * 1024)
            self.logger.info(f"视频验证通过: {file_path} ({size_mb}MB, {duration or '?'}s)")
            return VerificationResult(
                success=True,
                file_path=file_path,
                file_size=size,
                duration=duration
            )

        except Exception as e:
            self.logger.error(f"视频验证异常: {e}")
            return VerificationResult(
                success=False,
                error=str(e)
            )


# ============================================
# 工厂函数
# ============================================

def create_media_verifier(driver) -> MediaVerifier:
    """创建媒体验证器实例"""
    return MediaVerifier(driver)

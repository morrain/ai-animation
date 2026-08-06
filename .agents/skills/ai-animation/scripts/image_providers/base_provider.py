#!/usr/bin/env python3
"""
base_provider.py
ai-animation Skill 生图大模型 Provider 抽象基类
定义统一的硬契约与方法签名。
"""

from abc import ABC, abstractmethod

class BaseImageProvider(ABC):
    """所有生图大模型 API 驱动器的抽象基类"""

    @abstractmethod
    def generate(self, prompt: str, output_image_path: str, reference_image_path: str = None, reference_image_url: str = None, size: str = "2K", ratio: str = "16:9"):
        """
        生成/修改单张静态关键帧图片的核心契约方法：
        :param prompt: 图生图 / 文生图控制提示词
        :param output_image_path: 输出 PNG/JPG 图片的物理绝对路径
        :param reference_image_path: 参考基准图本地路径 (图生图模式)，若为 None 则为纯文生图模式
        :param reference_image_url: 参考基准图公网 HTTP URL（优先级高于 reference_image_path），用于 img2img API 直接传 URL
        :param size: 分辨率预设等级 (如 1K, 2K, 3K, 4K 或 1280x720)
        :param ratio: 画面纵横比 (如 16:9)
        :return: (ok: bool, image_url: str | None) 元组；生成并保存成功 ok=True，失败 ok=False
        """
        pass

#!/usr/bin/env python3
"""
base_provider.py
ai-animation Skill 视频大模型 Provider 抽象基类硬接口
"""

import abc

class BaseVideoProvider(abc.ABC):
    """所有第三方 AI 视频大模型 API 插件必须继承的抽象父类"""
    
    @abc.abstractmethod
    def generate(self, first_frame_path: str, last_frame_path: str, prompt: str, output_mp4_path: str, duration_sec: float = 6.5, fps: int = 24) -> bool:
        """
        生成单镜无声 MP4 视频的核心方法
        
        :param first_frame_path: 动作初始首帧图片物理路径
        :param last_frame_path: 动作完成尾帧图片物理路径
        :param prompt: 视频大模型运动指导 Prompt (英文)
        :param output_mp4_path: 目标输出 MP4 物理文件路径
        :param duration_sec: 预期视频时长(秒)
        :param fps: 帧率
        :return: 生成并成功下载返回 True，否则返回 False
        """
        pass

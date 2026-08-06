#!/usr/bin/env python3
"""
image_providers/__init__.py
ai-animation Skill 统一生图 Factory 模块
唯一环境变量 `IMAGE_PROVIDER_CONFIG` 驱动。
"""

import os
from .base_provider import BaseImageProvider
from .generic_http_provider import GenericHttpImageProvider

def get_image_provider(provider_config: str = None) -> BaseImageProvider:
    """
    获取 AI 生图大模型 Provider 实例：
    :param provider_config: 配置文件路径或配置别名 (如 "agnes_ai" 或 "providers/image/agnes_ai.json")
    :return: 继承自 BaseImageProvider 的驱动对象
    """
    config_setting = provider_config or os.getenv("IMAGE_PROVIDER_CONFIG") or "agnes_ai"
    
    candidate_paths = [
        config_setting,
        f"providers/image/{config_setting}.json",
        f"providers/{config_setting}.json",
        os.path.expanduser(f"~/.config/ai-animation/providers/image/{config_setting}.json")
    ]
    
    resolved_path = None
    for path in candidate_paths:
        if path and os.path.exists(path):
            resolved_path = os.path.abspath(path)
            break
            
    if not resolved_path:
        print(f"⚠️ [WARNING]: 未能寻找到生图模型配置文件 [{config_setting}]，将回退至系统默认配置 providers/image/agnes_ai.json...")
        default_fallback = os.path.abspath("providers/image/agnes_ai.json")
        if os.path.exists(default_fallback):
            resolved_path = default_fallback
            
    return GenericHttpImageProvider(config_path=resolved_path)

#!/usr/bin/env python3
"""
video_providers 统一配置工厂
所有 AI 视频大模型提供商（包含 Agnes AI 默认配置及用户自定义扩展）均基于声明式 JSON 配置无缝加载。
配置文件统一存储于项目根目录 `providers/video/` 目录下。
"""

import os
from .base_provider import BaseVideoProvider
from .generic_http_provider import GenericHttpProvider

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 寻找到项目根目录 (Workspace Root)
WORKSPACE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))

def get_video_provider(provider_config: str = None) -> BaseVideoProvider:
    """
    极简统一配置工厂：
    解析 `provider_config` (或环境变量 `VIDEO_PROVIDER_CONFIG`，默认: `providers/video/agnes_ai.json`)。
    无论是文件路径还是短名称 (如 agnes_ai / kling)，统一解析为配置 JSON 并返回 GenericHttpProvider 实例。
    """
    target = provider_config or os.getenv("VIDEO_PROVIDER_CONFIG") or "agnes_ai"

    # 如果传进来的是现存的具体文件路径
    if os.path.exists(target):
        return GenericHttpProvider(config_path=target)

    # 规范化短名称 (如 agnes-ai -> agnes_ai)
    clean_name = target.lower().replace("-", "_")
    name_json = clean_name if clean_name.endswith(".json") else f"{clean_name}.json"

    candidate_paths = [
        os.path.join(WORKSPACE_ROOT, "providers", "video", name_json),
        os.path.join(WORKSPACE_ROOT, "providers", name_json),
        os.path.expanduser(f"~/.config/ai-animation/providers/video/{name_json}"),
        os.path.abspath(os.path.join("providers", "video", name_json)),
        os.path.abspath(os.path.join("providers", name_json))
    ]

    for p in candidate_paths:
        if os.path.exists(p):
            return GenericHttpProvider(config_path=p)

    # 默认兜底读取 providers/video/agnes_ai.json
    default_json = os.path.join(WORKSPACE_ROOT, "providers", "video", "agnes_ai.json")
    if os.path.exists(default_json):
        return GenericHttpProvider(config_path=default_json)

    print(f"⚠️ [WARNING]: 无法解析配置文件或提供商 [{target}]，使用兜底逻辑...")
    return GenericHttpProvider(config_path=default_json)

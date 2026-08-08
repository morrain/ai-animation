#!/usr/bin/env python3
"""
generic_http_provider.py
ai-animation Skill 方案三：通用声明式 JSON 配置驱动型 AI 视频大模型 Provider

实现零代码修改扩展：
用户只需编写一个 JSON 配置文件并设置 `export VIDEO_PROVIDER_CONFIG="/path/to/config.json"`，
系统即可自动解析 Header、Payload 模板与 JsonPath 下载逻辑。
"""

import os
import time
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from .base_provider import BaseVideoProvider

def file_to_base64_data_uri(file_path):
    """将本地图片文件转换为 Base64 Data URI"""
    if not file_path or not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        import base64
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
    return f"data:{mime};base64,{encoded}"

def get_nested_value(data, path_str):
    """根据点号分割的路径 (如 metadata.url) 从 nested dict 中提取值"""
    if not data or not path_str:
        return None
    keys = path_str.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return None
    return curr

def substitute_variables(template_obj, var_map):
    """递归完成 Payload/Header 中的变量占位符替换 (${VARIABLE_NAME})"""
    if isinstance(template_obj, str):
        result = template_obj
        for var_name, var_val in var_map.items():
            placeholder = f"${{{var_name}}}"
            if placeholder in result:
                if result == placeholder:
                    return var_val
                result = result.replace(placeholder, str(var_val) if var_val is not None else "")
        # 匹配环境变量
        def env_replacer(match):
            e_name = match.group(1)
            return os.getenv(e_name, "")
        result = re.sub(r"\$\{([A-Za-z0-9_]+)\}", env_replacer, result)
        return result
    elif isinstance(template_obj, dict):
        return {k: substitute_variables(v, var_map) for k, v in template_obj.items()}
    elif isinstance(template_obj, list):
        return [substitute_variables(v, var_map) for v in template_obj]
    else:
        return template_obj

class GenericHttpProvider(BaseVideoProvider):
    """声明式 JSON 驱动的核心视频生成驱动器"""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.getenv("VIDEO_PROVIDER_CONFIG")
        self.config = {}
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                print(f"📋 [GenericHttpProvider]: 成功加载声明式视频 API 配置: {self.config_path}")
            except Exception as e:
                print(f"❌ [GenericHttpProvider]: 加载配置文件失败 {self.config_path}: {e}")

    def generate(self, first_frame_path: str, last_frame_path: str, prompt: str, output_mp4_path: str, duration_sec: float = 6.5, fps: int = 24) -> bool:
        if not self.config:
            print("❌ [GenericHttpProvider Error]: 缺少有效配置文件！")
            print("请设置 `export VIDEO_PROVIDER_CONFIG=\"/path/to/provider_config.json\"` 后重试。")
            return False

        # 1. 构建变量映射表
        b64_first = file_to_base64_data_uri(first_frame_path)
        b64_last = file_to_base64_data_uri(last_frame_path)

        url_first = os.getenv("FIRST_FRAME_PUBLIC_URL") or b64_first
        url_last = os.getenv("LAST_FRAME_PUBLIC_URL") or b64_last

        var_map = {
            "FIRST_FRAME_BASE64": b64_first,
            "LAST_FRAME_BASE64": b64_last,
            "FIRST_FRAME_URL": url_first,
            "LAST_FRAME_URL": url_last,
            "FIRST_FRAME_PATH": first_frame_path,
            "LAST_FRAME_PATH": last_frame_path,
            "PROMPT": prompt,
            "DURATION": duration_sec,
            "FPS": fps,
            "AGNES_API_KEY": os.getenv("AGNES_API_KEY") or os.getenv("VIDEO_API_KEY") or "",
            "API_KEY": os.getenv("AGNES_API_KEY") or os.getenv("VIDEO_API_KEY") or ""
        }

        # 2. 解析 Create Request
        create_url = substitute_variables(self.config.get("create_url", ""), var_map)
        method = self.config.get("method", "POST").upper()
        headers = substitute_variables(self.config.get("headers", {}), var_map)
        payload_template = self.config.get("payload_template", {})
        payload = substitute_variables(payload_template, var_map)

        print(f"🚀 [Declarative Provider]: 发起 API 请求到 [{method}] {create_url}...", flush=True)

        req_data = json.dumps(payload).encode("utf-8") if payload else None

        # 机制：防止 API Rate Limit (如 Agnes AI 限制 1分钟1次)，支持自动重试 3 次
        res_data = None
        for attempt in range(3):
            req = urllib.request.Request(create_url, data=req_data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                if e.code == 429:
                    print(f"⏳ [HTTP 429 Rate Limit 触发]: 达到 API 频率限制，等待 60 秒后重试 (重试 {attempt+1}/3)...", flush=True)
                    time.sleep(60)
                else:
                    print(f"❌ [API 请求失败 HTTP {e.code}]: {err_body}", flush=True)
                    return False
            except Exception as e:
                print(f"❌ [API 请求发起异常]: {e}", flush=True)
                return False

        if not res_data:
            print(f"❌ [错误]: 请求重试次数用尽，未能获取有效响应数据。")
            return False

        # 3. 判断是同步直接返回 URL 还是异步轮询
        async_poll = self.config.get("async_poll", False)

        if not async_poll:
            video_url_path = self.config.get("response_video_url_path", "video_url")
            video_url = get_nested_value(res_data, video_url_path)
            if video_url:
                os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
                urllib.request.urlretrieve(video_url, output_mp4_path)
                print(f"🎉 同步生成视频成功下载至: {output_mp4_path}")
                return True
            else:
                print(f"❌ [错误]: 响应中根据路径 [{video_url_path}] 未提取到视频 URL: {res_data}")
                return False
        else:
            # 异步轮询模式
            task_id_path = self.config.get("response_task_id_path", "task_id")
            task_id = get_nested_value(res_data, task_id_path)
            if not task_id:
                print(f"❌ [错误]: 异步任务创建成功但未返回 Task ID (Key: {task_id_path}): {res_data}")
                return False

            var_map["TASK_ID"] = task_id
            var_map["VIDEO_ID"] = task_id

            poll_url = substitute_variables(self.config.get("poll_url_template", ""), var_map)
            poll_headers = substitute_variables(self.config.get("poll_headers", headers), var_map)
            poll_status_path = self.config.get("poll_status_path", "status")
            completed_value = self.config.get("poll_completed_value", "completed")
            poll_video_url_path = self.config.get("poll_video_url_path", "metadata.url")
            max_attempts = self.config.get("max_poll_attempts", 120)
            poll_interval = self.config.get("poll_interval_sec", 5)

            print(f"✅ 任务 ID [{task_id}] 提交成功! 开始轮询 {poll_url}...")

            for attempt in range(max_attempts):
                time.sleep(poll_interval)
                q_req = urllib.request.Request(poll_url, headers=poll_headers, method="GET")
                try:
                    with urllib.request.urlopen(q_req, timeout=30) as q_resp:
                        q_res = json.loads(q_resp.read().decode("utf-8"))
                except urllib.error.HTTPError as e:
                    err_text = ""
                    try:
                        err_text = e.read().decode("utf-8")
                    except Exception:
                        pass
                    print(f"  ❌ [Attempt {attempt+1}] 轮询接口返回 HTTP 异常 ({e.code}): {err_text}", flush=True)
                    if e.code == 400 or "error" in err_text.lower() or "policy" in err_text.lower():
                        return False
                    continue
                except Exception as e:
                    print(f"  [Attempt {attempt+1}] 轮询查询异常: {e}，继续等待...", flush=True)
                    continue

                curr_status = get_nested_value(q_res, poll_status_path)
                print(f"  ⏳ [Attempt {attempt+1}/{max_attempts}] 状态: {curr_status}", flush=True)

                if str(curr_status).lower() == str(completed_value).lower():
                    final_video_url = get_nested_value(q_res, poll_video_url_path)
                    if not final_video_url:
                        print(f"❌ [错误]: 任务已完成但根据 JsonPath [{poll_video_url_path}] 未提取到 URL: {q_res}")
                        return False
                    
                    os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
                    urllib.request.urlretrieve(final_video_url, output_mp4_path)
                    print(f"🎉 异步任务生成成功，视频已下载保存至: {output_mp4_path}")
                    return True
                elif str(curr_status).lower() in ["failed", "error", "canceled"]:
                    print(f"❌ [任务生成失败]: {q_res}")
                    return False

            print(f"⏰ [超时]: 异步任务轮询超时！")
            return False

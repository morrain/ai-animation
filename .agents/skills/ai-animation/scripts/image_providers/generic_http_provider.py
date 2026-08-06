#!/usr/bin/env python3
"""
generic_http_provider.py
ai-animation Skill 声明式 JSON 配置驱动型 AI 生图大模型 Provider
支持文生图（Text-to-Image）与参考图控制生图（Image-to-Image / Multi-Image Composition）。
"""

import os
import time
import json
import re
import base64
import urllib.request
import urllib.parse
import urllib.error
from .base_provider import BaseImageProvider

def file_to_base64_data_uri(file_path, max_dim=768, quality=75):
    """将本地图片文件高效缩放并转换为 Base64 JPEG Data URI (保持在 130KB 以内避免 API 500)"""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        from PIL import Image
        import io
        with Image.open(file_path) as img:
            img.thumbnail((max_dim, max_dim))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        # 回退原始读取
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        return f"data:{mime};base64,{encoded}"

def get_nested_value(data, path_str):
    """根据点号分割的路径 (如 data.0.url 或 data[0].url) 从 nested dict/list 中提取值"""
    if data is None or not path_str:
        return None
    # 替换 [0] 为 .0
    clean_path = path_str.replace("[", ".").replace("]", "")
    keys = clean_path.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        elif isinstance(curr, list) and k.isdigit():
            idx = int(k)
            if 0 <= idx < len(curr):
                curr = curr[idx]
            else:
                return None
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

class GenericHttpImageProvider(BaseImageProvider):
    """声明式 JSON 驱动的核心生图驱动器"""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.getenv("IMAGE_PROVIDER_CONFIG")
        self.config = {}
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                print(f"📋 [GenericHttpImageProvider]: 成功加载声明式生图 API 配置: {self.config_path}", flush=True)
            except Exception as e:
                print(f"❌ [GenericHttpImageProvider]: 加载生图配置文件失败 {self.config_path}: {e}", flush=True)

    def generate(self, prompt, output_image_path, reference_image_path=None, reference_image_url=None, size="2K", ratio="16:9"):
        """使用 HTTP POST 请求调用生图 API"""
        if not self.config:
            print("❌ [GenericHttpImageProvider Error]: 缺少有效生图配置文件！", flush=True)
            print("请设置 `export IMAGE_PROVIDER_CONFIG=\"/path/to/provider_config.json\"` 后重试。", flush=True)
            return False, None

        # 1. 构建变量映射表
        ref_b64 = file_to_base64_data_uri(reference_image_path) if reference_image_path else ""
        ref_url = reference_image_url or os.getenv("REF_IMAGE_PUBLIC_URL") or ref_b64

        var_map = {
            "PROMPT": prompt,
            "SIZE": size,
            "RATIO": ratio,
            "REF_IMAGE_BASE64": ref_b64,
            "REF_IMAGE_URL": ref_url,
            "REF_IMAGE_PATH": reference_image_path or "",
            "AGNES_API_KEY": os.getenv("AGNES_API_KEY") or os.getenv("IMAGE_API_KEY") or "",
            "API_KEY": os.getenv("AGNES_API_KEY") or os.getenv("IMAGE_API_KEY") or ""
        }

        # 2. 判断选择纯文生图模版还是图生图/参考图模版
        if (reference_image_url or reference_image_path) and "img2img_payload_template" in self.config:
            payload_template = self.config["img2img_payload_template"]
            ref_name = reference_image_url if reference_image_url else os.path.basename(reference_image_path)
            mode_desc = f"图生图控制模式 (参考图: {ref_name})"
        else:
            payload_template = self.config.get("payload_template", {})
            mode_desc = "纯文生图模式"

        create_url = substitute_variables(self.config.get("create_url", ""), var_map)
        method = self.config.get("method", "POST").upper()
        headers = substitute_variables(self.config.get("headers", {}), var_map)
        payload = substitute_variables(payload_template, var_map)

        print(f"\n==================== 🔍 [API DEBUG LOG START] ====================", flush=True)
        print(f"📌 [Raw Prompt]:\n{prompt}\n", flush=True)
        print(f"📌 [Target URL]: {create_url}", flush=True)
        print(f"📌 [Headers]: {json.dumps({k: ('***' if 'auth' in k.lower() else v) for k, v in headers.items()})}", flush=True)
        print(f"📌 [Payload JSON Sent to API]:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n", flush=True)
        print(f"==================================================================\n", flush=True)

        req_data = json.dumps(payload).encode("utf-8") if payload else None

        res_data = None
        for attempt in range(3):
            req = urllib.request.Request(create_url, data=req_data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    resp_text = resp.read().decode("utf-8")
                    print(f"📩 [API Response JSON Body]:\n{resp_text[:500]}...", flush=True)
                    res_data = json.loads(resp_text)
                    break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                if e.code == 429:
                    print(f"⏳ [HTTP 429 Rate Limit]: 达到生图 API 频率限制，等待 30 秒后重试 ({attempt+1}/3)...", flush=True)
                    time.sleep(30)
                elif reference_image_path and payload_template != self.config.get("payload_template", {}):
                    print(f"⚠️ [生图 API 图生图失败 HTTP {e.code}]: {err_body}，自动降级为纯文生图模式重试...", flush=True)
                    return self.generate(prompt=prompt, output_image_path=output_image_path, reference_image_path=None, size=size, ratio=ratio)
                else:
                    print(f"❌ [生图 API 请求失败 HTTP {e.code}]: {err_body}", flush=True)
                    return False
            except Exception as e:
                print(f"⚠️ [生图 API 网络波动]: {e}，正在尝试重试 ({attempt+1}/3)...", flush=True)
                time.sleep(5)

        if not res_data:
            print("❌ [生图 API 请求多次重试后仍然失败]", flush=True)
            return False

        if not res_data:
            print(f"❌ [错误]: 重试次数用尽，未收到有效生图 API 响应。", flush=True)
            return False

        # 3. 提取图像结果 (支持 URL 提取与 Base64 提取)
        image_url_path = self.config.get("response_image_url_path", "data.0.url")
        image_b64_path = self.config.get("response_image_b64_path")

        image_url = get_nested_value(res_data, image_url_path)
        image_b64 = get_nested_value(res_data, image_b64_path) if image_b64_path else None

        os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)

        if image_url:
            print(f"📥 正在下载生成的图片: {image_url} -> {output_image_path}...", flush=True)
            import ssl
            download_success = False
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            for attempt in range(3):
                try:
                    req = urllib.request.Request(image_url, headers=headers)
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp, open(output_image_path, "wb") as f:
                        f.write(resp.read())
                    download_success = True
                    break
                except Exception as e:
                    print(f"  ⚠️ 下载图片重试 ({attempt+1}/3): {e}", flush=True)
                    time.sleep(2)
            if download_success and os.path.exists(output_image_path) and os.path.getsize(output_image_path) > 0:
                print(f"🎉 静态关键帧生成成功保存至: {output_image_path}", flush=True)
                return True, image_url
            else:
                print(f"❌ 图像文件下载落地失败!", flush=True)
                return False, None
        elif image_b64:
            print(f"💾 正在解码 Base64 图像保存至: {output_image_path}...", flush=True)
            img_bytes = base64.b64decode(image_b64)
            with open(output_image_path, "wb") as f:
                f.write(img_bytes)
            print(f"🎉 静态关键帧生成成功保存至: {output_image_path}", flush=True)
            return True, None
        else:
            print(f"❌ [生图解析错误]: 响应中未根据 JsonPath [{image_url_path}] 找到有效的图片 URL/Base64! 原始响应: {res_data}", flush=True)
            return False

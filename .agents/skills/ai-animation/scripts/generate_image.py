#!/usr/bin/env python3
"""
generate_image.py
ai-animation Skill 底层单张图像渲染引擎

纯粹实现单图生成逻辑（文生图 / 图生图），不绑定 storyboard.json 或分镜迭代。
上层业务（Skill/Agent）根据分镜与首尾帧策略，自行按需多次调度本脚本。

用法:
  python3 generate_image.py --prompt "..." --output "path/to/output.png" [--ref "path/to/ref.png"] [-c CONFIG] [--project_dir DIR]
  或
  python3 generate_image.py "path/to/output.png" "prompt text..." [--ref "path/to/ref.png"] [-c CONFIG]
"""

import sys
import os
import json

# 挂载技能脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from image_providers import get_image_provider

def clean_prompt(raw_prompt: str) -> str:
    """保留原版提示词，不做任何规则过滤与清洗"""
    if not raw_prompt:
        return ""
    return raw_prompt.strip()

def get_style_postfix(project_dir: str) -> str:
    """获取项目冰封风格或系统预设风格的 prompt_postfix"""
    if not project_dir:
        return ""
    style_postfix = ""
    style_sel_path = os.path.join(project_dir, "state", "style-selection.json")
    if os.path.exists(style_sel_path):
        try:
            with open(style_sel_path, "r", encoding="utf-8") as f:
                sid = json.load(f).get("style_id", "vox")
            style_json = os.path.join(os.path.dirname(script_dir), "resources", "styles", sid, "style.json")
            if os.path.exists(style_json):
                with open(style_json, "r", encoding="utf-8") as f:
                    style_postfix = json.load(f).get("visual", {}).get("prompt_postfix", "")
        except Exception:
            pass
    return style_postfix

def generate_image(prompt: str, output_path: str, reference_image_path=None, reference_image_url=None, provider_config=None, project_dir=None):
    """渲染单张图像核心方法"""
    cleaned_prompt = clean_prompt(prompt)
    if project_dir:
        style_postfix = get_style_postfix(project_dir)
        if style_postfix and "paper collage" not in cleaned_prompt.lower():
            cleaned_prompt += f", {style_postfix}"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    provider = get_image_provider(provider_config)

    print(f"🎨 [generate_image] 渲染单张图像: {os.path.basename(output_path)}")
    print(f"  ├─ 输出路径: {output_path}")
    if reference_image_path:
        print(f"  ├─ 参考图像: {reference_image_path}")
    print(f"  └─ Prompt: {cleaned_prompt[:100]}...")

    res = provider.generate(
        prompt=cleaned_prompt,
        output_image_path=output_path,
        reference_image_path=reference_image_path,
        reference_image_url=reference_image_url
    )
    ok = res[0] if isinstance(res, tuple) else res
    if not ok:
        print(f"💥 图像生成失败: {output_path}")
        return False

    print(f"✨ 图像成功落盘: {output_path}")
    return True

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("用法:")
        print("  python3 generate_image.py --prompt \"...\" --output \"path/to/output.png\" [--ref \"path/to/ref.png\"] [-c CONFIG] [--project_dir DIR]")
        print("  python3 generate_image.py \"path/to/output.png\" \"prompt text...\" [--ref \"path/to/ref.png\"] [-c CONFIG]")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ["-h", "--help"] else 1)

    prompt = None
    output_path = None
    ref_image = None
    provider_config = None
    project_dir = None

    # 位置参数解析降级兼容
    if not sys.argv[1].startswith("-"):
        output_path = sys.argv[1]
        if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
            prompt = sys.argv[2]

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--prompt" and i + 1 < len(sys.argv):
            prompt = sys.argv[i+1]
            i += 2
        elif arg == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i+1]
            i += 2
        elif arg in ["--ref", "--ref_image", "--reference_image_path"] and i + 1 < len(sys.argv):
            ref_image = sys.argv[i+1]
            i += 2
        elif arg in ["-c", "--provider_config"] and i + 1 < len(sys.argv):
            provider_config = sys.argv[i+1]
            i += 2
        elif arg == "--project_dir" and i + 1 < len(sys.argv):
            project_dir = sys.argv[i+1]
            i += 2
        else:
            i += 1

    if not prompt or not output_path:
        print("❌ [ERROR]: 缺少必填参数 --prompt 与 --output！")
        sys.exit(1)

    ok = generate_image(
        prompt=prompt,
        output_path=output_path,
        reference_image_path=ref_image,
        provider_config=provider_config,
        project_dir=project_dir
    )

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()

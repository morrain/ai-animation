#!/usr/bin/env python3
"""
generate_image.py
ai-animation Skill 阶段二（视觉阶段）静态关键帧图像自动化生成与调度引擎

根据 <project_dir>/01-director/storyboard.json 与 <project_dir>/02-visual/visual_spec.json
调用已接入的 AI 生图模型 Provider（默认 Agnes Image 2.1 Flash），渲染生成单镜首尾关键帧：
  - shot_XX_first.png (文生图或风格迁移首帧)
  - shot_XX_last.png (首帧锚点图生图演进尾帧)

用法:
  python3 generate_image.py <project_dir> [--shot_id N] [--all] [-c / --provider_config CONFIG_PATH]
"""

import sys
import os
import json
import re

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




def generate_shot_keyframes(project_dir, shot_id=1, provider_config=None, generate_both_frames=True):
    """为指定分镜渲染首尾控制帧"""
    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    if not os.path.exists(sb_path):
        print(f"❌ [ERROR]: 找不到 storyboard.json 编导方案: {sb_path}")
        return False

    with open(sb_path, "r", encoding="utf-8") as f:
        sb = json.load(f)

    shots = sb.get("shots", [])
    target_shot = next((s for s in shots if s["shot_id"] == shot_id), None)
    if not target_shot:
        print(f"❌ [ERROR]: 未在分镜数据中查找到 shot_id = {shot_id}")
        return False

    keyframes_dir = os.path.join(project_dir, "02-visual", "keyframes")
    os.makedirs(keyframes_dir, exist_ok=True)

    first_png = os.path.join(keyframes_dir, f"shot_{shot_id:02d}_first.png")
    last_png = os.path.join(keyframes_dir, f"shot_{shot_id:02d}_last.png")

    kp = target_shot.get("keyframe_prompts", {})
    raw_first = kp.get("first_frame_prompt") or target_shot.get("first_frame_prompt") or target_shot.get("image_prompt") or ""
    raw_last = kp.get("image_prompt") or kp.get("last_frame_prompt") or target_shot.get("last_frame_prompt") or target_shot.get("image_prompt") or ""

    # 自动获取项目选定 Style 的 prompt_postfix 避免画风漂移
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

    first_prompt = clean_prompt(raw_first)
    last_prompt = clean_prompt(raw_last)

    if style_postfix and "paper collage" not in first_prompt.lower():
        first_prompt += f", {style_postfix}"
    if style_postfix and "paper collage" not in last_prompt.lower():
        last_prompt += f", {style_postfix}"

    provider = get_image_provider(provider_config)

    print(f"🎨 正在为主题 [{os.path.basename(project_dir)}] 调度生成镜头 #{shot_id:02d} 静态控制帧...")

    # 检查是否为连续分镜（需参考上一分镜尾帧）
    refer_prev = target_shot.get("refer_previous_end_frame") or target_shot.get("continuity", {}).get("refer_previous_shot")
    ref_shot_id = target_shot.get("reference_shot_id") or target_shot.get("continuity", {}).get("reference_shot_id")
    if ref_shot_id is None and refer_prev:
        ref_shot_id = shot_id - 1

    first_ref_image = None
    if ref_shot_id:
        prev_last = os.path.join(keyframes_dir, f"shot_{ref_shot_id:02d}_last.png")
        prev_first = os.path.join(keyframes_dir, f"shot_{ref_shot_id:02d}_first.png")
        prev_single = os.path.join(keyframes_dir, f"shot_{ref_shot_id:02d}.png")
        if os.path.exists(prev_last):
            first_ref_image = prev_last
            print(f"  ├─ 🔗 [跨镜头连续性]: 首帧参考分镜 #{ref_shot_id:02d} 的尾帧 ({os.path.basename(prev_last)})")
        elif os.path.exists(prev_single):
            first_ref_image = prev_single
            print(f"  ├─ 🔗 [跨镜头连续性]: 首帧参考分镜 #{ref_shot_id:02d} 的主帧 ({os.path.basename(prev_single)})")
        elif os.path.exists(prev_first):
            first_ref_image = prev_first
            print(f"  ├─ 🔗 [跨镜头连续性]: 首帧参考分镜 #{ref_shot_id:02d} 的首帧 ({os.path.basename(prev_first)})")
        else:
            print(f"  ⚠️ [WARNING]: 分镜 #{shot_id:02d} 标记参考分镜 #{ref_shot_id:02d}，但物理参考图像文件未在 {keyframes_dir} 找到!")

    print(f"  ├─ 净化的首帧 Prompt: {first_prompt[:80]}...")

    # 1. 渲染首帧
    res_first = provider.generate(
        prompt=first_prompt, 
        output_image_path=first_png,
        reference_image_path=first_ref_image
    )
    if isinstance(res_first, tuple):
        ok_first, first_url = res_first
    else:
        ok_first, first_url = res_first, None

    if not ok_first:
        print(f"💥 镜头 #{shot_id:02d} 首帧渲染失败!")
        return False

    if generate_both_frames:
        print(f"  ├─ 净化的尾帧 Prompt: {last_prompt[:80]}...")
        # 2. 渲染尾帧 (图生图：传递首帧图片路径及公网 URL)
        res_last = provider.generate(
            prompt=last_prompt,
            output_image_path=last_png,
            reference_image_path=first_png,
            reference_image_url=first_url
        )
        ok_last = res_last[0] if isinstance(res_last, tuple) else res_last
        if not ok_last:
            print(f"💥 镜头 #{shot_id:02d} 尾帧渲染失败!")
            return False

    return True

def generate_all_keyframes(project_dir, provider_config=None):
    """批量渲染所有分镜的关键帧"""
    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    if not os.path.exists(sb_path):
        print(f"❌ 找不到 storyboard.json 编导方案: {sb_path}")
        return False

    with open(sb_path, "r", encoding="utf-8") as f:
        sb = json.load(f)

    shots = sb.get("shots", [])
    print(f"🚀 开始全量批量生成 {len(shots)} 个分镜的静态关键帧...")

    for shot in shots:
        sid = shot["shot_id"]
        ok = generate_shot_keyframes(project_dir, shot_id=sid, provider_config=provider_config, generate_both_frames=True)
        if not ok:
            print(f"💥 镜头 #{sid:02d} 生成失败，中止调度。")
            return False

    print(f"✨ 所有分镜静态关键帧生成完成！")
    return True

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("用法: python3 generate_image.py <project_dir> [--shot_id N] [--all] [-c / --provider_config CONFIG_PATH]")
        print("例: python3 generate_image.py why-is-the-sky-blue --shot_id 1")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ["-h", "--help"] else 1)

    project_dir = sys.argv[1]
    shot_id = 1
    generate_all = False
    provider_config = None

    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--shot_id" and i + 1 < len(sys.argv):
            shot_id = int(sys.argv[i+1])
        elif sys.argv[i] == "--all":
            generate_all = True
        elif sys.argv[i] in ["-c", "--provider_config"] and i + 1 < len(sys.argv):
            provider_config = sys.argv[i+1]

    if generate_all:
        ok = generate_all_keyframes(project_dir, provider_config=provider_config)
    else:
        ok = generate_shot_keyframes(project_dir, shot_id=shot_id, provider_config=provider_config)

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()

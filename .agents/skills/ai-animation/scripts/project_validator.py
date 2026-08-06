#!/usr/bin/env python3
"""
project_validator.py
ai-animation Skill 项目契约与 Schema 全阶段静态校验工具

功能：
1. validate-director: 校验 01-director/storyboard.json 结构与规则（18.375s 硬上限、字幕标点剥离、双端提示词）。
2. validate-visual: 校验 02-visual/visual_spec.json 的镜头覆盖率与关键帧图片存在性。
3. validate-motion: 校验 03-motion/shots/ 单镜 MP4 文件落地与存在性。
4. validate-audio: 校验 04-audio/shots/ 单镜 WAV 文件与 audio_timeline.json 的一致性。
5. validate-all: 一键串联运行全局合规校验。
"""

import sys
import json
import os
import re

MAX_SHOT_DURATION_SEC = 18.375

def check_punctuation_stripped(phrases):
    """校验 caption_phrases 是否剥离了常见标点符号"""
    punctuation_pattern = re.compile(r'[，。！？；：、“”—…（）!?,.:;"]')
    for phrase in phrases:
        if punctuation_pattern.search(phrase):
            return False, phrase
    return True, None

def validate_storyboard(storyboard_path):
    """校验编导阶段 storyboard.json"""
    if not os.path.exists(storyboard_path):
        return False, f"找不到 storyboard.json 文件: {storyboard_path}"

    try:
        with open(storyboard_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, f"JSON 解析失败: {str(e)}"

    shots = data.get("shots", [])
    if not shots:
        return False, "storyboard.json 中不包含任何镜头 (shots)"

    for shot in shots:
        shot_id = shot.get("shot_id")
        motion_plan = shot.get("motion_plan", {})
        est_duration = motion_plan.get("estimated_duration_sec", 0.0)

        # 1. 18.375s 硬上限拆镜校验
        if est_duration > MAX_SHOT_DURATION_SEC:
            return False, f"镜头 #{shot_id} 预估时长 ({est_duration}s) 超过 18.375s 硬上限，必须在自然停顿处强制拆镜！"

        # 2. 字幕标点剥离校验
        caption_phrases = shot.get("caption_phrases", [])
        is_clean, bad_phrase = check_punctuation_stripped(caption_phrases)
        if not is_clean:
            return False, f"镜头 #{shot_id} 的 caption_phrases 包含未剥离标点: '{bad_phrase}'"

        # 3. 自包含提示词校验
        prompts = shot.get("keyframe_prompts", {})
        if not prompts.get("first_frame_prompt") or not prompts.get("image_prompt"):
            return False, f"镜头 #{shot_id} 缺失 first_frame_prompt 或 image_prompt"

        # 4. 连续分镜参考合规校验
        refer_prev = shot.get("refer_previous_end_frame") or shot.get("continuity", {}).get("refer_previous_shot")
        ref_shot_id = shot.get("reference_shot_id") or shot.get("continuity", {}).get("reference_shot_id")
        if refer_prev or ref_shot_id is not None:
            target_ref_id = ref_shot_id if ref_shot_id is not None else (shot_id - 1)
            all_shot_ids = [s.get("shot_id") for s in shots]
            if target_ref_id not in all_shot_ids or target_ref_id >= shot_id:
                return False, f"镜头 #{shot_id} 标记了连续参考分镜 #{target_ref_id}，但被引用的分镜不存在或非法！"

        # 5. 视觉寓意、具象元素明细与分镜动画效果说明校验
        visual = shot.get("visual", {})
        has_metaphor = visual.get("metaphor_meaning") or visual.get("meaning") or visual.get("metaphor")
        has_elements = visual.get("elements_detail") or visual.get("elements")
        has_motion = visual.get("motion_description") or shot.get("motion_plan", {}).get("motion_prompt")
        if not has_metaphor or not has_elements or not has_motion:
            return False, f"镜头 #{shot_id} 缺少完整的 visual 说明（需包含视觉寓意、具体元素明细 elements_detail 与动画效果运动说明 motion_description）"

    return True, f"storyboard.json 校验通过！共包含 {len(shots)} 个合规分镜。"

def validate_visual(project_dir):
    """校验视觉阶段 02-visual 产物完整性与镜头覆盖率"""
    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    v_spec_path = os.path.join(project_dir, "02-visual", "visual_spec.json")

    if not os.path.exists(v_spec_path):
        return False, f"找不到 02-visual/visual_spec.json: {v_spec_path}"

    with open(sb_path, "r", encoding="utf-8") as f:
        sb_shots = json.load(f).get("shots", [])
    expected_shot_ids = {s["shot_id"] for s in sb_shots}

    try:
        with open(v_spec_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)
    except Exception as e:
        return False, f"visual_spec.json 解析失败: {str(e)}"

    keyframes = v_data.get("keyframes", [])
    recorded_shot_ids = {kf.get("shot_id") for kf in keyframes}

    # 检查是否全部镜头覆盖
    missing_shots = expected_shot_ids - recorded_shot_ids
    if missing_shots:
        return False, f"02-visual/visual_spec.json 遗漏了镜头: {sorted(list(missing_shots))}，未达成 100% 覆盖！"

    # 检查关键帧图片文件在本地是否存在
    visual_dir = os.path.join(project_dir, "02-visual")
    for kf in keyframes:
        sid = kf.get("shot_id")
        kf_file = kf.get("keyframe_file") or kf.get("first_frame_file")
        if kf_file:
            abs_img = os.path.join(visual_dir, kf_file)
            if not os.path.exists(abs_img):
                return False, f"镜头 #{sid} 声明的关键帧图像文件不存在: {abs_img}"

    return True, f"02-visual 校验通过！已完整覆盖全量 {len(expected_shot_ids)} 个镜头关键帧。"

def validate_motion(project_dir):
    """校验运动阶段 03-motion 产物落地与存在性"""
    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    with open(sb_path, "r", encoding="utf-8") as f:
        sb_shots = json.load(f).get("shots", [])

    motion_shots_dir = os.path.join(project_dir, "03-motion", "shots")
    if not os.path.exists(motion_shots_dir):
        return False, f"找不到 03-motion/shots 目录: {motion_shots_dir}"

    for shot in sb_shots:
        sid = shot["shot_id"]
        # 兼容 shot_01.mp4 或 shot_1.mp4
        mp4_1 = os.path.join(motion_shots_dir, f"shot_{sid:02d}.mp4")
        mp4_2 = os.path.join(motion_shots_dir, f"shot_{sid}.mp4")

        target_mp4 = mp4_1 if os.path.exists(mp4_1) else (mp4_2 if os.path.exists(mp4_2) else None)

        if not target_mp4 or os.path.getsize(target_mp4) == 0:
            return False, f"镜头 #{sid} 缺失有效的 03-motion 动画视频产物 (未找到 {mp4_1} 或文件为空)！"

    return True, f"03-motion 校验通过！{len(sb_shots)} 个分镜视频片段全量存在。"

def validate_audio(project_dir):
    """校验声音阶段 04-audio 产物落地与时间轴完整性"""
    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    timeline_path = os.path.join(project_dir, "04-audio", "audio_timeline.json")

    if not os.path.exists(timeline_path):
        return False, f"找不到 04-audio/audio_timeline.json: {timeline_path}"

    with open(sb_path, "r", encoding="utf-8") as f:
        sb_shots = json.load(f).get("shots", [])

    try:
        with open(timeline_path, "r", encoding="utf-8") as f:
            timeline = json.load(f)
    except Exception as e:
        return False, f"audio_timeline.json 解析失败: {str(e)}"

    recorded_shots = timeline.get("shots", [])
    rec_ids = {s.get("shot_id") for s in recorded_shots}
    exp_ids = {s["shot_id"] for s in sb_shots}

    missing = exp_ids - rec_ids
    if missing:
        return False, f"04-audio/audio_timeline.json 缺失音频记录镜头: {sorted(list(missing))}"

    audio_dir = os.path.join(project_dir, "04-audio")
    for s in recorded_shots:
        sid = s.get("shot_id")
        a_file = s.get("audio_file")
        if a_file:
            abs_a = os.path.join(audio_dir, a_file)
            if not os.path.exists(abs_a) or os.path.getsize(abs_a) == 0:
                return False, f"镜头 #{sid} 声明的 WAV 音频文件不存在或为空: {abs_a}"

    return True, f"04-audio 校验通过！全量 {len(exp_ids)} 个镜头音频文件与时间轴完备。"

def validate_all(project_dir):
    """全流程一键贯穿校验"""
    print(f"🧐 开始对项目 [{os.path.abspath(project_dir)}] 执行全阶段逻辑契约闭环校验...")

    sb_path = os.path.join(project_dir, "01-director", "storyboard.json")
    ok1, msg1 = validate_storyboard(sb_path)
    if not ok1:
        print(f"❌ Phase 1 校验失败: {msg1}")
        return False
    print(f"  └─ Phase 1 (Director): {msg1}")

    ok2, msg2 = validate_visual(project_dir)
    if not ok2:
        print(f"❌ Phase 2 校验失败: {msg2}")
        return False
    print(f"  └─ Phase 2 (Visual):   {msg2}")

    ok3, msg3 = validate_motion(project_dir)
    if not ok3:
        print(f"❌ Phase 3 校验失败: {msg3}")
        return False
    print(f"  └─ Phase 3 (Motion):   {msg3}")

    ok4, msg4 = validate_audio(project_dir)
    if not ok4:
        print(f"❌ Phase 4 校验失败: {msg4}")
        return False
    print(f"  └─ Phase 4 (Audio):    {msg4}")

    print("🎉 [SUCCESS]: 全流程 5 阶段项目契约与文件覆盖率闭环校验全部通过！")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 project_validator.py <command> [project_dir/file_path]")
        print("命令: validate-director <path_to_storyboard.json>")
        print("命令: validate-visual [project_dir]")
        print("命令: validate-motion [project_dir]")
        print("命令: validate-audio [project_dir]")
        print("命令: validate-all [project_dir]")
        sys.exit(1)

    cmd = sys.argv[1]
    target_path = sys.argv[2] if len(sys.argv) >= 3 else "."

    if cmd == "validate-director":
        ok, msg = validate_storyboard(target_path)
        if ok:
            print(f"✅ {msg}")
        else:
            print(f"❌ [VALIDATION ERROR]: {msg}")
            sys.exit(1)
            
    elif cmd == "validate-visual":
        ok, msg = validate_visual(target_path)
        if ok: print(f"✅ {msg}")
        else: print(f"❌ {msg}"); sys.exit(1)

    elif cmd == "validate-motion":
        ok, msg = validate_motion(target_path)
        if ok: print(f"✅ {msg}")
        else: print(f"❌ {msg}"); sys.exit(1)

    elif cmd == "validate-audio":
        ok, msg = validate_audio(target_path)
        if ok: print(f"✅ {msg}")
        else: print(f"❌ {msg}"); sys.exit(1)

    elif cmd == "validate-all":
        ok = validate_all(target_path)
        if not ok: sys.exit(1)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()

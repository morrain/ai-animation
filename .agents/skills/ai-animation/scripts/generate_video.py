#!/usr/bin/env python3
"""
generate_video.py
ai-animation Skill 阶段三 (Phase 3 Motion Stage) 流程指挥官与资产调度引擎

职责逻辑：
1. 专门解析前续步骤的资产（<project_dir>/01-director/storyboard.json 与 <project_dir>/02-visual/visual_spec.json）。
2. 按 shot_id 提取镜头对应的首帧 keyframes/shot_XX_first.png、尾帧 keyframes/shot_XX_last.png、motion_prompt 与动作时长。
3. 从第三方解耦插件库 video_providers 中调起指定大模型驱动器生成视频。
"""

import sys
import os
import json
import argparse

# 动态挂载本地脚本路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from video_providers import get_video_provider

def generate_shot_video(project_dir, shot_id=1, provider_config=None):
    """读取前续步骤阶段产物并驱动选定的视频大模型插件生成单镜视频"""
    project_dir = os.path.abspath(project_dir)
    storyboard_path = os.path.join(project_dir, "01-director", "storyboard.json")
    visual_spec_path = os.path.join(project_dir, "02-visual", "visual_spec.json")

    if not os.path.exists(storyboard_path):
        print(f"❌ [错误]: 找不到阶段一编导产物 {storyboard_path}")
        return False
    if not os.path.exists(visual_spec_path):
        print(f"❌ [错误]: 找不到阶段二视觉产物 {visual_spec_path}")
        return False

    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    with open(visual_spec_path, "r", encoding="utf-8") as f:
        visual_spec = json.load(f)

    # 定位镜头参数
    shots_storyboard = {int(s["shot_id"]): s for s in storyboard.get("shots", [])}
    vis_list = visual_spec.get("keyframes") or visual_spec.get("shots", [])
    shots_visual = {int(s["shot_id"]): s for s in vis_list}

    if shot_id not in shots_storyboard or shot_id not in shots_visual:
        print(f"❌ [错误]: 镜头 #{shot_id} 在 storyboard.json 或 visual_spec.json 中未找到!")
        return False

    sb_shot = shots_storyboard[shot_id]
    vis_shot = shots_visual[shot_id]

    motion_prompt = sb_shot.get("motion_plan", {}).get("motion_prompt", "")
    duration_sec = sb_shot.get("motion_plan", {}).get("estimated_duration_sec", 6.5)

    # 解析关键帧文件物理路径
    rel_first = vis_shot.get("first_frame_file") or vis_shot.get("keyframe_file")
    rel_last = vis_shot.get("last_frame_file") or vis_shot.get("keyframe_file")

    first_frame_path = os.path.join(project_dir, "02-visual", rel_first)
    last_frame_path = os.path.join(project_dir, "02-visual", rel_last)
    
    out_mp4_path = os.path.join(project_dir, "03-motion", "shots", f"shot_{shot_id:02d}.mp4")

    print(f"🎬 正在为主题 [{os.path.basename(project_dir)}] 调度生成镜头 #{shot_id} 无声视频...")
    print(f"  ├─ 首帧路径: {first_frame_path}")
    print(f"  ├─ 尾帧路径: {last_frame_path}")
    print(f"  ├─ 预估时长: {duration_sec}s")
    print(f"  └─ 运动 Prompt: {motion_prompt}")

    # 强化 12fps 剪纸定格 Prompt 物理约束
    full_motion_prompt = f"12fps stop-motion paper assembly, items slide in and lock into place from empty backdrop, 2D flat paper motion, zero fluid morphing, zero 3D volumetric light, zero glow. {motion_prompt}"

    # 获取解耦出来的 Video Provider (默认解析 VIDEO_PROVIDER_CONFIG 或 providers/video/agnes_ai.json)
    provider = get_video_provider(provider_config)

    success = provider.generate(
        first_frame_path=first_frame_path,
        last_frame_path=last_frame_path,
        prompt=full_motion_prompt,
        output_mp4_path=out_mp4_path,
        duration_sec=duration_sec
    )

    if not success:
        print(f"⚠️ [WARNING]: 视频 Provider 渲染镜头 #{shot_id} 失败（可能受限于云端排队），自动调起 FFmpeg 本地缓动定格引擎作为优雅 fallback...")
        ffmpeg_bin = None
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
        if not ffmpeg_bin or not os.path.exists(ffmpeg_bin):
            ffmpeg_bin = "ffmpeg"

        half_dur = max(1.0, duration_sec / 2.0)
        offset = max(0.5, half_dur - 0.5)
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)
        import subprocess
        ff_cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1", "-t", str(half_dur), "-i", first_frame_path,
            "-loop", "1", "-t", str(half_dur), "-i", last_frame_path,
            "-filter_complex", f"[0:v]fade=t=out:st={offset:.2f}:d=0.5[v0];[1:v]fade=t=in:st=0:d=0.5[v1];[v0][v1]concat=n=2:v=1:a=0,fps=12,format=yuv420p",
            "-c:v", "libx264", "-r", "12",
            out_mp4_path
        ]
        res = subprocess.run(ff_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ret = res.returncode
        if ret == 0 and os.path.exists(out_mp4_path) and os.path.getsize(out_mp4_path) > 0:
            print(f"✨ [FFmpeg Fallback]: 镜头 #{shot_id} 本地 12fps 定格缓动动画合成成功: {out_mp4_path}")
            success = True
        else:
            print(f"💥 镜头 #{shot_id} 视频生成与 FFmpeg fallback 均失败!")

    if success and os.path.exists(out_mp4_path):
        # 强制执行 12fps 抽帧与色彩平坦化净化后处理
        ffmpeg_bin = None
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
        if ffmpeg_bin and os.path.exists(ffmpeg_bin):
            clean_tmp = out_mp4_path.replace(".mp4", "_12fps_clean.mp4")
            clean_cmd = [
                ffmpeg_bin, "-y",
                "-i", out_mp4_path,
                "-vf", "fps=12,eq=saturation=1.1:contrast=1.05",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                clean_tmp
            ]
            if os.system(" ".join(clean_cmd) + " >/dev/null 2>&1") == 0 and os.path.exists(clean_tmp):
                os.replace(clean_tmp, out_mp4_path)
                print(f"✨ [12fps Stop-Motion Cleaned]: 镜头 #{shot_id} 已成功执行 12fps 抽帧定格净化！")

        print(f"✨ 镜头 #{shot_id} 视频处理完成: {out_mp4_path}")

    return success

def generate_all_videos(project_dir, provider_config=None):
    """全量批量生成所有分镜的动态视频（跳过已在审核阶段生成的第一个分镜）"""
    storyboard_path = os.path.join(project_dir, "01-director", "storyboard.json")
    if not os.path.exists(storyboard_path):
        print(f"❌ [错误]: 找不到 {storyboard_path}")
        return False
    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shots = data.get("shots", [])
    print(f"🚀 开始全量批量生成分镜动态视频（从第 2 个分镜开始，共 {len(shots)} 个分镜）...")
    all_ok = True
    for s in shots:
        sid = s["shot_id"]
        if sid == 1:
            print(f"  ⏭️ [跳过]: 镜头 #01 已在审核阶段生成，无需重复渲染。")
            continue
        ok = generate_shot_video(project_dir, shot_id=sid, provider_config=provider_config)
        if not ok:
            all_ok = False
    return all_ok

def main():
    parser = argparse.ArgumentParser(description="ai-animation Skill Phase 3 流程指挥官与资产调度引擎")
    parser.add_argument("project_dir", help="主题项目根目录路径 (如 why-is-the-sky-blue)")
    parser.add_argument("--shot_id", type=int, default=1, help="需要生成的目标分镜 ID (默认: 1)")
    parser.add_argument("--all", action="store_true", help="全量批量生成所有分镜")
    parser.add_argument("--provider_config", "-c", default=None, help="视频模型 JSON 配置文件路径或配置名 (默认: 环境变量 VIDEO_PROVIDER_CONFIG 或 providers/video/agnes_ai.json)")

    args = parser.parse_args()

    if args.all:
        ok = generate_all_videos(args.project_dir, provider_config=args.provider_config)
        if not ok:
            sys.exit(1)
    else:
        ok = generate_shot_video(args.project_dir, shot_id=args.shot_id, provider_config=args.provider_config)
        if not ok:
            sys.exit(1)

if __name__ == "__main__":
    main()

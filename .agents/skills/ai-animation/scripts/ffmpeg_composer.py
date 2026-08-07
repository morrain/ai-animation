#!/usr/bin/env python3
"""
ffmpeg_composer.py
ai-animation Skill 合成层极速打包与双引擎路由器 (FFmpeg / HyperFrames)

功能：
1. 自动探测系统 FFmpeg/FFprobe（支持 Homebrew、系统 PATH 与 Python 第三方路径）。
2. 支持传入主题目录 <project_dir>，以 WAV 为 Master Clock 调节视频 setpts 速率，无缝合轨并烧录字幕导出 <project_dir>/output/final.mp4。
"""

import sys
import os
import subprocess
import json
import glob
import re

def find_binary(name):
    """优先通过 imageio_ffmpeg 或系统的真实路径获取真实二进制，防范伪 stub 的干扰"""
    if name == "ffmpeg":
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if os.path.exists(exe):
                return exe
        except Exception:
            pass

    user_home = os.path.expanduser("~")
    candidates = [
        os.path.join(user_home, "Library", "Python", "3.7", "lib", "python", "site-packages", "imageio_ffmpeg", "binaries", "ffmpeg-osx64-v4.2.2"),
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/usr/bin/{name}"
    ]
    for path in candidates:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return name

FFMPEG_BIN = find_binary("ffmpeg")
FFPROBE_BIN = find_binary("ffprobe")

def get_media_duration(file_path):
    """精确获取音视频绝对时长（秒）"""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        cmd = [FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprintwrappers=1:nokey=1", file_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        dur = float(res.stdout.strip())
        if dur > 0:
            return dur
    except Exception:
        pass
    
    # 备用方案：对 ffmpeg 输出正则提取
    try:
        cmd = [FFMPEG_BIN, "-i", file_path]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            hours, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return hours * 3600 + mins * 60 + secs
    except Exception:
        pass
    return None

def check_node_environment():
    """检测当前系统环境是否安装 Node.js >= 18"""
    try:
        res = subprocess.run(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if res.returncode == 0:
            version_str = res.stdout.strip().lstrip("v")
            major_ver = int(version_str.split(".")[0])
            return major_ver >= 18
    except Exception:
        pass
    return False

def has_audio_stream(file_path):
    """检测音视频文件中是否存在音频流（使用 FFMPEG_BIN 防范 macOS 假 ffprobe stub 干扰）"""
    if not file_path or not os.path.exists(file_path):
        return False
    try:
        cmd = [FFMPEG_BIN, "-i", file_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = (res.stdout or "") + (res.stderr or "")
        if "Audio:" in output:
            return True
    except Exception:
        pass
    try:
        cmd = [FFPROBE_BIN, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", file_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        txt = res.stdout.strip().lower()
        if txt and txt != "ffprobe stub" and "audio" in txt:
            return True
    except Exception:
        pass
    return False

def get_atempo_filter(tempo):
    """生成 FFmpeg 动态 atempo 音频变速滤镜链（自动处理 [0.5, 2.0] 边界）"""
    tempo = max(0.1, min(10.0, tempo))
    filters = []
    curr = tempo
    while curr < 0.5:
        filters.append("atempo=0.5")
        curr /= 0.5
    while curr > 2.0:
        filters.append("atempo=2.0")
        curr /= 2.0
    filters.append(f"atempo={curr:.4f}")
    return ",".join(filters)

def compose_via_ffmpeg(project_dir, output_mp4=None, mix_sfx=True, sfx_volume=0.30):
    """FFmpeg 引擎实现 WAV 主时钟 setpts 动态拉伸对齐与全流烧录，支持视频原音效混音模式"""
    if not output_mp4:
        output_mp4 = os.path.join(project_dir, "output", "final.mp4")

    print(f"🛠️ [FFmpeg Engine]: 正在读取主题目录 [{os.path.abspath(project_dir)}] 各阶段产物，基于 WAV 主时钟合轨...")
    
    if not FFMPEG_BIN:
        print("❌ [ERROR]: 系统中未找到 ffmpeg 可执行二进制！请使用 'brew install ffmpeg' 或安装 Python 包 'pip install imageio-ffmpeg'")
        return False

    print(f"📌 [FFmpeg Binary Location]: 已定位 FFmpeg 可执行路径: {FFMPEG_BIN}")

    motion_dir = os.path.join(project_dir, "03-motion", "shots")
    audio_dir = os.path.join(project_dir, "04-audio", "shots")
    comp_dir = os.path.join(project_dir, "05-composition")
    os.makedirs(comp_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)

    # 检索单镜 mp4 文件
    mp4_files = sorted(glob.glob(os.path.join(motion_dir, "shot_*.mp4")))
    if not mp4_files:
        print(f"❌ 错误: 在 {motion_dir} 中没有找到 shot_*.mp4 视频片段！")
        return False

    scaled_v_files = []
    wav_list_for_concat = []
    sfx_list_for_concat = []
    any_has_sfx = False

    sfx_status_str = f"开启 ({int(sfx_volume*100)}% 音量)" if mix_sfx else "关闭"
    print(f"🎬 正在对 {len(mp4_files)} 个单镜视频进行 WAV 主时钟 setpts 速率重调与音视频合轨 (音效混音: {sfx_status_str})...")

    for mp4_path in mp4_files:
        base_name = os.path.basename(mp4_path)
        shot_id_str = base_name.replace("shot_", "").replace(".mp4", "")
        
        # 查找对应 wav 文件
        wav_path = os.path.join(audio_dir, f"shot_{shot_id_str}.wav")
        if not os.path.exists(wav_path):
            try:
                shot_num = int(shot_id_str)
                wav_path = os.path.join(audio_dir, f"shot_{shot_num:02d}.wav")
                if not os.path.exists(wav_path):
                    wav_path = os.path.join(audio_dir, f"shot_{shot_num}.wav")
            except ValueError:
                pass

        if not os.path.exists(wav_path):
            print(f"⚠️ [WARNING]: 未找到镜头 #{shot_id_str} 的音频文件 {wav_path}")
            continue

        v_dur = get_media_duration(mp4_path)
        a_dur = get_media_duration(wav_path)

        scaled_v_out = os.path.join(comp_dir, f"scaled_v_shot_{shot_id_str}.mp4")

        if v_dur and a_dur and v_dur > 0:
            scale = a_dur / v_dur
            print(f"  ├─ Shot #{shot_id_str}: 视频原长 {v_dur:.2f}s | 音频主时钟 {a_dur:.2f}s | setpts 变速率: {scale:.4f}")
            ff_v_cmd = [
                FFMPEG_BIN, "-y",
                "-i", mp4_path,
                "-filter_complex", f"[0:v]setpts={scale:.6f}*PTS[v]",
                "-map", "[v]",
                "-an",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                scaled_v_out
            ]
        else:
            print(f"  ├─ Shot #{shot_id_str}: 无法获取精确时长...")
            ff_v_cmd = [
                FFMPEG_BIN, "-y",
                "-i", mp4_path,
                "-an",
                "-c:v", "copy",
                scaled_v_out
            ]

        res_v = subprocess.call(ff_v_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res_v == 0 and os.path.exists(scaled_v_out):
            scaled_v_files.append(scaled_v_out)
            wav_list_for_concat.append(wav_path)
        else:
            print(f"❌ 镜头 #{shot_id_str} FFmpeg 速率重调失败！")
            return False

        # 辅助 SFX 音轨处理
        if mix_sfx:
            sfx_out = os.path.join(comp_dir, f"sfx_shot_{shot_id_str}.wav")
            target_dur = a_dur if (a_dur and a_dur > 0) else (v_dur if (v_dur and v_dur > 0) else 3.0)
            if has_audio_stream(mp4_path):
                tempo = (v_dur / a_dur) if (v_dur and a_dur and a_dur > 0 and v_dur > 0) else 1.0
                atempo_filter = get_atempo_filter(tempo)
                ff_sfx_cmd = [
                    FFMPEG_BIN, "-y",
                    "-i", mp4_path,
                    "-filter_complex", f"[0:a]{atempo_filter},volume={sfx_volume:.4f}[a]",
                    "-map", "[a]",
                    "-t", f"{target_dur:.4f}",
                    "-c:a", "pcm_s16le",
                    sfx_out
                ]
                res_sfx = subprocess.call(ff_sfx_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res_sfx == 0 and os.path.exists(sfx_out) and os.path.getsize(sfx_out) > 1000:
                    sfx_list_for_concat.append(sfx_out)
                    any_has_sfx = True
                else:
                    ff_silent_cmd = [
                        FFMPEG_BIN, "-y",
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", f"{target_dur:.4f}",
                        "-c:a", "pcm_s16le",
                        sfx_out
                    ]
                    subprocess.call(ff_silent_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    sfx_list_for_concat.append(sfx_out)
            else:
                ff_silent_cmd = [
                    FFMPEG_BIN, "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", f"{target_dur:.4f}",
                    "-c:a", "pcm_s16le",
                    sfx_out
                ]
                subprocess.call(ff_silent_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                sfx_list_for_concat.append(sfx_out)

    # 1. 拼合无声 Master 视频轨
    v_concat_list_path = os.path.join(comp_dir, "v_file_list.txt")
    with open(v_concat_list_path, "w", encoding="utf-8") as f:
        for v_path in scaled_v_files:
            f.write(f"file '{os.path.abspath(v_path)}'\n")

    master_v_path = os.path.join(comp_dir, "master_video_track.mp4")
    concat_v_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", v_concat_list_path,
        "-c:v", "copy",
        master_v_path
    ]
    subprocess.call(concat_v_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. 拼合全局 Master 无损音轨 (防范 AAC Delay 累加漂移)
    a_concat_list_path = os.path.join(comp_dir, "a_file_list.txt")
    with open(a_concat_list_path, "w", encoding="utf-8") as f:
        for w_path in wav_list_for_concat:
            f.write(f"file '{os.path.abspath(w_path)}'\n")

    master_a_path = os.path.join(comp_dir, "master_audio_track.wav")
    concat_a_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", a_concat_list_path,
        "-c:a", "pcm_s16le",
        master_a_path
    ]
    subprocess.call(concat_a_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. 如果开启了辅助音效混音，拼合 SFX 轨并与 Master 口播音轨双轨融合
    master_audio_final = master_a_path
    if mix_sfx and any_has_sfx and len(sfx_list_for_concat) == len(wav_list_for_concat):
        sfx_concat_list_path = os.path.join(comp_dir, "sfx_file_list.txt")
        with open(sfx_concat_list_path, "w", encoding="utf-8") as f:
            for s_path in sfx_list_for_concat:
                f.write(f"file '{os.path.abspath(s_path)}'\n")

        master_sfx_path = os.path.join(comp_dir, "master_sfx_track.wav")
        concat_sfx_cmd = [
            FFMPEG_BIN, "-y",
            "-f", "concat", "-safe", "0", "-i", sfx_concat_list_path,
            "-c:a", "pcm_s16le",
            master_sfx_path
        ]
        subprocess.call(concat_sfx_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(master_sfx_path) and os.path.getsize(master_sfx_path) > 1000:
            master_mixed_a_path = os.path.join(comp_dir, "master_mixed_audio_track.wav")
            mix_cmd = [
                FFMPEG_BIN, "-y",
                "-i", master_a_path,
                "-i", master_sfx_path,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map", "[a]",
                "-c:a", "pcm_s16le",
                master_mixed_a_path
            ]
            res_mix = subprocess.call(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res_mix == 0 and os.path.exists(master_mixed_a_path):
                master_audio_final = master_mixed_a_path
                print(f"🔊 [音效混音]: 已将视频原背景音效 ({int(sfx_volume*100)}% 音量) 与口播主音轨平滑混合！")

    # 检查是否存在 subtitles.srt
    srt_path = os.path.join(comp_dir, "subtitles.srt")
    has_srt = os.path.exists(srt_path) and os.path.getsize(srt_path) > 0

    print("🎞️ 正在基于 Master 音视轨合成全片成片并打入对齐字幕...")

    if has_srt:
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        final_cmd = [
            FFMPEG_BIN, "-y",
            "-i", master_v_path,
            "-i", master_audio_final,
            "-vf", f"subtitles='{srt_escaped}':force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=30'",
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            output_mp4
        ]
    else:
        final_cmd = [
            FFMPEG_BIN, "-y",
            "-i", master_v_path,
            "-i", master_audio_final,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            output_mp4
        ]

    res = subprocess.call(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res == 0 and os.path.exists(output_mp4):
        total_final_dur = get_media_duration(output_mp4)
        dur_str = f" (总长: {total_final_dur:.2f}s)" if total_final_dur else ""
        print(f"✅ [FFmpeg Engine]: 已完成 WAV 主时钟全流校准！最终成片输出至: {output_mp4}{dur_str}")
        return True
    else:
        print("❌ 最终 FFmpeg 视频拼接合成失败！")
        return False

def compose_via_hyperframes(project_dir, output_mp4=None, mix_sfx=True, sfx_volume=0.30):
    """HyperFrames 引擎实现动效渲染导出"""
    if not output_mp4:
        output_mp4 = os.path.join(project_dir, "output", "final.mp4")

    print(f"🚀 [HyperFrames Engine]: 检测到 Node.js 环境，生成 master_timeline.json 调起 Web 动效渲染...")
    timeline_path = os.path.join(project_dir, "05-composition", "master_timeline.json")
    os.makedirs(os.path.dirname(timeline_path), exist_ok=True)

    master_timeline = {
        "engine": "hyperframes",
        "version": "1.0.0",
        "canvas": {"width": 1280, "height": 720, "fps": 24},
        "project_dir": os.path.abspath(project_dir),
        "notes": "HyperFrames 声明式渲染映射描述文件"
    }

    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(master_timeline, f, ensure_ascii=False, indent=2)

    print(f"📄 已成功导出时间轴配置文件: {timeline_path}")
    print("⚠️ 注意: 当前仍使用系统底层 FFmpeg 极速渲染管线完成最终成片导出...")
    return compose_via_ffmpeg(project_dir, output_mp4, mix_sfx=mix_sfx, sfx_volume=sfx_volume)

def compose_master(project_dir, output_mp4=None, use_hyperframes=False, mix_sfx=True, sfx_volume=0.30):
    """双引擎平滑路由选择"""
    if use_hyperframes:
        if check_node_environment():
            return compose_via_hyperframes(project_dir, output_mp4, mix_sfx=mix_sfx, sfx_volume=sfx_volume)
        else:
            print("⚠️ [WARNING]: 已指定 --use-hyperframes，但未检测到 Node.js >= 18 环境！")
            print("⚠️ [FALLBACK]: 自动平滑降级至 FFmpeg 极速合轨引擎...")
            return compose_via_ffmpeg(project_dir, output_mp4, mix_sfx=mix_sfx, sfx_volume=sfx_volume)
    else:
        return compose_via_ffmpeg(project_dir, output_mp4, mix_sfx=mix_sfx, sfx_volume=sfx_volume)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 ffmpeg_composer.py <project_dir> [output_mp4] [--use-hyperframes] [--no-sfx] [--sfx-volume 0.30]")
        print("例: python3 ffmpeg_composer.py why-is-the-sky-blue --sfx-volume 0.30")
        sys.exit(1)

    project_dir = sys.argv[1]
    output_mp4 = None
    use_hyperframes = "--use-hyperframes" in sys.argv
    mix_sfx = "--no-sfx" not in sys.argv
    sfx_volume = 0.30

    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        if not arg.startswith("--") and output_mp4 is None:
            output_mp4 = arg
        elif arg == "--sfx-volume" and i + 1 < len(sys.argv):
            try:
                sfx_volume = float(sys.argv[i+1])
            except ValueError:
                pass

    ok = compose_master(project_dir, output_mp4, use_hyperframes=use_hyperframes, mix_sfx=mix_sfx, sfx_volume=sfx_volume)
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()

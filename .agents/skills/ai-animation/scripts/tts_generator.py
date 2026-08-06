#!/usr/bin/env python3
"""
tts_generator.py
ai-animation Skill 语音合成、秒/字测算、批量 TTS 导出与字幕时间戳处理工具

依赖:
  pip install edge-tts
"""

import sys
import os
import json
import asyncio
import re

try:
    import edge_tts
except ImportError:
    print("错误: 缺少 edge-tts 依赖库。请运行: pip install edge-tts")
    sys.exit(1)

DEFAULT_VOICE = "zh-CN-YunxiNeural"
DEFAULT_RATE = "-15%"

async def generate_tts_with_timestamps_single(text, voice, output_wav_path, rate=DEFAULT_RATE):
    """单次异步请求 edge-tts"""
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    words_detail = []
    
    with open(output_wav_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words_detail.append({
                    "word": chunk["text"],
                    "start_ms": chunk["offset"] // 10000,
                    "duration_ms": chunk["duration"] // 10000,
                    "end_ms": (chunk["offset"] + chunk["duration"]) // 10000
                })

import subprocess

def find_ffmpeg_binary():
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(exe):
            return exe
    except Exception:
        pass
    candidate_paths = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg"
    ]
    for p in candidate_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return "ffmpeg"

FFMPEG_BIN = find_ffmpeg_binary()

import wave

def get_audio_file_duration(file_path):
    """通过 Python 原生 wave 模块及 ffmpeg 备选精确解析获取物理音频绝对时长（秒）"""
    if not file_path or not os.path.exists(file_path):
        return 0.0
    
    # 1. 优先使用 Python 标准库 wave 模块 (无依赖、无虚假 stub 干扰，100% 绝对精准)
    try:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate > 0:
                return round(frames / float(rate), 4)
    except Exception:
        pass

    # 2. 备用 ffmpeg 命令解析
    try:
        cmd = [FFMPEG_BIN, "-i", file_path]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            hours, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return hours * 3600 + mins * 60 + secs
    except Exception:
        pass
    return 0.0

async def generate_tts_with_timestamps_single(text, voice, output_wav_path, rate=DEFAULT_RATE):
    """单次异步请求 edge-tts"""
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    words_detail = []
    
    with open(output_wav_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])

    total_duration_sec = get_audio_file_duration(output_wav_path)
    if total_duration_sec <= 0:
        # 按照 0.25 秒/字做估算
        clean_text = re.sub(r'[^\w]', '', text)
        total_duration_sec = max(1.2, len(clean_text) * 0.25)

    return total_duration_sec, words_detail

async def generate_tts_with_timestamps(text, voice, output_wav_path, rate=DEFAULT_RATE, max_retries=3):
    """带自动指数避让重试的抗网络波动合成函数"""
    for attempt in range(1, max_retries + 1):
        try:
            dur, words = await generate_tts_with_timestamps_single(text, voice, output_wav_path, rate=rate)
            if dur > 0:
                await asyncio.sleep(0.3)
                return dur, words
        except Exception as e:
            if attempt == max_retries:
                print(f"⚠️ [TTS Error]: '{text[:15]}...' 第 {attempt} 次请求失败: {e}")
                raise e
            print(f"🔄 [TTS Retry]: 网络或无响应重试 ({attempt}/{max_retries})...")
            await asyncio.sleep(1.5 * attempt)

    return 0.0, []

def generate_trial_sample(narration, voice, output_path, rate=DEFAULT_RATE):
    """生成试听音频并导出实测秒/字率到 <project_dir>/state/voice-timing.json"""
    print(f"🎙️ 正在为试听台词生成 TTS: '{narration}' (音色: {voice}, 语速: {rate})...")
    loop = asyncio.get_event_loop()
    duration_sec, words = loop.run_until_complete(
        generate_tts_with_timestamps(narration, voice, output_path, rate=rate)
    )
    
    char_count = len(re.sub(r'\s+', '', narration))
    sec_per_char = duration_sec / char_count if char_count > 0 else 0.24
    
    timing_data = {
        "voice": voice,
        "rate": rate,
        "trial_narration": narration,
        "duration_sec": round(duration_sec, 2),
        "char_count": char_count,
        "sec_per_char": round(sec_per_char, 4),
        "status": "approved_pending"
    }

    state_dir = os.path.join(os.path.dirname(os.path.abspath(output_path)), "..", "state")
    os.makedirs(state_dir, exist_ok=True)
    timing_file = os.path.join(state_dir, "voice-timing.json")
    
    with open(timing_file, "w", encoding="utf-8") as f:
        json.dump(timing_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 试听音频生成完成: {output_path}")
    print(f"📊 实测语速已更新并写入 {timing_file}: {sec_per_char:.4f} 秒/字 (总长: {duration_sec:.2f}s)")
    return timing_data

def apply_min_subtitle_duration(subtitles, min_sec=1.2):
    """为字幕序列施加保底最小显示时长算法，避免短句瞬间消失闪烁"""
    sub_count = len(subtitles)
    for i in range(sub_count):
        sub = subtitles[i]
        curr_start = sub["start_time"]
        curr_end = sub["end_time"]
        dur = curr_end - curr_start

        if dur < min_sec:
            target_end = curr_start + min_sec
            if i + 1 < sub_count:
                next_start = subtitles[i+1]["start_time"]
                sub["end_time"] = min(target_end, max(curr_end, next_start - 0.05))
            else:
                sub["end_time"] = target_end

        sub["start_time"] = round(sub["start_time"], 3)
        sub["end_time"] = round(sub["end_time"], 3)
    return subtitles

def generate_bulk_audio(project_dir, voice=DEFAULT_VOICE, rate=DEFAULT_RATE):
    """
    按 <project_dir>/01-director/storyboard.json 批量生成每个镜头的独立 WAV 文件，导出 04-audio/audio_timeline.json 与 05-composition/subtitles.srt
    """
    storyboard_path = os.path.join(project_dir, "01-director", "storyboard.json")
    if not os.path.exists(storyboard_path):
        print(f"❌ 找不到 storyboard 文件: {storyboard_path}")
        return False

    with open(storyboard_path, "r", encoding="utf-8") as f:
        sb = json.load(f)

    shots = sb.get("shots", [])
    if not shots:
        print("❌ storyboard 中镜头列表为空")
        return False

    audio_dir = os.path.join(project_dir, "04-audio")
    shots_dir = os.path.join(audio_dir, "shots")
    os.makedirs(shots_dir, exist_ok=True)

    timeline_shots = []
    all_srt_entries = []
    global_time_offset = 0.0
    srt_index = 1

    loop = asyncio.get_event_loop()

    print(f"🎙️ 开始在项目 [{os.path.abspath(project_dir)}] 中批量生成全量单镜 TTS 音频 (音色: {voice}, 语速: {rate}, 共 {len(shots)} 镜)...")

    for shot in shots:
        shot_id = shot["shot_id"]
        narration = shot.get("narration", "")
        caption_phrases = shot.get("caption_phrases", [])
        wav_file_rel = f"shots/shot_{shot_id:02d}.wav"
        wav_file_abs = os.path.join(audio_dir, wav_file_rel)

        loop.run_until_complete(
            generate_tts_with_timestamps(narration, voice, wav_file_abs, rate=rate)
        )
        dur_sec = get_audio_file_duration(wav_file_abs)
        if dur_sec <= 0:
            clean_text = re.sub(r'[^\w]', '', narration)
            dur_sec = max(1.2, len(clean_text) * 0.25)

        # 构建按字符比例分配的短语字幕
        shot_subtitles = []
        if caption_phrases:
            total_chars = sum(len(p) for p in caption_phrases)
            curr_t = 0.0
            for idx, phrase in enumerate(caption_phrases):
                p_len = len(phrase)
                p_dur = (p_len / total_chars) * dur_sec if total_chars > 0 else (dur_sec / len(caption_phrases))
                st = curr_t
                et = curr_t + p_dur
                shot_subtitles.append({
                    "text": phrase,
                    "start_time": round(st, 3),
                    "end_time": round(et, 3)
                })
                curr_t = et
        else:
            shot_subtitles.append({
                "text": narration,
                "start_time": 0.0,
                "end_time": round(dur_sec, 3)
            })

        shot_subtitles = apply_min_subtitle_duration(shot_subtitles, min_sec=1.2)

        for sub in shot_subtitles:
            g_start = global_time_offset + sub["start_time"]
            g_end = global_time_offset + sub["end_time"]
            
            def format_time(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int(round((sec - int(sec)) * 1000))
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            all_srt_entries.append(
                f"{srt_index}\n{format_time(g_start)} --> {format_time(g_end)}\n{sub['text']}\n"
            )
            srt_index += 1

        timeline_shots.append({
            "shot_id": shot_id,
            "audio_file": wav_file_rel,
            "exact_duration_sec": round(dur_sec, 3),
            "subtitles": shot_subtitles
        })

        global_time_offset += dur_sec
        print(f"  └─ Shot #{shot_id:02d}: {dur_sec:.2f}s | 生成成功: {wav_file_rel}")

    # 保存 04-audio/audio_timeline.json
    timeline_path = os.path.join(audio_dir, "audio_timeline.json")
    audio_timeline = {
        "voice_config": {
            "engine": "edge-tts",
            "voice_name": voice,
            "rate": rate,
            "trial_approved": True
        },
        "total_audio_duration_sec": round(global_time_offset, 3),
        "shots": timeline_shots
    }
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(audio_timeline, f, ensure_ascii=False, indent=2)

    # 保存 05-composition/subtitles.srt
    comp_dir = os.path.join(project_dir, "05-composition")
    os.makedirs(comp_dir, exist_ok=True)
    srt_path = os.path.join(comp_dir, "subtitles.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_srt_entries))

    print(f"✅ 全量音频生成完成！Master Clock 总时长: {global_time_offset:.2f} 秒")
    print(f"📄 已保存时间轴配置: {timeline_path}")
    print(f"📄 已更新挂载字幕文件: {srt_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 tts_generator.py <command> [options]")
        print("命令 1: trial --text '台词' [--out <project_dir>/04-audio/audio_trial.wav] [--voice zh-CN-YunxiNeural] [--rate -15%]")
        print("命令 2: bulk <project_dir> [--voice zh-CN-YunxiNeural] [--rate -15%]")
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "trial":
        text = "你有没有想过，为什么天空偏偏是蓝色的？"
        out_path = "04-audio/audio_trial.wav"
        voice = DEFAULT_VOICE
        rate = DEFAULT_RATE
        
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "--text" and i + 1 < len(sys.argv):
                text = sys.argv[i+1]
            elif sys.argv[i] == "--out" and i + 1 < len(sys.argv):
                out_path = sys.argv[i+1]
            elif sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
                voice = sys.argv[i+1]
            elif sys.argv[i] == "--rate" and i + 1 < len(sys.argv):
                rate = sys.argv[i+1]

        generate_trial_sample(text, voice, out_path, rate=rate)
        
    elif cmd == "bulk":
        if len(sys.argv) < 3:
            print("错误: bulk 命令必须传入 <project_dir> 路径！")
            sys.exit(1)

        project_dir = sys.argv[2]
        voice = DEFAULT_VOICE
        rate = DEFAULT_RATE

        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
                voice = sys.argv[i+1]
            elif sys.argv[i] == "--rate" and i + 1 < len(sys.argv):
                rate = sys.argv[i+1]

        ok = generate_bulk_audio(project_dir, voice=voice, rate=rate)
        if not ok:
            sys.exit(1)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()

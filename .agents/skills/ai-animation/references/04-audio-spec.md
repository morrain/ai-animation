# Phase 4: 声音阶段规范 (Audio Spec)

## 📌 阶段目标
按镜头独立生成 TTS 口播旁白音频文件，抓取精确的字/句级时间戳，并配置背景音乐 (BGM) 轨道。

## 📥 输入说明
- 编导产物：`01-director/storyboard.json` 中的 `narration` 字段
- 音色与语音参数（如 `voice_id`, `pitch`, `rate`）

## 🎙️ 旁白试听与语速校准 (Audio Trial & Voice Timing)

本阶段生成的 WAV 音频为**全片绝对总时钟 (Master Clock)**：只变速无声画面，绝对不变速音频。

1. **生成旁白试听片段 (Audio Trial Sample)**：
   - 优先抽取代表性单镜生成试听音频 `04-audio/audio_trial.wav`。
2. **实测语速校准 (Voice Timing Calibration)**：
   - 试听成功后，测量并记录当前音色实际字符播放速率（秒/字），导出保存至 `state/voice-timing.json`。
   - 上游编导与运动阶段将根据此实测秒/字精确反算后续画面渲染的映射帧数。
3. **人工确认三要素 (Human Gate)**：
   - 将试听音频 `04-audio/audio_trial.wav` 呈交用户进行人工确认：🎤 音色 (Voice Timbre)、⏱️ 语速 (Speaking Rate) 与 ⏸️ 断句 (Pauses & Phrasing)。在 `human-gated` 模式下，呈报后**必须暂停流程（不得发起下一轮 Tool Call）**。
4. **批量生成无损 WAV (Bulk WAV Generation)**：
   - 用户确认通过后，按分镜批量渲染无损 WAV 音频文件（`shots/shot_{shot_id}.wav`），并捕捉精准字/句级时间戳。

### 3. 时间轴及精准度硬性防线
- **WAV 物理精准度防线**：计算每个分镜的音频物理时长及 SRT 字幕时间戳时，必须优先使用 Python 标准库原生 `wave` 模块（解析真实采样数 `wf.getnframes() / wf.getframerate()`），严禁在获取本地已生成的真实 WAV 声音文件时降级误用粗暴的字符估算逻辑！
- **字幕零漂移规则**：所有 SRT 全局时间戳均基于全片零 AAC 延时的无损物理 WAV 时间轴直接累加计算。

## 📤 中间产物规范
保存路径：
1. 试听旁白音频：`04-audio/audio_trial.wav`
2. 单镜独立旁白音频：`04-audio/shots/shot_{shot_id}.wav`
3. 音频时间轴与字幕时间戳定义：`04-audio/audio_timeline.json`

### `audio_timeline.json` 契约范例：
```json
{
  "voice_config": {
    "engine": "edge-tts",
    "voice_name": "zh-CN-YunxiNeural",
    "rate": "+0%",
    "trial_approved": true
  },
  "shots": [
    {
      "shot_id": 1,
      "audio_file": "shots/shot_01.wav",
      "exact_duration_sec": 4.32,
      "subtitles": [
        { "text": "你有没有想过", "start_time": 0.0, "end_time": 1.2 },
        { "text": "为什么天空是蓝色的？", "start_time": 1.25, "end_time": 4.32 }
      ]
    }
  ]
}
```

## ⚠️ 解耦逻辑
- **换音色/调语速**：修改音色参数或台词时，仅需重新运行 Phase 4 生成新的旁白 WAV 及时间轴配置，完全不需要破坏原有的动画视频文件。

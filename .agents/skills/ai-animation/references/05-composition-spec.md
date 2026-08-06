# Phase 5: 合成阶段规范 (Composition Spec)

## 📌 阶段目标
读取单镜视频片段 (`03-motion/shots/`)、单镜旁白音频 (`04-audio/shots/`)、时间轴数据与背景音乐，对齐全局音画时间线，渲染动态高亮字幕，使用 FFmpeg 输出最终完整 MP4 视频。

## 📥 输入说明
- 编导转场方案：`01-director/storyboard.json`
- 单镜视频资源：`03-motion/shots/shot_{shot_id}.mp4`
- 单镜旁白音频：`04-audio/shots/shot_{shot_id}.wav`
- 音频时间轴数据：`04-audio/audio_timeline.json`
- 背景音乐资源 (BGM)

## 🎬 音画时间线与字幕合轨规范 (Timeline & Subtitle Assembly)

1. **WAV 音轨主时钟原则 (Master Clock Alignment)**：
   - 全片音轨以清理后的 WAV 累计长度为绝对总时钟。合成层仅按需变换无声画面视频速率，**绝不变速口播音频**。
2. **转场中点台词无缝交接 (Mid-Transition Crossing)**：
   - 过渡动画模式下，台词边界落于转场中点：上一场景台词覆盖转场前半段，下一场景台词从转场中点开始并覆盖后半段。整条音轨禁止插入静音断档。
3. **字体选择与自动回退 (Font Fallback System)**：
   - 优先加载并使用固定版本的“得意黑”字体；若本地或网络不可用，自动平滑回退为系统的黑体（macOS 苹方 / Windows 微软雅黑），并将最终选定的字体信息写入 `state/font-selection.json`。
4. **单行无印字幕渲染**：
   - 字幕单行显示、无背景底框、白字黑描边，在真实语义停顿处无缝切换，不掩盖画面主体。

5. **SubAgent 成片合轨与质量巡检 (Phase 5 SubAgent Review)**：
   - 成片导出后，必须调起 SubAgent 严格依照 [validation-rules.md](validation-rules.md#合成阶段校验规则-phase-5-composition-rules) 对 `master_timeline.json`、`subtitles.srt` 及 `output/final.mp4` 进行巡检，确保成片画面规格 (1280x720 24fps H.264)、音画时间线同步及音质无异常破音。

## 📤 中间产物与终产物
1. 字幕与字体配置：`state/font-selection.json`
2. 合成时间线与对齐映射表：`05-composition/master_timeline.json`
3. 独立字幕文件：`05-composition/subtitles.srt` (及 `.vtt` / `.ass`)
4. 最终视频成果：`output/final.mp4` (1280x720, 24fps, H.264 + AAC)

## ⚠️ 解耦与增量合成逻辑
- **低成本重渲染**：只要上游的单镜视频、音频或字幕文件发生替换，执行 Phase 5 可以在几秒到十几秒内极速完成 FFmpeg 合成，无需耗时重算 AI 模型或重新渲染全部镜头。

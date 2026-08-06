# 🎬 AI 科普动画 Agent Skill (`ai-animation`)

`ai-animation` 是一个标准的 **Agent Skill** 框架与可扩展工具链，旨在分阶段将用户的**想法、问题、文章或参考资料**，自动化或交互式地改写并制作成包含**专业口播语音、动态画面/矢量动画、高亮精准字幕与背景音乐**的完整科普动画视频。

---

## 🌟 核心架构与设计哲学

工程采用 **5 阶段解耦流水线 (5-Stage Modular Pipeline)** 架构。核心设计哲学为：**中间产物透明持久化，图片、视频、音频、字幕与风格基线完全独立。**

- 🧱 **分层独立持久化**：编导、视觉、运动、声音、合成 5 个阶段均将结果保存为结构化 JSON 及无损媒体资产。
- 📦 **主题独立目录隔离 (Topic Isolation)**：每个视频项目采用英文小写 Kebab-case Slug（如 `why-is-the-sky-blue`）创建独立工作区，杜绝文件散落。
- 🧊 **状态冰封快照 (State Freezing Protocol)**：初始化项目时将全局风格基因、色板 HEX、字体链与实测语速快照落盘至 `<topic_slug>/state/`，杜绝全局变动破坏历史项目。
- 🛑 **Human-Gated 逐级门控与硬阻断**：编导脚本、首镜静帧、试听音频与无声动效试看均支持 SubAgent 盲审与人工确认门控，待用户确认满意后再全量渲染。
- 🔌 **声明式 Provider 解耦**：生图与生视频大模型统一抽象为硬契约抽象类（`BaseImageProvider`, `BaseVideoProvider`），支持通过 JSON 声明式配置文件添加或切换第三方 API。
- 🔄 **原子级增量更新**：换音色、调台词、更换大模型或重做某一特定分镜（Shot），无需将整条视频从头重新生成。
- 🎞️ **双渲染引擎路由**：支持 FFmpeg 极速 WAV 主时钟合轨与 HyperFrames (Node.js/React) 声明式 Web 动效渲染双引擎平滑降级切换。

---

## 🗺️ 五阶段流水线与目录架构

```text
                               ┌──────────────────┐
                               │  1. 编导 (Director)
                               │  核心观点、台词分镜与 Prompt ───> 01-director/storyboard.json
                               └────────┬─────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
   │  2. 视觉 (Visuals)│       │  3. 运动 (Motion)│       │  4. 声音 (Audio)  │
   │  静帧控制图与 specs│       │  单镜无声视频片段 │       │  WAV 口播与时间轴 │
   │  02-visual/      │       │  03-motion/      │       │  04-audio/       │
   └────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       ▼
                             ┌──────────────────┐
                             │  5. 合成 (Comp)   │
                             │  双引擎合轨/字幕  │
                             │  output/final.mp4│
                             └──────────────────┘
```

### 📁 项目工作区目录规范 (`/<topic_slug>/`)

```text
/<topic_slug>/
├── 01-director/
│   └── storyboard.json             # 核心观点、分镜台词、中英 Prompt 及运动计划
├── 02-visual/
│   ├── visual_spec.json            # 视觉规格、镜头覆盖率与关键帧映射描述
│   └── keyframes/                  # 单镜首尾控制帧 (shot_XX_first.png / shot_XX_last.png)
├── 03-motion/
│   └── shots/                      # 单镜无声 MP4 动态视频 (shot_XX.mp4)
├── 04-audio/
│   ├── audio_timeline.json         # 口播时间轴与精确字幕时间戳
│   ├── audio_trial.wav             # 旁白试听样本
│   └── shots/                      # 单镜无损 WAV 音频 (shot_XX.wav)
├── 05-composition/
│   ├── master_timeline.json        # 合成时间线与渲染映射描述
│   ├── file_list.txt               # FFmpeg Concat 列表
│   └── subtitles.srt               # 挂载高亮字幕文件
├── state/                          # 项目状态冰封目录
│   ├── style-selection.json        # 选定风格 ID、画幅与帧率规范
│   ├── style-definition.md         # 风格视觉基因与 5 段式 Prompt 指南快照
│   ├── font-selection.json         # 字体链与高亮边框标度快照
│   └── voice-timing.json           # 实测秒/字语速与 TTS 参数快照
└── output/
    └── final.mp4                   # 最终合成成片
```

---

## 📖 阶段规范与流水线协议 (Pipeline Specs)

每个阶段均有强约束的契约规范与详细格式，完整文档见 `references/` 目录：

| 阶段 | 规范文档 | 职责与产出物 |
| :--- | :--- | :--- |
| **Phase 1 编导** | [01-director-spec.md](file:///.agents/skills/ai-animation/references/01-director-spec.md) | 提取核心观点、单镜因果推导，按 5 段式结构导出 `<slug>/01-director/storyboard.json` |
| **Phase 2 视觉** | [02-visual-spec.md](file:///.agents/skills/ai-animation/references/02-visual-spec.md) | 生成 Shot #1 样板静帧，确认后批量导出首尾控制帧及 Contact Sheet 拼图 |
| **Phase 3 运动** | [03-motion-spec.md](file:///.agents/skills/ai-animation/references/03-motion-spec.md) | 驱动 AI 视频大模型/代码渲染 Shot 首尾帧控制动画，导出 `<slug>/03-motion/shots/shot_XX.mp4` |
| **Phase 4 声音** | [04-audio-spec.md](file:///.agents/skills/ai-animation/references/04-audio-spec.md) | 试听音色并记录物理语速，批量生成无损 WAV 旁白与 `<slug>/05-composition/subtitles.srt` |
| **Phase 5 合成** | [05-composition-spec.md](file:///.agents/skills/ai-animation/references/05-composition-spec.md) | 调起 FFmpeg/HyperFrames 引擎，以 WAV 为 Master Clock 变速率对齐导出 `output/final.mp4` |

---

## 🎨 视觉风格引擎与扩展 (Style Engine)

内置风格存储于 `.agents/skills/ai-animation/resources/styles/` 目录，均受 `_schema.json` 强校验：

- ✂️ **`vox` (Vox 纸拼贴风格)**：黑白半调人物、彩色卡纸拼贴、12fps 定格复古组装、纸张纹理与撕裂边框。适用于科技、商业、历史与科普观点表达。
- 📖 **`storybook` (Storybook 微风纸雕绘本风格)**：多层纸雕景深、温暖水彩/马卡龙色彩、柔和微阴影与 30fps `easeInOutSine` 轻微呼吸浮动。适用于温馨绘本与故事解说。
- ⚙️ **自定义风格扩展**：新建 `resources/styles/<your_style>/` 并放置符合 schema 的 `style.json` 与 `prompt_template.md`，或者直接在对话中以自然语言指定。

---

## 🔌 大模型 Provider 解耦架构 (API Providers)

生图与视频 API 的调起均基于声明式 JSON 配置，统一存储在根目录 `providers/` 中：

```text
providers/
├── image/
│   ├── agnes_ai.json               # 默认 Agnes AI 生图配置 (agnes-image-2.1-flash)
│   └── template.json               # 自定义 HTTP 生图 Provider JSON 模版
└── video/
    ├── agnes_ai.json               # 默认 Agnes AI 生视频配置 (agnes-video-v2.0)
    └── template.json               # 自定义 HTTP 生视频 Provider JSON 模版
```

配置支持自动环境变量占位符替换（如 `${PROMPT}`, `${FIRST_FRAME_URL}`, `${LAST_FRAME_URL}`, `${AGNES_API_KEY}`）及异步轮询机制。可以通过环境变量显式覆盖：

```bash
export IMAGE_PROVIDER_CONFIG="providers/image/agnes_ai.json"
export VIDEO_PROVIDER_CONFIG="providers/video/agnes_ai.json"
```

---

## 🛠️ CLI 工具链与使用说明 (Tools & CLI)

项目根目录及 `scripts/` 内提供了一套完备的 Python/Node 自动化脚本：

### 1. 项目完整性与 Schema 静态校验

```bash
# 全流程贯穿校验 (依次校验编导、视觉、运动、音频产物落地情况)
python3 .agents/skills/ai-animation/scripts/project_validator.py validate-all why-is-the-sky-blue

# 校验阶段一 18.375s 时长限制与标点符号剥离
python3 .agents/skills/ai-animation/scripts/project_validator.py validate-director why-is-the-sky-blue/01-director/storyboard.json
```

### 2. 静态关键帧自动化生成

```bash
# 渲染单镜 static 首尾帧 (Shot #1 样板确认)
python3 .agents/skills/ai-animation/scripts/generate_image.py why-is-the-sky-blue --shot_id 1

# 全量批量生成所有镜头控制帧
python3 .agents/skills/ai-animation/scripts/generate_image.py why-is-the-sky-blue --all
```

### 3. 图像规整与 Contact Sheet 拼合

```bash
# 无损铺面模式规整图像至 1280x720 (16:9)
python3 .agents/skills/ai-animation/scripts/video_builder.py resize input.png output.png

# 合成分镜预览联系单 (Contact Sheet)
python3 .agents/skills/ai-animation/scripts/video_builder.py contact-sheet sheet.jpg img1.png img2.png img3.png
```

### 4. 动态无声视频片段渲染

```bash
# 调度视频大模型渲染 Shot #1 试看片段
python3 .agents/skills/ai-animation/scripts/generate_video.py why-is-the-sky-blue --shot_id 1

# 批量生成所有镜头 MP4 片段
python3 .agents/skills/ai-animation/scripts/generate_video.py why-is-the-sky-blue --all
```

### 5. 语音 TTS 合成与字幕处理

```bash
# 生成旁白试听音频片段并记录物理测算语速至 state/voice-timing.json
python3 .agents/skills/ai-animation/scripts/tts_generator.py trial --text "为什么天空偏偏是蓝色的？" --out why-is-the-sky-blue/04-audio/audio_trial.wav

# 批量导出全片 WAV 单镜音频及 subtitles.srt 字幕文件
python3 .agents/skills/ai-animation/scripts/tts_generator.py bulk why-is-the-sky-blue --voice zh-CN-YunxiNeural
```

### 6. 最终音画全流合成与字幕挂载

```bash
# FFmpeg 引擎：按 WAV 主时钟 setpts 动态拉伸对齐，挂载 subtitles.srt 导出 final.mp4
python3 .agents/skills/ai-animation/scripts/ffmpeg_composer.py why-is-the-sky-blue

# HyperFrames Web 动效渲染引擎
python3 .agents/skills/ai-animation/scripts/ffmpeg_composer.py why-is-the-sky-blue --use-hyperframes
```

---

## 📥 安装配置 (Installation)

根据需要在目标项目中引入 Skill 依赖：

### 方式一：项目局部安装（推荐）

```bash
cd /path/to/your-project
mkdir -p .agents/skills
cp -r /path/to/ai-animation/.agents/skills/ai-animation .agents/skills/
```

### 方式二：通过 `skills.json` 注册

在目标项目的 `.agents/skills.json` 中指定路径：

```json
{
  "entries": [
    { "path": "/path/to/ai-animation/.agents/skills" }
  ]
}
```

### 系统环境依赖

- Python 3.8+ (`edge-tts`, `Pillow`, `requests`)
- `ffmpeg` 命令行工具 (`brew install ffmpeg`)
- Node.js >= 18 (可选，用于 HyperFrames Web 动效渲染引擎)

---

## 💬 触发示例 (Skill Triggers)

Skill 注册后，可在 AI 交互客户端中直接使用自然语言指令：

- 🗣️ *"帮我把这篇文章制作成一段科普动画视频"*
- ❓ *"用动画讲解的形式回答：为什么天是蓝色的？"*
- 🔄 *"重做第 3 镜的运动效果，保持其他镜头与音频不变"*
- 🎙️ *"把全片的口播旁白换成 Edge-TTS 云希音色，并重新合成成片"*

---

## 📄 开源协议

[MIT License](file:///Users/morrain/Documents/GitHub/ai-animation/LICENSE) Copyright (c) 2026 Morrain


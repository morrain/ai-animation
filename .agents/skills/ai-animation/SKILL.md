---
name: ai-animation
description: 将想法、问题、文章等资料改写并制作成带专业口播语音、动态矢量/画面动画、高亮字幕与背景音乐的完整科普视频。采用编导、视觉、运动、声音、合成 5 阶段解耦流水线，支持中间产物独立存储与分镜增量修改。当用户提出要制作科普视频、动画视频、讲解视频或把文章/想法转为动画时触发此 Skill。
---

# AI 科普动画生成 Skill (ai-animation)

本 Skill 用于引导 AI 助手分阶段将用户的输入素材（想法、问题、文章或资料）转化为高质量的科普动画视频。

工程整体采用 **5 阶段解耦流水线 (5-Stage Modular Pipeline)** 架构，图片、视频、音频和字幕均彼此独立存储。任何阶段的增量修改（如重做某一镜、换模型、换音色）均无需重新全量生成。

---

## 📂 主题独立文件夹隔离规范 (Topic Directory Isolation)

**核心原则**：所有生成的内容必须保存在该主题对应的独立文件夹中，不得散落在 Git 仓库根目录。

**英文目录规范 (English Slug Rule)**：
为了避免路径编码与跨平台兼容性问题，**主题文件夹名称必须统一使用英文小写及连字符 (kebab-case)**。若用户输入为中文主题（如“为什么天空偏偏是蓝色的？”），Agent 必须在 Phase 1 初始化项目时将其自动转写为对应的简短英文 Slug（如 `why-is-the-sky-blue`），并在工作区根目录下创建对应的主题文件夹 `/<topic_slug>/`（例如 `why-is-the-sky-blue/`）：

```
/<topic_slug>/
├── 01-director/
│   └── storyboard.json             # 核心观点、台词分镜与转场计划
├── 02-visual/
│   ├── visual_spec.json            # 视觉规格与盲审记录
│   └── keyframes/                  # 静态关键帧图像
├── 03-motion/
│   └── shots/                      # 单镜无声动画视频
├── 04-audio/
│   ├── audio_timeline.json         # 口播时间轴与字幕时间戳
│   └── shots/                      # 单镜 WAV 旁白音频
├── 05-composition/
│   ├── master_timeline.json        # 合成时间线与渲染映射描述
│   └── subtitles.srt               # 挂载字幕文件
├── state/
│   ├── style-definition.md         # 风格配置快照
│   ├── style-selection.json        # 选中风格 ID
│   ├── font-selection.json         # 字体回退配置
│   └── voice-timing.json           # 语速测算快照
└── output/
    └── final.mp4                   # 最终合成导出视频
```

---

## 🎨 视觉风格引擎 (Style Engine)

技能内置两大主题风格，且支持用户通过 JSON/Prompt 插件机制自由扩展：

1. **`vox` (Vox 纸拼贴科普风格)**：
   - 黑白半调人物 + 彩色卡纸 + 视觉隐喻 + 逐件组装动画。适合科普解说、观点表达与抽象概念解析。
2. **`storybook` (Storybook 微风纸雕绘本风格)**：
   - 多层纸雕景深 + 温暖水彩/马卡龙色彩 + 柔和阴影 + 轻微呼吸沉浸式浮动。适合儿童故事与温馨绘本动画。
3. **用户自定义风格 (`custom`)**：
   - 可以在 `.agents/skills/ai-animation/resources/styles/` 下添加符合 `_schema.json` 的风格 JSON，或在对话中通过自然语言直接要求。

**风格选择优先级算法**：
- 优先选择用户明确指定的风格 ID 或别名（如 `vox` / `storybook` / 自定义 ID）；
- 若用户未指定，默认使用 **`vox` 风格**；
- 选定后读取其 `reference` 指向的完整风格定义与 Prompt 指南，指导后续阶段渲染。

---

## 🚦 SubAgent 盲审与 Human-Gated 双门控模式

Skill 默认开启 **SubAgent 自动化审查 + 人工门控机制**：

1. **编导方案门控 (Director Gate)**：Phase 1 编导方案生成后暂停，全量呈报 `storyboard.json` 的所有关键信息（包含核心观点、事实核查依据、台词字幕拆解、**一句话视觉命题 (`visual_proposition`)**、**3–6 个核心物件 (`key_objects`)**、**视觉寓意 (`metaphor_meaning`)**、**物件动作与因果表达逻辑 (`object_actions`)**、**组装落位顺序 (`assembly_sequence`)**、**整体分镜动画效果与运动说明 (`motion_description`)**、生图 Prompt **及全量中文完整对译 (`*_zh`)**、多节拍运动计划与预估时长），由用户全面审核确认。
2. **静帧样板组 SubAgent 盲审与门控 (Keyframe Gate)**：
   - 严禁一次性全量批量调用生图模型！在 Phase 2 开始时，**必须且仅能优先生成 Shot #1 的单张关键帧样板图**。
   - **SubAgent 盲审**：调起 SubAgent 严格依照 `references/validation-rules.md` 审核 Shot #1 样板图的 8 项静态视觉指标（包含物理落地、隐喻清晰度、无变形假字及动作方案契合度等）。
   - **人工确认**：将 Shot #1 样板图呈现给用户，**停止后续 Tool Call 等待确认**。用户确认风格与画质满意后，方可批量生成 Shot #2~N 的全量静帧及首末帧控制图。
3. **动画样片 SubAgent 动态审核与门控 (Motion Pilot Gate)**：
   - 必须通过 AI 图生视频大模型（Image-to-Video Model）输入首末帧与 `motion_prompt` 渲染真实视觉元素运动视频（详见 `references/03-motion-spec.md`）。
   - 优先渲染首个单镜头（Shot #1）的动态无声视频样片。
   - **SubAgent 动态审核**：调起 SubAgent 严格依照 `references/validation-rules.md` 检查机位、构图、物理变形、真实运动迹线、末帧对齐及视觉元素切入节奏。
   - **人工确认**：审核通过后提交用户试看确认。
4. **旁白试听门控 (Audio Trial Gate)**：
   - 优先生成一小段旁白试听音频片段（`audio_trial.wav`）。
   - **人工确认**：交由用户确认音色、语速与断句停顿。确认无误后再按分镜批量生成无损 WAV 音频及字幕时间戳。

**双驱动模式与门控硬阻断协议 (Hard Gate Stop Protocol)**：
- **`human-gated` (默认模式)**：按上述 4 重门控逐级呈报用户原话批准，确保品质完全可控。
  - 🛑 **硬阻断规则 (Mandatory Turn End)**：Agent 在生成当前阶段的中间产物并调起 SubAgent 依照 `references/validation-rules.md` 审核通过后，**必须立即停止调用后续阶段的任何工具（即本轮 Turn 不再发起 Tool Call）**，并在回复文本中将呈报内容（脚本表格、样板静态网格、无声样片视频或试听音频）完整展现给用户，明确提示等待用户审核批准。禁止在未收到用户确认前连同后续 Tool 一并执行。
- **`full-auto` (全自动模式)**：仅在用户输入中包含显式全自动指令授权（如开启 `--full-auto` 标识）时生效。自动跳过人工等待，但保留 Agent 自动盲审质检与失败阻断。

**项目状态冰封快照协议 (`<topic_slug>/state/`)**：
初始化主题项目时，**必须将该项目依赖的风格全局定义与配置全量冰封落盘**至 `<topic_slug>/state/` 目录，严禁使用过于简短的几行摘要代过：
1. **`style-selection.json`**：完整保存 `style_id`、`version`、`frame_policy`、`render_spec`（包含分辨率 1280x720、16:9 比例、12fps 帧率、`mode=pad` 铺面模式）与 `motion_preset` 运动预设。
2. **`style-definition.md`**：全量快照复制选中风格的视觉基因、语义色板 HEX 映射表、5 段式 Prompt 协议指南、描边影深规则与缓动组装参数。
3. **`font-selection.json`**：完整写入中英文主力字体、降级字体链、行高、边距与字幕高亮背景框标度。
4. **`voice-timing.json`**：在音频阶段生成，记载物理测算语速（如 4.16 字/秒）、音色配音模型、采样率与句末停顿换算系数。
后续各阶段生成严禁读取外部全局易变定义，必须纯粹基于项目自身的 `state/` 冰封快照读取，防止 Skill 全局配置更新意外破坏历史项目。

---

## 🎯 核心工作流 (5-Stage Pipeline)

```
[原始输入: 想法/文章/问题]
       │
       ▼ (新建 /<topic_slug>/ 主题文件夹)
┌──────────────────┐
│ 1. 编导 (Director)│ ──> 导出核心观点、台词、分镜表与转场计划 (<topic_slug>/01-director/storyboard.json)
└────────┬─────────┘
         │
    ┌────┴────────────────────────┬────────────────────────┐
    ▼                             ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 2. 视觉 (Visuals)│    │ 3. 运动 (Motion) │    │ 4. 声音 (Audio)  │
│ 视觉规格与关键帧  │    │ 单镜动画生成     │    │ 分镜旁白与TTS对齐 │
│ (shot_xx.png/svg)│    │ (shot_xx.mp4)    │    │ (shot_xx.wav)    │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │ 5. 合成 (Comp)   │
                       │ 字幕/音画时间线/ │
                       │ 最终 MP4 合成    │
                       └──────────────────┘
```

---

## 📋 阶段规范指引 (Reference Protocols)

每个阶段的详细输入输出契约、数据结构与处理指令，请查阅 `references/` 对应的规范文档：

1. **[编导阶段 (Director)](references/01-director-spec.md)**
   - **输入**：用户原始资料/想法/主题。
   - **核心约束**：**一镜只讲一个意思（一镜头推导一因果）**；画面无字幕亦可看懂；Prompt 必须按选定 Style 的 `prompt_template.md` 强制落地 **5 段式结构**（包含 HEX 色号、画幅锁、字幕留白边界、材质白描边与负向排除）。
   - **输出**：`<topic_slug>/01-director/storyboard.json`（包含核心观点、叙事逻辑、分镜台词、中英双语提示词、视觉隐喻与转场计划）。

2. **[视觉阶段 (Visuals)](references/02-visual-spec.md)**
   - **输入**：`<topic_slug>/01-director/storyboard.json`。
   - **输出**：`<topic_slug>/02-visual/visual_spec.json` 与各镜关键帧 `<topic_slug>/02-visual/keyframes/shot_{id}.png` (或 `.svg`)。

3. **[运动阶段 (Motion)](references/03-motion-spec.md)**
   - **输入**：关键帧资源与 `<topic_slug>/01-director/storyboard.json` 运动指令。
   - **输出**：各镜无声片段 `<topic_slug>/03-motion/shots/shot_{id}.mp4`（基于 Remotion/Canvas/AI 动画）。

4. **[声音阶段 (Audio)](references/04-audio-spec.md)**
   - **输入**：`<topic_slug>/01-director/storyboard.json` 旁白台词与音色配置。
   - **输出**：单镜旁白 `<topic_slug>/04-audio/shots/shot_{id}.wav` 与对齐数据 `<topic_slug>/04-audio/audio_timeline.json`。

5. **[合成阶段 (Composition)](references/05-composition-spec.md)**
   - **输入**：单镜视频、单镜音频、时间线配置与 BGM。
   - **输出**：字幕文件 `<topic_slug>/05-composition/subtitles.srt` 与最终视频 `<topic_slug>/output/final.mp4`。

---

## 🔄 增量替换与独立演进规则 (Incremental Update Rules)

- **换单镜 (Shot Re-rendering)**：修改第 N 镜画面或动作时，仅需重新运行 Phase 2/3 生成 `shot_N.mp4`，合成阶段自动使用更新后的资源重新打包。
- **换音色/改台词 (Voice Swap / Script Edit)**：更改音频参数或口播台词时，仅需重新触发 Phase 4 重新合成 `shot_N.wav` 并更新时间轴，不影响图像与动画。
- **换画风/模型 (Style / Model Swap)**：更换视觉生成 Prompt 或模型时，仅更新 Phase 2/3 的产物，声音与剧本结构保持完好。

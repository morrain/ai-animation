# Phase 1: 编导阶段规范 (Director Spec)

## 📌 阶段目标
将输入的原始资料（文章、问题或想法）提炼出科普核心观点，改写为通俗易懂且富有人性化节奏的口播台词，并切割为按单镜分割的分镜脚本与转场计划。

本阶段的完整内容导演策略请参阅 [director.md](director.md)，剪辑与转场策略请参阅 [transitions.md](transitions.md)。

---

## ⚠️ 编导核心首要约束 (Paramount Constraint)

在创作分镜脚本与画面隐喻时，必须坚决遵守以下两条铁律：

1. **一镜只讲一个意思 (One Shot, One Proposition)**：
   - 每一个镜头（Shot）只能承载并推导**一个独立的因果关系或逻辑命题**。若一句话包含两个独立因果、两个时空或两个结论，必须拆分为不同镜头；若两句话仅改写同一件事，必须合并为同一镜头。
2. **无字幕依然直观可读 (Subtitles-Free Visual Readability)**：
   - 视觉隐喻、组件关系与动作必须具备极强的独立叙事力，**即便关闭所有声音与字幕，观众仅看画面动作也能直观读懂因果推导**。画面内严禁生硬画入术语大字，严禁依靠字幕或画面打字来补全逻辑。

---

## 📥 输入说明
- 原始资料文本（Markdown/纯文本）
- 目标时长约束（如 30秒、60秒、3分钟）
- 受众风格设定（显式指定风格 ID / 默认 `vox` 风格）
- 转场剪辑偏好（显式指定策略 / 默认 `hard-cut`）

---

## 🔍 编导核心思考与联网核查流程 (Fact-Checking & Brainstorming)

Agent 接收到原始素材后，**绝不直接凭空生成脚本**，必须严格遵循以下四步流程：

1. **联网检索与事实核查 (Fact-Checking)**：
   - 必须先调起 `search_web` 工具，检索涉及的专业概念、科学原理、最新研究或历史背景数据。
   - 校验原始素材是否存在伪科学、逻辑漏洞或描述失准，记录核查结果到 `meta.fact_check_notes`，防止“凭空捏造与瞎说”。
2. **叙事逻辑与核心观点提炼 (Narrative Architecture)**：
   - 梳理知识演进线（抛出 Hook 悬念 -> 科学原理/反常冲突 -> 概念命名 -> 机制展开 -> 适用边界 -> 总结记忆句）。
3. **视觉隐喻与运动效果设计 (Visual Metaphor & Motion Design)**：
   - 将抽象概念转化为具体的视觉比喻与动画轨迹（包含：画面呈现什么具象寓意、具体要有哪些画面元素、元素如何运动呈现因果关系；如：将“瑞利散射”比喻为“弹珠穿过网格筛网”，将“神经元传导”比喻为“电路接力”）。
4. **分镜切分与转场规划 (Shot Breakdown & Transitions)**：
   - 逐镜头拆解台词，为每一个单镜分配精准的画面描述、具象元素明细、视觉寓意、整体动画效果说明、自包含 Prompt 与转场指令。

---

## 🎨 风格选择规则 (Style Selection Rules)

Agent 遵循以下严格顺序确定当前项目的视觉与运动风格规范：

1. **显式指定优先**：若用户在输入中明确指定了风格 ID 或别名（如 `vox`, `storybook` 或其他自定义风格），直接选择对应项。
2. **默认回退**：若用户未显式指定风格，**默认使用 `vox` 风格**。
3. **规范加载与全量冰封落盘 (State Snapshot Rule)**：
   - 读取选中风格的完整定义文件（`resources/styles/{style_id}/style.json` 与 `prompt_template.md`）。
   - **必须立即在 `<topic_slug>/state/` 目录中生成全量冰封快照**：
     - `style-selection.json`：全量记录 `style_id`, `version`, `frame_policy`, `render_spec` (1280x720, 12fps, `mode=pad`) 与 `motion_preset`。
     - `style-definition.md`：全量冰封存储选定 Style 的核心基因、HEX 语义色表、5 段式 Prompt 约束、字幕避让规范与 12fps 缓动曲线。
     - `font-selection.json`：全量存储字体 fallback 链条、字幕边距与样式。
   - 严禁使用几行简漏文字敷衍替代，确保项目后续渲染完全脱离外部易变配置，实现绝对的版本漂移阻断。
4. **提示词丰富化与中英双语对译协议 (5-Part Prompt & Dual-Language Protocol)**：
   - 编写 `keyframe_prompts` 与 `motion_plan.motion_prompt` 时，**严禁使用简短的 1-2 句自然语言描述**。
   - 必须基于加载的 `prompt_template.md`，强制按照以下 **5 段结构** 填充扩充英文 Prompt：
     1. **资产与画幅属性 (`Asset Type & Framing`)**：提示词开头必须包含 `--ar 16:9`，明确 `16:9 widescreen horizontal landscape aspect ratio`，要求模型原生直接输出 16:9 画面，严禁事后做二次切头切尾裁剪。
     2. **视觉主体与隐喻 (`Subject & Visual Proposition`)**：渲染序列遵循“首帧优先渲染，尾帧继承首帧”原则。针对 `image_prompt` (尾帧)，必须同时显式保留选定风格的核心画风材质（如 `Vox style paper collage, cut-out paper shapes`），并声明 `Inherit exact background scene elements, character appearance, object scale, and camera framing from reference image ImagePaths[0]; keep all static shared elements 100% identical and frozen`。
     3. **构图与字幕避让 (`Composition & Subtitle Margin`)**：字幕避让是指将人脸、核心隐喻符号等焦点元素置于中上部区域避开底部字幕遮挡；背景及延伸场景可自然铺满整屏，严禁刻意挖空挖洞或写 clear for subtitles 以防模型画出黑色字幕框。
     4. **材质与 HEX 色号 (`Materials & Semantic Palette`)**：显式写入风格规范中的背景 HEX 色号（如 `#F4F1EA` / `#1D3557`）及点缀色 HEX 色号、白描边 Keyline 属性与切面阴影。
     5. **负向硬排除 (`Negative Constraints`)**：必须包含 `no cropping, no black bars, no letterbox, no borders, no solid black subtitle rectangle, no readable text, no letters, no numbers, no logos, no glossy 3D, no neon glow, no volumetric light, no digital lens flare`，防止模型把光谱或彩虹生成为科技感三维发光/虚化光晕。
   - **双语字段硬绑定**：在 `storyboard.json` 中，所有英文提示词字段必须附带对应的 `*_zh` 中文对译字段（如 `first_frame_prompt_zh`, `image_prompt_zh`, `motion_prompt_zh`），专供人类审计阅读，实现“英文供模型生成，中文供人类审阅”。
5. **连续分镜视觉继承协议 (Continuous Shot Continuity Protocol)**：
   - **连续场景判定与标记**：在编导拆分分镜时，若判定当前分镜 N（如分镜 2）与前一分镜 N-1（如分镜 1）在视觉场景、人物、色彩或空间逻辑上是连续承接的，必须在 `storyboard.json` 镜头字段中显式标记连续性参数：`"refer_previous_end_frame": true` 与 `"reference_shot_id": N-1`。
   - **首帧 Prompt 继承指令**：分镜 N 的 `first_frame_prompt` 头部必须显式声明继承前一镜头尾帧的背景与元素，写为：`Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #{N-1} end frame (reference image ImagePaths[0]); keep all static shared elements 100% identical and frozen`。
   - **中文 Prompt 同步对译**：对应的 `first_frame_prompt_zh` 也需显式写入：`继承分镜 #{N-1} 尾帧的背景场景、人物形象、色彩色板与构图视角，保持共有静态元素完全一致`。

---

## 🎞️ 运动剪辑与转场策略选择 (Transition Strategy Rules)

参照 [transitions.md](transitions.md)，转场策略独立于视觉风格。编导必须根据内容复杂度和用户需求从以下三种模式中选择一种，并写入 `storyboard.json` 的 `meta.transition_strategy` 字段：

1. **`hard-cut`（硬切，默认模式）**：
   - 转场时长为 0。相邻场景边界直接硬切过渡。
   - 每个叙事场景独立生成其完成态/首尾帧关键帧与内容动画。
2. **`transition-separated`（独立转场，高质量动画模式）**：
   - 适用于用户明确要求高质量流畅过渡动画时。成片默认转场时长为 `1.0` 秒。
   - 对场景 A、B 拆分为 `A 内容动画 (A0->A1)` -> `独立转场动画 (A1->B0)` -> `B 内容动画 (B0->B1)`。
3. **`transition-fused`（融合转场，极简模式）**：
   - 适用于元素极少、简单动作且需要减少生成任务的场景。单任务覆盖内容动作与转场（把动作与转场写成两个清晰节拍）。

## 📏 单镜时长上限与多节拍规划 (Shot Capping & Multi-Beat Motion)

1. **18.375 秒硬上限拆镜**：
   - 在 24fps 下，视频单镜头动画渲染硬上限为 `441 帧 (18.375 秒)`。
   - 若台词预估时长超过 18.375 秒，**必须在自然语义停顿处强制切拆为不同镜头**，严禁生成超长视频后强行变速伸缩。
2. **字符数预估公式 (`char_count`)**：
   - 编导阶段统计有效字符数：`char_count = 汉字数 + 英文单词数 + 数字位数`。
   - 初始预估时长公式：`estimated_duration_sec = char_count * 0.24`（按基线语速约 4.1~4.2 字/秒折算），后续在 Phase 4 声音试听确认后修正精确值。
3. **字幕短语与 TTS 标点解耦**：
   - `narration`：保留完整的标点符号，专门用于 TTS 自然断句与停顿合成。
   - `caption_phrases`：**完全剥离标点符号**，按语义及停顿分割为干净短语数组，专供画面动态字幕高亮渲染。
4. **中长镜头多节拍规划 (`multi_beats`)**：
   - 对于时长为 8~18 秒的中长镜头，`motion_plan.motion_prompt` 必须按时间轴划分为多个有先后顺序的节拍（Beats），避免单一动作死板持续十几秒。

---

## 📤 中间产物规范
保存路径：`<topic_slug>/01-director/storyboard.json`

```json
{
  "meta": {
    "title": "科普主题名称",
    "core_viewpoint": "核心科普观点摘要",
    "narrative_logic": "从生活悬念引出光的散射原理，最后用几何隐喻完成解说",
    "emotional_arc": "好奇悬念 -> 科学探秘 -> 豁然开朗",
    "selected_style": {
      "style_id": "vox",
      "source": "default_fallback"
    },
    "transition_strategy": "hard-cut",
    "fact_check_notes": [
      "已通过 search_web 确认：瑞利散射波长λ的四次方反比定律无误",
      "已确认：蓝光波长约 400-450nm，散射效率显著高于红光"
    ],
    "total_shots": 2
  },
  "shots": [
    {
      "shot_id": 1,
      "purpose": "用生活悬念引出散射主题",
      "emotion": "curious",
      "narration": "你有没有想过，为什么天空偏偏是蓝色的？",
      "caption_phrases": ["你有没有想过", "为什么天空偏偏是蓝色的"],
      "char_count": 18,
      "visual": {
        "meaning": "视角从晴朗天空穿透大气层，出现抽象的大气气体分子阵列",
        "metaphor_meaning": "用筛网阻挡与太阳白光分光束流，直观呈现看似纯白的光线实际上暗藏多色混合的因果命题",
        "elements": ["sun_light_ray", "atmosphere_grid", "blue_scattering_particles"],
        "elements_detail": "包含：仰望天空的黑白半调人物剪纸、规则点阵大气层线框筛网、太阳复合白光束、散落的蓝色卡纸圆形微粒",
        "motion_description": "开场半调人物平移入场并抬头；太阳白光沿中轴线向下快速延伸穿入大气筛网；蓝光粒子撞击筛网节点后爆发向四周放射状平移动画"
      },
      "keyframe_prompts": {
        "first_frame_prompt": "Use case: educational explainer animation. Asset type: content-rich initial keyframe...",
        "first_frame_prompt_zh": "Vox解说风格纸拼贴初始关键帧：黑白半调人物仰望，太阳开始萌发多色彩虹光束...",
        "image_prompt": "Use case: educational explainer animation. Asset type: final completed keyframe...",
        "image_prompt_zh": "Vox解说风格纸拼贴完成态关键帧：彩虹光束完整延伸穿入大气线网格..."
      },
      "motion_plan": {
        "motion_prompt": "12fps stop-motion assembly. Beat 1 (0-2s): Atmosphere grid enters; Beat 2 (2-4.5s): Blue particles scatter on collision...",
        "motion_prompt_zh": "12fps抽帧定格动画组装。节拍1 (0-2s): 大气网格入场落位；节拍2 (2-4.5s): 蓝光粒子碰撞爆散...",
        "multi_beats": [
          { "beat": 1, "timing": "0-2.0s", "action": "Atmosphere grid enters and settles" },
          { "beat": 2, "timing": "2.0-4.5s", "action": "Blue light rays hit grid and scatter" }
        ],
        "transition_in": "none",
        "transition_out": "none",
        "estimated_duration_sec": 4.5
      }
    },
    {
      "shot_id": 2,
      "purpose": "微观连续视角：近距展示微粒与蓝光碰撞细节",
      "emotion": "focused",
      "refer_previous_end_frame": true,
      "reference_shot_id": 1,
      "narration": "因为蓝光波长极短，穿过空气时更容易撞击微粒爆散开来。",
      "caption_phrases": ["因为蓝光波长极短", "穿过空气时更容易撞击微粒爆散开来"],
      "char_count": 22,
      "visual": {
        "meaning": "特写视角连续承接上镜，近景放大大气微粒与蓝光光束",
        "metaphor_meaning": "用乒乓球碰撞密集筛网直观演示粒子爆散与波长反比规律",
        "elements": ["atmosphere_grid", "blue_scattering_particles", "magnified_particle"],
        "elements_detail": "包含：特写放大气体单分子、蓝色小球粒子束、高亮折射环形线条",
        "motion_description": "镜头从镜头1尾帧缓速向前推镜拉近；蓝色小球撞击放大微粒，弹出四周高亮波纹与能量散落动画"
      },
      "keyframe_prompts": {
        "first_frame_prompt": "Use case: educational explainer animation. Asset type: initial keyframe for continuous shot #2. Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #1 end frame (ImagePaths[0]); keep all static shared elements 100% identical and frozen...",
        "first_frame_prompt_zh": "Vox解说风格初始关键帧（分镜2）：继承分镜1尾帧的大气网格与蓝光粒子底纹，特写镜头聚焦单个微粒...",
        "image_prompt": "Use case: educational explainer animation. Asset type: final completed keyframe...",
        "image_prompt_zh": "Vox解说风格完成态关键帧（分镜2）：微粒四周散射出高亮蓝光折射环..."
      },
      "motion_plan": {
        "motion_prompt": "12fps stop-motion zoom-in assembly. Beat 1 (0-2s): Zoom in on single particle; Beat 2 (2-5s): Rays shatter into ambient blue glow...",
        "motion_prompt_zh": "12fps定格推镜组装。节拍1 (0-2s): 特写微粒；节拍2 (2-5s): 光线爆散为蓝色环境弥散光...",
        "multi_beats": [
          { "beat": 1, "timing": "0-2.0s", "action": "Zoom in on single particle from shot #1 end frame" },
          { "beat": 2, "timing": "2.0-5.0s", "action": "Rays explode into blue ambient light" }
        ],
        "transition_in": "none",
        "transition_out": "none",
        "estimated_duration_sec": 5.0
      }
    }
  ]
}
```

---

- Agent 需向用户**全量呈报编导方案中 `storyboard.json` 的所有关键信息**，包含：
  1. **全局元信息 (`meta`)**：核心观点、叙事逻辑、情绪弧线、选定风格、转场模式及**事实核查依据 (`fact_check_notes`)**。
  2. **分镜完整结构 (`shots`)**：
     - 镜头 ID、目的、情绪、口播台词与**字幕短语拆解 (`caption_phrases`)**。
     - **视觉寓意与逻辑推导 (`metaphor_meaning`)**。
     - **具体画面元素明细 (`elements_detail`)**。
     - **整体分镜动画效果与运动轨迹说明 (`motion_description`)**。
     - **生图 Prompt (`first_frame_prompt`, `image_prompt`)（必须附带中文对译）**。
     - **运动与多节拍计划 (`motion_prompt`, `multi_beats`, `estimated_duration_sec`, 转场)**。
- 呈报后 Agent **必须暂停流程（不得发起下一轮 Tool Call）**，等待用户审核确认。
- 仅在收到用户明确确认或修改反馈后，方可进入 Phase 2 视觉样帧生成流程。

---

## ⚠️ 解耦逻辑
该文件为后续所有阶段（视觉、运动、声音）的唯一上游标准。若修改台词或分镜分配，仅更新此文件对应字段。

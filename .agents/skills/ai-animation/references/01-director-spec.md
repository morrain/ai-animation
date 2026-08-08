# Phase 1: 编导阶段规范 (Director Spec)

## 📌 阶段目标
将输入的原始资料（文章、问题或想法）提炼出科普核心观点，改写为通俗易懂且富有人性化节奏的口播台词，并切割为按单镜分割的分镜脚本与转场计划。

本阶段的完整内容导演策略请参阅 [director.md](director.md)，剪辑与转场策略请参阅 [transitions.md](transitions.md)。

---

## ⚠️ 编导核心首要约束 (Paramount Constraint)

在创作分镜脚本与画面隐喻时，必须坚决遵守以下三条铁律：

1. **一镜只讲一个意思 (One Shot, One Proposition)**：
   - 每一个镜头（Shot）只能承载并推导**一个独立的因果关系或逻辑命题**。若一句话包含两个独立因果、两个时空或两个结论，必须拆分为不同镜头；若两句话仅改写同一件事，必须合并为同一镜头。
2. **无字幕解说依然直观可读 (Subtitles-Free Visual Readability)**：
   - 视觉隐喻、组件关系与动作必须具备极强的独立叙事力，**即便关闭所有声音与字幕，观众仅看画面动作也能直观读懂因果推导**。允许且鼓励在关键物件上印刷精准科学公式（如 `E=mc²`）、符号（如 `H₂O`）与数字标签，但严禁依靠背景硬画满屏解说大字或无意义乱码来补全逻辑。
3. **单镜单动作与物理拆镜原则 (Single Action Per Shot / Atomic Motion Rule)**：
   - 为彻底防范 AI 图生视频（I2V）在处理多变轨、多几何变换时的变形、融化与跳闪乱动隐患，分镜必须精细拆解为【**单镜单动作**】模式。每一个分镜只能包含**一个主导平面物理动作或单一物理态变**（如：仅平移落位、仅旋转切入、仅印压盖章或仅碰撞爆散）。
   - **复合动作强制拆镜自检规程 (Atomic Shot Pre-Creation Audit)**：Agent 在生成 `storyboard.json` 之前，必须对每个初步分镜执行【首尾帧态变单步检验】。若首帧至尾帧发生了**多于 1 种物理动效**（例如：白光向下延伸 + 彩虹纸带展开；或红光穿透 + 蓝光爆散），或者涉及**多于 1 个核心物件的独立动效**，必须强制在动作拐点处拆分为独立的连续子镜头。
   - **动作动词归一约束 (Single Action Verb Constraint)**：每一个分镜的 `visual.action_verbs` 必须收敛至**有且仅有 1 个主导动作动词**（如 `["垂直延伸"]` 或 `["折射展开"]`）。严禁在一个镜头中填入多个不同动作的动词组合（如 `["平移入场", "折射展开"]`），包含 2 个及以上动作动词的初步分镜必须在 Phase 1 阶段由 Agent 自动拆分，严禁将复合动作推给人类门控或后续阶段。
   - **禁止依赖 `multi_beats` 强行合镜**：`multi_beats` 只能用于表达单一平滑动作的时间轴调速节拍，严禁在一个分镜的 `multi_beats` 中写入两个不同动作动词。

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
   - 绝不先想画面再强凑观点。严格执行编导提炼步骤：**①核心意思 -> ②情绪功能 -> ③一句话视觉命题 -> ④明确 3–8 个核心物件 (`key_objects`) -> ⑤核心动作动词 (`action_verbs`) -> ⑥物件动作与组装逻辑 (`object_actions` & `assembly_sequence`)**。
   - 将抽象概念转化为具体的具象物体互动（如：将“经验重复消耗”设计为“剪刀在胶片时钟上切断”；将“瑞利散射”设计为“蓝光微粒撞击规则大气网格筛网向四周爆散”）。
4. **分镜切分与转场规划 (Shot Breakdown & Transitions)**：
   - 逐镜头拆解台词，为每一个单镜分配精准的视觉命题、3–8 个核心物件明细 (`key_objects`)、动作动词、物件动作逻辑映射、组装顺序、自包含 Prompt 与转场指令。

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
     2. **视觉主体与隐喻 (`Subject & Visual Proposition`)**：渲染序列遵循“首帧优先渲染，尾帧继承首帧”原则。针对图生图关键帧（如尾帧 `last_frame_prompt` 参考首帧），**严禁重复描绘大段全量背景（避免全量提示词导致生图偏差）**，提示词必须遵循**【图生图增量提示词法则 (Img2Img Delta Prompting Protocol)】**：开头声明继承参考图静态元素（如 `Reference Image Conditioning: Inherit exact background scene elements, character appearance, object scale, and camera framing from reference image ImagePaths[0]; keep all static shared elements 100% frozen`），后续**仅精确描述增量改变与具体的元件挪动及新状态**（如 `Delta changes: Move [object A] from [position 1] to [position 2], slide in [object B] at right.`）。
     3. **构图与字幕避让 (`Composition & Subtitle Margin`)**：字幕避让是指将人脸、核心隐喻符号等焦点元素置于中上部区域避开底部字幕遮挡；背景及延伸场景可自然铺满整屏，严禁刻意挖空挖洞或写 clear for subtitles 以防模型画出黑色字幕框。
     4. **材质与色彩描述 (`Materials & Color Description`)**：使用精确自然语言色彩描述（如 `cream beige`, `crimson red`, `deep ocean blue`），**严禁将 HEX 色号写入提示词文本**，防止大模型将色号误识别为需要渲染在画面上的文字标签。
     5. **负向硬排除 (`Negative Constraints`)**：必须包含 `no cropping, no black bars, no letterbox, no borders, no solid black subtitle rectangle, no AI gibberish text, no random unreadable letters, no logos, no glossy 3D, no neon glow, no volumetric light, no digital lens flare`，防止模型生成杂乱 AI 乱码假字或把光谱生成为科技感三维发光/虚化光晕。
   - **双语全量对译硬绑定**：在 `storyboard.json` 中，所有英文提示词字段必须附带对应的 `*_zh` 中文对译字段（如 `first_frame_prompt_zh`, `last_frame_prompt_zh`, `motion_prompt_zh`），专供人类审计阅读。**中文对译绝不能仅写成 1–2 句简略摘要，必须完整保留英文 Prompt 的全部细节与段落结构**（包含资产画幅、视觉命题、场景背景、风格材质、HEX 色号、参考图继承锚点、负向硬排除以及运动节拍等），实现英文供模型生成、中文供人类审阅的 1:1 全量内容对等。
5. **连续分镜视觉继承协议 (Continuous Shot Continuity Protocol)**：
   - **连续场景判定与标记**：在编导拆分分镜时，若判定当前分镜 N（如分镜 2）与前一分镜 N-1（如分镜 1）在视觉场景、人物、色彩或空间逻辑上是连续承接的，必须在 `storyboard.json` 镜头字段中显式标记连续性参数：`"refer_previous_end_frame": true` 与 `"reference_shot_id": N-1`。
   - **首帧增量 Prompt 继承指令**：分镜 N 的 `first_frame_prompt` 遵循**增量提示词法则**，头部显式声明继承前一镜头尾帧的背景与元素（写为 `Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #{N-1} end frame (reference image ImagePaths[0]); keep all static shared elements 100% frozen`），后续**仅精准描述该分镜相对于前一分镜的物理增量改变与元件位移**（如：`Delta changes: Move [object X] to center, and drop in [object Y].`）。
   - **中文 Prompt 同步对译**：对应的 `first_frame_prompt_zh` 也需显式写入：`继承分镜 #{N-1} 尾帧的背景场景、人物形象与构图视角，增量移动/切入以下物件：[具体增量描述]`。
6. **首尾帧演进范式 (Assemble-From-Empty Rule)**：
   - **尾帧是视觉真相**：尾帧 (`last_frame`) 必须完整表达隐喻，所有最终纸片元素、位置、比例和颜色均在尾帧确定。
   - **首帧为初始空场/基座态 (`Assemble-From-Empty`)**：首帧 (`first_frame`) 必须是冲突发生前或变化启动前的初始状态/空场背景（只保留必要的主体或环境框架，留出充足负空间），为后续纸片元素滑入落位提供运动空间。
   - **首帧排除入场物件铁律 (First Frame Object Exclusion Rule)**：针对在后续运动节拍 (`multi_beats`) 中计划旋转切入、降落落位或平滑滑入的任何核心物件（如太阳、问号、光线），在 `first_frame_prompt` 的正向描述与负向排除 (`Avoid`) 中**必须强制显式排除该物件**（如 `Avoid: no sun, no question mark`），严禁首帧提前出现未来节拍才切入的物件，防止首尾帧出现物件位置跳闪突变或状态矛盾。
   - **运动描述规范 (`motion_description`)**：只能使用 2D 剪纸平移 (Slide)、落位 (Drop)、旋转 (Rotate)、遮罩显现 (Mask) 等平面物理动作；**严禁使用** `flowing, glowing, shimmering, morphing, light rays` 等可能诱导 AI 生成 3D 流体变形或科幻光晕的模糊描述。
7. **运动 Prompt 防误幻觉与预渲染姿态锁规范 (Motion Prompt Posture Lock Protocol)**：
    - **首帧在场主体姿态锁定**：在首帧 (`first_frame_prompt`) 中已预渲染落座/伫立的人物或主体，`motion_prompt` 必须显式声明其**保持初始直立姿态不动**（如 `the halftone cut-out person remains standing upright, static and frozen in place; zero posture morphing, no rising from floor`）。
    - **严禁使用动作歧义动词**：严禁使用 `slides in from bottom`（易被模型误理解为从地面翻起卧倒）、`enters from ground` 等模糊词汇。若需刚体平移，必须显式声明为 **平面 2D 刚体平移**（如 `slides horizontally from left edge in upright standing pose, 2D rigid translation, no body bending or crawling`）。

8. **提示词视觉命题表达对齐校验规程 (Prompt Semantic Alignment Protocol)**：
    - **分镜意图完全覆写与表达**：编导在撰写每个分镜的 `first_frame_prompt` 与 `last_frame_prompt` 时，必须核查提示词的 `Primary request` 与 `Delta changes` **是否 100% 精准承载并描述了该分镜的视觉命题 (`visual_proposition`)、核心物件 (`key_objects`) 以及科学寓意 (`metaphor_meaning`)**。
    - **严禁遗漏与偏离**：若提示词遗漏了分镜核心要表达的视觉元件（如受体高亮框、红光穿透网格等），或画面描绘方向与台词寓意脱节，在 Phase 1 自检时必须判定为不合格，强制重新完善 Prompt 直至能够精准表意。

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
2. **字符数预估公式与精确更正 (`char_count`)**：
   - 编导阶段统计有效字符数：`char_count = 汉字数 + 英文单词数 + 数字位数`。
   - 初始预估时长公式：`estimated_duration_sec = char_count * 0.24`（精确按基线语速约 4.16 字/秒折算），后续在 Phase 4 声音生成物理 WAV 后，以实测精确定步修正覆盖为 `exact_duration_sec`。
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
        "visual_proposition": "太阳白光束向下穿入大气规则筛网，撞击爆发放射状蓝光粒子散落",
        "metaphor_meaning": "用筛网阻挡与太阳白光分光束流，直观呈现看似纯白的光线实际上暗藏多色混合的因果命题",
        "key_objects": ["人物剪纸", "大气网格筛网", "太阳白光束", "蓝光散射粒子"],
        "action_verbs": ["平移入场", "延伸穿透", "撞击爆散"],
        "object_actions": [
          "人物剪纸：平移入场并抬头仰望，引导视线",
          "太阳白光束：沿中轴线向下延伸穿透大气筛网",
          "蓝光散射粒子：撞击网格节点后爆发放射状平散"
        ],
        "assembly_sequence": ["大气网格筛网入场落位", "白光束向下延伸", "蓝光粒子撞击爆发"],
        "motion_description": "开场半调人物平移入场并抬头；太阳白光沿中轴线向下快速延伸穿入大气筛网；蓝光粒子撞击筛网节点后爆发向四周放射状平移动画"
      },
      "keyframe_prompts": {
        "first_frame_prompt": "Use case: educational explainer animation. Asset type: content-rich initial keyframe...",
        "first_frame_prompt_zh": "Vox解说风格纸拼贴初始关键帧：黑白半调人物仰望，太阳开始萌发多色彩虹光束...",
        "last_frame_prompt": "Use case: educational explainer animation. Asset type: final completed keyframe...",
        "last_frame_prompt_zh": "Vox解说风格纸拼贴完成态关键帧：彩虹光束完整延伸穿入大气线网格..."
      },
      "motion_plan": {
        "motion_prompt": "12fps stop-motion assembly. Beat 1 (0-2s): Atmosphere grid enters; Beat 2 (2-4.32s): Blue particles scatter on collision...",
        "motion_prompt_zh": "12fps抽帧定格动画组装。节拍1 (0-2s): 大气网格入场落位；节拍2 (2-4.32s): 蓝光粒子碰撞爆散...",
        "multi_beats": [
          { "beat": 1, "timing": "0-2.0s", "action": "Atmosphere grid enters and settles" },
          { "beat": 2, "timing": "2.0-4.32s", "action": "Blue light rays hit grid and scatter" }
        ],
        "transition_in": "none",
        "transition_out": "none",
        "estimated_duration_sec": 4.32
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
        "visual_proposition": "特写放大单个气体微粒，极短波长蓝光束高速撞击弹散出环形光晕",
        "metaphor_meaning": "用乒乓球碰撞密集筛网直观演示粒子爆散与波长反比规律",
        "key_objects": ["放大气体单分子", "蓝光粒子束", "折射环形线条"],
        "action_verbs": ["推镜聚焦", "高速撞击", "弹散波纹"],
        "object_actions": [
          "镜头：向前微推聚焦于上镜尾帧的单个微粒",
          "蓝光粒子束：精准撞击放大微粒核心",
          "折射环形线条：向外层层弹出波纹与能量散落"
        ],
        "assembly_sequence": ["推镜锁住中央微粒", "蓝光束射入撞击", "环形折射波纹弹出"],
        "motion_description": "镜头从镜头1尾帧缓速向前推镜拉近；蓝色小球撞击放大微粒，弹出四周高亮波纹与能量散落动画"
      },
      "keyframe_prompts": {
        "first_frame_prompt": "Use case: educational explainer animation. Asset type: initial keyframe for continuous shot #2. Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #1 end frame (ImagePaths[0]); keep all static shared elements 100% identical and frozen...",
        "first_frame_prompt_zh": "Vox解说风格初始关键帧（分镜2）：继承分镜1尾帧的大气网格与蓝光粒子底纹，特写镜头聚焦单个微粒...",
        "last_frame_prompt": "Use case: educational explainer animation. Asset type: final completed keyframe...",
        "last_frame_prompt_zh": "Vox解说风格完成态关键帧（分镜2）：微粒四周散射出高亮蓝光折射环..."
      },
      "motion_plan": {
        "motion_prompt": "12fps stop-motion zoom-in assembly. Beat 1 (0-2s): Zoom in on single particle; Beat 2 (2-5.28s): Rays shatter into ambient blue glow...",
        "motion_prompt_zh": "12fps定格推镜组装。节拍1 (0-2s): 特写微粒；节拍2 (2-5.28s): 光线爆散为蓝色环境弥散光...",
        "multi_beats": [
          { "beat": 1, "timing": "0-2.0s", "action": "Zoom in on single particle from shot #1 end frame" },
          { "beat": 2, "timing": "2.0-5.28s", "action": "Rays explode into blue ambient light" }
        ],
        "transition_in": "none",
        "transition_out": "none",
        "estimated_duration_sec": 5.28
      }
    }
  ]
}
```

---

## 🔍 SubAgent 编导契约审核规程 (Phase 1 SubAgent Review)

在 `storyboard.json` 落地后，**必须调起 SubAgent** 对编导产物严格依照 [validation-rules.md](validation-rules.md#编导阶段校验规则-phase-1-director-rules) 进行契约巡检（包含 Schema 完整性、18.375s 单镜上限、字幕标点剥离、提示词自包含与中英双语对译、连续镜头引用合法性及视觉语义三要素完整性）。

- **编导门控精简汇报规范 (Streamlined Director Gate Protocol)**：
  Agent 在向用户呈报 Director Gate 时，必须摒弃冗长的原始 Prompt 等底层技术细节，**采用精简清晰的结构重点汇报以下核心维度**：
  1. **全局重点 (Global Overview)**：
     - 💡 **核心观点 (Core Idea)**：科学原理或主题解说的核心论断。
     - 🗺️ **叙事逻辑 (Narrative Architecture)**：分镜间的逻辑递进与起承转合结构。
  2. **分镜精简清单 (Shot Core Details)**（建议采用表格或简洁列表）：
     - 🗣️ **镜头 ID & 口播台词 (Shot ID & Narration)**
     - 🧩 **3–8 个核心物件 (`key_objects`) & 核心动作动词 (`action_verbs`)**
     - 🎯 **物件动作与逻辑映射说明 (`object_actions`)**：哪个物件执行什么动作，映射什么论证含义。
     - 🎬 **整体分镜动画效果与运动轨迹说明 (`motion_description`)**：组件落位组装及运动轨迹效果。
- SubAgent 审核通过并向用户呈报后，Agent **必须暂停流程（不得发起下一轮 Tool Call）**，等待用户审核确认。
- 仅在收到用户明确确认或修改反馈后，方可进入 Phase 2 视觉样帧生成流程。

---

## ⚠️ 解耦逻辑
该文件为后续所有阶段（视觉、运动、声音）的唯一上游标准。若修改台词或分镜分配，仅更新此文件对应字段。


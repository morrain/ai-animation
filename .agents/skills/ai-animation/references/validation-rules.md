# AI Animation 阶段规则与 SubAgent 审查规范 (Validation Rules)

本规范定义了 AI Animation Skill 5-Stage 模块化流水线中各个阶段的**结构契约、物理断言、业务约束与 SubAgent 审核指标**。

Agent 或 SubAgent 在各个阶段生成中间产物后，必须按照本规范对应的阶段规则进行自主审查或调起 SubAgent 审计。审查不通过时，必须阻断流程并修复产物，严禁带病推进至下一阶段。

---

## 编导阶段校验规则 (Phase 1: Director Rules)

SubAgent 在审查 `<topic_slug>/01-director/storyboard.json` 时，必须逐一验证以下规则：

### 1. 结构与文件契约 (Schema & Existence)
- 必须存在 `<topic_slug>/01-director/storyboard.json` 文件且可被解析为标准 JSON。
- JSON 中必须包含非空的分镜数组 `shots` 以及包含核心观点与事实核查的 `meta` 元数据。

### 2. 18.375s 硬上限拆镜约束 (Shot Duration Limit)
- 每个分镜的预估时长 `motion_plan.estimated_duration_sec` **硬性限制不得超过 18.375 秒** (对应 24fps 下 441 帧上限)。
- 若旁白预估时长超过 18.375 秒，编导必须在自然语义停顿处将其拆分为独立的镜头，严禁生成超长分镜。

### 3. 字幕短语标点剥离约束 (Punctuation Stripping)
- `caption_phrases` 数组中的所有短语必须**完全剥离**常见标点符号（包含 `，。！？；：、“”—…（）!?,.:;"`）。
- 标点符号仅允许保存在 `narration` 字段中用于 TTS 停顿合成。

### 4. 提示词自包含与中英双语对译约束 (Self-Contained & Dual Prompts)
- 每个分镜的 `keyframe_prompts` 必须同时具备非空的 `first_frame_prompt` 以及 `image_prompt` (或 `last_frame_prompt`)。
- 提示词必须遵循 5 段式 Prompt 协议（画幅 `--ar 16:9`、主体与隐喻、字幕留白避让、HEX 色号与白描边、负向硬排除）。
- 所有提示词字段必须提供对应的中文对译字段 (`first_frame_prompt_zh`, `image_prompt_zh`, `motion_prompt_zh`)，且**中文对译必须完整包含对应英文 Prompt 的全部细节与段落结构**（不得缩减为一句话摘要）。

### 5. 连续分镜引用合法性约束 (Shot Continuity Reference)
- 若分镜标记了 `refer_previous_end_frame: true` 或指定了 `reference_shot_id`，被引用的镜头 ID (Target Ref ID) 必须在 `shots` 中真实存在，且 Target Ref ID **必须严格小于当前 `shot_id`**。

### 6. 视觉语义三要素完整性约束 (Visual Spec Completeness)
- 每个分镜的 `visual` 对象必须完整包含以下三要素：
  1. **视觉寓意与因果推导 (`metaphor_meaning`)**：明确画面表达的科学/逻辑含义。
  2. **具象元素明细 (`key_objects` / `elements_detail`)**：列出画面中的 3–6 个核心视觉物件。
  3. **动画效果与运动说明 (`motion_description`)**：使用 2D 剪纸滑入、旋转、落位等确切动作描述。

### 7. 运动 Prompt 姿态锁定与防误幻觉约束 (Motion Posture Locking)
- 检查 `motion_plan.motion_prompt`：针对首帧（`first_frame`）中已预渲染呈现的人物/主体，`motion_prompt` **必须包含主体姿态锁定向指令**（如 `remains standing upright, static and frozen in place; zero posture morphing, no rising from floor`）。
- **严禁包含歧义动词**：严禁使用 `slides in from bottom`、`rises from ground` 等诱导模型生成“卧倒爬起”或“肢体扭曲”的描述。

---

## 视觉阶段校验规则 (Phase 2: Visual Rules)

SubAgent 在审查 `<topic_slug>/02-visual/` 产物时，必须逐一验证以下规则：

### 1. 镜头 100% 覆盖率契约 (100% Shot Coverage)
- 必须存在 `<topic_slug>/02-visual/visual_spec.json`。
- `visual_spec.json` 中 `keyframes` 数组所记录的镜头必须 100% 覆盖 `storyboard.json` 中定义的所有 `shot_id`，不得遗漏任何一个镜头。

### 2. 关键帧图像磁盘落地与非空校验 (File Existence & Non-Empty)
- `visual_spec.json` 中声明的关键帧文件路径（`keyframe_file` / `first_frame_file` / `last_frame_file`）在 `<topic_slug>/02-visual/` 目录下必须**物理存在**。
- 图片文件大小必须大于 0 字节，严禁出现损坏或空文件。

### 3. SubAgent 静态视觉盲审 8 项指标 (Visual Quality Metrics)
对于渲染出的关键帧图像（尤其是 Shot #1 样板帧），SubAgent 需进行以下盲审评估：
1. 🎯 **视觉隐喻清晰度 (`metaphor_clear`)**：视觉符号直观易懂，能够独立传递科学或观点因果。
2. 👤 **人物与主体无变形 (`no_character_distortion`)**：黑白半调人物肢体自然，无多头多手或结构变质。
3. 🔤 **文字纯净度 (`no_gibberish_text`)**：画面背景与素材中绝无 AI 乱码假字或无意义拼写字母。
4. 🎨 **视觉风格系统统一性 (`style_unified`)**：配色 HEX、纸纹材质、阴影与白描边严格契合当前选定的 Style。
5. 📐 **首尾帧基准锚点对齐 (`first_last_anchor_alignment`)**：在双帧模式下，首帧与尾帧的场景构图框架与背景底色保持一致，无跳闪。
6. 🧩 **关键物件完整性 (`key_objects_complete`)**：对照 `storyboard.json` 该分镜中 `key_objects` 声明的 3–6 个核心视觉物件/构件，检查静态帧画面是否完整包含所有关键物件，绝无遗漏缺失。
7. 📍 **关键物件与固件位置逻辑性 (`object_positions_logical`)**：核心物件与固件在画面中的物理摆放位置、比例关系与空间层次符合科学逻辑与隐喻推导，避开底部字幕区，无重叠挤压、位置相悖或空间混乱。
8. 🎬 **动画方案与动作要求契合度 (`animation_plan_compliant`)**：静态帧画面（首帧空场/基座态与尾帧完成态）严格符合动画方案。审查与呈报时，**必须结合 3–6 个核心物件 (`key_objects`) 报告当前分镜的详细动作规划 (`motion_plan.multi_beats`)**：严密核验首帧是否为平移/落位/旋转预留充足入场空间，且**严禁首帧提前出现后续节拍才切入的物件**（如后续节拍切入的太阳，首帧绝不能提前出现），尾帧精准表达动作终止后的最终完成态。

---

## 运动阶段校验规则 (Phase 3: Motion Rules)

SubAgent 在审查 `<topic_slug>/03-motion/` 产物时，必须逐一验证以下规则：

### 1. 单镜 MP4 落地与 100% 覆盖率契约 (Shot MP4 Completion)
- 必须存在 `<topic_slug>/03-motion/shots/` 目录。
- 对应 `storyboard.json` 中的每一个 `shot_id`，必须生成对应的无声视频文件 `shot_{sid:02d}.mp4`（或 `shot_{sid}.mp4`）。
- 视频文件大小必须大于 0 字节。

### 2. SubAgent 动态运动质量 7 项指标 (Motion Quality Metrics)
SubAgent 对动态视频样片及全量片段执行以下动态审查：
1. 📷 **机位角度一致性 (`camera_framing_aligned`)**：推拉摇移契合分镜设计，无莫名震颤。
2. 🖼️ **画面构图重心稳定 (`composition_balanced`)**：组件运动过程中主体始终保留在视线焦点。
3. 🌀 **物理运动真实无变质 (`no_physical_deformation`)**：遵循 2D 定格拼贴运动，绝无 AI 3D 融化、水状流动或异物突变。
4. 🕺 **姿态稳定无误起立/卧倒 (`no_posture_hallucination`)**：预渲染人物/主体动作自然，绝无无故卧倒、地面起立爬升或肢体翻折等非编导设定的误动作。
5. 🔄 **转场切入平滑性 (`transition_smoothness`)**：镜头出入场动效自然无卡顿。
6. 🏁 **末帧落脚点精确对齐 (`end_frame_alignment`)**：动画终止时刻的画面与 Phase 2 的 `last_frame_file` 静帧完美吻合。
7. 📥 **元素按计划切入节奏 (`plan_entry_rhythm`)**：组件按照多节拍 (`multi_beats`) 的时间点有序切入。

---

## 声音阶段校验规则 (Phase 4: Audio Rules)

SubAgent 在审查 `<topic_slug>/04-audio/` 产物时，必须逐一验证以下规则：

### 1. 时间轴契约与 100% 镜头覆盖率 (Audio Timeline Coverage)
- 必须存在 `<topic_slug>/04-audio/audio_timeline.json` 文件且 JSON 格式正确。
- `audio_timeline.json` 中的 `shots` 数组必须 100% 包含 `storyboard.json` 中的所有 `shot_id`。

### 2. 单镜 WAV 物理落地与非空校验 (WAV File Existence)
- 每个镜头声明的 `audio_file` (如 `shots/shot_01.wav`) 在 `<topic_slug>/04-audio/` 目录下必须物理存在。
- 音频文件大小必须大于 0 字节，能正常播放无静音断音。

### 3. WAV 物理采样精准时长与字幕零漂移 (Master Clock Precision)
- 音频精确时长 `exact_duration_sec` 必须采用标准库 `wave` 原生模块通过物理采样点计算所得，严禁使用粗暴的字数估算。
- `subtitles` 数组必须精准覆盖句级/短语级时间戳，无缺漏错位。

---

## 合成阶段校验规则 (Phase 5: Composition Rules)

SubAgent 在审查成片 `<topic_slug>/output/final.mp4` 时，必须逐一验证以下规则：

### 1. 产物与字幕落地契约 (Master Deliverables)
- 必须存在 `<topic_slug>/05-composition/master_timeline.json` 与挂载字幕 `<topic_slug>/05-composition/subtitles.srt`。
- 必须在 `<topic_slug>/output/final.mp4` 导出最终成片，文件大小必须大于 0 字节。

### 2. 成片质量与音画合轨巡检 (Final Output Inspection)
- 画面分辨率必须为 `1280x720` (16:9)，帧率为 `24fps`，视频编码为 `H.264`，音频编码为 `AAC`。
- 音画时间轴完全同步，字幕居中无遮挡，背景音乐 (BGM) 与旁白混音比例协调无破音。

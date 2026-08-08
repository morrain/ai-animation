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
- 每个分镜的 `keyframe_prompts` 必须同时具备非空的 `first_frame_prompt` 以及 `last_frame_prompt`。
- 提示词必须遵循 5 段式 Prompt 协议（画幅 `--ar 16:9`、主体与隐喻、字幕留白避让、自然色彩描绘与白描边、负向硬排除）。
- **图生图增量提示词约束 (Img2Img Delta Prompting Rule)**：针对图生图关键帧（如尾帧 `last_frame_prompt` 参考首帧），提示词**必须采用增量模式**：头部声明参考图继承锚点锁死共有元素，主体部分**仅增量描写物件的具体移位、状态更新与新入场元素**，严禁重复大段全量描写背景以防生图偏差。
- 所有提示词字段必须提供对应的中文对译字段 (`first_frame_prompt_zh`, `last_frame_prompt_zh`, `motion_prompt_zh`)，且**中文对译必须完整包含对应英文 Prompt 的全部细节与段落结构**（不得缩减为一句话摘要）。

### 5. 连续分镜引用合法性约束 (Shot Continuity Reference)
- 若分镜标记了 `refer_previous_end_frame: true` 或指定了 `reference_shot_id`，被引用的镜头 ID (Target Ref ID) 必须在 `shots` 中真实存在，且 Target Ref ID **必须严格小于当前 `shot_id`**。

### 6. 视觉语义三要素完整性约束 (Visual Spec Completeness)
- 每个分镜的 `visual` 对象必须完整包含以下三要素：
  1. **视觉寓意与因果推导 (`metaphor_meaning`)**：明确画面表达的科学/逻辑含义。
  2. **具象元素明细 (`key_objects` / `elements_detail`)**：列出画面中的 3–8 个核心视觉物件。
  3. **动画效果与运动说明 (`motion_description`)**：使用 2D 剪纸滑入、旋转、落位等确切动作描述。

### 7. 运动 Prompt 姿态锁定与防误幻觉约束 (Motion Posture Locking)
- 检查 `motion_plan.motion_prompt`：针对首帧（`first_frame`）中已预渲染呈现的人物/主体，`motion_prompt` **必须包含主体姿态锁定向指令**（如 `remains standing upright, static and frozen in place; zero posture morphing, no rising from floor`）。
- **严禁包含歧义动词**：严禁使用 `slides in from bottom`、`rises from ground` 等诱导模型生成“卧倒爬起”或“肢体扭曲”的描述。

### 8. 单镜单动作与复合动作物理防范拆镜约束 (Single Action Per Shot Inspection)
- 检查每个分镜的 `visual.action_verbs`：**数组元素数量必须严格等于 1**。若 `action_verbs` 包含 2 个及以上不同的动作动词（如 `["平移入场", "折射展开"]`），SubAgent **必须直接判定审查失败并阻断**，要求编导自动拆解为独立分镜。
- 检查每个分镜的 `visual.object_actions` 与 `motion_plan.motion_prompt`：**必须严格保证单镜头对应单一平面物理动作**（如仅有平移落位、仅有旋转、仅有印压或仅有爆散）。
- 检查 `motion_plan.multi_beats`：严禁在一个镜头的多节拍中安排跨越不同物件或不同动效的复合序列（如 Beat 1 描述光束延伸，Beat 2 描述彩虹纸带展开）。若存在复合序列，**必须判定审查失败并拒绝交由人类审核**。
- **复合动作强行混杂阻断**：若 SubAgent 发现单镜头中包含跨越多个姿态改变或多重变轨的复合动作序列，必须硬阻断并要求编导在动作拐点与自然语义停顿处切拆为多个独立的 100% 原子化单动作镜头。

### 9. 提示词视觉命题语义表达对齐约束 (Prompt Semantic Alignment Audit)
- SubAgent 在审查分镜时，必须对每个分镜的生图提示词 (`first_frame_prompt`, `last_frame_prompt`) 执行**语义对齐与意图表达硬性核查**：
  1. **意图完全承载**：生图提示词的主体诉求 (`Primary request`) 与增量描述 (`Delta changes`) **必须 100% 精准覆盖并传达该分镜的视觉命题 (`visual.visual_proposition`)、科学寓意 (`visual.metaphor_meaning`) 与全部关键物件 (`key_objects`)**。
  2. **偏离与遗漏硬阻断**：若提示词未能完整描述分镜的核心物件与动作（例如漏写了受体高亮、分子网格或红光穿透），或者提示词描绘的画面与分镜旁白意图产生偏差，SubAgent **必须直接判定审查不通过**。
  3. **强制退回修正**：审查失败后，必须要求 Agent 立即重新修改并完善对应的英文 Prompt 及 `_zh` 中文对译字段，直至提示词能够完全描述传达分镜意图后，方可允许提交人类确认或进入 Phase 2 生图。

---

## 视觉阶段校验规则 (Phase 2: Visual Rules)

SubAgent 在审查 `<topic_slug>/02-visual/` 产物时，必须逐一验证以下规则：

### 1. 镜头 100% 覆盖率契约 (100% Shot Coverage)
- 必须存在 `<topic_slug>/02-visual/visual_spec.json`。
- `visual_spec.json` 中 `keyframes` 数组所记录的镜头必须 100% 覆盖 `storyboard.json` 中定义的所有 `shot_id`，不得遗漏任何一个镜头。

### 2. 关键帧图像磁盘落地与非空校验 (File Existence & Non-Empty)
- `visual_spec.json` 中声明的关键帧文件路径（`keyframe_file` / `first_frame_file` / `last_frame_file`）在 `<topic_slug>/02-visual/` 目录下必须**物理存在**。
- 图片文件大小必须大于 0 字节，严禁出现损坏或空文件。

### 3. SubAgent 静态视觉单帧盲审与图生图增量比对规程 (Single Keyframe Visual Audit Protocol)
每当生成一张静态关键帧时（包含 Shot #1 样板帧以及后续 Shot #2 ~ Shot #N 逐一生成的关键帧），SubAgent **仅针对当前刚生成的该张单帧图像**进行盲审评估。评估分为两种情形：

#### A. 文生图盲审情形 (Text-to-Image Standard Audit)
当当前生成的帧为无参考图的文生图时（如镜头 1 的首帧 `shot_01_first.png`），执行以下 6 项标准盲审评估：
1. 🎯 **视觉隐喻与构图清晰度 (`metaphor_clear`)**：视觉隐喻精准落地，主体位于中上部 70% 区域，底部留出字幕避让区。
2. 👤 **人物与主体无变形 (`no_character_distortion`)**：黑白半调人物肢体结构自然，无多肢、畸变或结构混淆。
3. 🔤 **文字纯净度 (`no_gibberish_text`)**：无无意义 AI 乱码假字；关键物件上允许有清晰精准的公式、符号、数字与标签。
4. 🎨 **视觉风格系统统一性 (`style_unified`)**：HEX 色板、纸质撕边、切面阴影与白描边严格遵循选定 Style 契约。
5. 🧩 **3–8 个核心物件完整性 (`key_objects_complete`)**：对照该分镜 `key_objects` 声明，检查当前帧是否完整包含计划在场的核心物件。
6. 📍 **物件与固件位置逻辑性 (`object_positions_logical`)**：物件摆放层次清晰，避开底部字幕避让区，首帧预留充足入场空间。

#### B. 图生图增量盲审情形 (Image-to-Image Delta Audit)
当当前生成的帧为基于参考图的图生图时（如尾帧 `shot_XX_last.png` 参考首帧，或连续分镜首帧参考前一分镜尾帧），**重点对比当前生成帧与参考图 (`ImagePaths[0]`)**，深度审查以下 4 项增量精准指标：
1. 🎯 **增量变更精准性 (`delta_change_exact`)**：**重点审查是否仅改动了 Prompt 要求的增量内容**（如特定元件的移位、缩放或状态演进），共有背景与不动主体是否 100% 锁死未动。
2. 🚫 **无元素遗漏/少东西 (`no_missing_elements`)**：**重点审查有无遗漏或丢掉参考图原有的共有静态背景、人物主体或基础固件**（严禁图生图过程把已有背景元素抹除变丢）。
3. 🛑 **无幻觉杂物/多东西 (`no_extra_hallucinations`)**：**重点审查有无生出 Prompt 未要求的额外画外杂物、幻觉乱码、多余肢体或背景乱字**（严禁多出无关多余元素）。
4. 📐 **场景底图与锚点对齐 (`background_anchor_aligned`)**：背景 HEX 底色、场景透视与相机视角与参考图完全一致无跳闪。

### 4. 静态帧门控呈报与后续分镜盲审规程 (Keyframe Gate & Sequential Audit Protocol)
1. **样板门控呈报**：在向用户呈报 Keyframe Gate 时，**必须同时提交首帧与尾帧图**，且汇报文本必须具备清晰的结构划分，**重点突出**：
   - 🎬 **首尾帧动画动作与过渡逻辑 (Motion Transition)**：清晰描述从首帧（初始/入场态）到尾帧（完成/终止态）物件如何随多节拍 (`multi_beats`) 发生平移、旋转、缩放或组装落位。
   - 💡 **画面视觉隐喻与科学含义 (Visual Metaphor & Meaning)**：解释画面构图与视觉符号如何映射剧本核心观点与科学因果。
   - 🧩 **3–8 个核心物件状态对比 (Key Objects State Evolution)**：逐一列出核心物件在首帧与尾帧中的显示状态（如：`首帧未出现/隐藏 -> 尾帧组装完成`）。
2. **后续分镜逐一生成与盲审**：人工审批通过 Shot #1 门控后，Agent 逐一生成 Shot #2 ~ Shot #N 的静态帧。**每生成一个分镜/单张图片，必须即刻触发 SubAgent 对当前生成图片的盲审流程**。盲审通过后方可生成下一个分镜；若盲审失败，在当前分镜自动修复或重新生成。

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

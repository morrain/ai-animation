# Phase 2: 视觉阶段规范 (Visual Spec)

## 📌 阶段目标
根据编导阶段的分镜描述，确定全片视觉规格（色板 Palette、字体 Family、画面比例、视觉风格），并为每一个单镜生成/设计静态关键帧（Keyframe）。

## 🎨 风格预设与项目快照 (Style Snapshot & Frame Policy)

本阶段根据输入的 `style_id` 加载对应的风格文件，并复制快照固化至项目的 `<topic_slug>/state/style-definition.md` 和 `<topic_slug>/state/style-selection.json`，确保项目后续渲染不受全局配置变动影响：

- **`vox`**：黑白半调人物、彩色卡纸拼贴、纸质纹理与视觉隐喻（采用 `frame_policy: distinct-first-end` 双帧策略）。
  - **首尾双帧契约与首帧基准图继承协议 (First-Frame Anchor Conditioning Protocol)**：
    1. **首帧优先渲染 (First Frame First)**：对于每个分镜，必须优先基于 `first_frame_prompt` 生成 `shot_XX_first.png`（动作初始首帧），建立该镜头场景构图、角色形象、静态背景元素与色彩关系的“视觉基准锚点”。
    2. **图生图参考继承 (Image-to-Image Conditioning)**：在生成对应的 `shot_XX_last.png`（完成态尾帧）时，**必须将 `shot_XX_first.png` 的物理路径作为参考图 (`ImagePaths=[shot_XX_first.png]`) 传入 `generate_image`**。
    3. **跨镜头连续首帧参考继承协议 (Cross-Shot Continuity Reference Protocol)**：当分镜 N 在 `storyboard.json` 中标记为与前一分镜 N-1 连续（`refer_previous_end_frame: true` 或 `reference_shot_id: N-1`）时，生成分镜 N 的首帧 `shot_{N}_first.png` 时，**必须将分镜 N-1 的尾帧物理路径 `shot_{N-1}_last.png` 作为参考图 (`ImagePaths=[shot_{N-1}_last.png]`) 传入 `generate_image`**。构成 `分镜 N-1 首帧 -> 分镜 N-1 尾帧 -> 分镜 N 首帧 -> 分镜 N 尾帧` 的连续视觉递进控制链，确保分镜 N 首帧与分镜 N-1 尾帧中的视觉元素、场景风格与构图框架同构一致。
    4. **图生图增量提示词法则 (Img2Img Delta Prompting Protocol)**：针对图生图关键帧（如尾帧 `last_frame_prompt` 参考首帧），**严禁重复描绘全量背景或不动的共有元素**，提示词必须声明 `Inherit exact background scene elements, character appearance, object scale, and camera framing from reference image ImagePaths[0]; keep all static shared elements 100% frozen`，并**仅增量描写具体的位移与动作变化**（如将哪些物件移到何处、新切入了什么元件），防范全量提示词导致画风与定位产生二次随机偏差。
- **`storybook`**：多层纸雕景深、温暖调性、立体阴影柔光（采用 `frame_policy: shared-hero-frame` 共享 Hero 帧策略）。
  - **共享 Hero 帧契约**：仅需生成 1 张精细主关键帧 `shot_XX.png`，`first_frame_file`、`last_frame_file` 与 `keyframe_file` 均指向该统一主图像。
- **自定义 `custom`**：加载用户传入的 JSON 配置或实时生成的规则。

## 🔍 SubAgent 视觉审核与人工确认门控 (Review & Gate)

在全量生成动画素材前，本阶段遵循两级审查机制：

1. **生成 Shot #1 样板静态关键帧 (Pilot Keyframe Generation)**：
   - 严禁一次性全量调用生图工具生成全部分镜图片！Agent 根据 `storyboard.json` 方案与风格策略，通过 `run_command` 调用底层单图脚本 `python3 .agents/skills/ai-animation/scripts/generate_image.py --prompt "..." --output "<topic_slug>/02-visual/keyframes/shot_01_first.png" --project_dir "<topic_slug>"` 逐帧生成 Shot #1 的目标控制图片（如首帧 `shot_01_first.png`、尾帧 `shot_01_last.png` 或单主帧 `shot_01.png`）。
   - **原生 16:9 比例生成硬要求**：生图 Prompt 头部必须携带 `--ar 16:9 widescreen 16:9 horizontal landscape aspect ratio` 指令，要求 AI 生图模型直接原生输出 16:9 构图，严禁生成 1:1 正方形图片后再做二次切头切尾裁剪导致视觉元素缺失。
2. **SubAgent 静态视觉单帧盲审 (SubAgent Check)**：
   - 调起 SubAgent 严格依照 [validation-rules.md](validation-rules.md#3-subagent-静态视觉单帧盲审与图生图增量比对规程-single-keyframe-visual-audit-protocol) **仅对当前刚生成的单张帧图像进行精准盲审**。
   - 若当前帧为文生图，校验画风、质感、构图避让与隐喻落地；若当前帧为图生图，**重点与参考图比对审查是否只改动了增量内容、有无漏遗共有元素（少东西）或生出幻觉杂物（多东西）**。
3. **样板确认门控与重点突出汇报 (Keyframe Pilot Gate)**：
   - 将 SubAgent 盲审通过的 **Shot #1 样板图对比**及审查报告提交用户做**人工确认**。
   - **重点突出汇报要求**：汇报内容必须**重点突出展示首尾两帧之间的动画动作与过渡逻辑、视觉隐喻与科学含义、3–8 个核心物件的状态与空间位置变化**，便于用户清晰评估首末帧构图与运动可行性。
   - 在 `human-gated` 模式下，呈报后**必须暂停流程（不得发起下一轮 Tool Call）**。
4. **后续分镜逐一生成与单帧实时盲审 (Sequential Keyframe Generation & Per-Image Review)**：
   - **仅在用户明确回复“确认通过”样板图（完成静态帧人工审批）后**，Agent 方可遍历分镜数组，**逐一生成其它分镜（Shot #2 ~ Shot #N）的静态帧图片**。
   - **每生成一个分镜的静态帧（如 `shot_XX_first.png` 或 `shot_XX_last.png`），必须即刻触发 SubAgent 对当前生成的图片进行盲审流程**（对照 `references/validation-rules.md`）。盲审通过后方可推进生成下一个分镜；若盲审不通过，在当前分镜自动修复重试。
   - 全部分镜静态帧生成且盲审通过后，导出并更新 `visual_spec.json`。

### `visual_spec.json` 契约范例：
```json
{
  "style_id": "vox",
  "theme": {
    "aspect_ratio": "16:9",
    "color_palette": {
      "background": "#F4F1EA",
      "primary": "#E63946",
      "secondary": "#457B9D",
      "accent": "#F4A261",
      "text": "#1D3557"
    },
    "element_style": "cutout_paper_collage",
    "font_family": "Inter, Noto Sans SC, sans-serif"
  },
  "keyframes": [
    {
      "shot_id": 1,
      "keyframe_file": "keyframes/shot_01.png",
      "first_frame_file": "keyframes/shot_01_first.png",
      "last_frame_file": "keyframes/shot_01_last.png",
      "subagent_review": {
        "metaphor_clear": true,
        "no_character_distortion": true,
        "no_gibberish_text": true,
        "style_unified": true,
        "first_last_anchor_alignment": true,
        "key_objects_complete": true,
        "object_positions_logical": true,
        "animation_plan_compliant": true
      },
      "prompt_used": "Vox style paper collage animation, black and white halftone character cutout, vibrant colored paper shapes, 8k resolution"
    }
  ]
}
```

### 🤖 生图大模型声明式接入与 CLI 驱动规范 (Image Provider Architecture)

Phase 2 关键帧生成由 Skill 内部脚本 `scripts/generate_image.py` 结合项目根目录生图模型配置库 `providers/image/` 声明式驱动：

- **规则 1：统一画风主描述词（Mandatory Style Prefix）**
  每镜提示词头部必须强制包含：`editorial stop-motion paper collage, flat solid colored background HEX #F4F1EA, black-and-white halftone photographic cut-outs, selective colored cardstock, crisp warm-cream paper keylines #FFFDF7, soft low-opacity physical drop shadows`。

- **规则 2：显式硬否定限制（Mandatory Anti-Glow Negative Prompt）**
  尾部必须强制注入否定限制：`Negative constraints: no cropping, no black bars, no letterbox, no borders, no solid black subtitle rectangle, no AI gibberish text, no random unreadable letters, no glossy 3D, no neon glow, no volumetric light, no digital lens flare, no fluid morphing, no motion blur`。

- **单环境变量与 CLI 配置参数 (`IMAGE_PROVIDER_CONFIG`)**：
  - 系统优先读取环境变量 `IMAGE_PROVIDER_CONFIG` 或 CLI 参数 `-c / --provider_config <name_or_path>`；
  - 默认加载项目根目录声明式配置 `providers/image/agnes_ai.json`（对接 Agnes Image 2.1 Flash 模型 `agnes-image-2.1-flash`）。
- **零代码修改扩展自定义生图 API**：
  - 用户可复制模版 `providers/image/template.json` 创建自定义模型 JSON 描述文件，灵活支持文生图与图生图（Base64 Data URI 或公开 URL）。
- **CLI 调度命令行范例（由 Agent 根据业务策略按需调用）**：
  - **文生图渲染单张静态首帧**：`python3 .agents/skills/ai-animation/scripts/generate_image.py --prompt "..." --output "<topic_slug>/02-visual/keyframes/shot_01_first.png" --project_dir "<topic_slug>"`
  - **图生图渲染单张静态尾帧**：`python3 .agents/skills/ai-animation/scripts/generate_image.py --prompt "..." --output "<topic_slug>/02-visual/keyframes/shot_01_last.png" --ref "<topic_slug>/02-visual/keyframes/shot_01_first.png" --project_dir "<topic_slug>"`

## ⚠️ 解耦逻辑
- 视觉增量修改：若用户更换视觉模型或调试第 N 镜画风，仅需替换对应静帧及首末帧文件，不会影响旁白音频生成。

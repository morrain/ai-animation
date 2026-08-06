# Phase 3: 运动阶段规范 (Motion Spec)

## 📌 阶段目标
根据视觉关键帧及编导中的动作指令，将静态画面转化为动态动画片段（无声视频）。支持前端代码渲染（Remotion / HTML Canvas）或 AI 视频帧运动合成。

## 📥 输入说明
- 编导产物：`01-director/storyboard.json`
- 视觉关键帧：`02-visual/keyframes/shot_{shot_id}.png` / `visual_spec.json`

## 🎬 AI 视频大模型驱动法则 (AI Image-to-Video Generation Protocol)

1. **大模型图生视频强制规范 (AI Motion Engine Mandatory Rule)**：
   - 本阶段生成的单镜无声视频（`shot_XX.mp4`），**必须且仅能通过 AI 图生视频大模型（Image-to-Video Engine，如 Runway / Kling / CogVideoX / HunyuanVideo / Luma 等）渲染真实物理与视觉元素运动**。
   - **严禁使用本地 Python 脚本做透明度渐变、渐隐渐现 (Crossfade / Fade Blending)、静态图片拼接或 Alpha 混合擦除来伪造动画**！
2. **生成输入契约 (Generation Input Contract)**：
   - **控制基准图**：以 `first_frame_file` (`keyframes/shot_XX_first.png`) 作为起始帧图，`last_frame_file` (`keyframes/shot_XX_last.png`) 作为终止控制帧。
   - **运动 Prompt 指令**：使用 `storyboard.json` 中定义的 `motion_plan.motion_prompt` 作为大模型物理运动控制指令，精准指挥画面中纸雕光束的萌发延伸、人脸微动与粒子碰撞散落。
3. **模型抽象与通用 CLI 调用协议 (Model Abstraction & CLI Protocol)**：
   - Phase 3 视频生成统一由通用模型抽象层脚本 `scripts/generate_video.py` 执行，实现模型提供商完全解耦与用户自定义扩展。
   - **模型 JSON 配置文件位置**：位于项目根目录的 `providers/video/` 目录下（默认 `providers/video/agnes_ai.json`）。
   - **环境变量配置**：通过 `VIDEO_PROVIDER_CONFIG` 设置具体的 JSON 文件路径（如 `/path/to/my_kling.json`）或配置名（如 `kling` / `agnes_ai`）。
   - **标准 CLI 驱动命令**：
     ```bash
     # 默认使用 providers/video/agnes_ai.json 生成单镜视频
     python3 .agents/skills/ai-animation/scripts/generate_video.py why-is-the-sky-blue --shot_id 1

     # 显式覆盖配置文件 / 供应商
     python3 .agents/skills/ai-animation/scripts/generate_video.py why-is-the-sky-blue --shot_id 1 -c providers/video/kling.json
     ```

## 风格驱动的运动帧率与参数 (Style-Driven Motion Easing)

本阶段渲染无声视频时，读取 `visual_spec.json` 中配置的风格与运动特征：

1. **Vox 风格 (`vox`)**：
   - 帧率：12 fps (抽帧定格感)
   - 缓动算法：`steps(4, end)` / Snap Discrete
   - 动作演进逻辑：从空场或初始基座逐件滑入卡位组装 (`Assemble-From-Empty`)，动作提示词包含 `12fps stop-motion paper assembly, items slide in and lock into place from empty backdrop, 2D flat paper motion, zero fluid morphing`
   - 动作效果：组件逐件组装 (Assembly)、盖章压印、平移滑入
   - 净化处理：生成的 MP4 强制经过 FFmpeg `fps=12` 抽帧定格下采样与色彩平坦化净化
2. **Storybook 风格 (`storybook`)**：
   - 帧率：30 fps
   - 缓动算法：`easeInOutSine`
   - 动作效果：微风呼吸浮动 (Breathing ambient wave)、低振幅慢速漂移

## 🔍 动画样片 SubAgent 动态审核与人工确认门控 (Review & Gate)

在全量生成所有单镜动画之前，执行样片试做与两级审查：

1. **生成单镜动画样片 (Pilot Sample Generation)**：
   - 基于静态关键帧及其首尾帧，优先渲染首个单镜（Shot #1）的动态无声视频样片。
2. **SubAgent 动态审核 (SubAgent Motion Review)**：
   - 调起 SubAgent 严格依照 [validation-rules.md](validation-rules.md#运动阶段校验规则-phase-3-motion-rules) 检验单镜 MP4 文件存在性与非空落地，并执行 6 项动态质量指标审查（详情参阅 [validation-rules.md](validation-rules.md#2-subagent-动态运动质量-6-项指标-motion-quality-metrics)）。
3. **人工确认门控 (Human Gate)**：
   - 将 SubAgent 审核通过的动画样片提交给用户进行**人工确认**。在 `human-gated` 模式下，呈报后**必须暂停流程（不得发起下一轮 Tool Call）**。
   - 用户确认满意后，系统方全量批量推进其余分镜的动画生成。

## 📤 中间产物规范
保存路径：
1. 动画方案配置/代码：`03-motion/code/shot_{shot_id}.tsx` (或 `.json`)
2. 渲染后单镜无声视频：`03-motion/shots/shot_{shot_id}.mp4`

## ⚠️ 解耦逻辑
- **单镜独立控制**：若需要调整第 N 镜的运动轨迹、转场动画速度或缓动函数，只需重做 `03-motion/shots/shot_N.mp4`，其他单镜片段及音频均不受影响。

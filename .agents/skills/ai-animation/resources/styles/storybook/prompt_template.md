# Storybook 1.0 彩色纸雕绘本风格指南与 Prompt 模板

版本：`1.0`  
关键帧策略：`shared-hero-frame`（共享主画面）  
运动策略：`same-frame-breathing-keyframes`（同帧微风呼吸）

---

## 🎯 1. 视觉签名 (Visual Signatures)

- **纸雕小型舞台**：背景由分层裁切的手工纸片搭成的小型立体舞台（Layered Papercraft Diorama），包含清晰的裁切边与微阴影。
- **贴纸造型主体**：前景人物与核心物件呈现带暖米白（Warm Off-White）裁切轮廓的贴纸造型。
- **低刺激绘色**：使用低刺激、温暖舒适的配色（奶油白、暖黄、砖红、柔和蓝绿、橄榄绿）。
- **空间构图**：16:9 故事书视角，主体位于中央 70% 区域且脚下有明确的视觉支撑落点；**底部 15–18% 严格留白用于单行字幕**。

---

## 🎨 2. 隐喻与场景选择 (Metaphor & Scenarios)

建立一眼可读的生活化低认知负担情境：
> **具体人物/群体 → 面对可见的选择、关系或变化 → 呈现概念结果**

- **单镜元素控制**：保持 **3–7 个大组**，优先使用家庭、商店、村庄、道路、花园、储蓄罐、篮子、桥梁等儿童易理解的情境。
- **抽象落地**：抽象概念必须落到具体人物、物件和空间关系上。严禁生成无意义 AI 乱码假字或背景大字包围框，允许关键物件上带有精准符号与数字标签。

---

## 🖼️ 3. 共享主画面策略 (Shared Hero Frame Strategy)

为了彻底锁死人物形象与构图一致性，防止动画推理中人物发声扭曲：
1. **单场景仅生一张主图**：视觉阶段调起图像模型生成一张权威主图（Hero Frame）。
2. **首尾帧复用**：`first_frame_prompt` 与 `image_prompt` 写入完全相同的 Prompt，同时登记为首帧与尾帧。
3. **低频呼吸运动**：视频生成模型仅执行克制的人员贴纸缓慢入场与微风正弦呼吸浮动。

---

## 📝 4. 共享主画面 Prompt 模板 (Authoritative Hero Frame Prompt)

```text
Use case: friendly educational explainer animation.
Asset type: authoritative hero frame for a locked 16:9 storybook shot.

Create a warm tactile layered cut-paper storybook diorama showing:
[CONCRETE_VISUAL_PROPOSITION]. Include [3-7 LARGE_READABLE_GROUPS] already arranged in their final positions.

Style & Materials:
Colorful handcrafted paper layers, visible fine paper fibers, clean cut edges, warm off-white sticker outlines around foreground characters, and soft low-opacity physical paper shadows with one consistent direction.

Composition & Lighting:
Fixed 16:9 storybook framing, eye-level camera view, subjects centered in middle 70% area with solid footing ground. Bottom 15-18% completely clear for single-line subtitles. Warm volumetric daylight color palette (cream white, warm yellow, brick red, soft teal).

Negative constraints:
No readable text, no letters, no numerals, no logos, no glossy 3D, no depth-of-field blur, no plastic highlights, 8k resolution.
```

---

## 🎬 5. 运动提示词法则 (Motion Prompting)

- **帧率**：30 fps
- **动作控制**：`same_frame_breathing_float`。贴纸元素轻柔定点移出/移入，落位后保持极其微弱的正弦平缓呼吸浮动（Subtle breathing sine wave），运动柔和安静。

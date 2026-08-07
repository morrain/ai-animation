# Vox 2.0 纸拼贴风格指南与 Prompt 模板 (Vox Style Spec)

版本：`2.0`  
运动策略：`content-to-completed-keyframes`  

对用户展示的风格名称固定为“Vox 风格”。下文列出的题材只是适用范围，不是风格名称。

---

## 📌 1. 适用范围 (Scope & Suitability)

**适合**：
- 抽象概念、经济机制、认知偏差和观点解释；
- 需要把因果关系压成一个视觉命题的短镜头（Sharp Visual Idea）；
- 固定机位、逐件组装（Assemble-from-empty）、落位后近乎静止的解说动画。

**不适合**：
- 真实产品广告、写实人物表演或口型同步；
- 精确复杂遮挡、镜头穿越或连续空间叙事；
- 依赖可读长文字、真实软件界面或数据表格的内容。

---

## 🎯 2. 视觉签名 (Visual Signatures)

- **强色场**：强烈、平坦、均匀的纸张纯色色场。
- **黑白半调骨架**：主人物、人脸、物体或核心机械采用高对比度黑白半调网点（Halftone Cutout），犹如杂志或旧报纸剪裁。
- **彩色卡纸信息层**：彩纸（Selective Colored Cardstock）仅用于信息层级引导与重点突显，不为了“热闹”乱加颜色。
- **裁切边与 Keyline**：干净清晰的纸张剪裁边缘，附带暖奶油白（Cream White `#FFFDF7`）Keyline 描边。
- **纸片柔阴影**：低透明度、方向统一的软边缘纸质投影（Soft Drop Shadows），仅表达层次交叠，不制造真实景深。
- **纸张纤维**：细微未涂布纸纤维纹理（Uncoated Paper Fiber）。
- **编辑海报构图与字幕避让**：原生 16:9 横屏海报构图，主体与重要视觉焦点置于中上部 70% 区域。**字幕避让是指避免将人脸、核心隐喻符号等焦点元素放置在底部 15–18% 区域以防字幕遮挡，背景及延伸场景可自然铺满整屏，严禁刻意挖空或画框底条**。
- **纯净无杂质**：画面内无 logo、水印、UI、glossy 3D 或写实房间。

> **同一视频必须统一半调密度、纸张颗粒、描边宽度和阴影方向。背景色可随语义变化，但需保持全片风格和谐统一。**

---

## 🎨 3. 语义色场法则 (Semantic Color Mapping)

背景色与主体色彩按科普语义匹配，单镜采用 **1 个主背景色 + 2~4 个点缀卡纸色**：

| 色彩 | HEX 色号 | 语义匹配 |
| :--- | :--- | :--- |
| **焦橙 / 红色** | `#E63946` | 劳动消耗、时间紧迫、风险暴露、冲突焦点 |
| **芥末黄** | `#E9C46A` | 警示、关键节点、工具属性、知识漏洞、经验漏失 |
| **墨绿** | `#2A9D8F` | 系统重置、判断修复、成长、科学结论 |
| **深紫** | `#4A4E69` | 制度、记忆、深层机制、抽象反思 |
| **青绿** | `#264653` | 协作网络、机会点、自动化流程、连接管道、自动执行 |
| **奶油白** | `#FFFDF7` | 边缘 Keyline、纸张切面、中性连接结构、信封与边缘 |

> **每镜使用 1 个主背景色和 2–4 个点缀卡纸色。彩色纸张服务于信息层级，严禁为了“热闹”无意义堆砌颜色。**

---

## 💡 4. 视觉隐喻与元素收敛 (Metaphor Design)

每镜**只表达一个**明确的因果关系：
> **主体 A → 通过特定动作 → 改变主体 B → 展现可见结果**

- **控制元素组数量**：单镜保持 **3–8 个大组合件**。一个“人群”“店铺链”或“信封序列”可作为一组，避免堆砌零散小碎片。
- **推荐隐喻符号**：
  - **容器**：储蓄罐、漏斗、透明档案盒
  - **连接**：管道、纸带、齿轮组、桥梁
  - **变化**：收窄、缩小、分叉、锁住、被光芒照亮
  - **循环**：轨轮、链条、闭合路径
  - **对照**：一个个体与一个网络、投入与结果
- **防止 AI 乱码与杂乱大字 (No AI Gibberish & Fullscreen Captions)**：严禁无意义 AI 乱码假字 (gibberish text)、杂乱伪字符或背景标题画框。**允许且鼓励在关键物件上印刷清晰的科学公式（如 E=mc²）、单位符号（如 H₂O, kg）、精准数字标号（如 01, 100%）或矢量节点标签**。

---

## 🖼️ 5. 首尾帧 Prompt 编写法则与标准 Key-Value 模板

每一镜必须编写两条**自包含 (Self-contained)** 的英文图像提示词，绝对不能仅简写 "same as last frame"。

### 标准 Key-Value 结构化 Prompt 模板

```text
Use case: educational-explainer
Asset type: [initial/final] still frame for a 16:9 image-to-video B-roll clip
Primary request: Create a finished editorial paper-collage image expressing [一句话视觉命题].
Scene/backdrop: perfectly flat [背景颜色描述] paper field [HEX色号] with subtle uncoated paper fiber.
Style/medium: premium editorial stop-motion paper collage; black-and-white halftone photographic cut-outs mixed with selective [点缀色彩] colored cardstock.
Composition/framing: horizontal 16:9 locked poster frame; central subject within the middle 70 percent; generous clean color-field negative space; 3–8 large separable paper groups for later assemble-from-empty animation.
Materials/textures: visible printed halftone dots, crisp machine-cut edges, thin warm-cream paper keylines, soft low-opacity physical drop shadows.
Constraints: [本条隐喻必须一眼看懂的关系说明].
Avoid: no AI gibberish text, no random unreadable letters, no random pseudo-symbols, no fullscreen title boxes, no logos, no watermark, no UI, no subtitles, no glossy 3D, no photoreal environment, no clutter.
```

### 锚点对齐与图生图参考继承 (Anchor Conditioning & Image-to-Image Protocol)
- **尾帧基准锚点 (Last Frame Prompt Anchor)**：
  在 `image_prompt` (尾帧) 中，必须包含参考首帧锚点的指令：
  `Reference Image Conditioning: Always pass first_frame_file via ImagePaths=[first_frame_path] to lock shared visual elements. Inherit exact background scene elements, character appearance, object scale, dot/grid density, and camera framing from reference image ImagePaths[0]. Keep all static shared background elements 100% identical and frozen.`
- **连续分镜基准锚点 (Continuous Shot Prompt Anchor)**：
  在分镜 N 的 `first_frame_prompt` (首帧) 中，若标记继承分镜 N-1 尾帧，必须包含：
  `Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #{N-1} end frame (reference image ImagePaths[0]); keep all static shared elements 100% identical and frozen.`

### 双语对译与连续继承契约 (Dual Language & Continuity Protocol)
- **双语全量对译硬绑定**：`storyboard.json` 中所有英文提示词必须附带对应的 `*_zh` 中文对译字段（如 `first_frame_prompt_zh`, `image_prompt_zh`, `motion_prompt_zh`），专供人类审计与审阅。**中文对译必须保留英文 Prompt 的全部内容与段落结构细节**（包含画幅、背景 HEX、组件列表、继承锚点、负向排除等），严禁缩简为一句话总结。
- **连续分镜继承（Continuous Shot Continuity）**：当分镜 N 承接分镜 N-1 时，标记 `"refer_previous_end_frame": true` 与 `"reference_shot_id": N-1`，保持主体形象、空间关系与色彩基调前后贯通。

---

## 🎬 6. 运动提示词法则 (Motion Prompting)

- **帧率**：12 fps 定格动画感（Stop-motion）。
- **动作控制**：以**逐件落位组装 (Assemble-from-empty / Item-by-item Assembly)**、平移扣合、盖章压印为核心，动作结束后镜头迅速稳定落位（Nearly still at keyframe completion）。

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
| **深紫** | `#4A4E69` | 记忆、深层机制、抽象反思、宇宙高空 |
| **青绿** | `#264653` | 协作网络、波长介质、大气层网格、自动化流程 |
| **奶油白** | `#FFFDF7` | 边缘 Keyline、纸张切面、中性连接结构、太阳白光束 |

---

## 💡 4. 视觉隐喻与元素收敛 (Metaphor Design)

每镜**只表达一个**明确的因果关系：
> **主体 A → 通过特定动作 → 改变主体 B → 展现可见结果**

- **控制元素组数量**：单镜保持 **3–6 个大组合件**。
- **禁止可读文字**：**画面内绝对不要生成包含字母、数字、标题或乱码印章**。所有文字仅在合成阶段的字幕层体现。

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
Composition/framing: horizontal 16:9 locked poster frame; central subject within the middle 70 percent; generous clean color-field negative space; 3–6 large separable paper groups for later assemble-from-empty animation.
Materials/textures: visible printed halftone dots, crisp machine-cut edges, thin warm-cream paper keylines, soft low-opacity physical drop shadows.
Constraints: [本条隐喻必须一眼看懂的关系说明].
Avoid: no typography, no readable letters, no numerals, no logos, no watermark, no UI, no subtitles, no glossy 3D, no photoreal environment, no clutter.
```

### 锚点对齐与图生图参考继承 (Anchor Conditioning & Image-to-Image Protocol)
- **尾帧基准锚点 (Last Frame Prompt Anchor)**：
  在 `image_prompt` (尾帧) 中，必须包含参考首帧锚点的指令：
  `Reference Image Conditioning: Always pass first_frame_file via ImagePaths=[first_frame_path] to lock shared visual elements. Inherit exact background scene elements, character appearance, object scale, dot/grid density, and camera framing from reference image ImagePaths[0]. Keep all static shared background elements 100% identical and frozen.`
- **连续分镜基准锚点 (Continuous Shot Prompt Anchor)**：
  在分镜 N 的 `first_frame_prompt` (首帧) 中，若标记继承分镜 N-1 尾帧，必须包含：
  `Inherit exact background scene elements, character appearance, object scale, color palette and camera framing from Shot #{N-1} end frame (reference image ImagePaths[0]); keep all static shared elements 100% identical and frozen.`

---

## 🎬 6. 运动提示词法则 (Motion Prompting)

- **帧率**：12 fps 定格动画感（Stop-motion）。
- **动作控制**：以**逐件落位组装 (Assemble-from-empty / Item-by-item Assembly)**、平移扣合、盖章压印为核心，动作结束后镜头迅速稳定落位（Nearly still at keyframe completion）。

### 🚀 2D复古科幻游戏资产生成工具 (PC-98风格/四视图版)

这是一个模块化的 Prompt 模板。请复制下方的代码块，每次生成新资产时，只需修改 **`【模块 3：主体核心描述】`** 中的内容即可。

Markdown

# 

`A strictly organized technical reference sheet in a 2x2 grid layout showing 4 views of a [在此处填入简短物体名称，例如: High-Tier Sci-Fi Engine].

**【模块 1：布局与格式硬性约束 (LAYOUT & FORMAT CRITERIA)】**
**CRITICAL - READ FIRST:**
The final image must be a clean, professional reference sheet showing exactly four views.
The views must be arranged in a precise 2x2 GRID on the canvas (Aspect Ratio 1:1).
VIEWS MUST BE ISOLATED AND MUST NOT OVERLAP.
Background must be PURE SOLID WHITE (#FFFFFF).

**【模块 2：视角协议 (VIEW ANGLES PROTOCOL)】**
The sheet must contain these 4 distinct views of the exact same object, ensuring structural consistency:
1. Orthographic Front View (Top Left)
2. Orthographic Side View (Top Right)
3. Orthographic Top View (Bottom Left)
4. Isometric Perspective View (3/4 view) (Bottom Right)

**【模块 3：主体核心描述 (SUBJECT DESCRIPTION)】**
(在此处详细描述你要生成的组件。请包含设计语言、关键特征、否定约束和材质感。)
> **CRITICAL DESIGN NOTE:** [在此处填写核心否定约束，告诉AI不要画什么。例如：This is a LASER EMITTER. NO projectile barrels.]
>
> [在此处填写物体的整体设计风格和体量感描述。例如：This design is a massive, late-game heavy energy weapon array. It looks like a fortified emplacement.]
> **Key Features:**
> 1. [特征1，例如：Twin-Linked Emitters: Two massive rectangular optical housings with glowing blue lenses.]
> 2. [特征2，例如：Active Cooling System: Exposed thick pipes with glowing coolant and large rear vents.]
> 3. [特征3，例如：Fortified Structure: Thick segmented composite armor plates with visible heavy bolts.]
> 4. [特征4，例如：Massive Base: A huge rotating platform with visible gears and hydraulics.]

**【模块 4：艺术风格规范 (ART STYLE - Unified PC-98 Cel-Shading)】**
Retro Japanese PC-98 computer game aesthetic fused with anime cel-shading.
1. Bold, distinct black outlines on all edges.
2. Hard-edged block shading across ALL views to show weight and depth. High contrast retro anime look. No soft gradients.
**Color Palette:** [在此处定义配色，例如：Off-white heavy armor, intense glowing blue energy elements, dark metallic grey mechanical parts.]`

---

### 📖 模块结构详解指南

为了让你用好这个工具，了解每个部分都在对 AI 做什么是非常重要的。

### 【模块 1：布局与格式硬性约束】(固定不变)

- **功能**：这是 Prompt 的“地基”和“宪法”。它强制 AI 在开始绘画之前先设定好画布规则。
- **关键点**：
    - `precise 2x2 GRID` 和 `Aspect Ratio 1:1`：确保了你想要的四格正方形构图。
    - `MUST NOT OVERLAP`：防止四个视图挤在一起粘连。
    - `PURE SOLID WHITE Background`：确保背景纯白，方便你后期抠图。
- **使用建议**：**永远不要修改这一段**，除非你想改变输出的基本格式（比如变成横向排列）。

### 【模块 2：视角协议】(固定不变)

- **功能**：明确告诉 AI 那四个格子里分别应该画什么视角，以及它们的排列顺序。
- **关键点**：它强调了 `exact same object`（完全相同的物体）和 `structural consistency`（结构一致性），这是保证三视图可用的核心指令。
- **使用建议**：通常不需要修改。

### 【模块 3：主体核心描述】(⭐️核心可变区域⭐️)

- **功能**：这是你发挥创意的地方，告诉 AI 你要画什么。
- **关键点**：
    - **CRITICAL DESIGN NOTE (否定约束)**：非常重要！用来打破 AI 的刻板印象（比如把激光画成大炮）。一定要明确告诉它**“不是什么”**。
    - **整体风格句**：奠定物体的级别（初级/高级）和体量感（轻型/重型）。
    - **Key Features (关键特征列表)**：不要写大段的散文。用列表项清晰地描述 3-5 个关键的视觉组件（如：透镜、散热器、底座、线缆）。结构化的描述能让 AI 更准确地理解复杂的机械结构。
- **使用建议**：每次生成新资产时，集中精力改写这一部分。描述越具体、越结构化，效果越好。

### 【模块 4：艺术风格规范】(半固定)

- **功能**：这是我们调试多次定下来的“PC-98 + 赛璐璐”画风滤镜。
- **关键点**：`Bold black outlines`（粗黑边）和 `Hard-edged block shading`（硬边色块阴影）是这个风格的灵魂。
- **使用建议**：
    - 风格描述部分通常不需要动，以保持全套资产的统一性。
    - **Color Palette (配色)**：你可以根据不同的阵营或装备类型修改配色方案（例如：把蓝白配色改成红黑配色）。

希望这个结构化工具能帮助你高效地建立起你的游戏素材库！
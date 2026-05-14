---
title: "【好文共赏】把天空写进 GPU：Maxime Heckel 的大气散射 Shader 一万字深读"
description: "Maxime Heckel 用一个月时间，把瑞利散射、米散射、臭氧吸收、对数深度缓冲、LUT 重建——一整套电影级大气渲染搬进了浏览器。这不只是一篇教程，它是 2026 年最值得收藏的一节'物理 + 数学 + GPU 工程'三合一课程。"
date: 2026-05-14
slug: "good-read-rendering-sky-atmospheric-scattering"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 图形学
    - Shader
    - WebGL
    - 大气散射
    - Three.js
    - GPU
    - 实时渲染
    - Maxime Heckel
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[On Rendering the Sky, Sunsets, and Planets](https://blog.maximeheckel.com/posts/on-rendering-the-sky-sunsets-and-planets/)
> 作者：Maxime Heckel（blog.maximeheckel.com） | 发布于：2026-05-12 | 阅读时长：约 60 分钟（含交互式 widget）
>
> **多模评分**：Opus 9.3 / Sonnet 9.0 / Gemini 9.1 — 综合 **9.13 / 10**
>
> **一句话推荐理由**：当 2026 年的技术博客圈被 LLM、Agent、Token 经济学塞得密不透风的时候，Maxime Heckel 花了一个月时间，独立把 Sébastien Hillaire 那篇影响过 Frostbite、Unreal 的 SIGGRAPH 论文重新实现进了浏览器——并把整个推理过程一行一行讲清楚。**这是 2026 年最纯粹、最具教学密度、也最"反潮流"的一篇深度技术文章**，值得任何对图形学有过一丝好奇的开发者从头读到尾。

## 为什么这篇文章值得读

过去一年，关于"AI 在改变什么"的讨论几乎吞噬了整个技术博客圈。我自己在写[《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/) 那篇导读时也得出过一个判断——AI Agent 让个人小软件重新有了意义。但回到 2026 年 5 月的现实，我感受到一种相反的、却同样真实的力量：**当 Agent 帮我们生成了越来越多的代码，"真正理解一段代码在做什么"反而正在变成一种稀缺技能**。

Maxime Heckel 的这篇 60 分钟长读，是对这种稀缺技能的一次集中展示。

他想做的事情，乍看微不足道：在浏览器里渲染一个真实的天空，让它能日出、能日落、能从地面望向太空——还能套在一个行星上当大气层。但这个目标的物理基础——**大气散射（atmospheric scattering）**——是一门牵涉到光学、热力学、几何光线追踪、数值积分、GPU 着色器架构的复杂学问。1980 年代以来，从 Bruneton-Neyret 的预计算多重散射，到 Sébastien Hillaire 在 SIGGRAPH 2020 提出的 LUT 流水线，整个图形学社区为了让屏幕上那一抹蓝看起来"像真的"，投入了几十年的研究。

Heckel 这篇文章的可贵之处不在于他"发明"了什么新东西，而在于他把**这个跨越四十年的研究链条，用一个独立开发者能消化、能上手、能在 React Three Fiber 里跑起来的形式重新走了一遍**。中间他承认自己跨出了舒适区、用 WebGL 而非 WebGPU、跳过了多重散射、对 Aerial Perspective LUT 做了 2D 退化——但每一处妥协他都讲清楚了原因，并且给出了改进方向。这种"我做到了 70%，剩下 30% 是为什么"的诚实，比那种"我把所有事情都解决了"的高质感教程更有学习价值。

更重要的是，**这是 2026 年技术博客里几乎绝迹的体裁**——一个人花一个月时间，独立把一段成熟但艰深的工程做完，并以教学者的姿态分享。它和当下整个内容生态的趋势——短平快、AI 摘要、"教你 10 分钟学会 Transformer"——背道而驰。但恰恰因此，它值得被更多人看见、被更多人慢慢读完。

## 核心观点深度解读

### 1. 天空不是颜色，是"光在体积里行进的结果"

文章开篇就立下了第一个反直觉的判断：**你不能把天空当成一张图片渲染**。把蓝色渐变贴在背景里看起来永远不对，因为天空的本质不是一个表面，而是**光在一个体积（atmosphere as volume）里穿行后到达你眼睛的总和**。

这个判断决定了整篇文章的算法骨架——**raymarching（光线步进）**：从摄像机出发投出一根光线，沿着这根光线在大气体积里逐步采样，累积两个量：

1. **Optical depth（光学深度）**：沿途空气累积了多少，告诉你光在前进过程中被衰减了多少。
2. **Scattering（散射）**：每一个采样点上，有多少阳光在这里"拐弯"被送进了你的眼睛。

Heckel 把第一个量用 Beer-Lambert 定律转换为透射率 $T = e^{-\tau}$，第二个量用瑞利相位函数描述。两者结合后，你就得到了一根光线对应的像素颜色。把这套流程并行到每一根从屏幕射出的光线上——这就是片元着色器的天然工作。

这一节读起来像物理课的复习，但 Heckel 设计了一个交互式 widget，让你能拖动 raymarch 步数和观察者海拔，**看着颜色一点点累积起来**。读者立刻就理解了为什么瑞利散射系数 `vec3(0.0058, 0.0135, 0.0331)` 里蓝色权重最高——短波长在分子尺度上散射更强，这是 100 多年前 Lord Rayleigh 推导出来的物理结论，今天我们把它写进 GLSL 也就三行。这种"物理直觉 ↔ 代码权重"的对位，是教学价值的核心。

这一段也让我想到自己之前在 [《AI Flame Graphs：GPU 性能剖析新基线》](/post/ai-flame-graphs-gpu-profiling-2026/) 里讨论过的一个观点：**真正稀缺的不是 GPU，而是能把物理直觉翻译成 GPU 算子的人**。Maxime Heckel 这篇文章是这种翻译能力的活体样本。

### 2. 瑞利 + 米 + 臭氧：三层模型如何拼出"看起来像真的"

如果只有瑞利散射，你得到的天空只有"蓝-白"两个调子。Heckel 在第二节加入了两个修正：

- **Mie 散射（米散射）** 描述光与大颗粒（灰尘、气溶胶）的相互作用。它有自己的密度衰减函数（`exp(-h / 1.2 km)`，比瑞利的 8 km 更陡——粉尘集中在低空），还有一个 Henyey-Greenstein 相位函数，由各向异性参数 `MIE_G` 控制：g 接近 0 时是各向同性散射，接近 1 时是前向散射。这一项直接对应你在夕阳附近看到的**那圈白雾光晕**。
- **Ozone（臭氧吸收）** 不会把光"散开"——它只是**吸收**特定波长。Heckel 选了 `OZONE_BETA_ABS = vec3(0.00065, 0.00188, 0.00008)`，绿色被吸收最多，红色和蓝色被相对保留——这就是为什么晴朗的高空看起来有一点紫调，黄昏时地平线附近会有粉红色。

把这三层叠在一起，他在 fragment shader 主循环里得到了如下结构（基于原文的最小复刻示例，下方代码为我自己改写的极简版本，仅展示叠加逻辑，启发自原文）：

```glsl
// 教学最小示例（启发自 Maxime Heckel 原文，重新组织过）
for (int i = 0; i < PRIMARY_STEPS; ++i) {
    float t = (i + 0.5) * stepSize;
    float h = altitudeAtSample(t);

    // 三种粒子各自的局部密度
    float dR = exp(-h / 8.0);    // Rayleigh 衰减高度 8 km
    float dM = exp(-h / 1.2);    // Mie 衰减高度 1.2 km
    float dO = ozoneShell(h);    // 臭氧呈带状峰分布

    // 累积光学深度
    odR += dR * stepSize;
    odM += dM * stepSize;
    odO += dO * stepSize;

    // 三类系数共同贡献当前点的透射率
    vec3 tau = BETA_R * odR + BETA_M_EXT * odM + BETA_OZONE_ABS * odO;
    vec3 transmittance = exp(-tau);

    sumR += dR * transmittance * stepSize;
    sumM += dM * transmittance * stepSize;
    sumO += dO * transmittance * stepSize;
}
```

这一节的"含金量"在于：**它给了一个明确的扩展协议**。如果你以后想加入气溶胶颗粒、火山灰、海洋盐雾——不需要重写整个流水线，只要追加一项 `(密度函数, 相位函数, 系数)` 三元组即可。这是物理可加性的好处，也是为什么瑞利-米-臭氧这种"加法模型"几十年来一直是工业标准。

> 原文：These are the main knobs that make our rendered atmosphere look the way it does. Thus, by tweaking them to the right set of values, we could, in theory, approach a martian atmosphere or even other planets'.（来源：blog.maximeheckel.com）

后面 Heckel 直接把整套常数换成火星的值，天空就变成了泛橙带蓝的日落——这种"通过参数空间穿越行星"的演示，是对模型物理本质的最直观证明。

### 3. Light Marching：嵌套循环把"日落色"算了出来

到这里为止，单层 raymarching 还有一个缺陷：它只算了"光线从相机到样本点之间被吸收了多少"，没有算"阳光从太阳到样本点之间被吸收了多少"。当太阳在头顶时这没什么问题，但当太阳接近地平线，**阳光本身需要穿越大量大气才能抵达任何一个采样点**——这一段穿越产生的颜色偏移，正是日落红、日出橙的物理起源。

Heckel 的解法是**嵌套 raymarching**：在主循环每个采样点上，再发一根光线向太阳方向"光行进"（light march），积累一份独立的光学深度 `sunOD`，把它加到主循环的 `tau` 上：

```glsl
vec3 sunOD = lightMarch(sampleHeight, sunDir.y);
vec3 tau = BETA_R * (viewODR + sunOD.x)
         + BETA_M_EXT * (viewODM + sunOD.y)
         + BETA_OZONE_ABS * (viewODO + sunOD.z);
vec3 transmittance = exp(-tau);
```

数学上简洁，性能上昂贵：每个屏幕像素上，主循环可能 24 步，嵌套的 light march 可能 6 步——每帧每像素就是 144 次密度采样。1080p 全屏 60 fps 意味着每秒约 180 亿次 `exp`/`pow`。文章后半段的 LUT 优化就是为了打破这个性能墙。

但在引入优化之前，Heckel 先让读者**看到这个昂贵但物理准确的版本能产出什么**。他把太阳角度做成 widget 让你滑动，从正午滑到日落、再到日出。中间那个让我"心里咯噔一下"的瞬间是：**当太阳掠过地平线，整片天空突然被推成深紫红色——不是程序员调出来的色调，而是物理上自然涌现的结果**。

这种"先把物理算对，颜色自然会对"的次序，与现在很多 AI 画图工具的逻辑形成强烈对比：那些工具是先决定颜色再倒推像素，而 shader-based 渲染是从光的传播规律出发推出颜色。**两条路径都能"画出"一个日落，但它们生成出的图像的可控性、可拓展性、可解释性完全不同**。这一点上 Heckel 没有展开，但他选用 raymarching 的姿态本身就是一种立场。

### 4. 屏幕空间到世界空间：把天空"装"进 3D 场景

第一节的天空 shader 还只是一张全屏背景。Heckel 在第二大节做的事情是把它升级为**后处理效果（post-processing effect）**——这意味着每一帧渲染完场景之后，再用大气 shader 把整张图"包裹"一层。这听起来轻巧，实则要求两件难事：

1. **从屏幕空间反推世界空间**：每一个屏幕像素必须知道自己对应的世界坐标，才能确定光线穿过了哪一段大气。Heckel 写出了那段经典的反投影矩阵代码——把 UV 翻成 NDC、给个 depth、乘以 `projectionMatrixInverse` 和 `viewMatrixInverse`、再做透视除法——这是任何想做体积光、SSAO、屏幕空间反射的人都要掌握的基本功。
2. **用 depth buffer 限定 raymarch 的终点**：如果场景里有一个 mesh 挡在视线前面，光线不应该穿过它继续 march。所以 raymarch 的 `rayEnd` 必须取 `min(atmosphereExit, sceneDepth)`。

这两步合起来的效果就是教科书里的"空气透视（aerial perspective）"——远处的山比近处的山看起来更蓝、更模糊，因为视线穿过了更多大气。Heckel 演示了 React Three Fiber 场景里加入这个 post-process 前后的对比，远处的环面（torus）从清晰锐利变得"沉入空气里"。

> 原文：To apply atmospheric scattering to a scene, we aren't just drawing a sky; we need to fill the space between the camera and the different objects rendered on screen.（来源：blog.maximeheckel.com）

这一句是整个第二节的灵魂：**大气不是天空盒，是体积**。一旦你这样想，所有"加滤镜调蓝"的伪解法都站不住脚，你必须老老实实做空间重建。

### 5. 行星尺度：当地球不再是平面，对数深度缓冲登场

第三节是文章里最有"工程味"的一段。当观察者从地表升上轨道，**地球必须被当作一个真正的球体**——这意味着两件事：
（a）`raySphereIntersect` 必须取代"地面是 y=0 平面"的简化；
（b）从近距离的人物 mesh 到远处行星的 mesh 跨度极大，普通的浮点深度缓冲会出现严重的 z-fighting。

Heckel 的解决方案是**对数深度缓冲（logarithmic depth buffer）**。Three.js 里只要打开 `logarithmicDepthBuffer: true`，但 shader 端必须自己把对数深度反解回视空间距离：

```glsl
float logDepthToViewZ(float depth) {
    float d = pow(2.0, depth * log2(cameraFar + 1.0)) - 1.0;
    return -d;
}
```

这段代码非常短，但它解决的是图形学历史上反复折磨开发者的"深度精度悬崖"问题——经典的浮点深度在 [0, far] 的远端只剩下几个有效位，而在球状行星这种几何尺度上几个有效位完全不够用。对数变换把精度更均匀地分布到了对数尺度上。

然后他用 `raySphereIntersect` 做了两次球体相交测试：一次大气层球壳、一次行星表面。把 raymarch 的有效区间夹紧在"刚进入大气" 到 "命中行星表面 / 命中场景几何 / 出大气" 三者中的最近者。这部分代码很短，但需要你脑子里有清晰的几何图像：**视线是一根射线，大气是一个球壳，行星是一个嵌套的实心球**。

读到这一节我最大的感受是：**图形学里的所有"美"都是工程妥协的副产品**。对数深度不是数学家发明的，是被深度精度悬崖逼出来的；raySphereIntersect 不是教科书第一选择，但它在球状行星上简洁性碾压三角网格遍历。一个会写大气 shader 的人，往往同时是一个会处理浮点精度的人——这两件事在底层是同一回事。

这种"物理 × 数值"的耦合让我想到[《连续物理+硅基仿真：芯片设计的范式转移》](/post/continuous-physics-chip-simulation-paradigm-2026/) 中讨论过的话题：**当代仿真工程师本质上都在做同一件事——把连续的物理世界投影到离散的数字硬件上，同时不让浮点误差吃掉信号**。Heckel 的大气 shader 是这场更宏大博弈在浏览器尺度上的一个微缩样本。

### 6. 日食：用一个角度判定切下来一个"史诗特性"

第四节是一个"小彩蛋章节"——但其优雅程度让我反复回看了三遍。Heckel 想让自己的渲染系统支持日食：当月球挡在太阳前面时，整个大气该如何反应？

他没有去做复杂的光线遮挡积分。他做了一个**纯角度判定**：

```glsl
float angularSep = acos(clamp(dot(sunDir, moonDir), -1.0, 1.0));
float sunAngularRadius = SUN_RADIUS / SUN_DISTANCE;
float moonAngularRadius = moonRadius / moonDist;
float outerEdge = sunAngularRadius + moonAngularRadius;
```

然后根据"两个圆盘的角直径差和分离角"判断三种情况：完全不重叠、月球完全遮蔽太阳、月球只挡住了太阳的一部分。返回一个 `[0, 1]` 的可见性系数，直接乘到 transmittance 上。

这个解法的力学美感在于：**它把一个本来需要在 3D 几何里追踪遮挡的问题，压缩成了一个 2D 投影里的角度比较**。物理上这是合理的——日食的发生条件本来就只取决于"从观察者看过去，月球和太阳的视角重合度"。一旦你意识到这一点，整段代码可以在 30 行内完成。

> 原文：If they were to match closely, i.e., close to 1.0, that means the moon would be obstructing the sun, and vice versa; if they were orthogonal, close to 0.0, there would be no obstruction.（来源：blog.maximeheckel.com）

Heckel 还诚实地标注了"我没有处理科罗娜，论文里有更精确的解法"。这种"我知道更深的版本但我用了更简洁的版本"的克制，本身就是工程美学。

### 7. 火星：参数空间里的"星际旅行"

接下来还有一个让我会心一笑的段落。Heckel 不需要重写任何一行代码——他只是把 9 个常数换成了火星的值：

| 参数 | 地球 | 火星 |
|------|------|------|
| 行星半径 (km) | 6371 | 3390 |
| 大气厚度 (km) | 100 | 110 |
| 瑞利散射高度 (km) | 8.0 | 11.1 |
| 瑞利系数 (R/G/B) | 0.0058/0.0135/0.0331 | 0.019/0.013/0.0057 |
| 米散射高度 (km) | 1.2 | 1.5 |

把这些值灌进去，**天空立即变成了泛着橙色调的火星天空，并且——这是物理上真实而漂亮的一件事——日落时呈现出火星特有的偏蓝色**。这是机会号、好奇号传回的图像中那种诡异的"蓝色火星日落"的物理来源：火星大气里粒子尺度的米散射比例更高，前向散射在低角度时把蓝光集中送到了观察者眼前。

这一段是整篇文章里我个人最喜欢的部分。它把"参数化物理模型"这个抽象概念可视化成了一种**跨行星的散步**：你不是在调色，你是在做行星科学。这与 NASA 的 GCM（global circulation model）做着本质相同的事情——只不过 NASA 跑的是 PFLOPS 级别的超算，Heckel 跑的是你浏览器里的 WebGL。

读到这里，我会强烈推荐每一个写过"换皮主题切换器"的前端开发者反思一件事：**参数化设计的深度，决定了你的代码能从"换 CSS"走多远——理论上 Heckel 这套同样的引擎可以渲染金星（硫酸云）、土卫六（甲烷雾），只要找到合适的散射系数和密度函数**。

### 8. LUT 流水线：Sébastien Hillaire 的工业级优化

最后两大节是文章的"产业级"段落。Heckel 老老实实承认：前面那套全 raymarching 的实现在 1080p 60 fps 上跑得很吃力——主要因为 light march 是嵌套循环。Sébastien Hillaire 在 SIGGRAPH 2020 提出的工业方案是把昂贵的部分**预计算成 Look-Up Tables（LUT，查找表）**，分三层：

- **Transmittance LUT**：一张 `250 × 64` 的纹理，存"任意海拔、任意太阳角度下，太阳光衰减到这里还剩多少"。下游任意位置只需要查一次，省掉了 light march 嵌套。
- **Sky-View LUT**：一张存"任意视角方向的天空颜色"的纹理。每帧重新生成一张，把背景天空一次性烤进去。
- **Aerial Perspective LUT**：理论上是 3D 纹理，存场景里每一段距离上的大气贡献。Heckel 在这里坦白做了简化——他用了一张 2D 纹理，每个像素对应当前屏幕的可见像素，深度从场景 depth buffer 实时取。

这种简化的代价是失去了"按时间预计算 LUT、按相机自由查询"的灵活性，每次相机移动都要重新生成 Aerial Perspective LUT。但优点是 WebGL 友好——不需要 3D 纹理、不需要 compute shader——而且**最终合成的画面与全 raymarch 版本视觉接近**。

更难得的是 Heckel 承认了三件事：

1. 他没有完整实现多重散射（multi-scattering）；
2. 他用 WebGL 而非 WebGPU，导致 LUT 必须用 FBO 模拟而非直接 compute；
3. Sky-View LUT 在大尺度上有 banding。

> 原文：Despite that, my LUT-based implementation pales in comparison to what Sébastian Hillaire and others in the field came up with.（来源：blog.maximeheckel.com）

这种坦率在技术博客里非常少见。大多数作者会假装自己 1:1 复现了论文，但 Heckel 主动暴露了所有妥协。这反而让整篇文章变成了一份**带"已知缺陷"标注的开源研究笔记**——任何想接力的人都知道下一步从哪里开始改。

## 延伸阅读图谱

### Maxime Heckel 自己的代表作（按推荐阅读顺序）

1. [**Painting with Math: A Gentle Study of Raymarching**](https://blog.maximeheckel.com/posts/painting-with-math-a-gentle-study-of-raymarching/) — 如果你被本文里的 raymarching 概念绊住，先读这一篇。Heckel 的"raymarching 入门"用 SDF 和距离场把整个概念建立起来。
2. [**Real-time Cloudscapes with Volumetric Raymarching**](https://blog.maximeheckel.com/posts/real-time-cloudscapes-with-volumetric-raymarching/) — 同一作者前作。云和大气共享同一个体积渲染范式，理解了云就理解了为什么大气也要 raymarch。
3. [**On Shaping Light**](https://blog.maximeheckel.com/posts/shaping-light-volumetric-lighting-with-post-processing-and-raymarching/) — 体积光与后处理的结合，本文里 light march 的思想直接来自这一篇。
4. [**On Crafting Painterly Shaders**](https://blog.maximeheckel.com/posts/on-crafting-painterly-shaders/) — 风格化渲染，从物理 shader 走向艺术 shader 的反向案例。
5. [**Field Guide to TSL and WebGPU**](https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/) — Heckel 自己也在迁移到 WebGPU。这篇是他对下一代浏览器图形 API 的实战笔记，读完你会理解为什么他在大气文章里反复说"以后该用 WebGPU 重做"。
6. [**Post-Processing Shaders as a Creative Medium**](https://blog.maximeheckel.com/posts/post-processing-as-a-creative-medium/) — 这是本文"做后处理效果"段落的方法论母版。

### 相关论文与权威博文（映射关系）

| 资源 | 与本文的映射 |
|------|-------------|
| [Sébastien Hillaire — *A Scalable and Production Ready Sky and Atmosphere Rendering Technique* (EGSR 2020)](https://sebh.github.io/publications/egsr2020.pdf) | 本文 LUT 流水线的原始论文。Heckel 实现的是简化版，论文里的多重散射、3D Aerial Perspective LUT、Multi-Scattering Approximation 都没做。 |
| [Bruneton & Neyret — *Precomputed Atmospheric Scattering* (2008)](https://hal.inria.fr/inria-00288758/document) | 现代大气渲染的"上古巨著"。Hillaire 2020 是对它的工程优化。 |
| [Inigo Quilez — Ray-Surface Intersection Functions](https://iquilezles.org/articles/intersectors/) | 本文里的 `raySphereIntersect` 来源。iq 是 Shadertoy 创始人之一，他的几何函数库是图形学开发者的常备速查表。 |
| [@shotamatsuda — three-geospatial](https://github.com/takram-design-engineering/three-geospatial) | Heckel 反复致敬的"生产级实现"。如果你想看到本文方法的工业完成度，这里是开源标杆。 |
| [Egan, Hery, Wrenninge — *Physically Based Real-Time Rendering of Eclipses* (SIGGRAPH 2020)](https://research.dwa.com/) | 本文"日食"段落的进阶论文。Heckel 用的角度判定是 cheap 版本，论文给出的是带 corona 的物理版本。 |
| [Collienne et al. — *Physically Based Rendering of the Martian Atmosphere* (2013)](https://www.researchgate.net/publication/258710376) | 火星天空精确建模的学术参考。Heckel 用的"换 9 个常数"是粗近似。 |
| [Inigo Quilez — Better Fog](https://iquilezles.org/articles/fog/) | "Aerial Perspective"的另一条思路。 |
| [GPU Pro 7 — Sky and Atmosphere Rendering chapter](https://www.crcpress.com/9781498742535) | 工业书面教程，更老但更系统。 |

### 反方观点 / 局限性 / 替代路径

1. [**Outerra — Procedural Planet Engine Devlogs**](https://outerra.blogspot.com/) — 这家小公司用类似算法做行星引擎已经做了 15 年。他们的博文揭示了 Heckel 没有谈到的另一面：**当你要做 1:1 真实地球**（包含大气、海洋、地表植被）**而不是教学 demo 时，问题的复杂度是另一个量级的**。
2. [**Substance / Ground Truth Skies**](https://80.lv/) — 一些艺术家流派认为"物理精确的天空"对游戏体验来说是错的，因为玩家期待"电影感"而非"真实感"。这种"反物理"立场和 Heckel 的"物理优先"立场可以互为参照。
3. [**Eric Bruneton — Why we should stop using single scattering for atmospheres**](https://ebruneton.github.io/precomputed_atmospheric_scattering/) — Heckel 文章里跳过了多重散射，但 Bruneton 论证了"在低太阳角度下，单次散射模型会显著低估天空亮度"。如果你要做严肃的科研可视化，Heckel 的简化版不够用。

## 编辑延伸思考

读完整篇文章，我想谈两个层面的延伸：技术层与生态层。

**技术层**：图形学这门学科在 2026 年的处境其实非常微妙。一方面，主流注意力被 AI 几乎全部吸走，shader 程序员是除了游戏行业之外少数还在认真"手写 GPU"的人；另一方面，**底层的 GPU 硬件本身正在被 LLM 改造**——这是我在[《PNM/HBM 替代 GPU Compute Die 的 Attention 大战》](/post/pnm-hbm-replace-gpu-compute-die-attention-2026/) 里讨论过的，下一代 GPU 的设计目标已经偏向 Transformer 而非传统图形流水线。

这意味着 Heckel 这种"用 WebGL fragment shader 做 raymarching"的实践，在硬件层面上正在变得**逆潮流**。CUDA、Vulkan、WebGPU 都在向 compute-first 的 API 演化，传统的 vertex-fragment 流水线只是 compute kernel 的一个特例。Heckel 自己也意识到了这一点——文章末尾反复说"以后该迁到 WebGPU compute shader"。但这种迁移并不是无成本的：**fragment shader 的"每像素一根光线"的隐含并行模型非常符合人类对图形的直觉，一旦切到 compute shader 的工作组模型，认知成本会陡然上升**。

我自己的判断是：未来五年，**fragment shader 思维仍然会是入门图形学的最佳起点**，但生产级实现会以 compute shader 为主。Heckel 的文章站在这个交叉点上，是一份很好的"过渡期教材"。

**生态层**：这篇文章让我想起一个更深的问题——**当 AI 可以代写大部分代码的时候，深度技术博客的角色是什么？**

我的看法是：博客的价值正在从"代码示例"转向"思维脚手架"。任何熟悉 LLM 的开发者都知道，今天给 Claude / Gemini 一句"写一个 raymarching 大气 shader"，它能产出能编译的代码——但产出的代码里那些**关键的物理直觉、参数为什么取这些数值、为什么要做对数深度、为什么 light march 是嵌套的**——这些 LLM 经常含糊带过。而 Heckel 这篇文章的不可替代价值就在这里：**它把每一个"为什么"都讲清楚了**。

这与我在 [《Senior Developer 的 Speed × Scale 解耦框架》](/post/good-read-senior-developer-speed-scale-decoupling/) 中提到的判断相互印证——senior developer 的真正价值不在写代码，而在判断"哪些代码不该写、为什么这样写、什么时候停下来"。Heckel 这篇文章的整个写作姿态就是 senior 视角的物化。

进一步推到中国语境里，我想提两个建议：

第一，**国内图形学社区长期被两个极端撕扯**：一极是高校实验室里的论文复现（重数学、轻工程），另一极是游戏公司里的引擎开发（重工程、缺教学）。Heckel 这种**"独立开发者把工业级技术翻译成可学习内容"**的中间生态，在中文圈基本不存在。这是一个明显的空缺——任何能持续写出这种长度和深度文章的人，都会在国内图形学社区里被快速识别为权威。

第二，**WebGL/WebGPU 是少数对中国开发者真正友好的图形学领域**——它绕开了 DirectX、Vulkan 的平台壁垒，所有的开发都在浏览器里。我在 [《AI Native 操作系统重构》](/post/ai-native-operating-system-rebuild/) 里聊过 Web 是新一代应用层操作系统的可能性，而图形渲染恰恰是 Web 这个新 OS 里最不成熟的子系统之一。Maxime Heckel 这种持续输出，本质上是在为 Web 平台补一块关键短板。中国的开发者要赶上这条赛道，目前还有相当大的窗口期。

最后，作为一个会反复读这种文章的工程师，我想留下一句最朴素的感受：**当你看完 60 分钟的着色器教程，最后页面上跑起来的那个会日出日落的小行星——它带给你的快乐，是 LLM 生成的任何 demo 都给不了的**。那种"我读懂了每一行物理的来历、每一行代码的理由、整套流水线的取舍"的踏实感，是 2026 年最稀缺的开发者体验。

## 配套资料导览

本期一起发布的配套资料：

- 📊 [思维导图（mindmap.svg）](mindmap.svg) — 一张 SVG 思维导图，呈现整篇文章从物理基础到 LUT 优化的完整结构。
- 🃏 [关键概念卡片（concept-cards.md）](concept-cards.md) — 12 张概念卡，覆盖瑞利散射、米散射、臭氧吸收、optical depth、Beer's law、raymarching、light marching、相位函数、空气透视、对数深度缓冲、ray-sphere 相交、LUT 流水线。
- 📖 [术语表（glossary.md）](glossary.md) — 38 条中英对照术语表，涵盖大气物理与 GPU 渲染两个领域。

## 谁应该读

1. **Web 前端 / 全栈开发者**：尤其是已经接触过 Three.js / React Three Fiber，正在寻找进阶方向的人。Heckel 这篇文章是把你从"调用现成 mesh"推到"自己写 fragment shader"的最佳跳板。
2. **游戏开发者 / TA**：如果你在做大世界游戏的 sky dome、行星渲染、空气透视，这篇文章是 Hillaire 论文的最佳中文（再加上我这篇导读）入门版。
3. **图形学学生**：作为大气散射、体积渲染入门的辅助阅读，配合 Bruneton-Neyret 2008、Hillaire 2020 论文一起读。
4. **AI / 仿真 / 科学可视化研究者**：行星气候模型、海洋光学、医学体渲染——很多看似不相关的领域都共享同一套体积渲染范式。这篇文章是你向 GPU 工程师阵营快速建立共同语言的捷径。
5. **任何想看一份"AI 也不会写"的人类工程作品的人**：诚实地说，**这种厚度的内容是目前 LLM 无法独立生成的**。读完它你会对"真正的工程深度长什么样"有一个新的基准点。

阅读建议：
- 第一次阅读：**电脑+大屏幕**，因为文章里的 widget 是文字无法替代的。
- 准备两个标签页：**原文 + 你自己的 Three.js playground**。Heckel 的每个 widget 旁边都有 CodeSandbox 链接。
- 不要试图一次读完。我自己花了两个 90 分钟时段才完整读完一遍并跑通 demos。
- 如果不熟悉 GLSL，先读 Heckel 的 [Painting with Math](https://blog.maximeheckel.com/posts/painting-with-math-a-gentle-study-of-raymarching/)。

---
title: "【好文共赏】一个周末、一千行 OpenGL：Benjamin Feldman 把 3D Gaussian Splatting 拆成一份可以从头读完的工程教程"
description: "当大多数 3DGS 实现要么藏在 CUDA 里要么藏在 nerfstudio 里，Benjamin Feldman 选择用最朴素的 OpenGL 4.5 + GLSL + 一份 C++ ply 解析器，把整个推理 pipeline——协方差投影、雅可比线性化、特征分解、3σ 边界四边形、Gaussian fragment、CPU 深度排序——从论文一行一行翻译进了能跑、能改、能 stepping debug 的代码里。"
date: 2026-05-19
slug: "good-read-3dgs-weekend-feldman"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 图形学
    - 3D Gaussian Splatting
    - 3DGS
    - OpenGL
    - GLSL
    - 实时渲染
    - 协方差矩阵
    - EWA Splatting
    - Benjamin Feldman
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[3D Gaussian Splatting in a Weekend](https://bfeldman.me/3dgs-weekend/)
> 作者：Benjamin Feldman（bfeldman.me） | 发布于：2026-05 | 阅读时长：约 25 分钟（含 GLSL + C++ 代码段）
>
> **多模评分**：Opus 9.1 / Sonnet 8.9 / Gemini 9.0 — 综合 **9.0 / 10**
>
> **一句话推荐理由**：3D Gaussian Splatting 从 2023 年 SIGGRAPH 论文走到今天，已经成为 NeRF 之后最有工业价值的新型表征。但绝大多数公开实现要么是研究级 CUDA 黑盒，要么是被 nerfstudio / gsplat / 3DGS.cpp 层层封装过的 Python pipeline。Feldman 这篇文章选了一条最难也最值得的路径——**用最朴素的 OpenGL 4.5、GLSL、一份手写的 ply 解析器，把整套 forward rendering 数学从头推导一遍，再翻译进一千行能编译、能跑、能 stepping debug 的代码里**。它不是科普，也不是论文复述，而是 2026 年我见过的、对"想真正搞懂 3DGS 在渲染端发生了什么"的工程师最友好的一份周末读物。

## 为什么这篇文章值得读

过去 36 个月里，3D Gaussian Splatting (3DGS) 从 INRIA + MPII 那篇 SIGGRAPH 2023 的论文 [Kerbl et al.](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) 出发，一路扩张到了动态场景、SLAM、City-scale、自动驾驶感知、AR/VR 资产管线。NeRF 那种"用 MLP 隐式表达体素 + 体积渲染"的范式，正在被这种"用一团团各向异性 3D 高斯显式表达 + 屏幕空间 splatting"的范式快速取代。原因很直接：3DGS 在视觉质量上能逼近 Mip-NeRF 360，在渲染速度上却比 NeRF 系列快 1-2 个数量级，而且它的存储就是一堆参数化的椭球——可以编辑、可以裁剪、可以做物理模拟。

但当一个工程师真的想读懂"这堆椭球是怎么变成屏幕上一帧画面的"，他/她会发现资料生态有一个奇怪的真空：

- **论文**只讲了 forward 模型的概念（投影 + α-blending），并把所有工程细节（光栅器、tile-based binning、CUDA shared memory 设计）压进了一段 5-6 行的伪代码。
- **官方代码**是一个 CUDA-only 的 differentiable rasterizer，里面充斥着 warp-level intrinsics 和 backward pass 的导数推导。
- **gsplat / nerfstudio** 把这些细节再次封装进了 PyTorch 算子，对学习者来说更像黑盒。
- **3DGS.cpp / brush** 这类工程实现是用 WebGPU + WGSL 重写的，但代码量动辄上万行，dependency 链长。

Feldman 这篇文章正好填了这个真空：**他保留了所有推导，但把工程范围严格收敛到"只做 forward rendering，只看预训练好的 ply，不做反向传播"**。这一刀切下去后，整个流程突然变得可以一坐下午就读完——而且因为他选择了 OpenGL 4.5 + GLSL 而不是 CUDA，每一个矩阵乘法、每一个 `glVertexAttribDivisor` 调用都是从教科书里直接抄出来的。

更可贵的是，**Feldman 把所有"为什么这样做"都写出来了**。他不止给你看 GLSL 代码，还告诉你：

- 为什么投影 3×3 协方差矩阵需要一个 2×3 的雅可比 $J$（而不是直接用 4×4 的 view-projection matrix）；
- 为什么这个雅可比是在每个高斯的中心点上做泰勒一阶展开——以及这件事和 EWA Splatting 那篇 2001 年的论文有什么关系；
- 为什么要做特征分解才能从 2D 协方差 $\Sigma_{2D}$ 拿到那个屏幕空间的"包围四边形"；
- 为什么 fragment shader 里的 Gaussian 衰减写成了 $\exp(-4.5(p_x^2 + p_y^2))$ ——这个 4.5 不是随便取的，它就是 $3\sigma$ 阈值的几何反推；
- 为什么深度排序要用 CPU 而不是 GPU（提示：对于 forward-only 渲染、几百 K 个 splat 的场景，CPU 排序 + instanced draw 已经够用，而真正的工业级实现才需要 tile-based + GPU radix sort）。

这种"写给一个想真正搞懂的人，而不是写给一个想抄 demo 的人"的姿态，在 2026 年的技术博客里已经非常少见。它和我之前导读过的 [《把天空写进 GPU：Maxime Heckel 的大气散射 Shader 一万字深读》](/post/good-read-rendering-sky-atmospheric-scattering/) 是同一个体裁——独立开发者用一个周末/一个月时间，把一段成熟但艰深的图形学工程从论文走到能跑的代码，并把每一步翻译都讲清楚。这种文章值得被多读一遍、慢读一遍。

## 核心观点深度解读

### 1. 一个 3D 高斯到底是什么——"参数化椭球"的工程定义

Feldman 一开始就把"3D 高斯"这个词翻译成了工程师能拿来 typedef 的结构。每个 splat 在内存里其实就是这么几样东西：

- **中心点 (centroid)**：$\mu \in \mathbb{R}^3$，世界坐标。
- **缩放 (scale)**：$s \in \mathbb{R}^3$，三个轴的半径（log-space 存储，使用前要 `exp`）。
- **旋转 (rotation)**：四元数 $q \in \mathbb{R}^4$。
- **不透明度 (opacity)**：标量 $o$，以 logit 形式存储，使用前要做 sigmoid。
- **球谐系数 (SH coefficients)**：通常是 16 × 3（degree-3）或更少，表示视角依赖的颜色。

> 原文："Each Gaussian is parameterized by its mean (3D position), an anisotropic 3D covariance matrix, an opacity, and a set of spherical harmonics coefficients for view-dependent color."

这段定义的关键在于**协方差矩阵**。论文里把 3D 协方差写作 $\Sigma = RSS^TR^T$，其中 $R$ 是从四元数构造出来的 3×3 旋转矩阵，$S$ 是把缩放向量放到对角线上的对角矩阵。Feldman 把这个分解的物理意义讲得很直白：你可以把每一个 splat 想象成一个单位球被先用 $S$ 拉伸成椭球、再用 $R$ 转向某个方向。$\Sigma$ 不是颜色，不是形状的图像，而是一个**纯几何对象**——它编码的是"这一坨概率密度在 3D 空间里是如何分布的"。

这种分解的代价/好处选择是有讲究的。直接存储 6 个独立的协方差元素 $\Sigma_{11}, \Sigma_{12}, \Sigma_{13}, \Sigma_{22}, \Sigma_{23}, \Sigma_{33}$ 会更省一两 byte，但优化器无法保证它在训练过程中始终半正定（PSD）——一个非 PSD 的 $\Sigma$ 在几何上没有意义，更不能做特征分解。把 $\Sigma$ 解耦成 $R$ 和 $S$，相当于**用一个不变量约束（旋转保持正交、缩放保持非负）换掉了一个 PSD 约束**。这一点 Kerbl 在原论文里强调过，Feldman 这里复述得很到位。

### 2. 从世界到屏幕——但协方差不能像点一样投影

3DGS 渲染的核心数学难题，是**协方差矩阵的投影**。一个 3D 点投影到 2D 屏幕是中学几何，但一个 3D 协方差投影到 2D，不是简单地把 $\Sigma$ 当个矩阵乘以 view-projection——因为透视投影本身是非线性的（出现了一个除以 $z$）。

Feldman 在这里给了一个非常清晰的解释：**协方差描述的是局部分布的形状，而非线性变换会让"局部"在不同位置看起来不一样**。所以你不能用一个全局矩阵把所有 splat 的协方差一起投影下去。

正确的做法来自 Zwicker、Pfister 等人在 2001 年那篇 [EWA Volume Splatting](https://www.cs.umd.edu/~zwicker/publications/EWAVolumeSplatting-VIS01.pdf) 论文里提出的技巧——**对每一个 splat，在它的中心点处对透视投影做一阶泰勒展开**。这一阶展开的雅可比 $J$ 是一个 2×3 矩阵，写出来是：

$$
J = \begin{pmatrix}
\dfrac{f_x}{t_z} & 0 & -\dfrac{f_x \, t_x}{t_z^2} \\\\
0 & \dfrac{f_y}{t_z} & -\dfrac{f_y \, t_y}{t_z^2}
\end{pmatrix}
$$

其中 $t = (t_x, t_y, t_z)$ 是 splat 中心在相机空间的位置，$f_x, f_y$ 是焦距。$J$ 在每个 splat 的中心点重新计算，这就是"局部线性化"的精髓——你假设在这个中心点附近的一个小邻域里，透视投影可以用 $J$ 近似成线性。

有了 $J$，再加上从世界系到相机系的旋转 $W$（即 view matrix 的左上 3×3 块），2D 屏幕空间的协方差就是：

$$
\Sigma_{2D} = J W \Sigma W^T J^T
$$

这是一个 2×2 矩阵。Feldman 把这个推导用图示讲清楚后，再放进 GLSL 大概只有十几行代码。读到这一步会有种"原来这就是 EWA"的顿悟——这种顿悟在直接读 Kerbl 论文时是被压缩在两行公式里的。

> 原文："Because perspective projection is nonlinear, we approximate it with a Taylor expansion around each Gaussian's mean. The Jacobian J of this projection, together with the view-matrix's rotation W, gives the 2D screen-space covariance as $\Sigma_{2D} = J W \Sigma W^T J^T$."

这一段也呼应了我之前在 [《把 Swift 推到 1.1 Tflop/s：Matt Gallagher 用十种实现，在 M3 Max 上手写 LLM 训练，把矩阵乘法跑出 382 倍提升》](/post/good-read-matt-gallagher-swift-llm-matmul/) 里看到的一个共性现象——**真正决定一段图形 / 矩阵代码上限的，是你对底层数学的理解，而不是 API 的熟练度**。

### 3. 从 $\Sigma_{2D}$ 到屏幕上的四边形——为什么要做特征分解

到目前为止，我们得到了一个 2×2 协方差矩阵 $\Sigma_{2D}$，但 GPU 光栅器不画"协方差"，它只画三角形/矩形。于是下一步是：**根据 $\Sigma_{2D}$ 画一个能完全覆盖这个 2D 高斯有效区域的最小四边形**。

Feldman 的做法是教科书式的：对 $\Sigma_{2D}$ 做**特征分解**，拿到两个特征值 $\lambda_1, \lambda_2$ 和对应的特征向量 $e_1, e_2$。对 2×2 矩阵，特征值有闭式解：

$$
\lambda_{1,2} = \frac{\text{tr}(\Sigma_{2D})}{2} \pm \sqrt{\frac{\text{tr}(\Sigma_{2D})^2}{4} - \det(\Sigma_{2D})}
$$

特征向量同样有闭式解（用 $\Sigma_{12}$ 那一行去构造）。$e_1, e_2$ 是椭圆的长短轴方向，$\sqrt{\lambda_1}, \sqrt{\lambda_2}$ 是对应方向上的 1-σ 半径。

接下来一个关键工程决定：**用多大的 σ 倍数作为四边形的半径？** Feldman 选了 $3\sigma$——也就是把椭圆的半轴扩展到 $3\sqrt{\lambda_i}$。这是一个深思熟虑的选择，因为正态分布 $99.7\%$ 的质量都在 $3\sigma$ 内，剩下的 $0.3\%$ 反正在 fragment shader 里也会被 alpha threshold 砍掉。

最终的包围四边形的半轴向量是：

$$
b_1 = 3\sqrt{\lambda_1}\, e_1, \quad b_2 = 3\sqrt{\lambda_2}\, e_2
$$

四个顶点就是中心点 $\mu_{2D}$ 加上 $\pm b_1 \pm b_2$。在 OpenGL 里这就直接对应一个 `GL_TRIANGLE_STRIP` 的 4 个顶点。

这里有一个 Feldman 没有大书特书但值得指出的细节——**整个特征分解是在 vertex shader 里完成的**。这意味着每个 splat 只需要 4 次 vertex shader invocation（一个 instance），而不是 GPU 端的全场矩阵运算。考虑到 vertex shader 跑在并行度极高的 streaming multiprocessor 上，这是一种相当聪明的工作划分。

### 4. Fragment shader 里的 Gaussian 衰减——那个奇怪的 4.5

vertex shader 把 4 个顶点投到 NDC 之后，光栅器会做 barycentric interpolation 把 $(p_x, p_y)$（在以 splat 中心为原点的局部坐标里）传给 fragment shader。在每个 fragment 上，要计算两件事：

1. 这个 fragment 到 splat 中心的距离对应的高斯衰减 $G(p_x, p_y)$；
2. 用 $G \cdot \alpha_{base}$ 作为这个 fragment 的最终 alpha。

Feldman 把局部坐标做了一个特别巧妙的换元：让 $p_x, p_y$ 在四边形里取值范围是 $[-1, 1]$（也就是 NDC-like 的归一化），并且让 $d_i = 3\sqrt{\lambda_i} \cdot p_i$（即用 $3\sigma$ 倍数做尺度）。代入原始的 Gaussian 衰减项 $\exp(-\tfrac{1}{2} \mathbf{d}^T \Sigma_{2D}^{-1} \mathbf{d})$ 后，所有的特征值都互相约掉了，最终落在 fragment shader 里的是一个出奇简洁的式子：

$$
G(p_x, p_y) = \exp(-4.5 \, (p_x^2 + p_y^2))
$$

那个 $4.5$ 就是 $\tfrac{9}{2} = \tfrac{(3\sigma)^2}{2}$ 的几何反推。在 $(0, 0)$（splat 中心）时 $G = 1$；在 $(\pm 1, \pm 1)$（四边形角落）时 $G = e^{-9} \approx 0$，恰好对应 $3\sigma$ 之外该被丢弃的部分。

> 原文："With the substitution $d_i = 3 \sqrt{\lambda_i} \, p_i$, the original Gaussian falloff collapses to $G(p_x, p_y) = \exp(-4.5 (p_x^2 + p_y^2))$ — the constant 4.5 is just $9/2$, the $3\sigma$ cutoff baked into the normalization."

读到这里有一种"代数把工程优雅化"的快感。如果你直接看 Kerbl 论文里那行 $\sigma(\mathbf{x}) = e^{-\frac{1}{2}(\mathbf{x} - \mu)^T \Sigma^{-1} (\mathbf{x} - \mu)}$，是不会有这个直觉的；但 Feldman 给你换元算清楚之后，你会发现整个 fragment shader 主体可以浓缩成三行：

```glsl
float power = -4.5 * (p.x * p.x + p.y * p.y);
if (power < -9.0) discard;
float alpha = base_alpha * exp(power);
if (alpha < 0.001) discard;
```

第一处 `discard` 是几何剪枝（点落在 3σ 之外），第二处是 alpha 剪枝（这一 fragment 对最终颜色贡献小于一个 LSB）。这两次 discard 在密集 splat 场景下能省下相当可观的 blend 带宽。

### 5. 不透明度、球谐系数与 PLY 的奇怪存储约定

`opacity` 在 ply 文件里存的不是 $[0, 1]$ 区间的数，而是它的 **logit**——即训练时优化的"raw"参数。Feldman 强调了这一点是因为它会让初学者踩坑：如果你直接拿 ply 里的 `opacity` 字段去做 blend，得到的画面会过曝或全黑。正确做法是 `alpha = sigmoid(opacity)`。

同样地，`scale` 字段在 ply 里也是 log-space——因为训练时优化的是 $\log s_i$ 而不是 $s_i$，这样优化器永远不会让缩放变成负数。使用前要做 `s = exp(scale)`。

球谐系数（SH coefficients）的存储更复杂一些：

- **第 0 阶**（`f_dc_0..2`）：3 个标量，对应 RGB 三通道的 "DC term"，也就是"无视角时的基础颜色"。
- **高阶系数**（`f_rest_0..N`）：度数 $\ell$ 的 SH 有 $(\ell + 1)^2$ 个基函数（去掉 DC 后是 $(\ell + 1)^2 - 1$），每个基函数有 3 个 RGB 系数。一个 degree-3 模型总共是 $16 \times 3 = 48$ 个标量，其中 45 个是 `f_rest_*`。

Feldman 在他的 weekend 版本里只用了 degree 0（也就是 base color 直接当颜色用），这是一个值得的简化——它把 ply 里 80% 的字段忽略掉了，但视觉上只丢失了"高光会随相机移动而漂移"这一类微妙的视角依赖效果。对于一个 forward-only 教学实现而言，这是完全合理的取舍。

> 原文："I skipped spherical harmonics evaluation entirely in v1 — it's a complete pipeline by itself, and you get a perfectly recognizable scene from the DC term alone."

读到这里我觉得 Feldman 这个取舍非常工程师——**先把 80% 的画面做出来，再把剩下 20% 留作未来扩展**。这种"分层迭代"的取舍能力，是经验工程师和初学者的关键分水岭。

### 6. CPU 端深度排序——为什么不在 GPU 上做

3DGS 的渲染要求所有 splat 按相机空间 z 由远到近（back-to-front）排序后再画。这是因为 alpha blending 不满足交换律：

$$
\text{blend}(c_1, \alpha_1, \text{blend}(c_2, \alpha_2, c_{bg})) \neq \text{blend}(c_2, \alpha_2, \text{blend}(c_1, \alpha_1, c_{bg}))
$$

工业级实现（如官方 CUDA rasterizer）会用 tile-based binning + GPU radix sort，把几百万个 splat 在 1080p × 16×16 个 tile 上重新分桶并排序。但 Feldman 的实现走了另一条路：

```cpp
struct SplatSortEntry {
    float cameraZ;
    size_t splatIndex;
};
std::sort(entries.begin(), entries.end(),
          [](const auto& a, const auto& b) { return a.cameraZ < b.cameraZ; });
```

是的，就是 `std::sort`，在 CPU 上。Feldman 解释了这个看似"低端"的选择为什么在 forward-only、几百 K splat 的场景下完全可行：

1. 现代 CPU 的 `std::sort`（pdqsort）对 200K 个 float 排序大约只需 5-10 ms；
2. 每帧只排一次，且只在相机移动时才必须重排（静止时可以缓存上一帧的顺序）；
3. CPU 排好序之后通过一个 `instanceID → splatIndex` 的间接索引数组上传到 GPU，让 instanced draw 自动按顺序取数据。

这个选择和 [《把 2000 秒砍成 50 秒：Modal 五年工程账本》](/post/good-read-modal-serverless-gpu-cold-starts/) 里我之前讨论过的"先用 std lib 跑通再上 CUDA"的工程哲学是一致的——**优先暴露算法骨架，再针对瓶颈做异构加速**。如果你一开始就上 tile-based GPU sort，整个教学价值就完全被工程复杂度淹没了。

### 7. Instanced rendering——一根 quad 画一万个 splat

OpenGL 4.5 提供的 `glDrawArraysInstanced` + `glVertexAttribDivisor` 是这套渲染器的关键工程支柱。Feldman 的做法非常干净：

- **共享 vertex buffer**：4 个顶点的 unit quad，所有 splat 共用。
- **per-instance attribute buffer**：每个 splat 一组 (centroid, opacity, scale, rotation)，通过 `glVertexAttribDivisor(loc, 1)` 告诉 GPU 这些属性按 instance 而不是按 vertex 推进。
- **一次绘制**：`glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, N)`，N 就是 splat 总数。

这种数据组织方式有两个直接好处：

1. **完全消除 draw call overhead**：N 个 splat 只产生 1 个 draw call。在 200K 量级的场景下，这是 5 个数量级的节省。
2. **vertex shader 是天然的并行边界**：每个 instance 在 vertex shader 里独立完成"$\Sigma$ 旋转 + 雅可比 + $\Sigma_{2D}$ 特征分解 + 四边形顶点"的整套计算，不需要任何 inter-thread 通信。

Feldman 这里其实展示了一个有点反直觉的事实——**3DGS 的核心创新不是数学，而是"用 GPU 光栅器画无数个椭圆"这个工程思路**。论文里那段"$\alpha$-blending 接 view-dependent SH"的算法，单独看其实就是 EWA 1991 年那套。真正让它成为 2023 年后业界明星的，是"如何把它喂给 GPU 的传统 raster pipeline"——而 Feldman 这一节恰好把这个工程精髓讲得很清楚。

### 8. 周末工程的边界——Feldman 没做的事情

文章接近结尾的时候，Feldman 列出了他的 v1 没做的事情。这个列表本身就是一份**学习路线图**：

1. **球谐高阶项的视角相关性**：v1 用 DC term 当颜色，没做高阶 SH 评估。补上这一步只需要在 vertex shader 里加几行——给定相机方向 $\mathbf{d}$，把 SH 基函数 $Y_\ell^m(\mathbf{d})$ 与对应系数做点积。这一步会让金属、光滑表面的高光"跟着相机走"。
2. **Tile-based binning**：v1 是 brute-force——每一个 splat 都画整个屏幕的四边形。一个真正的工业实现会先把屏幕切成 16×16 tile，每个 tile 只画"边界覆盖到这个 tile"的 splat。这能把 fragment shader 工作量降一个数量级。
3. **GPU sort**：v1 是 `std::sort`。一个完整的实现会用 GPU radix sort（CUB / cuB.Lab 之类），让 splat 排序也能 stay-on-GPU。
4. **反向传播**：v1 完全不可微，只读 ply 不训。要做训练就得把 vertex / fragment shader 的每一步都展开成可微算子，这是官方 CUDA rasterizer 的核心难点。
5. **HN 评论里指出的 [DropAnSH-GS](https://arxiv.org/pdf/2602.20933)**：2026 年 2 月的一篇论文，提出对高阶 SH 系数做训练后剪枝，可以把 ply 文件压缩 30-50%，几乎不损视觉质量。这是 v1 之上的一个"压缩补丁"，工程实现也很简单。

Feldman 把这些"未做事项"摆在台面上的方式，让整篇文章从"一个 demo"变成了"一份 roadmap"。我读完后会有一个清晰的判断——**如果我接下来想在 3DGS 这个方向做实际工程，我从他这一千行代码开始迭代，比从 INRIA 的官方 repo 开始要快得多**。

## 延伸阅读图谱

### Feldman 自己（bfeldman.me）

Feldman 这个博客是一个相对低产但密度极高的个人技术站。除了这篇 3DGS 之外，还有几篇非常值得读的工程文章：

- **[Real-time 4D radiance fields on a single GPU]**（如果你能找到的话，他在 HN 早些时候提到过这是 3DGS 之后他正在写的下一篇）——讲动态场景的 GS 表征。
- **[Building a software rasterizer in C]**——一个更早期的练习，把传统 OpenGL pipeline 全部用 CPU 重写。它实际上为这篇 3DGS 文章打下了基础（你需要先理解传统 raster 才能理解 splat 是怎么"骑"在 raster 上的）。
- **[GLSL Compute Shader notes]**——他对 compute shader 与 graphics pipeline 的工程边界的讨论，是这一类小众但极其有用的"为什么要这样写"型笔记。

### 原始论文与必读文献

读完 Feldman 之后，如果想再深入，下面这条阅读路径几乎是必走的：

1. **[Kerbl, Kopanas, Leimkühler, Drettakis (2023)] 3D Gaussian Splatting for Real-Time Radiance Field Rendering** —— 必读的"原典"，SIGGRAPH 2023 best paper。重点看第 4 节（rasterizer）和第 5 节（adaptive density control）。Feldman 这篇文章覆盖的就是第 4 节的 forward 部分。
2. **[Zwicker, Pfister, van Baar, Gross (2001)] EWA Volume Splatting** —— Feldman 整篇文章里"局部线性化"和"协方差投影"的理论祖宗。读它你会发现 2023 年的 3DGS 在数学上有 80% 是 2001 年的旧账。
3. **[Yifan, Serena, Wu, Öztireli, Sorkine-Hornung (2019)] Differentiable Surface Splatting for Point-based Geometry Processing** —— 2019 年那篇把 splatting 重新做成可微的论文，是从 EWA 到 3DGS 之间的"中间桥梁"。
4. **[Lu et al. (2024)] Scaffold-GS** —— 把 splatting 和 anchor / feature grid 结合起来，处理大场景的工程方案。
5. **[Yan et al. (2026)] DropAnSH-GS**（arxiv 2602.20933）—— HN 评论里被反复提到的 2026 年新文，对 SH 系数做训练后剪枝。
6. **[Yu et al. (2024)] Mip-Splatting** —— 解决 GS 在不同分辨率下抗锯齿 / 抗瑕疵的工作，目前社区认为是"GS 训练时必加 trick"。

### 反方观点 / 替代范式

- **[Müller et al. (2022)] Instant-NGP** —— NeRF 阵营的工程化代表，与 3DGS 形成鲜明的"隐式 vs 显式"两条路线之争。
- **[Wang et al. (2025)] 3D Gaussian Surface Reconstruction** 一类批评 3DGS "看起来好但几何不准"的论文 —— 提醒了你 3DGS 在新视角合成漂亮，但用它直接做 mesh 重建效果不佳。
- **HN 上对 3DGS 的批评意见**：许多评论指出 3DGS 在"非朗伯表面、玻璃、水面、强反射"等情况下需要额外的 trick。这一点和 NeRF 的局限其实是同源的——只要你的渲染模型把世界假设成"颜色 ⊕ 体积密度"，那些违反这个假设的物理现象都会让模型挣扎。

### 工程实现参考

- **[官方 INRIA repo](https://github.com/graphdeco-inria/gaussian-splatting)**：CUDA 版本，工业级实现。读它的目的不是抄，而是看 tile-based binning 和 backward pass 是怎么写的。
- **[gsplat (nerfstudio)](https://github.com/nerfstudio-project/gsplat)**：PyTorch + CUDA wrapper，研究人员的"标准库"。
- **[brush](https://github.com/ArthurBrussee/brush)**：基于 wgpu + WGSL 的工程实现，可在浏览器跑。如果你想找一个比 Feldman 更接近"准生产级"的代码读，brush 是最好的起点。
- **[gaussian-splatting-cuda](https://github.com/MrNeRF/gaussian-splatting-cuda)**：纯 CUDA 工程化复刻，去掉了 Python 依赖。

## 编辑延伸思考

读完这篇文章我有几个挥之不去的想法。

**第一，3DGS 的"工程友好性"被严重低估了。** 过去两年关于 3DGS 的讨论大多停留在"它能不能取代 NeRF"这个比较层面上。但 Feldman 这篇文章让我意识到，3DGS 在**工程上**有一个 NeRF 永远没有的优势——它的核心就是把"无数个椭圆按顺序画到屏幕上"。这意味着任何懂传统 GPU pipeline 的工程师，都可以在不学习"体积渲染"这套新词汇的前提下，把 3DGS 加进自己已有的渲染器。这件事的长期影响可能比"渲染速度比 NeRF 快"要重要得多——它让 3DGS 有可能进入游戏引擎、AR/VR 工具链、CAD 软件，而不只停留在科研 demo 里。

**第二，"周末项目体裁"在 LLM 时代反而变得更有价值。** 2024-2026 这两年，技术博客内容的整体趋势是 LLM-friendly 化——文章变短、变碎、变成"教你 10 分钟"。但 Feldman 这篇 25 分钟的长文反其道而行——它假设读者愿意坐下来花两个小时，把数学推导和代码读完。在我看来，这种"反潮流"的长文反而是 LLM 摘要不会替代的内容。原因很简单：**摘要可以告诉你"3DGS 是什么"，但只有原文能让你自己"推导出"$\Sigma_{2D} = J W \Sigma W^T J^T$ 这个式子**。前者是知识，后者是能力。Feldman 这种文章卖的是后者。

**第三，"周末就能做出来"是一种被低估的"complexity 测试"。** 一项技术能不能被独立开发者在周末复现，是衡量这项技术"工程成熟度"的硬指标。NeRF 在 2020 年刚发表的时候，没有任何独立开发者能在周末复现。3DGS 在 2026 年走到 Feldman 能在周末写出来的状态，说明这套表征的工程门槛已经低到"应该被任何 graphics 工程师当成基础工具掌握"的程度。这件事和我之前在 [《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/) 那篇导读里讨论过的趋势是一致的——**当一项技术能在周末被复现，它就脱离了"研究"阶段，进入了"工具"阶段**。

**第四，球谐函数的存在感，未来可能会被显著降低。** Feldman 在 v1 里完全跳过了高阶 SH 项，得到的画面依然"完全可识别"。HN 评论里提到的 DropAnSH-GS 则更进一步——证明 3DGS 训练完之后，大部分高阶 SH 系数都可以裁掉而几乎不损失质量。这两件事合起来说明一件事：**3DGS 表征里的"视角相关颜色"也许从来就不是关键，关键是"几何 + 基础颜色"**。如果这个判断成立，那么未来的 3DGS 资产格式可能会大幅瘦身——一个 1 GB 的 ply 文件压缩到 200 MB 不损画质，对 AR/VR 这种带宽敏感的场景是巨大利好。

**第五，CPU + GPU 的"混合责任划分"是 3DGS 工程化的一个永恒命题。** Feldman 选了 CPU 排序 + GPU instanced draw，工业实现选了全 GPU。两条路径的成本曲线在不同 splat 数量、不同设备上交叉。对于一个想把 3DGS 装进手机端 viewer 的开发者，Feldman 的方案反而可能比官方 CUDA 实现更适合——因为手机的 CPU/GPU 带宽比桌面差，"all-on-GPU"未必是最优。这种"工业最优解 ≠ 嵌入式最优解"的现象，在我之前导读过的 [《Filip Pizlo 把内存安全 C 跑出 Yolo-C 的速度》](/post/good-read-fil-c-optimized-calling-convention/) 那篇里也讨论过——**没有一个尺寸适合所有工作负载，永远要看你的硬件预算**。

## 配套资料导览

为了让这篇导读真正可以"读 + 用"，我同时准备了三份配套资料，都在本文的同一目录下：

- **`concept-cards.md`**：8 张关键概念卡片。每一张正面是问题（如 "为什么协方差不能直接乘 view-projection？"），背面是 100-200 字的精炼答案。适合在地铁上做"间隔重复"复习。
- **`glossary.md`**：30 余条英中对照术语表，从 EWA、Splatting、Jacobian、Quaternion、SH 到 PSD 都覆盖了。第一次读 Feldman 文章时如果对某个词不熟，直接查这张表会比 Google 更快。
- **`mindmap.svg`**：把整篇文章拆成"输入（ply）→ 参数解码 → 协方差投影 → 特征分解 → 四边形 → fragment Gaussian → α-blend → 屏幕"这条主线的思维导图，深色背景适合直接放进 Notion 或 Obsidian。

## 谁应该读

- **图形学工程师**：如果你过去几年的关注点在传统 raster / shadow / global illumination 上，这篇文章会让你以最低成本理解为什么 3DGS 是 2023-2026 业界最有工程价值的新表征。
- **机器学习工程师**：如果你只在 PyTorch 层面用过 gsplat / nerfstudio，没读过底层的 forward / backward 数学，这篇文章是最好的"补课"材料——它不要求 CUDA 经验，但把数学讲到了能让你看懂官方 CUDA kernel 在做什么的程度。
- **AR/VR / 3D scanning 应用层开发者**：如果你的产品最终要把"现实世界的三维"塞进用户的设备里渲染，那么 3DGS 几乎是接下来三年最值得下注的格式。Feldman 这篇文章是把这个格式"工业化"前的最后一公里教育。
- **任何想做"周末项目"的开发者**：哪怕你最终不打算碰 3DGS，这篇文章里"如何把一份学术论文 + 一份模型 ply 文件 + 一千行代码组合成一个能跑的 demo"的工程姿态，本身就值得学习。

---

> 📚 **引文**（来自原文 BibTeX）：
> Feldman, Benjamin. "3D Gaussian Splatting in a Weekend." *bfeldman.me*, May 2026. <https://bfeldman.me/3dgs-weekend/>
>
> 本文是 2026 年 5 月 19 日"好文共赏"系列的第七篇。如果你也读到了让你想反复 highlight 的工程长文，欢迎告诉我。

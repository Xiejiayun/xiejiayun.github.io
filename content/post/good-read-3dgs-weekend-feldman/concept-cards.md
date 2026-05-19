# 3D Gaussian Splatting — 关键概念卡片

> 配合 Benjamin Feldman 的 [3D Gaussian Splatting in a Weekend](https://bfeldman.me/3dgs-weekend/) 阅读。每张卡片正面是问题，背面是约 100-200 字的精炼答案。

---

## Card 1 · 一个 3D 高斯到底由什么参数化？

**Q**：3D Gaussian Splatting 里"一个高斯"在内存里到底存什么？

**A**：六组参数。
1. **中心点** $\mu \in \mathbb{R}^3$（世界坐标）；
2. **缩放** $s \in \mathbb{R}^3$（log-space，使用前要 `exp`）；
3. **旋转** $q \in \mathbb{R}^4$（四元数）；
4. **不透明度** $o$（logit，使用前要 sigmoid）；
5. **球谐系数** $c_0 \ldots c_{15}$（degree-3 模型共 16×3=48 个标量）。

协方差矩阵 $\Sigma = R S S^T R^T$ 由 $R$（从四元数构造的 3×3 旋转）和 $S$（对角缩放矩阵）合成而来——这种分解保证了 $\Sigma$ 永远半正定。

---

## Card 2 · 为什么协方差不能直接乘 view-projection 矩阵？

**Q**：3D 点投影到 2D 是一个矩阵乘法。为什么 3D 协方差投影到 2D 协方差不是？

**A**：因为透视投影是**非线性的**——它包含一个"除以 z"的步骤。一个全局矩阵 $M$ 不能正确投影协方差，因为协方差描述的是"局部分布的形状"，而非线性变换会让"局部"在不同位置呈现不同的扭曲。

正确做法是：对每个 splat 单独，在它的中心点处对透视投影做**一阶泰勒展开**，得到一个 2×3 的雅可比矩阵 $J$。然后用 $\Sigma_{2D} = J W \Sigma W^T J^T$ 把 3D 协方差投影成屏幕空间的 2D 协方差，其中 $W$ 是 view matrix 的左上 3×3 块。这个技巧由 Zwicker 等人在 2001 年的 EWA Volume Splatting 论文中提出。

---

## Card 3 · 雅可比 $J$ 长什么样？

**Q**：3DGS 协方差投影里的雅可比 $J$ 怎么写？

**A**：设 splat 中心在相机空间是 $t = (t_x, t_y, t_z)$，焦距是 $f_x, f_y$，那么：

$$
J = \begin{pmatrix}
\dfrac{f_x}{t_z} & 0 & -\dfrac{f_x t_x}{t_z^2} \\\\
0 & \dfrac{f_y}{t_z} & -\dfrac{f_y t_y}{t_z^2}
\end{pmatrix}
$$

注意它是 **2×3** 的——因为我们要把 3D 协方差投影到 2D 协方差。$J$ 在每个 splat 中心点重新计算，这就是"局部线性化"。

---

## Card 4 · 怎么从 $\Sigma_{2D}$ 算出包围四边形的四个顶点？

**Q**：得到 2D 协方差之后怎么画一个能完全包住高斯有效区的四边形？

**A**：对 $\Sigma_{2D}$ 做**特征分解**。

2×2 矩阵的特征值有闭式解：
$$
\lambda_{1,2} = \frac{\text{tr}(\Sigma_{2D})}{2} \pm \sqrt{\frac{\text{tr}(\Sigma_{2D})^2}{4} - \det(\Sigma_{2D})}
$$
特征向量 $e_1, e_2$ 也有闭式解（用 $\Sigma_{12}$ 那一行构造，再做正交）。然后用 $3\sigma$ 倍数作为半径——这样 99.7% 的高斯质量都被覆盖：
$$
b_1 = 3\sqrt{\lambda_1}\, e_1, \quad b_2 = 3\sqrt{\lambda_2}\, e_2
$$
四个顶点就是中心点 $\mu_{2D} \pm b_1 \pm b_2$，正好对应一个 `GL_TRIANGLE_STRIP` 的 4 个顶点。

---

## Card 5 · Fragment shader 里那个 4.5 是什么？

**Q**：Feldman 的 fragment shader 里写 `exp(-4.5 * (p.x*p.x + p.y*p.y))`，这个 4.5 哪来的？

**A**：它是 $\tfrac{(3\sigma)^2}{2} = \tfrac{9}{2}$。

整个推导是这样的：把四边形内的局部坐标 $p_x, p_y$ 归一化到 $[-1, 1]$，并用 $d_i = 3\sqrt{\lambda_i} \cdot p_i$ 做尺度变换。代入原始的 Gaussian 衰减 $\exp(-\tfrac{1}{2} \mathbf{d}^T \Sigma_{2D}^{-1} \mathbf{d})$，所有的特征值都和 $3\sigma$ 系数互相约掉，剩下的就是：
$$
G(p_x, p_y) = \exp(-4.5 (p_x^2 + p_y^2))
$$
中心 $G(0,0)=1$，四角 $G(\pm 1, \pm 1) = e^{-9} \approx 0$，正好对应 $3\sigma$ 之外被自然衰减为零的区域。

---

## Card 6 · 为什么 ply 里的 opacity 不能直接用？

**Q**：从 ply 文件读到的 `opacity` 字段是 −5.2 这种值，怎么 blend？

**A**：因为 ply 存的是**优化器看到的 raw 参数**，不是 $[0, 1]$ 区间的概率。

3DGS 训练时优化的是 logit——这样优化器永远不需要担心边界约束。使用前必须做 sigmoid：
$$
\alpha_{base} = \sigma(o) = \frac{1}{1 + e^{-o}}
$$

同样地，`scale` 字段也是 log-space（避免缩放变负），使用前要做 `exp`。这两个变换是新手踩坑的常见点。

---

## Card 7 · 为什么需要 back-to-front 深度排序？

**Q**：为什么 3DGS 必须做严格的深度排序，而不能像普通三角形那样依赖 depth buffer？

**A**：因为 alpha blending 不满足交换律。

普通三角形的颜色是 opaque 的，depth buffer + early-Z 就能保证正确遮挡。但 3DGS 的每个 splat 都是**半透明**的，颜色累积公式是 $C = \sum_i T_i \alpha_i c_i$，其中 $T_i = \prod_{j<i}(1 - \alpha_j)$。这个累积顺序**必须是从远到近**——否则透射率 $T$ 计算错位，最终颜色就不对。

工程实现一般有两条路径：(1) 全场 CPU 排序 + instanced draw（Feldman 的 v1 选择，几百 K splat 量级完全够用）；(2) tile-based binning + per-tile GPU radix sort（INRIA 官方 CUDA 实现），用空间局部性换大场景吞吐。

---

## Card 8 · `glVertexAttribDivisor` 在 3DGS 渲染里起什么作用？

**Q**：Feldman 用 OpenGL 的 instanced rendering 画 splat，关键 API 是 `glVertexAttribDivisor(loc, 1)`。它到底做什么？

**A**：它告诉 GPU "这个 vertex attribute 不要按 vertex 推进，按 instance 推进"。

具体来说：所有 splat 共享一个 4 顶点的 unit quad VBO。然后每个 splat 的 (centroid, opacity, scale, rotation) 作为 per-instance attribute，divisor=1 表示"每画完 1 个 instance 才换下一组属性"。这样一次 `glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, N)` 就画完了 N 个 splat，全过程只产生 **1 个 draw call**，彻底消除 CPU-GPU 同步开销。这是 3DGS 渲染能在普通 GPU 上跑到实时 fps 的关键工程支柱。

---

## Card 9 · v1 跳过球谐高阶项，画面会丢失什么？

**Q**：Feldman 在 v1 里只用了 DC term，跳过了所有高阶 SH。画面会差多少？

**A**：丢失的是**视角相关的高光漂移**——也就是当相机绕物体转动时，金属、塑料、抛光表面上"高光位置随视线移动"的微妙效果。但对于哑光物体、漫反射主导的场景，DC term 已经能画出完全可识别的视觉。

补全 SH 的工程量并不大：在 vertex shader 里给定归一化的视向量 $\mathbf{d}$，计算 SH 基函数 $Y_\ell^m(\mathbf{d})$（degree-3 需要 16 个基函数），然后与 ply 里 `f_rest_*` 系数做点积，叠加到 DC color 上即可。HN 评论里提到的 [DropAnSH-GS](https://arxiv.org/pdf/2602.20933) 论文进一步证明，训练完成后大部分高阶 SH 系数都可以裁掉而几乎不损质量——这是一个值得跟进的压缩思路。

---

## Card 10 · 3DGS 相比 NeRF 的核心工程优势是什么？

**Q**：一句话总结，3DGS 为什么在 2024-2026 取代了 NeRF 成为业界明星？

**A**：**它能直接坐在传统 GPU 光栅器上跑**，而 NeRF 必须重新发明体积渲染。

NeRF 的每个像素都要做一次 ray marching + 几十次 MLP 前向——这是"用神经网络隐式表达 + 学术级体积渲染"，工程上很难塞进游戏引擎或浏览器。3DGS 反过来，把场景显式表达成一堆椭圆，渲染就是"按深度排序后 alpha-blend 一堆 splat"——这套流程对任何用过 OpenGL/Vulkan/Metal 的工程师都是熟悉的。结果就是 3DGS 在 RTX 3060 上能跑实时，在浏览器里也能跑，编辑、裁剪、移植到 AR/VR 都顺理成章。

这是一个非常典型的"算法接 hardware 的范式"在工程上完胜"算法忽视 hardware 的范式"的案例。

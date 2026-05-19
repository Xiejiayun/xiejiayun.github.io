# 术语表 · Glossary

> 配合 Benjamin Feldman 的 [3D Gaussian Splatting in a Weekend](https://bfeldman.me/3dgs-weekend/) 阅读。中英对照、按主题分组。

## 一、3DGS 基本概念

| 英文 | 中文 | 解释 |
|---|---|---|
| 3D Gaussian Splatting (3DGS) | 三维高斯泼溅 | 用一堆参数化的各向异性 3D 高斯椭球显式表达场景的新视图合成范式。 |
| Splat | 泼溅 / 喷溅元 | 单个被投影到屏幕的高斯椭球。本意是"墨点"。 |
| Radiance Field | 辐射场 | 描述场景中每个位置、每个方向上发出的光的函数。NeRF / 3DGS 都属于辐射场表征。 |
| NeRF (Neural Radiance Field) | 神经辐射场 | 用 MLP 隐式表达 $F: (x, y, z, \theta, \phi) \to (R, G, B, \sigma)$ 的方法，2020 年 Mildenhall 等人提出。 |
| Anisotropic | 各向异性 | 不同方向有不同性质（如 3DGS 的椭球三个轴半径不同）。对应词 isotropic（各向同性）。 |
| Forward Rendering | 前向渲染 | 给定预训练参数渲染图像，不涉及反向传播。本文实现的就是 forward-only。 |
| View-Dependent Color | 视角相关颜色 | 同一个表面点在不同观察方向看起来颜色不同（如金属高光）。3DGS 用 SH 系数表达。 |

## 二、协方差与投影

| 英文 | 中文 | 解释 |
|---|---|---|
| Covariance Matrix | 协方差矩阵 | 描述多维高斯分布形状的对称矩阵。3DGS 的 $\Sigma_{3D}$ 是 3×3 对称半正定。 |
| Positive Semi-Definite (PSD) | 半正定 | 所有特征值非负的对称矩阵。$\Sigma = RS S^T R^T$ 的分解天然保证 PSD。 |
| Eigendecomposition | 特征分解 | 把矩阵拆成 $\Sigma = Q \Lambda Q^T$，得到特征值和特征向量。2×2 有闭式解。 |
| Jacobian | 雅可比矩阵 | 多元函数的一阶偏导数矩阵。3DGS 中用 2×3 雅可比对透视投影做局部线性化。 |
| Taylor Expansion | 泰勒展开 | 在某点附近用多项式逼近函数。一阶展开 = Jacobian 线性化。 |
| Local Linearization | 局部线性化 | 在每个 splat 中心单独做一阶近似——非线性透视投影的处理技巧。 |
| EWA Splatting | EWA 泼溅 | Elliptical Weighted Average Splatting，Zwicker 等人 2001 年提出的体积渲染技术，是 3DGS 数学骨架的祖宗。 |

## 三、参数与变换

| 英文 | 中文 | 解释 |
|---|---|---|
| Quaternion | 四元数 | 四个分量的"超复数"，紧凑表达 3D 旋转，无万向锁，3DGS 用它存储旋转。 |
| Log-Space Scaling | 对数尺度 | 把缩放参数存为 $\log s$ 而非 $s$，使优化器永远不会产生负值。 |
| Logit | 对数几率 | $\text{logit}(p) = \log(p / (1-p))$。3DGS 的 opacity 存为 logit，使用前做 sigmoid。 |
| Sigmoid | S 型函数 | $\sigma(x) = 1 / (1 + e^{-x})$。把任意实数映射到 (0, 1) 区间。 |
| View Matrix | 视图矩阵 | 把世界坐标转到相机坐标的 4×4 矩阵。 |
| Projection Matrix | 投影矩阵 | 把相机坐标投影到裁剪空间的 4×4 矩阵（含透视除法）。 |
| NDC (Normalized Device Coordinates) | 归一化设备坐标 | 透视除法之后的 [-1, 1]^3 空间，GPU 光栅器的标准输入。 |
| Camera Space / View Space | 相机空间 / 视图空间 | view matrix 之后、projection matrix 之前的空间。3DGS 的深度排序就在这个空间。 |

## 四、球谐函数

| 英文 | 中文 | 解释 |
|---|---|---|
| Spherical Harmonics (SH) | 球谐函数 | 球面上的正交基函数族 $\{Y_\ell^m\}$，可以紧凑表达视角相关的颜色。 |
| SH Degree | 球谐度数 | $\ell$ 的最大值。degree-3 SH 共 $(3+1)^2 = 16$ 个基函数。 |
| SH Coefficients | 球谐系数 | 给定颜色场在每个 SH 基上的投影系数，3DGS 训练的就是这些系数。 |
| DC Term | 直流项 | SH 的零阶项 $Y_0^0$，对应"无视角依赖的基础颜色"。Feldman 的 v1 只用了 DC term。 |

## 五、渲染管线

| 英文 | 中文 | 解释 |
|---|---|---|
| Vertex Shader | 顶点着色器 | 处理每个顶点的可编程阶段，3DGS 在这里完成协方差投影和四边形构造。 |
| Fragment Shader | 片元着色器 | 处理每个 fragment 的可编程阶段，3DGS 在这里计算 Gaussian 衰减和 alpha。 |
| Rasterizer | 光栅器 | GPU 固定功能阶段，把三角形/四边形栅格化为 fragment。 |
| Instanced Rendering | 实例化渲染 | 用一次 draw call 画 N 个共享几何但各自属性不同的对象。 |
| `glVertexAttribDivisor` | 顶点属性步进 | OpenGL API，控制属性是按 vertex 还是按 instance 推进。 |
| `glDrawArraysInstanced` | 实例化绘制调用 | 一次 draw call 画 N 个 instance。 |
| `GL_TRIANGLE_STRIP` | 三角形条带 | 一种几何拓扑，4 个顶点画 2 个三角形（共享一条边），3DGS 的四边形用它。 |
| Alpha Blending | 透明度混合 | $C_{out} = \alpha C_{src} + (1-\alpha) C_{dst}$，3DGS 严格按 back-to-front 顺序做。 |
| Discard | 丢弃 | fragment shader 里的 `discard` 关键字，提前终止当前 fragment 的处理。 |

## 六、深度与排序

| 英文 | 中文 | 解释 |
|---|---|---|
| Back-to-Front Sorting | 由远到近排序 | 3DGS 渲染要求 splat 按相机空间 z 从大到小依次绘制，否则 alpha blend 错误。 |
| Tile-Based Binning | tile 分桶 | 工业级 3DGS 实现把屏幕切成 16×16 tile，每个 tile 内独立做小规模排序。 |
| Radix Sort | 基数排序 | 一种 $O(n)$ 排序算法，GPU 上有 CUB / cub::DeviceRadixSort 等成熟实现。 |
| Painter's Algorithm | 画家算法 | "先画远的，再画近的覆盖"。3DGS 本质上是画家算法在半透明物体上的应用。 |
| Beer-Lambert Law | 比尔-朗伯定律 | $T = e^{-\tau}$，描述光在介质中的衰减。3DGS 的 $T = \prod(1-\alpha)$ 是它的离散版本。 |

## 七、文件格式

| 英文 | 中文 | 解释 |
|---|---|---|
| PLY (Polygon File Format) | PLY 多边形文件格式 | Stanford 1990 年代提出的几何文件格式，3DGS 用它存训练好的高斯参数。 |
| `f_dc_0..2` | DC 颜色字段 | ply 里的 SH degree-0 系数，3 个标量对应 RGB。 |
| `f_rest_*` | 高阶 SH 字段 | ply 里的 degree-1+ SH 系数，degree-3 模型共 45 个标量。 |

## 八、相关论文

| 文献 | 年份 | 主题 |
|---|---|---|
| Kerbl et al. | 2023 | 原始 3DGS 论文（SIGGRAPH best paper）。 |
| Zwicker et al. | 2001 | EWA Volume Splatting——3DGS 数学骨架的祖宗。 |
| Yifan et al. | 2019 | Differentiable Surface Splatting——splatting 可微化的中间桥梁。 |
| Yu et al. | 2024 | Mip-Splatting——多分辨率抗锯齿。 |
| Lu et al. | 2024 | Scaffold-GS——anchor + GS 处理大场景。 |
| DropAnSH-GS | 2026 | 高阶 SH 系数训练后剪枝，arxiv 2602.20933。 |
| Mildenhall et al. | 2020 | NeRF 原论文，3DGS 的"前任"。 |
| Müller et al. | 2022 | Instant-NGP——NeRF 工程化代表。 |

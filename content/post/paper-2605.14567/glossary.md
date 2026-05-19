# 术语表 / Glossary

下表收录本文涉及的关键术语，按重要性排序。

| # | 中文 | English | 简释 |
|---|------|---------|------|
| 1 | 标度律 | Scaling law | 模型性能与参数 / 数据 / 计算量呈幂律关系 |
| 2 | 顺序特征恢复 | Sequential feature recovery | 训练过程中特征按信息指数从低到高逐级被学到 |
| 3 | 信息指数 | Information exponent | 决定单指标模型样本复杂度的最低非零 Hermite 阶数 |
| 4 | 高维渐近 | High-dimensional asymptotics | 维度与样本量同阶增长极限下的统计分析框架 |
| 5 | BBP 相变 | BBP (Baik–Ben Arous–Péché) transition | 尖峰协方差模型中信号强度跨越临界值时外离群特征值出现的相变 |
| 6 | 随机矩阵理论 | Random matrix theory (RMT) | 研究大维随机矩阵谱分布的数学工具 |
| 7 | 高斯正交系综 | Gaussian Orthogonal Ensemble (GOE) | 实对称高斯随机矩阵系综，用于谱噪声建模 |
| 8 | 经验协方差矩阵 | Empirical covariance matrix | 由样本估计的协方差矩阵，谱用于特征检测 |
| 9 | 尖峰检测 | Spike detection | 从噪声谱中识别由信号产生的离群特征值 |
| 10 | 离群特征值 | Outlier eigenvalue | 跳出 bulk 谱之外、对应信号方向的特征值 |
| 11 | 体谱 | Bulk spectrum | 大维矩阵特征值分布的连续主体（如 Marchenko–Pastur） |
| 12 | 特征向量恢复 | Eigenvector recovery | 估计的特征向量与真实信号方向的对齐程度 |
| 13 | 信噪比 | Signal-to-noise ratio (SNR) | 信号尺度与噪声尺度之比，决定可恢复性 |
| 14 | 样本复杂度 | Sample complexity | 达到给定恢复 / 泛化精度所需的样本数 |
| 15 | 算子范数 | Operator norm | 矩阵的最大奇异值，用于谱扰动控制 |
| 16 | Frobenius 范数 | Frobenius norm | 矩阵元素平方和的平方根，常用于误差度量 |
| 17 | Hermite 多项式 | Hermite polynomial | 关于高斯测度正交的一元多项式基 |
| 18 | Hermite 张量 | Hermite tensor | Hermite 多项式的高维张量推广，给出函数的正交分解 |
| 19 | Wiener 混沌分解 | Wiener chaos decomposition | $L^2(\gamma)$ 函数按 Hermite 阶数的正交直和分解 |
| 20 | 高斯等价性 | Gaussian equivalence | 非线性特征图的统计性质可由匹配低阶矩的高斯模型替代 |
| 21 | 多项式特征 | Polynomial features | 输入坐标的多项式构成的特征映射 |
| 22 | 多指标模型 | Multi-index model | 目标函数仅依赖输入在低维子空间上的若干投影 |
| 23 | 单指标模型 | Single-index model | 目标函数 $f(x)=\sigma(\langle w^*,x\rangle)$ 的特例 |
| 24 | 随机层级模型 | Random hierarchy model | 由随机组合规则递归构造的层级目标 |
| 25 | 深度分离 | Depth separation | 深层网络可表达 / 学习而浅层不可的函数族分离现象 |
| 26 | 组合式目标 | Compositional target | 由若干子函数复合而成的目标函数 |
| 27 | 潜在特征 | Latent features | 目标函数依赖的隐藏低维方向或表征 |
| 28 | Davis–Kahan 定理 | Davis–Kahan theorem | 利用谱隙界定特征空间在扰动下的旋转 |
| 29 | Neumann 级数 | Neumann series | 算子逆 $(I-A)^{-1}=\sum A^k$ 的级数展开 |
| 30 | 预解式 | Resolvent | $(zI-M)^{-1}$，谱分析与扰动展开的核心工具 |
| 31 | 特征向量扰动 | Eigenvector perturbation | 矩阵小扰动下特征向量的变化分析 |
| 32 | 谱隙 | Spectral gap | 相邻特征值之差，决定扰动稳定性 |
| 33 | 懒惰区 | Lazy regime | 训练中权重几乎不变、等价于核方法的区域 |
| 34 | 特征学习区 | Feature learning regime | 隐表征显著演化、超越固定核的训练区域 |
| 35 | 神经切线核 | Neural tangent kernel (NTK) | 无限宽极限下的线性化训练核 |
| 36 | 最大更新参数化 | Maximal update parameterization (μP) | 保证宽度极限下特征学习的参数化 |
| 37 | 弱恢复 | Weak recovery | 估计与真实方向相关性渐近非零 |
| 38 | 强恢复 | Strong recovery | 估计与真实方向相关性渐近趋于 1 |
| 39 | 岭回归 | Ridge regression | 带 $\ell_2$ 正则的最小二乘回归 |
| 40 | 核回归 | Kernel regression | 在再生核 Hilbert 空间中的回归方法 |
| 41 | 均方误差 | Mean squared error (MSE) | 预测与真实值差的平方均值 |
| 42 | 泛化误差 | Generalization error | 模型在未见样本上的期望损失 |
| 43 | Chinchilla 标度律 | Chinchilla scaling law | 参数与数据按近 1:1 比例同步缩放的计算最优配方 |
| 44 | Kaplan 标度律 | Kaplan scaling law | 更倾向于增大参数量的早期 LLM 标度配方 |
| 45 | 计算最优 | Compute-optimal | 在固定算力预算下选择最优参数/数据比例 |
| 46 | 数据受限 | Data-bound | 性能由数据量主导限制的训练区域 |
| 47 | 参数受限 | Parameter-bound | 性能由参数量主导限制的训练区域 |
| 48 | 张量主成分分析 | Tensor PCA | 从带噪高阶张量中恢复尖峰方向的问题 |
| 49 | 阶段式学习 | Staircase / staged learning | 损失曲线随训练呈阶梯式下降、对应逐级学到的特征 |
| 50 | 幂律指数 | Power-law exponent | 标度律中描述性能随规模衰减速率的指数 |

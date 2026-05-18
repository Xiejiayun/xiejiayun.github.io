# 关键概念卡片 · SANA-WM

每张卡片是一个独立的、可被引用的"原子知识单元"，按主题分组。

---

## 🟦 卡片 1：World Model（世界模型）

**英文**：World Model

**一句话**：给定一个初始状态 + 动作序列，能预测出未来观测的生成式模型；本质上是"可控的视频模拟器"。

**关键区分**：
- 与一般 video generation 的差异：必须支持 action conditioning
- 与 simulator 的差异：用数据驱动，不需要手写物理规则
- 与 LLM 的差异：输出是视频帧而非 token

**SANA-WM 中的具体形式**：输入 = 1 张图 + 6-DoF 相机轨迹 + 可选 text；输出 = 60 秒 720p 视频，相机精确遵循输入轨迹。

---

## 🟦 卡片 2：Frame-wise Gated DeltaNet（帧级 GDN）

**英文**：Frame-wise Gated DeltaNet

**一句话**：把原本"每个 token 一步递归"的 GDN 改造成"每帧一步递归"，一次性吞下该帧所有 $S$ 个空间 token。

**核心公式**：

$$\mathbf{S}_t = \mathbf{S}_{t-1}\mathbf{M}_t + \mathbf{U}_t, \quad \mathbf{M}_t = \gamma_t(\mathbf{I} - \hat{\mathbf{K}}_t\boldsymbol{\beta}_t\hat{\mathbf{K}}_t^\top)$$

**关键稳定性条件**：key 必须做 $1/\sqrt{DS}$ 缩放，保证 $\|\mathbf{M}_t\|_2 \leq \gamma_t \leq 1$。

**为什么重要**：内存恒定 $D \times D$，与视频长度无关——这是单 GPU 跑分钟级视频的钥匙。

---

## 🟦 卡片 3：Hybrid Attention（混合注意力）

**英文**：Hybrid Linear/Softmax Attention

**一句话**：每 4 层 GDN 之间插一层标准 softmax attention，用极少 softmax 层补足"长程精确检索"能力。

**SANA-WM 的比例**：20 层中，5 层 softmax（第 3/7/11/15/19）+ 15 层 GDN。

**先例**：
- Jamba（AI21）：1:7 比例
- Mamba-2 Hybrid：1:4–1:6
- StripedHyena（Together）：纯 Hyena + 1 层 softmax

**反直觉点**：纯线性吞吐量更高但质量崩；纯 softmax 质量好但内存爆。**少量 softmax 是"信息检索"的锚点**。

---

## 🟦 卡片 4：UCPE（Universal Camera Pose Encoding）

**英文**：Universal Camera Pose Encoding

**一句话**：把相机的 6-DoF 位姿编码成 latent token 上的位置嵌入，让模型"在 attention 中自然感知相机方向"。

**机制**：
1. 对每个 latent token，根据像素位置 + 相机内参 unproject 出世界空间射线
2. 构造 ray-local 坐标系 $(\mathbf{x}, \mathbf{y}, \mathbf{z})$
3. 把射线起点和方向编码后加到 token embedding 上

**类比**：相当于"为每个像素附一个相机标签"，让 transformer 隐式学会几何一致性。

---

## 🟦 卡片 5：Plücker Coordinates / Plücker Mixing

**英文**：Plücker Coordinates

**一句话**：用 6 个数 $(\mathbf{d}, \mathbf{m})$ 表示 3D 空间中的一条直线（方向+矩），是计算机视觉里编码射线的标准方式。

**为什么 SANA-WM 用它**：UCPE 在 latent space 工作，但 VAE 时间下采样会丢失子帧运动。**Plücker mixing 在原始像素分辨率上做几何补偿**，保证细粒度相机精度。

**与 NeRF 的关系**：NeRF 也用 Plücker 编码射线；SANA-WM 把这个表示借到了视频扩散里。

---

## 🟦 卡片 6：Two-Stage Generation Pipeline（两阶段生成）

**英文**：Two-Stage Generation Pipeline

**一句话**：Stage-1 用 2.6B 主干生成长视频，Stage-2 用 17B refiner 去除晚段质量衰减。

**为什么不直接把主干放大**：
- 主干放大 5 倍 = 训练成本 5–10×、推理成本 5×
- Refiner 只在推理时多 24GB 显存、吞吐量降 10%
- **代价/收益比远好于"全模型放大"**

**$\Delta_\text{IQ}$ 改善**：Simple 3.79 → 1.17，Hard 3.09 → 0.31。

---

## 🟦 卡片 7：Self-Forcing Distillation（自强迫蒸馏）

**英文**：Self-Forcing Distillation（Yin et al., 2024）

**一句话**：训练时，让 student 用自己的预测作为"下一步输入"，模拟推理时的 AR 部署条件。

**与传统蒸馏的差异**：
- Teacher Forcing：训练用 ground truth 作为下一步输入 → 推理时分布漂移
- Self-Forcing：训练时也用 student 自己的预测 → 训练-推理对齐

**SANA-WM 中的作用**：把 60 步 denoising 压到 4 步，同时保持视频质量。

---

## 🟦 卡片 8：NVFP4（NVIDIA FP4）

**英文**：NVIDIA FP4

**一句话**：NVIDIA Blackwell 引入的 4-bit 浮点格式，带 per-block scale，比 INT4 精度损失小得多。

**对比**：
- INT4：固定范围 [-8, 7]，精度低
- NVFP4：E2M1 浮点 + per-block scale → 动态范围更大
- FP8：精度高但 size 2×

**硬件支持**：RTX 5090 (Blackwell)、H200 部分支持；H100/A100 需软件模拟。

**SANA-WM 中的收益**：让 60 秒 720p 推理在 RTX 5090 上跑到 34 秒，比实时还快。

---

## 🟦 卡片 9：Attention Sink（注意力锚点）

**英文**：Attention Sink（Xiao et al., StreamingLLM, 2023）

**一句话**：在长上下文 attention 中保留"第一个 token 作为永久锚点"，缓解长序列衰减。

**SANA-WM 中的用法**：5 层 softmax attention 在 chunk-causal AR 推理时，把"第一帧"作为 sink + 局部时间窗口 → softmax 部分内存随 rollout 长度恒定。

**为什么有效**：第一帧 = 场景身份的"地标"，永远在 attention 里参与匹配，避免后期场景漂移。

---

## 🟦 卡片 10：213K Clips Data Pipeline（数据管线）

**一句话**：用 7 个数据源 + 改进的 VIPE 标注引擎，得到 21.3 万段带精确 metric-scale 6-DoF pose 的视频。

**关键升级**：
- VIPE 原版 depth 不稳 → 换 **Pi3X**（长序一致）+ **MoGe-2**（metric scale）
- 静态 3D 场景（DL3DV）→ FCGS 重建 + 渲染 60s 轨迹 + DiFix3D 去伪影
- 7 源：SpatialVID-HQ (158K)、DL3DV (5.7K + 14.9K)、OmniWorld、Sekai Game/Walking、MiraData

**对比 LingBot-World**：千万级 clips → SANA-WM 21.3 万，**节约两个数量级数据，质量高于数量**。

---

## 🟦 卡片 11：1-Minute World Model Benchmark（1 分钟基准）

**一句话**：SANA-WM 团队顺手做了一个新基准：80 张 Nano Banana Pro 生成的初始图 × 2 种 trajectory 难度 × 5 类指标。

**评测维度**：
1. **Pose Acc**：RotErr / TransErr / CamMC
2. **Visual Quality**：VBench 8 维 + Overall
3. **Revisit Memory**：相机回到出发点后场景一致性（PSNR/SSIM/LPIPS）
4. **Long-Term Degradation**：$\Delta_\text{IQ}$
5. **Efficiency**：Memory / Throughput

**为什么这是贡献**：之前没人系统性测过 minute-scale 一致性，这套指标很可能成为下一轮 SOTA 的标尺。

---

## 🟦 卡片 12：Context-Parallel (CP) Training

**一句话**：把单段 961 帧（60s @ 16 FPS）的训练在时间维上分片到 64 个 GPU，每片只持有 15 帧 latent。

**机制**：
- All-reduce 时同步 frame-recurrent state（GDN 的 $\mathbf{S}_t$）
- Softmax 5 层在 CP 边界用 ring attention 通信
- 这样训练显存随 GPU 数线性缩减

**为什么必要**：单 GPU 的 80GB 显存无法装下完整 961 帧训练，必须分片。

---

> 这些卡片可以独立引用，也可以组合成系统视图——架构（1-9）、数据（10）、评测（11）、训练系统（12）。

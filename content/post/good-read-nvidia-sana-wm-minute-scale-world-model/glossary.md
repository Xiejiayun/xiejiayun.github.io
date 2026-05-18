# 术语表 · SANA-WM 英中对照

围绕世界模型 / 线性注意力 / 视频扩散三大领域。35+ 条核心术语。

---

## A. 模型架构

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| World Model | 世界模型 | 给定初始观测+动作，预测未来观测的生成模型 |
| Diffusion Transformer (DiT) | 扩散 Transformer | 用 Transformer 替代 U-Net 的扩散模型主干 |
| Hybrid Linear Attention | 混合线性注意力 | 线性 + softmax 交替的注意力栈 |
| Gated DeltaNet (GDN) | 门控 DeltaNet | 带衰减门和 delta-rule 修正的线性 RNN |
| Frame-wise GDN | 帧级 GDN | 每帧一步递归，吞下整帧所有空间 token |
| Cumulative Linear Attention | 累积线性注意力 | ReLU-based 线性注意力，无衰减机制 |
| Attention Sink | 注意力锚点 | 永久保留第一个 token 在 attention 里 |
| Chunk-Causal | 分块因果 | AR 推理时按块处理，每块内部 bidirectional |

## B. 相机控制

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| 6-DoF Camera Pose | 6 自由度相机位姿 | 3 平移 + 3 旋转 |
| UCPE (Universal Camera Pose Encoding) | 通用相机位姿编码 | 把 6-DoF 信息编码到 latent token 上 |
| Plücker Coordinates | Plücker 坐标 | 6 维表示 3D 直线 (方向+矩) |
| Plücker Mixing | Plücker 混合 | 在像素分辨率上注入射线信息 |
| Dual-Branch Camera Control | 双轨相机控制 | 粗 (UCPE) + 细 (Plücker) 两路条件化 |
| RotErr / TransErr | 旋转/平移误差 | 相机轨迹精度指标 |
| CMC (Camera Motion Consistency) | 相机运动一致性 | 综合 R+T 的精度指标 |

## C. 训练与数据

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| Metric-Scale 6-DoF Pose | 米制 6-DoF 位姿 | 带真实物理尺度的相机参数 |
| Progressive Training | 渐进式训练 | 短视频 → 长视频，分 4 阶段递进 |
| Context-Parallel (CP) | 上下文并行 | 单段视频在时间维分片到多 GPU |
| VAE (Variational AutoEncoder) | 变分自编码器 | 把视频帧压缩到低维 latent space |
| LTX2-VAE | LTX2-VAE | Lightricks 的高压缩比视频 VAE |
| ST-DC-AE | 时空双重压缩 AE | SANA-Video 用的 VAE |
| 3DGS (3D Gaussian Splatting) | 3D 高斯喷溅 | 静态 3D 场景重建技术 |
| FCGS | 快速压缩高斯喷溅 | 3DGS 的加速变体 |
| VIPE | VIPE 标注器 | NVIDIA 出的视频 pose 标注引擎 |
| Pi3X / MoGe-2 | Pi3X / MoGe-2 | 长序列 depth + metric scale 估计模型 |

## D. 推理与部署

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| Self-Forcing Distillation | 自强迫蒸馏 | 让 student 用自己预测作为下一步输入 |
| NVFP4 | NVFP4 | NVIDIA Blackwell 的 4-bit 浮点格式 |
| Flow Matching | 流匹配 | 一种替代 DDPM 的扩散训练目标 |
| Autoregressive Rollout | 自回归滚动 | 一段段生成长视频的推理模式 |
| Throughput (videos/hour) | 吞吐量 | 单位时间内生成的视频数 |

## E. 评测指标

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| VBench | VBench | 视频生成质量综合基准 |
| Revisit Trajectory | 回访轨迹 | 相机回到起点附近，测 memory |
| PSNR / SSIM / LPIPS | PSNR/SSIM/LPIPS | 图像质量三件套 |
| $\Delta_\text{IQ}$ | IQ 退化 | 晚段视频质量相对早段的下降 |
| Subject Consistency (SC) | 主体一致性 | VBench 8 维之一 |
| Background Consistency (BC) | 背景一致性 | VBench 8 维之一 |
| Temporal Flickering (TF) | 时间抖动 | VBench 8 维之一 |
| Motion Smoothness (MS) | 运动平滑度 | VBench 8 维之一 |
| Aesthetic Quality (AQ) | 美学质量 | VBench 8 维之一 |
| Image Quality (IQ) | 图像质量 | VBench 8 维之一 |
| Dynamic Degree (DD) | 动态程度 | VBench 8 维之一 |
| Object Class (OC) | 物体类别 | VBench 8 维之一 |

## F. 相关系统/竞品

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| LingBot-World | 灵动世界 | 14B+14B 大模型 baseline |
| HY-WorldPlay | 腾讯混元 WorldPlay | 8B 世界模型 |
| Matrix-Game 3.0 | 矩阵游戏 3.0 | 5B 游戏域世界模型 |
| Infinite-World | 无限世界 | 1.3B AR 视频生成 |
| Cosmos | NVIDIA Cosmos | NVIDIA 自家上一代世界模型平台 |
| Genie 3 | DeepMind Genie 3 | DeepMind 闭源世界模型 |

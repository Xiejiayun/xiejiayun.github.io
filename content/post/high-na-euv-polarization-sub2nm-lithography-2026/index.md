---
title: "偏振效应不可忽略：High-NA EUV 在 sub-2nm 节点面临的光学物理新墙"
description: "东京科学大学论文揭示 High-NA EUV 光刻中偏振效应对成像质量的影响不可忽略，这是摩尔定律继续前进必须翻越的又一道物理障碍。"
date: 2026-05-07
slug: "high-na-euv-polarization-sub2nm-lithography-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - EUV光刻
    - High-NA
    - 半导体制造
    - 光刻技术
draft: false
---

> 2026 年 5 月，东京科学大学（Institute of Science Tokyo）的研究团队在 *Journal of Micro/Nanopatterning, Materials, and Metrology* 发表论文，扩展了 STCC（Source-position-dependent Transmission Cross Coefficient）公式以纳入偏振效应。这不是一篇普通的学术论文——它揭示了 High-NA EUV 光刻在推进到 sub-2nm 节点时，必须面对的一个全新物理障碍。

## 从 Low-NA 到 High-NA：数值孔径翻倍背后的物理代价

ASML 的 TWINSCAN EXE:5000 系列 High-NA EUV 系统将数值孔径（NA）从 0.33 提升到 0.55，分辨率极限从约 13nm 降至约 8nm。这是 sub-2nm 芯片制造（Intel 14A、TSMC A16 及更先进节点）的核心使能技术。

但更高的 NA 意味着更大的入射角度范围，这带来了一个在 Low-NA 时可以忽略、但在 High-NA 下 **不可忽略** 的物理效应：**偏振依赖性**。

```
Low-NA EUV (NA = 0.33):
  光线入射角 <= ~19 度
  偏振效应对成像的影响 < 1%
  -> 可以安全忽略

High-NA EUV (NA = 0.55):
  光线入射角 <= ~33 度
  偏振效应对成像的影响: 显著
  -> 不可忽略，需要新的仿真方法
```

## 偏振效应为什么在 High-NA 下变得重要

EUV 光刻使用 13.5nm 波长的极紫外光。当光线以大角度入射到掩模（mask）表面时，s偏振（垂直于入射面）和 p偏振（平行于入射面）的透射和反射特性出现 **显著差异**。

在 Low-NA 系统中，所有光线的入射角都很小，s/p 偏振的差异可以忽略。但 High-NA 将最大入射角从约 19 度扩大到约 33 度，在这个角度范围内：

1. **掩模三维效应（Mask 3D effects）**加剧：掩模吸收层的有限厚度对不同偏振的光产生不同的衍射效果
2. **偏振相关的像差**：光学系统在不同偏振方向上的传递函数不同
3. **光刻胶响应**：偏振影响光刻胶中的干涉图案

传统的 TCC（Transmission Cross Coefficient）公式假设偏振是均匀的——这在 Low-NA 下是合理的近似。但东京科学大学的论文证明，**在 High-NA 下这个近似不再成立**。

## STCC 公式的扩展：从标量到矢量

论文的核心贡献是将 STCC 公式从标量形式扩展为包含偏振的矢量形式：

| 传统 STCC | 扩展 STCC |
|-----------|-----------|
| 假设均匀偏振 | 包含偏振态和方向 |
| 标量衍射 | 矢量衍射 |
| 忽略掩模 3D 偏振耦合 | 纳入掩模 3D 偏振效应 |
| 快速但 High-NA 下不准确 | 准确且仍保持计算效率 |

这个扩展的意义在于：它不仅是更准确的物理描述，更是 **计算光刻（Computational Lithography）** 的关键基础设施。现代光刻的掩模设计（OPC/ILT）和工艺窗口优化高度依赖快速、准确的成像仿真。如果仿真公式本身存在系统性偏差，所有下游的掩模优化都会偏离目标。

## High-NA EUV 的"难题清单"

偏振效应只是 High-NA EUV 面临的众多挑战之一：

| 挑战 | 状态 | 影响 |
|------|------|------|
| **偏振效应** | 论文阶段，需工具链集成 | 仿真准确性 |
| 异形光学（Anamorphic） | 已部署，8x/4x 放大率 | 需要新掩模基础设施 |
| 防尘薄膜（Pellicle） | 开发中，更大面积更难做 | 良率和掩模寿命 |
| 吞吐量 | ~185 片/小时（目标） | 成本效率 |
| 设备成本 | ~$3.5-4 亿/台 | 资本支出 |
| 随机效应（Stochastics） | 持续研究 | 图案保真度 |
| 光刻胶灵敏度 | 需要新材料 | 成像质量 |

这些挑战的叠加效应是：High-NA EUV 的"从实验室到量产"之路，可能比 Low-NA EUV（ASML NXE 系列）更长、更曲折。Low-NA EUV 从第一台设备交付（2017 年）到高产量制造（2020-2021 年）花了约 3-4 年。High-NA 的第一台设备已于 2023 年底交付给 Intel，按照同样的时间线，量产应在 2027-2028 年——但偏振效应等新问题可能延长这一周期。

## 对产业链的连锁影响

### 对 ASML 的影响
ASML 需要在其计算光刻软件中集成偏振感知的仿真能力。这不是简单的软件更新——它需要与 Zeiss（光学系统供应商）紧密协作，确保光学设计和仿真模型的一致性。ASML 2025 年的计算光刻收入已超过 10 亿欧元，偏振效应的处理将是其下一代软件的核心卖点。

### 对晶圆厂的影响
Intel、TSMC、三星需要重新校准其 High-NA 工艺开发的仿真基础设施。偏振效应的准确建模将影响：
- OPC（光学邻近校正）的精度
- ILT（反向光刻技术）的掩模设计
- 工艺窗口的大小和鲁棒性

### 对 EDA 工具的影响
Synopsys、Cadence、Siemens EDA 需要在其光刻仿真工具中支持偏振感知的 STCC 模型。这是计算光刻工具链的一次系统性升级。

## 判断

**偏振效应不会阻止 High-NA EUV 的部署，但它会影响部署速度和初期良率**。

更深层的观察是：每一代光刻技术的推进，"可以忽略的近似"越来越少。从 193nm 到 EUV 是波长跳变，从 Low-NA 到 High-NA 是角度跳变，每次跳变都让之前可以偷懒的物理效应变成不可回避的工程问题。

摩尔定律的延续越来越不像工程问题，而像基础物理的博弈——每前进一步，都需要在更深的物理层面上做更精确的事情。STCC 公式的偏振扩展只是这场博弈的最新一手棋。

---

**参考资料：**

1. [Tanabe et al., J. Micro/Nanopatterning, Vol. 25, Issue 3, 031604, May 2026](https://doi.org/10.1117/1.JMM.25.3.031604) - 原始论文
2. [Semiconductor Engineering - High-NA EU Lithography: Extending The STCC Formula](https://semiengineering.com/high-na-eu-lithography-extending-the-stcc-formula-science-tokyo/) - 2026年5月
3. [ASML High-NA EUV TWINSCAN EXE:5000](https://www.asml.com/en/products/euv-lithography-systems/twinscan-exe-5000) - 产品技术规格
4. [SPIE Advanced Lithography + Patterning 2026](https://spie.org/conferences-and-exhibitions/advanced-lithography-and-patterning) - 会议来源

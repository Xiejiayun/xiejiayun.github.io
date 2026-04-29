---
title: "近存计算3D堆叠芯片：LLM推理的下一个范式转移"
description: "爱丁堡大学、北大、剑桥联合研究揭示近存计算微架构如何突破LLM推理的内存墙瓶颈"
date: 2026-04-29
slug: "near-memory-3d-stacked-llm-chips-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 半导体
    - 芯片架构
    - LLM推理
    - 近存计算
draft: false
---

## LLM推理的真正瓶颈：不是算力，是搬数据

如果你问一个GPU工程师"为什么LLM推理这么贵"，他的回答可能不是"算力不够"，而是**"数据搬不动"**。

SemiEngineering最新报道直指核心："Moving data has become the top challenge inside data centers。" 数据中心最大的挑战不再是计算，而是数据搬运。

为什么？因为LLM推理有一个独特的计算特征：**解码阶段（Decoding）是内存带宽受限的（Memory-bound），而不是计算受限的（Compute-bound）。**

每生成一个Token，模型需要从显存中读取完整的KV Cache和模型权重——对于一个70B参数的模型，这意味着每个Token需要搬运超过140GB的数据。即使是NVIDIA最高端的GPU，其HBM带宽也只有几TB/s，这成为了不可逾越的物理瓶颈。

**解决方案不是更快的计算单元，而是让计算靠近数据。**

## 学术突破：微架构-调度协同设计

爱丁堡大学、北京大学、剑桥大学等机构联合发表的论文"Rethinking Compute Substrates for 3D-Stacked Near-Memory LLM Decoding"提出了一个激进的方案：**不要把数据搬到GPU上计算，而是在内存旁边直接计算。**

这不是一个新概念——近存计算（Near-Memory Computing，NMC）已经讨论了几十年。但这篇论文的创新在于：**它第一次系统性地针对LLM解码任务，进行了微架构和调度的协同设计。**

| 对比维度 | 传统GPU方案 | 3D堆叠近存计算方案 |
|---------|-----------|-------------------|
| 数据搬运距离 | 内存→互连→计算核心（毫米级） | 内存层→计算层（微米级） |
| 带宽瓶颈 | HBM接口带宽（~几TB/s） | 3D堆叠TSV带宽（~数十TB/s） |
| 能效比 | 数据搬运占总能耗60%+ | 数据搬运能耗降低10-100倍 |
| 计算密度 | 受封装面积限制 | 垂直堆叠扩展计算层 |
| 适用场景 | 通用GPU计算 | 专门优化LLM解码 |
| 灵活性 | 高（可编程） | 中等（领域专用优化） |

关键创新点在于**调度器的协同设计**。论文发现，传统GPU调度器假设计算和内存是分离的，这在近存计算架构中完全不适用。新的调度策略需要考虑：

1. **数据局部性最大化**——将相关的KV Cache分片和计算任务放在同一个3D堆叠单元中
2. **层间通信最小化**——减少堆叠层之间的数据交换
3. **异构计算分配**——Attention计算在近存单元执行，FFN计算可以在传统计算核心执行

## TSMC的系统级视野：芯片设计的范式转移

几乎同时，TSMC在其2026年Technology Symposium上发出了一个明确信号：**AI时代的芯片设计已经从"做更好的晶体管"转向"做更好的系统"。**

SemiWiki对TSMC演讲的深度分析指出，TSMC认为AI的主要约束已经不再是模型能力，而是**运行这些模型所需的系统**——包括封装、互连、散热、供电等系统级挑战。

这与学术界的近存计算研究形成了完美的呼应。TSMC正在推进的几项关键技术：

- **CoWoS-L（Chip-on-Wafer-on-Substrate Large）**：支持更大面积的2.5D封装，容纳更多HBM
- **SoIC（System on Integrated Chips）**：3D堆叠技术，正是近存计算的物理实现基础
- **先进封装散热方案**：Georgia Tech等机构研究的氧化铝纳米线增强散热方案

## Chiplet架构：模块化的未来

SemiWiki另一篇深度报道"Scalable Network-on-Chip Enables a Modular Chiplet Platform"揭示了另一个关键趋势：**Chiplet（芯粒）架构正在从概念走向标准化**。

传统的单片SoC（System-on-Chip）面临物理极限：芯片越大，良率越低，成本指数增长。Chiplet方案将一个大芯片拆分成多个小芯片，通过先进封装互连。

对于LLM推理，Chiplet的意义在于：

1. **异构集成**——可以将计算芯粒（先进工艺）和内存芯粒（成熟工艺）混合封装
2. **可扩展性**——通过增加芯粒数量线性扩展算力和内存容量
3. **成本优化**——不同芯粒可以使用不同工艺节点，优化成本结构

## 稀疏性硬件：另一个被忽视的方向

IEEE Spectrum报道了"Better Hardware Could Turn Zeros into AI Heroes"——利用AI计算中大量存在的零值来加速推理。

这与近存计算形成了互补关系。LLM推理中，激活值（Activation）通常有50-90%是零或接近零的值。如果硬件能够原生跳过这些无效计算：

- **计算量减少2-10倍**
- **内存带宽需求等比下降**——不需要搬运零值数据
- **与近存计算叠加效果**——在数据旁边直接做稀疏计算，双重优化

## "可重写芯片"：灵活性与效率的平衡

IEEE Spectrum还报道了一个有趣的创新："The Chip That Made Hardware Rewriteable"——一种可以在部署后重新配置的芯片架构。

这对近存计算的意义在于：LLM模型迭代非常快，专用硬件面临的最大风险是**被新模型架构淘汰**。可重写芯片提供了一个折中方案——在保持近存计算效率优势的同时，允许硬件适应新的模型架构。

## 我的判断

**近存计算3D堆叠将在2-3年内从学术研究走向商业芯片产品。**

理由如下：

1. **需求确定**——LLM推理的Memory-bound特征是物理规律决定的，不会改变
2. **制造可行**——TSMC的SoIC、三星的X-Cube等3D堆叠技术已经成熟
3. **经济合理**——数据搬运占AI推理能耗的60%+，近存计算直接攻击最大成本项
4. **竞争驱动**——NVIDIA、AMD、Intel以及一众AI芯片创业公司都在这个方向布局

我的预测：

1. **2026年底**，至少一家AI芯片公司将发布基于3D堆叠近存计算的推理芯片
2. **2027年**，NVIDIA将在其下一代架构中引入近存计算元素
3. **LLM推理的每Token成本将在未来2年再下降一个数量级**——近存计算是关键推动力

## 给技术决策者的建议

1. **关注芯片架构趋势**——不要只看GPU TFLOPS，内存带宽和能效比是更重要的指标
2. **评估推理框架的硬件适配性**——vLLM等框架是否支持新的硬件后端将影响你的技术选型
3. **考虑推理专用硬件**——如果你有大规模推理需求，近存计算芯片可能在2年内提供10倍的成本优势

---

## 参考链接

- [SemiEngineering - Microarchitecture Tailored to 3D-Stacked Near-Memory Processing LLM Decoding](https://semiengineering.com/near-memory-llm-decoding/)
- [SemiWiki - The Shift to System-Level AI Drives Next-Generation Silicon](https://semiwiki.com/tsmc-2026-system-level-ai/)
- [SemiWiki - Scalable Network-on-Chip Enables a Modular Chiplet Platform](https://semiwiki.com/chiplet-noc-platform/)
- [SemiEngineering - New CPU Memory Module](https://semiengineering.com/new-cpu-memory-module/)
- [IEEE Spectrum - Better Hardware Could Turn Zeros into AI Heroes](https://spectrum.ieee.org/sparse-hardware-ai-2026)
- [IEEE Spectrum - The Chip That Made Hardware Rewriteable](https://spectrum.ieee.org/rewriteable-chip-2026)
- [SemiEngineering - Alumina Nanowires for Thermal Management in Advanced Packaging](https://semiengineering.com/alumina-nanowires-thermal/)

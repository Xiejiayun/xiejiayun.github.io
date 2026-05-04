---
title: "蛋白质语言模型的下半场：从结构预测走向功能与设计"
description: "AlphaFold 2/3 把结构问题打开后，真正的科学瓶颈从'折叠成什么样'转向'做什么、能不能设计出来'。本文梳理 ESM-3、RFdiffusion、Boltz-2 这一代模型如何把蛋白质从生物学问题变成可工程化对象。"
date: 2026-05-04
slug: "protein-language-models-function-prediction-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 蛋白质
    - 计算生物学
    - 学术前沿
    - 生成模型
draft: false
---

## 一、AlphaFold 之后的真问题

2021 年 AlphaFold 2 让"给序列预测三维结构"从一个开放科学难题变成一个工程问题。但生物学界很快意识到：**结构只是开始**。一个蛋白质有结构不代表知道它的功能，更不代表能按需设计一个新蛋白质来执行特定任务。2024-2026 这三年，蛋白质 AI 的研究重心彻底转向了三件事：

1. **功能预测**：给定序列/结构，预测它催化什么反应、与谁结合、亲和力多少。
2. **从头设计**(de novo design)：给定一个想要的功能，反向生成一段序列。
3. **湿实验闭环**：把预测/设计的结果在自动化实验室快速验证，形成数据飞轮。

这三件事中，第一件最难，第二件商业价值最大，第三件决定模型能不能持续进化。

## 二、模型代际：从 ESM 到 ESM-3 的范式转换

EvolutionaryScale 在 2024 年发布的 ESM-3 是这一代的标志性工作。它把蛋白质表示从单纯的"氨基酸序列"扩展为**三模态联合**：序列、结构(离散化为 structure tokens)、功能(SASA、二级结构、活性位点等注释)。

| 模型 | 年份 | 参数量 | 训练目标 | 主要能力 |
|------|------|--------|----------|----------|
| ESM-2 | 2022 | 15B | 掩码序列建模 | 序列嵌入、结构预测 |
| AlphaFold 3 | 2024 | ~10B | 配对距离扩散 | 复合物结构(蛋白+核酸+小分子) |
| ESM-3 | 2024 | 98B | 多模态掩码 | 序列↔结构↔功能任意填空 |
| RFdiffusion | 2023 | 小 | 结构空间扩散 | 给定 motif 生成骨架 |
| Boltz-2 | 2025 | 开源 | AlphaFold3 复刻+优化 | 开源的高质量复合物预测 |
| Chai-1 | 2024 | 闭源 | AF3 路线 | 商业 API 与药物筛选 |

ESM-3 真正的突破在于"任意填空"范式：你可以给定一段序列+一个想要的活性位点几何，模型补全剩下的结构和未确定的氨基酸。这从原理上把"设计"问题统一到了"条件生成"框架里。

## 三、为什么功能预测仍然没解决

外行经常以为有了结构就能算功能。事实上，**结构到功能的映射极度多对一且高度上下文依赖**：

```
   序列空间   ──→  结构空间   ──→   功能空间
   (~20^N)        (~10^4 fold)      (~10^∞ context)
       │              │                  │
   AF/ESM 解决   分类学清晰      仍是开放问题
   ~95% 准确度   有 CATH/SCOP    没有标签体系
```

具体困难在三处：
- **动态构象**：很多酶的活性来自纳秒-微秒尺度的构象变化，单帧静态结构无法刻画。AlphaFold 给你的是中位结构，不是功能态。
- **环境依赖**：同一个蛋白质在细胞质、膜上、复合物中行为完全不同。当前模型几乎全部假设孤立蛋白。
- **数据稀缺**：UniProt 有 2.5 亿序列，但有实验功能注释的不到 1%；高质量动力学数据(kcat、Km)更少，常常只有 10^4 量级。这是典型的"模型饿死于数据"。

谁能解决数据问题，谁就能赢功能预测的下半场。这正是 Insitro、Recursion、Isomorphic Labs 这些公司大举建设自动化湿实验平台的原因——不是为了便宜，而是为了独占功能数据。

## 四、从头设计：David Baker 路线已经赢了

2024 年 David Baker 拿诺贝尔化学奖之后，"从头设计蛋白质"从科学幻想变成了工程现实。RFdiffusion + ProteinMPNN 这一套组合，已经能稳定设计出：

- 与指定 epitope 高亲和力结合的 binder(纳摩尔级 K_d)
- 含特定金属/底物结合口袋的人工酶(虽然 kcat 还远不及天然酶)
- 自组装的纳米笼、跨膜通道
- 光控、pH 控的开关蛋白

商业落地最快的是 binder 设计，因为它的目标函数最清晰：高亲和力、高特异性、低免疫原性。Generate Biomedicines、Xaira Therapeutics、EvolutionaryScale 旗下的应用部门都在做。**预计 2027 年会有第一个完全 de novo 设计的治疗性蛋白进入临床 II 期**，这将是医药史上的拐点。

但人工酶仍然落后。天然酶经过亿年进化，活性位点的精细几何与动力学是当前模型难以重现的。Baker 实验室 2025 年最好的人工 retro-aldolase 比天然版本慢 10^4 倍，差距巨大。

## 五、湿实验闭环：被低估的护城河

模型的能力上限取决于训练数据，蛋白质数据 99% 来自湿实验。这就是为什么 **"AI + 自动化生物实验室"** 是这个领域真正的护城河：

- Emerald Cloud Lab、Strateos、Arctoris 提供云端实验调用
- Insitro 自建 100,000 平米的全自动 BSL-2 设施
- Isomorphic 与 Eli Lilly、Novartis 的合作本质是借大药企的实验产能换药物管线分成

这些数据不会进 UniProt，会变成各家私有的功能-序列数据集，进而训练出公司专有的微调模型。**学术界与商业界的能力差距会在 2026-2028 年被永久拉开**——这点和 LLM 领域的 OpenAI vs 学术界惊人相似。

## 六、几个反主流的判断

1. **AlphaFold 3 不是终点，而是过渡品**。下一代会是"分子动力学 + 扩散模型"的混合体，能输出构象集合而不是单一结构，预计 2027 出现。
2. **"通用蛋白质大模型"会被打散**。功能预测、binder 设计、酶设计会各自有专家模型，统一模型在所有任务上都不会是 SOTA。
3. **开源会赢学术，但输给商业**。Boltz-2、ESM-2 这些开源模型已经让学术研究者跟得上前沿，但缺数据闭环让他们永远赶不上 Insitro/Isomorphic 的下一代。

## 七、结语

蛋白质 AI 已经从"能预测吗"进入"能设计吗、能上市吗"的阶段。这是一个真正的"AI for Science"成功案例——不是 demo、不是 PR，而是会在五年内改变一个万亿美元行业的真实变革。如果你只关注 LLM 的喧嚣而错过这条线，会错过过去十年最大的科学—产业耦合机会。

---

### 参考资料

- Hayes T. et al., "Simulating 500 million years of evolution with a language model" (ESM-3), Science 2025 — https://www.science.org/doi/10.1126/science.ads0018
- Abramson J. et al., "Accurate structure prediction of biomolecular interactions with AlphaFold 3", Nature 2024 — https://www.nature.com/articles/s41586-024-07487-w
- Baker Lab, "RFdiffusion: De Novo Protein Design" — https://www.bakerlab.org/
- Boltz-2 Open Source Project — https://github.com/jwohlwend/boltz

---
title: "芯片验证的数学转向：当形式化方法从学术象牙塔走进 EDA 主战场"
description: "首次流片成功率跌至 20 年最低，验证成本吞噬 70% 工程预算——形式化验证正在从'锦上添花'变成'生死攸关'。"
date: 2026-05-08
slug: "formal-verification-chip-design-mathematical-turn-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 形式化验证
    - EDA工具链
    - 芯片设计
    - 数学方法
draft: false
---

## 引言：14% 的首次成功率

Wilson Research Group（Siemens EDA 赞助）2024 年的行业调查报告中有一个数字足以让芯片公司的 CFO 失眠：**ASIC/SoC 项目的首次流片成功率仅为 14%**——这是 20 多年追踪记录中的最低值。

在先进制程节点上，一套光掩膜（mask set）的成本以千万美元计。流片失败意味着数月的时间和巨额资金付诸东流。没有"先上线再打补丁"的选项——硅片一旦制造出来就无法修改。

与此同时，芯片设计中**60-70% 的工程工作量被验证环节消耗**。验证——确认设计按预期工作——早已不是设计流程的附属品，而是实际上的主体。

在这个背景下，一种长期被视为"学术玩具"的方法论正在加速走向工业主战场：**形式化验证（Formal Verification）**。

## 什么是形式化验证？

形式化验证的核心思想是：**用数学证明取代仿真测试，穷举式地验证设计的正确性**。

传统仿真（simulation）的工作方式是生成测试向量，输入到设计模型中，检查输出是否符合预期。这就像用有限的样本点去估计一个函数——你可以覆盖常见场景，但永远无法保证覆盖了所有边界条件。

形式化验证的工作方式完全不同。它不生成测试向量，而是将设计转换为数学模型，然后**证明或证伪**特定属性（properties）在所有可能的输入序列下都成立。

### 三大技术路线

| 方法 | 原理 | 优势 | 局限 |
|------|------|------|------|
| **模型检验（Model Checking）** | 穷举遍历状态空间，检查时序逻辑属性 | 全自动，能生成反例 | 状态空间爆炸：符号模型限制在数百比特 |
| **定理证明（Theorem Proving）** | 从系统描述和规约生成数学证明义务 | 可扩展性更强 | 需要专家引导 |
| **属性检查（Property Checking）** | 工程师用 SVA/PSL 编写断言，形式引擎穷举验证 | 实用性强，可集成到现有流程 | 依赖属性定义的完备性 |

实际工业应用中，**属性检查/断言式形式化验证（Assertion-Based Formal）** 是目前采用最广的方式。工程师用 SystemVerilog Assertions（SVA）或 Property Specification Language（PSL）编写设计应满足的属性，形式引擎穷举地证明或证伪每个属性。当属性被证伪时，引擎还能生成反例——一条具体的信号序列，展示设计如何违反了该属性。

## 为什么是现在？

### 1. 复杂度爆炸

现代 SoC 集成了数十个 IP 核、复杂的 NoC（片上网络）、异构计算单元和各种总线协议。交互空间呈指数增长，传统仿真的覆盖率越来越难以让人放心。

### 2. 安全关键领域的强制要求

汽车（ISO 26262）和航空航天（DO-254）等安全关键领域已经开始**强制要求**在验证流程中引入形式化方法。一个 ADAS 芯片中的一个未被发现的边界条件错误，可能导致真实的人身伤害。

### 3. 软件公司造芯的阵痛

Wilson Research Group 的调查特别指出：**系统公司（汽车 OEM、超大规模云厂商、消费电子品牌）正在自研芯片，但在验证上严重受挫**。这些"软件优先"的公司倾向于将验证视为开销（overhead），而非"硅片成功的生命线"。

当 Google、Amazon、Tesla 都在设计自己的定制芯片时，他们正在以惨痛的代价学习一个半导体行业的老道理：**芯片不是写完 RTL 就行的，验证才是真正的战场**。

### 4. RISC-V 的推动效应

开源 ISA 的普及使得更多团队能够设计自己的处理器核心，但也意味着更多的设计需要验证。RISC-V 生态正在加速形式化验证的采用——开放的指令集架构使得形式化验证核心实现变得更加可行。

## EDA 三巨头的形式化布局

| 厂商 | 主要形式化工具 | 特色 |
|------|--------------|------|
| **Synopsys** | VC Formal™、VC SpyGlass™ | 与 GenAI 结合自动生成断言（与 Marvell 合作） |
| **Cadence** | JasperGold、Conformal | 业界最早的商业形式化平台之一 |
| **Siemens EDA** | Questa Formal、OneSpin 360 DV | 统一验证平台 Questa One |

Synopsys 的一个值得关注的动向是：他们正在与 Marvell 合作，**用 GenAI 自动生成形式化验证的断言**。这可能是 AI 在 EDA 领域最有实际价值的应用之一——将形式化验证的门槛从"需要数学博士"降低到"需要设计意图描述"。

## Axiomise：让数学毕业生成为验证工程师

SemiWiki 2026 年 5 月的文章介绍了 Axiomise 的 Robert Simpson——一个数学专业毕业生转行成为形式化验证工程师的案例。Axiomise 的创始人认为，形式化验证需要的核心能力不是编程，而是**抽象思维、逻辑推理和穷举式思考**——这些恰恰是数学训练的核心。

Axiomise 开设了面向数学毕业生的半年度培训计划，并开发了 neoProve 工具用于 NoC 设计的形式化验证。他们的核心论点是：形式化验证能发现**所有非形式化验证方法都会遗漏的缺陷**——这不是效率提升，而是能力边界的扩展。

## 形式化 vs 仿真：互补而非替代

| 维度 | 仿真 | 形式化验证 |
|------|------|-----------|
| 覆盖范围 | 采样（随机/定向测试） | 穷举——覆盖所有可能的输入序列 |
| 发现的缺陷类型 | 常见/预期场景 | 极端边界条件、稀有交互 |
| 准备工作 | 需要测试平台（testbench）、激励生成、测试计划 | 不需要 testbench；需要编写属性/断言 |
| 可扩展性 | 对大型设计扩展良好 | 状态空间爆炸限制全芯片应用 |
| 入门门槛 | 较低 | 需要更强的数学/逻辑能力 |

行业共识是：**两者互补使用效果最佳**。形式化验证在模块级和协议级表现最强——验证 cache coherence 协议、总线仲裁逻辑、状态机正确性。仿真在全芯片系统级验证中仍然不可或缺。

## 核心判断

1. **形式化验证将从"可选"变成"必选"**。随着流片成本继续攀升、安全关键应用继续扩展，芯片公司无法承受首次流片失败的代价。形式化验证是唯一能在设计阶段提供穷举正确性保证的方法。

2. **GenAI + 形式化验证是 EDA 领域的高价值交叉点**。用 LLM 自动生成 SVA 断言可以大幅降低形式化验证的人力门槛，同时保留其数学严谨性。这可能比"AI 生成 RTL"更早产生实际价值。

3. **人才缺口是最大瓶颈**。形式化验证需要的数学直觉和逻辑思维很难速成。Axiomise 从数学专业招人的做法值得其他公司参考——EE 背景不是唯一的入口。

4. **RISC-V 将加速形式化验证的普及**。当更多团队设计自己的处理器核心时，对高效验证方法的需求会急剧增长。开放 ISA + 形式化验证的组合可能成为标配。

5. **"测试覆盖率 100%"是虚假安全感**。100% 的代码覆盖率不等于 100% 的功能覆盖率——仿真永远无法遍历所有输入组合。形式化验证提供的是不同维度的保证：在指定属性范围内的**数学证明级**正确性。

---

## 参考来源

1. [Bringing mathematical rigour in the world of hardware – a journey into Formal Verification - SemiWiki](https://semiwiki.com/semiconductor-services/axiomise/369080-bringing-mathematical-rigour-in-the-world-of-hardware-a-journey-into-formal-verification/) (2026-05-07)
2. [Why First-Silicon Success Is Getting Harder for System Companies - Siemens EDA / Wilson Research Group](https://blogs.sw.siemens.com/verificationhorizons/2025/09/03/why-first-silicon-success-is-getting-harder-for-system-companies/) (2025-09)
3. [VC Formal - Static & Formal Verification - Synopsys](https://www.synopsys.com/verification/static-and-formal-verification.html)
4. [Formal Verification - Wikipedia](https://en.wikipedia.org/wiki/Formal_verification) — 技术原理参考
5. [Chip Industry Week In Review - SemiEngineering](https://semiengineering.com/chip-industry-week-in-review-137/) (2026-05)

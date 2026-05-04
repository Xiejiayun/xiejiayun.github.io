---
title: "从仿真检查点到连续物理：芯片设计正在经历自 SPICE 以来最大的范式转移"
description: "SemiEngineering 一组关于'连续物理仿真'的新文章揭示了一个被忽视的工程革命：传统'离散检查点'的芯片验证流程正在被基于神经算子和 PDE 求解器的'连续物理'方法取代。这背后是 5nm 以下节点不可承受的验证成本，以及物理 AI 在 EDA 内部反向掀起的代际更替。"
date: 2026-05-04
slug: "continuous-physics-chip-simulation-paradigm-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 半导体
    - EDA
    - 仿真
    - 神经算子
draft: false
---

## 一、芯片验证的窒息时刻

如果你最近和任何一家 5nm 以下节点 SoC 团队聊过，会听到同一个抱怨：**验证 / 仿真已经吃掉了流片前 70% 以上的工期和成本，而且还在涨。**

SemiEngineering 最近一组文章——*From Simulation Checkpoints To Continuous Physics*、*Designing Chips In The Context Of Rapidly Evolving AI*、Bronco AI 关于全片 SoC 调试的演讲——共同勾画了一个工程领域的窒息时刻：

- 一颗 N3 节点的复杂 SoC，**signoff 阶段所有物理仿真任务**（thermal, EM, IR-drop, multi-physics SI/PI, aging）累计需要 **超过 4000 万 CPU-小时**；
- 同样的设计放到 N2 节点，根据 TSMC 内部模型，仿真规模再涨 **2.6×**；
- 如果继续沿用今天的"做一组 corner → 跑 → 改设计 → 再跑下一组 corner"的离散检查点（discrete checkpoint）流程，**N2 之后将无法在合理工期内完成 signoff**。

这不是"再买几台服务器"能解决的问题。这是物理仿真的算法复杂度撞上摩尔定律的算法复杂度——两条曲线交叉的位置就在 2026–2028。

## 二、什么是"离散检查点"，为什么它撑不住了

传统芯片物理验证的工作流大概是这样：

```
RTL → Synthesis → Place & Route → Static Timing → 
  ↓
固定 N 组 Corner（PVT, Aging, Workload）
  ↓
对每组 Corner 做：
   - SPICE-level 电路仿真
   - 多物理场仿真（thermal, IR-drop, EM）
   - 时序签核
  ↓
若任一 Corner fail → 改设计 → 全部重跑
```

这个流程的核心假设是：**Corner 数量是有限的、离散的、可枚举的**。在 28nm 时代这是合理近似，因为工艺漂移、热-电耦合、老化效应可以用 5–8 组角案例近似覆盖。

但在 N3 / N2 / A14 节点，这个假设崩了：

- **物理耦合非线性**：thermal 影响 carrier mobility，mobility 改变 timing，timing 又改变功耗分布，功耗回头改变 thermal——这是一个连续微分方程，离散 5 个 corner 已经不够；
- **AI workload 的瞬态变化**：芯片不再跑稳态负载，而是 LLM 推理这种"突发-冷却-突发"的强瞬态，瞬态特征无法用稳态 corner 表达；
- **老化的连续性**：HCI、BTI、EM 都是连续累积过程，在 5 年寿命内的任何一个瞬时切片都可能触发新故障模式，离散采样会漏掉。

结果就是：**为了"覆盖到"，必须不断增加 corner 数量。N2 节点上典型 SoC 的 sign-off corner 数已经从 N5 时代的 ~150 涨到 ~3000+**。每加一个 corner，仿真时间线性涨，迭代次数指数涨。

这就是 *Simulation Checkpoints* 范式的死期。

## 三、Continuous Physics：神经算子 + PDE 求解器的新栈

新范式的核心思路是：**把"枚举 corner"换成"在物理参数空间上连续求解一次"**。

具体技术栈大致是：

| 层级 | 传统方法 | Continuous Physics 新方法 |
|------|---------|--------------------------|
| 电路层 | SPICE per corner | 神经算子代理（FNO、DeepONet）|
| 多物理场 | FEM per corner | 物理-informed 神经网络（PINN）|
| 老化 | 离散时间快照 | 连续时间动力系统建模 |
| Signoff | 枚举验证 | 概率性"分布覆盖"证明 |
| 调试 | 后验日志分析 | 在线连续监控 + 因果回溯 |

关键技术点：

### 神经算子（Neural Operators）替代部分 SPICE

FNO（Fourier Neural Operator）和 DeepONet 这类神经算子，能在训练后用 ~10ms 给出原本需要 SPICE 跑数小时的电路响应。在 2024–2025 学术界证明了精度足够（< 2% 误差），2026 年 Cadence、Synopsys 已经在内部 toolchain 集成。

### 物理 informed 神经网络处理多物理场耦合

PINN 把 PDE 直接写进 loss function，可以在不离散化网格的情况下求解 thermal-electrical-aging 耦合方程。Bronco AI 演示的"15 分钟全片 SoC 调试"背后正是这一类方法。

### Continuous Coverage 替代 Corner Coverage

传统验证讲"我覆盖了 N 个 corner"，新范式讲"我证明在 PVT-aging-workload 联合分布上，failure 概率 ≤ 10⁻⁹"。这要求 EDA 工具输出 **概率性 signoff 报告** 而非二元 pass/fail。监管机构（汽车 ISO 26262、医疗 IEC 62304）已经开始接受这种证明形式。

## 四、为什么这件事 EDA 巨头也藏不住

EDA 历来是寡头垄断（Cadence、Synopsys、Siemens EDA）。新范式在原则上利好巨头——他们有数据、有客户、有积累。但 *Solving the EDA tool fragmentation crisis* 一文指出一个反直觉的现象：

**Continuous Physics 范式让初创公司第一次有了切入点。**

原因有三：

1. **算法栈完全不同**：神经算子 + PINN 不是传统 EDA 工程师的舒适区，巨头的内部团队反应慢；
2. **数据需要工艺厂深度合作**：而工艺厂（TSMC、三星、Intel Foundry、SMIC）更愿意和小团队做 POC，避免被单一 EDA 巨头锁定；
3. **客户已经撑不住**：IC 设计公司（Apple、英伟达、华为海思、地平线）愿意为节省 50% 验证时间付出溢价，绕开 EDA 巨头的 traditional roadmap。

Bronco AI、Quantiphi、还有几家在 stealth 阶段的初创公司，在 2025–2026 拿到了一系列大客户的早期验证合同。这是 1990 年代 PrimeTime 取代手工 STA 之后，EDA 行业最大的一次从下而上颠覆机会。

## 五、对中国半导体的特殊意义

这件事对中国半导体生态有极不寻常的战略价值。

中国 EDA 长期被 Cadence/Synopsys/Siemens 卡脖子，过去十年内的国产化（华大九天、概伦、芯华章）只能在传统范式里做"追赶"。但 **Continuous Physics 是一次"换跑道"**：

- 算法基础（神经算子、PINN）的论文公开、可复现；
- 训练数据可以通过国内工艺厂（中芯国际、华虹）的合作积累；
- 国内 AI 训练算力相对充足（昇腾、寒武纪、海光），不受 EDA 软件 license 卡脖子；
- 国内 IC 设计客户（华为、寒武纪、地平线、燧原）有强烈的"想用国产工具"的政治和商业动机。

如果国产 EDA 公司在 2026–2027 押对 Continuous Physics 这条新栈，**完全有可能在 N3 / 14nm DUV 这个区间获得真正的工具自主权**——这是过去三十年都没出现过的窗口。

## 六、三个判断

1. **2027 年第一颗"完全用 Continuous Physics 流程 signoff"的商用大芯片会出现**。最可能的候选是英伟达的某款数据中心 GPU 或苹果自研芯片，因为他们既有规模又有内部 ML 工程能力。

2. **传统 corner-based signoff 流程会在 2028–2030 进入退役通道**。先在 AI 加速器、汽车 SoC 上消失，再扩展到通用 SoC。模拟与射频前端会保留传统流程更久。

3. **EDA 行业的市值结构将重洗**。Cadence、Synopsys 短期受益（卖新工具），但中期会面临一批 AI-native EDA 初创的蚕食。中国国产 EDA 的窗口在 2026–2028 之间打开，错过这个窗口将意味着下一个十年依然在追赶。

---

**SPICE 在 1973 年发明，定义了之后 50 年的芯片验证流程**。Continuous Physics 不是又一次工具升级，而是 SPICE 之后第一次范式级的替代——它的胜负将决定下一个十年谁能造出 N2 以下节点的芯片。这个故事正在 EDA 行业内部安静地发生，外部很少人意识到它的重量。

---

## 引用来源

- [From Simulation Checkpoints To Continuous Physics — SemiEngineering](https://semiengineering.com/)
- [Designing Chips In The Context Of Rapidly Evolving AI — SemiEngineering](https://semiengineering.com/)
- [Bronco AI Webinar: Full-Chip SoC Debug in 15 Minutes — SemiWiki](https://semiwiki.com/)
- [Solving the EDA tool fragmentation crisis — SemiWiki](https://semiwiki.com/)
- [Li et al., *Fourier Neural Operator for Parametric PDEs*, arXiv:2010.08895](https://arxiv.org/abs/2010.08895)
- [Raissi et al., *Physics-Informed Neural Networks*, J. Comp. Phys. 2019](https://www.sciencedirect.com/science/article/pii/S0021999118307125)
- [TSMC N2 Process Disclosure, IEDM 2024](https://www.tsmc.com/)

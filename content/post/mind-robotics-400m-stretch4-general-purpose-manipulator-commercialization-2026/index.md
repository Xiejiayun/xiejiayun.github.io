---
title: "Mind Robotics 4 亿融资 vs Hello Robot 3 万美元 Stretch 4：通用机器人商业化的两条赌注路线"
description: "2026 年 5 月同一周，前 Rivian CEO 创办的 Mind Robotics 拿到 4 亿美元押注'foundation model + 制造业全栈'，而 Hello Robot 发布售价 29950 美元、可工作 8 小时的 Stretch 4——同样追求'通用'，路线却完全相反。本文拆解为什么 2026 是通用机器人路线分叉年。"
date: 2026-05-14
slug: "mind-robotics-400m-stretch4-general-purpose-manipulator-commercialization-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 具身智能
    - 通用机器人
    - Mind Robotics
    - Hello Robot
    - 制造业自动化
    - Rivian
    - 风险投资
    - 物理AI
draft: false
---

## 引子：同一周，两份相反的"通用机器人"答卷

2026 年 5 月 12 日，Hello Robot 发布 Stretch 4——售价 29,950 美元，开源、单臂、轮式底盘，能连续工作 8 小时，已经卖给 30 多个研究机构。

2026 年 5 月 14 日，Mind Robotics 宣布新一轮 4 亿美元融资，累计融资突破 10 亿美元，由 Kleiner Perkins 领投，Andreessen Horowitz、Accel、Meritech 跟投。这家公司由 Rivian 联合创始人 RJ Scaringe 在 2025 年 11 月成立，第一个客户是 Rivian 自己。Mind Robotics 没有发布任何机器人照片，他们的官网上只有一行字：

> "We are not building single-task machines. By leveraging modern progress in physical AI, we are developing a platform that generalizes across core tasks and scales across manufacturing domains."

**同一周内、同一个市场（"通用机器人"）、同一个目标（在工厂落地），两家公司给出的策略却几乎完全相反**。这种分叉非常罕见——它意味着行业还没有形成共识，资本却已经下了两边的注。

本文要回答的核心问题：

1. 这两条路线在技术、商业模式、单位经济上的本质区别是什么？
2. 为什么 2026 年是"通用机器人"路线必须分叉的年份？
3. 5 年后哪一边会赢——还是它们根本不在一个赛道？

## 一、两份产品规格的直接对比

先把数字摆上桌：

| 维度 | Hello Robot Stretch 4 | Mind Robotics（未命名） |
|------|----------------------|------------------------|
| 发布时间 | 2026-05-12（已售卖） | 待定（成立 6 个月，未公开形态） |
| 价格 | $29,950 / 台 | 不公开，估计 $50k-200k/台 |
| 形态 | 单臂 + 轮式 + 伸缩立柱 | 未知（推测多臂 + 移动） |
| 续航 | 8h + 自动充电桩 | 未知 |
| 软件栈 | ROS 2 + 开源 Stack | 自研 foundation model |
| 训练数据 | 用户自带 + 社区共享 | Rivian 工厂全量遥操数据 |
| 目标客户 | 研究者、高校、应用开发者 | 大型制造商 |
| 商业模式 | 卖硬件 + 软件 SDK | RaaS（Robot-as-a-Service）+ 集成 |
| 累计融资 | <$50M | >$1B |
| 首批客户 | 30+ 研究机构 | Rivian 一家（高密度部署） |
| 单台收入预期 | $30k 一次性 + 服务 | $50k-100k/年（RaaS） |

这不是两个产品的对比，**是两套商业逻辑的对比**。

## 二、路线 A：Hello Robot 的"研究者基础设施"

Hello Robot 创立于 2017 年，CEO Aaron Edsinger 出身 MIT Humanoid Robotics Group。这家公司过去 9 年的核心战略可以一句话总结：**做研究者愿意用、应用开发者愿意改的"通用机器人 Linux 盒子"**。

Stretch 系列的形态选择体现了这种哲学：

```text
┌─────────────────────────────────────────────────────────┐
│              Stretch 4 形态决策树                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  形态: 伸缩立柱 + 单臂                                  │
│   └─ 拒绝了双足/人形（成本×10、不稳定）                 │
│   └─ 拒绝了双臂（大多数家务/桌面任务单臂够用）          │
│                                                         │
│  传感: 2× 半球 3D LiDAR + 3× 高分辨率相机 + 6× 激光线   │
│   └─ "Waymo-style sensor-rich"——多冗余、可解释          │
│   └─ 拒绝了"纯视觉 + 大模型"路线（成本太高）            │
│                                                         │
│  软件: ROS 2 + Stretch AI Body + 开源 SDK              │
│   └─ 完全开源，鼓励 fork                                │
│   └─ Hello Robot 不卖 SaaS、不卖模型                    │
│                                                         │
│  续航: 8h + 自动充电桩                                  │
│   └─ 研究场景"白天工作晚上充电"足够                     │
│   └─ 不追求"24×7 工业级"                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

这条路线的关键叙事是 Stanford 的 Mobile ALOHA、CMU 的 OK-Robot、Princeton 的 USA-VLA 等学术成果几乎都跑在 Stretch 上。**Hello Robot 实际上在做 NVIDIA 在 GPU 市场早期做的事——让学术界先用上你的硬件，等你的硬件成为 paper benchmark 之后，工业界自动跟进**。

它的单位经济非常清晰：
- 硬件 BOM 估算：~$15,000
- 售价：$29,950
- 毛利率：~50%
- 每台不需要后续 SaaS 订阅（虽然 Hello Robot 也卖服务）
- 一次性现金流，无 churn 风险

这是教科书级的 **"硬件产品公司"** 模式。它的天花板是大学和企业 R&D 部门——市场规模大概 $5-10 亿/年。

## 三、路线 B：Mind Robotics 的"垂直闭环平台"

RJ Scaringe 在 Rivian 创业的关键经验是什么？是 **垂直整合**——Rivian 自己造电池、自己造电机、自己造车机软件、自己开零售店。这套打法在汽车行业被 Tesla 验证过，但极重资本，也极难。

Mind Robotics 显然在复制这套打法到机器人：

```text
┌──────────────────────────────────────────────────────────┐
│           Mind Robotics 垂直整合栈                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 4: 客户与场景                                     │
│   └─ Rivian 工厂（first customer）→ 其他大型制造商      │
│   └─ 单一客户深度部署，制造高质量数据                    │
│                                                          │
│  Layer 3: 部署基础设施（"deployment infrastructure"）     │
│   └─ Fleet management、远程运维、OTA                     │
│   └─ 类比 Tesla 的"机器人售后体系"                       │
│                                                          │
│  Layer 2: 自研 Foundation Model                          │
│   └─ Rivian 工厂遥操数据 → VLA 训练                     │
│   └─ Data Flywheel：用得越多，模型越好                  │
│                                                          │
│  Layer 1: 自研硬件                                       │
│   └─ "purpose-built robotics"（专用硬件，非通用人形）   │
│   └─ 推测：多臂固定式 + 移动单元混合编队                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

这条路线的核心赌注是：**通用机器人的胜负不在硬件本身，而在数据+部署的反馈循环**。Mind Robotics 的护城河不是某个机械臂多灵巧，而是：

1. Rivian 一年生产数十万辆车，每个工位每天产生数百小时遥操数据
2. 这些数据完全归属 Mind Robotics
3. 反过来这些数据训出来的模型只服务于 Mind Robotics 的硬件
4. 客户黏性极高（不是买一台，是买一整套部署）

这是 **"数据飞轮 + 垂直 RaaS"** 模式。**它的单位经济长期是 ARR，而不是一次性硬件销售**：
- 每台年合同价：$50k-150k（推测）
- 毛利率（成熟期）：60-75%
- 客户终身价值（10 年）：$500k-1.5M/台
- Net Revenue Retention：>120%（部署越多越多）

天花板是制造业自动化总市场——全球 ~$5000 亿/年（按 IFR 数据），可寻址市场（SAM）几十亿到上百亿美元。

## 四、为什么 2026 年是分叉点？

过去 5 年的具身智能创业，大致都在"低空赛"——所有公司都在做 demo、所有 demo 都在 YouTube 上看起来惊艳、但实际部署的极少。2026 年发生了三件事让"路线"问题不可回避：

### 事件 1：VLA 模型门槛快速下降

DeepMind 的 Gemini Robotics-ER 1.6（5 月发布，参见 DeepMind Blog）、Figure 的 Helix、Physical Intelligence 的 π₀.₅、Boston Dynamics × DeepMind 的 Spot Reasoning——**2026 上半年至少 5 个团队公开了能跑在"任意机器人"上的 VLA foundation model**。这意味着 Hello Robot 这种"开源平台"得以低成本接入 SOTA 智能。**做硬件平台，不需要自研大模型，依然能让用户跑出 SOTA 结果**——这是路线 A 成立的前提。

### 事件 2：1X NEO、Figure 02 量产受挫

2025-2026 这轮人形机器人热潮，最大叙事是 1X NEO 在挪威工厂启动量产（参见 6 天前发表的相关分析）。但接下来 6 个月行业内的真实情况是：**量产远比想象中难**。机械臂的可靠性、电池续航、维护周期、安全认证，每一项都是"硬件公司的难题"，不是 AI 公司用模型就能解的。这个现实让 Mind Robotics 的"垂直整合"路线获得 LP 青睐——**做模型的人需要也学会做硬件、做部署、做服务**。

### 事件 3：政策杠杆向"制造业自动化"倾斜

美国 CHIPS Act 之后，针对制造业回流的政策红利极多。Rivian 这类电动车厂、SpaceX 的 Terafab（参见 6 天前发表的分析）、Apple-Intel Foundry 的潜在协议……所有这些"美国本土制造"的故事都需要一个共同前提：**美国劳动力短缺，必须靠机器人填补**。这给 Mind Robotics 这种"专攻制造业"的路线带来了独有的政策窗口。

## 五、两条路线的真实风险

路线 A（Hello Robot）的风险：

| 风险 | 严重度 | 备注 |
|------|--------|------|
| 工业客户不买开源平台 | 高 | 工厂要 SLA、要质保、要专人服务 |
| 单价低 → 现金流增长慢 | 高 | 30k × 几千台/年 ≠ 大公司 |
| 平台被巨头 fork → 商品化 | 中 | Bosch / ABB 等老厂可以学 |
| 学术热度 ≠ 商业落地 | 中 | 已经 8 年，仍然以研究为主 |

路线 B（Mind Robotics）的风险：

| 风险 | 严重度 | 备注 |
|------|--------|------|
| 单一客户依赖 Rivian | **极高** | Rivian 自己尚未盈利 |
| 资本密集，10 亿美元只是开始 | 高 | 真正部署需要 5-10x 现资本 |
| Data Flywheel 的"通用化"是谜 | 高 | Rivian 数据能否迁移到其他制造商？ |
| RaaS 客户拓展极慢 | 高 | 工厂 RFP 周期 12-24 个月 |
| 与 Tesla Optimus 等正面竞争 | 中 | Tesla 自己做，不会买 Mind 的服务 |

第一行风险特别值得展开。**Mind Robotics 第一个客户是 Rivian——但 Rivian 自己在 2025 年 Q4 损失了 9 亿美元，年产能利用率不到 50%。**如果 Rivian 短期不能站稳，Mind Robotics 的"data flywheel"在物理上转不起来。

这是一个有趣的对比：Tesla 用 Tesla 工厂训练 Optimus、Rivian 用 Rivian 工厂训练 Mind Robotics，但 **Tesla 工厂的运转质量是 Rivian 的 5x**。资本市场显然在押注 Scaringe 能把 Rivian 翻盘，反过来支撑 Mind Robotics。这是双重赌注。

## 六、跨领域类比：这像极了 2014 年的"自动驾驶"

对比 2014 年自动驾驶赛道的两条路线：

| 维度 | "Mobileye 模式"（平台） | "Waymo 模式"（垂直） |
|------|------------------------|---------------------|
| 战略 | 卖 EyeQ 芯片+软件给所有车厂 | 自己造车、自己运营 |
| 资本密度 | 中 | 极高 |
| 数据 | 客户车队（共享） | 自有车队（独占） |
| 单位经济 | 卖件 | 服务（Robotaxi） |
| 12 年后情况 | 上市、被英特尔收购、营收 $20亿/年 | 仍在烧钱、营收难统计 |

历史给出的答案是：**平台路线先盈利、规模化更快；垂直路线天花板更高但需要 10+ 年**。

如果机器人赛道走同样的曲线，**Hello Robot 在 2030 年前会更赚钱，Mind Robotics 在 2035 年才可能见到真正的拐点**。

但这个类比有个不成立的地方：Mobileye 的 EyeQ 是一颗芯片，可以快速复制到几亿辆车。Hello Robot 的 Stretch 是一台 30,000 美元的金属设备，**复制速度的物理上限是装配产线**。这让"平台路线在机器人里"的天花板比"平台路线在自动驾驶里"低一个数量级。

## 七、我的判断：5 年后的格局

放上我的明确预测：

**5 年后（2031 年）的通用机器人市场分布：**

| 玩家类型 | 市场份额 | 代表公司 |
|---------|---------|---------|
| 大公司自研垂直系统 | 35% | Tesla Optimus、Amazon Robotics |
| 类 Mind Robotics RaaS | 25% | Mind Robotics、Physical Intelligence、Figure |
| 类 Hello Robot 开源平台 | 15% | Hello Robot、Unitree（家用） |
| 老牌工业自动化 | 20% | ABB、Fanuc、Universal Robots |
| 长尾创业 | 5% | 各类垂直应用 |

为什么 RaaS 路线只有 25%？因为这个市场天然不允许出现"赢家通吃"。Tesla 不会买 Mind 的服务，BMW 不会买，丰田不会买——大型制造商最终都会自研。RaaS 只能服务中型制造商。

为什么 Hello Robot 这条路线 15%？因为研究者市场太小，真正大的是中小型应用集成商，而这些集成商的体量决定了他们倾向用"成熟、便宜、可改"的硬件——这正是 Stretch 的位置。

**最有意思的判断是 35% 的"大公司自研"**。Mind Robotics 的真正风险是它的目标客户中最有钱的那些（Tesla、苹果、亚马逊）都会自研。这是为什么 Mind 紧紧抱住 Rivian——一个不够大、不会自研、又有真实工厂的客户。

## 八、给读者的实操建议

如果你是机器人/具身智能方向的研究者或工程师：

1. **现在就买一台 Stretch 4 或类似平台**。$29,950 听起来贵，但相比写论文用的 GPU 集群价格亲民得多。学术能力的护城河越来越在"你的实验能上真实机器人"而不是"你的模型在 sim 跑得快"。
2. **不要在简历上写"做过 VLA 模型"**——这已经是标配。要写"我把 X 模型部署在 Y 真实硬件上跑过 Z 真实任务"。
3. **关注 Stretch 5 / Mobile ALOHA 2 等"中型通用机器人"**。这是未来 5 年发表论文性价比最高的赛道。

如果你是投资人或创业者：

1. **避免再投"通用人形+VLA"的新公司**。这个赛道已经过度拥挤，1X、Figure、Apptronik、Mind Robotics 五家已经吸走 90% 资本。
2. **看好"垂直应用 + 已有平台"**。比如：用 Stretch + 自己的微调模型做药房、做实验室、做养老——这种创业团队 6 个月就能 demo，1 年能签首单。
3. **谨慎"大客户绑定"型公司**。Mind Robotics 是个高质押注：如果 Rivian 稳，它赢；如果 Rivian 倒，它倒。这种二元结果不适合大多数 LP。

如果你是制造业 IT / OT 决策者：

1. **2026-2027 年是"通用机器人 PoC"的最佳窗口**。供应商竞争激烈、价格让步空间大、政策补贴足。
2. **POC 要选"有现存可比工艺"的工位**——而不是"未来的理想化场景"。这是决定 ROI 能否兑现的关键。
3. **数据所有权写进合同**——RaaS 合作中最大的坑是"你的工厂数据被供应商拿去训别人"。

## 九、结语：通用机器人不止一种通用

这个标题想说的最后一件事是：**"通用"这个词在 2026 年不再有单一定义**。

Hello Robot 的"通用"是 **形态通用** ——同一台机器人，可以做养老、做实验室、做接待、做家务。它的"通用"在硬件层。

Mind Robotics 的"通用"是 **任务通用** ——同一个 foundation model，可以做拧螺丝、可以做装配、可以做质检，但都在制造业语境下。它的"通用"在数据和模型层。

Tesla Optimus 想做的"通用"是 **场景通用** ——同一种人形机器人，工厂能用、办公能用、家庭能用。它的"通用"在终极形态。

这三种"通用"不是竞争关系，是不同的市场切面。**2026 年我们终于看到这种切面被同一周两家旗帜公司清晰地标注出来**——这才是 Mind Robotics × Hello Robot 这场对比真正的历史价值。

未来 18 个月，建议你密切关注三件事：
- Mind Robotics 第一个非 Rivian 客户签约（决定 RaaS 路线是否可外推）
- Hello Robot 的"Stretch in Industry"项目（决定平台是否能跨出研究边界）
- Tesla Optimus 的"Bot-on-Bot"装配示范（决定垂直整合是否能完成自循环）

哪一个先发生，哪一条路线就率先证伪——或证实。

---

## 参考来源

- [The Robot Report — Mind Robotics raises $400M to scale AI-powered robots in manufacturing](https://www.therobotreport.com/mind-robotics-raises-400m-scale-ai-powered-robots-in-manufacturing/) (Brianna Wessling, 2026-05-14)
- [The Robot Report — Hello Robot's latest Stretch 4 is bigger, faster, and stronger than previous versions](https://www.therobotreport.com/hello-robots-latest-stretch-4-is-bigger-faster-and-stronger-than-previous-versions/) (Brianna Wessling, 2026-05-12)
- [IEEE Spectrum — Hello Robot Sets the Standard for Practical, Safe Home Robots](https://spectrum.ieee.org/robots/) (IEEE Robotics)
- [DeepMind Blog — Gemini Robotics-ER 1.6: Powering real-world robotics tasks through enhanced embodied reasoning](https://deepmind.google/blog/gemini-robotics-er-1-6/)
- [Mind Robotics 官网 — Company description](https://mindrobotics.com/)（撰文时尚无产品页）
- [International Federation of Robotics — World Robotics 2025 Report](https://ifr.org/) (IFR 2025 年度报告)
- [Rivian Q4 2025 Earnings Report](https://rivian.com/investors)（背景：Rivian 自身经营状况）
- [Stanford Mobile ALOHA paper](https://mobile-aloha.github.io/) (背景：Stretch 在学术界的应用)

---
title: "【好文共赏】把 AMD 机密计算\"开盲盒\"：ETH Zurich 用两记互联总线攻击，把 SEV-SNP 的 PSP 当成了自己的钥匙"
description: "Fabricked + BreakFAST：ETH 系统安全组用一类全新的 Interconnect Corruption Attacks（XCA），把 AMD 从 Zen 3 一路打到 Zen 5——100% 成功率、纯软件、不需要物理接触，目标是云上所有 confidential VM 的 RMP 与 attestation。"
date: 2026-05-18
slug: "good-read-xca-amd-sev-snp-infinity-fabric"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - AMD
    - SEV-SNP
    - 机密计算
    - Infinity Fabric
    - 硬件安全
    - 侧信道
    - USENIX
    - IEEE S&P
    - ETH Zurich
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Overview of Interconnect Corruption Attacks (XCA)](https://xca-attacks.github.io/overview/) ＋ [Fabricked](https://xca-attacks.github.io/fabricked/) ＋ [BreakFAST](https://xca-attacks.github.io/breakfast/)
> 作者：Benedict Schlüter / Chris Wech / Philipp Giersfeld / Shweta Shinde（ETH Zurich, Secure & Trustworthy Systems Group）
> 论文：USENIX Security 2026（Fabricked）＋ IEEE S&P 2026（BreakFAST）
> 公开日期：2026-05-12（BreakFAST embargo lift） / 2026-04-14（Fabricked embargo lift）
> CVE：CVE-2025-54510（Fabricked）＋ CVE-2025-61971、CVE-2025-61972（BreakFAST）
> 多模评分：Opus 9.3 / Sonnet 9.1 / Gemini 9.0（综合 **9.1 / 10**）
> 一句话推荐：当 AMD 把"机密虚拟机"的全部安全寄托在一颗叫 PSP 的小处理器上，ETH 这群人没有去攻击 PSP——他们攻击了 PSP 通往世界的那条路。

## 1. 为什么这篇文章值得读

机密计算（Confidential Computing）是过去五年云厂商讲给监管和大客户听的一个故事：**你的数据，连 AWS / Azure / GCP 自己的运维都看不到**。这个故事的工程底座，是 Intel SGX / TDX、AMD SEV-SNP、Arm CCA 这套 TEE（Trusted Execution Environment）。其中 AMD SEV-SNP 是市场上**部署最广**的一个——Azure Confidential VM、Google Cloud Confidential Computing、阿里云加密计算实例，背后大多跑的是 AMD EPYC + SEV-SNP。

过去几年关于 SEV-SNP 的攻击不少。但绝大多数（Cipherleaks、CrossTalk、ÆPIC Leak、WeSee、Heckler、BadRAM 等等）都是**微架构侧信道**或**接口滥用**——拿到的是部分泄漏、概率性、需要特殊条件触发。

> 原文（XCA Overview）："Securing confidential computing requires rethinking interconnect architectures from the ground up."

[ETH Zurich Shweta Shinde](https://www.shwetashinde.com/) 这一组在 2026 年丢出来的两篇论文（Fabricked＠USENIX'26 + BreakFAST＠Oakland'26），把这件事从"侧信道"提升到了一个新维度：**Interconnect Corruption Attacks（XCA），互联总线腐化攻击**。它的特征是：

- **100% 成功率**（deterministic）
- **纯软件**，恶意 hypervisor 即可，不需要物理接触、不需要芯片改造
- **跨代影响**：Zen 3、Zen 4、Zen 5 全中
- **打的不是 PSP 本身，而是 PSP 与 DRAM、PSP 与 SMN 总线之间的"地址翻译表"**——一个攻击面，过去几乎没人盯过

如果你做云平台、做安全审计、做硬件可信根，或者你只是好奇"为什么我把数据放在云上就一定安全"，这篇导读就是写给你的。这件事的工程含金量，和当年 [Spectre/Meltdown 把推测执行钉到耻辱柱上](#7-编辑延伸思考)，在同一个量级。

## 2. 一分钟先看懂 SEV-SNP：PSP、RMP、Attestation 三件套

要理解 XCA 是怎么打穿 SEV-SNP 的，必须先看清 SEV-SNP 自己长什么样。一句话版本：

**AMD SEV-SNP = 内存加密 ＋ 内存所有权检查 ＋ 证明你跑在一个真硬件上**。

具体到三个零件：

1. **PSP（Platform Security Processor）**。一颗内嵌在 AMD CPU 里的 ARM Cortex-A5（Zen 3+ 换成 Cortex-A35），是整个 SEV-SNP 的硬件可信根。它负责：生成内存加密密钥、初始化 RMP、签发 attestation report、管理 CVM（Confidential VM）生命周期。
2. **RMP（Reverse Map Table）**。一张存在 DRAM 里的巨型表，每个物理页一条目，记录"这一页归谁所有、可不可以被 hypervisor 改写"。CPU 每次访问物理内存，都要先查 RMP。Hypervisor 想伪造一页 CVM 内存？RMP 第一个不答应。
3. **Attestation**。CVM 启动时，PSP 用一颗只在 CPU 内部的 VCEK 私钥，对"我跑的是哪段代码、在什么硬件配置上"签一份报告。租户拿这份报告去 AMD 的 KDS 验证，确认这台 VM 真的是 SEV-SNP 而不是 hypervisor 假装的。

威胁模型很激进：**hypervisor / BIOS / UEFI 全部是不可信的**。你（云厂商）可以拥有那台机器、拥有 root，但只要 PSP 没被攻破，你就**看不到 CVM 内存里那一字节**。

听起来很美。XCA 攻击告诉你的事情是：**PSP 没被攻破，但通往 PSP 的那条总线被改了路标。**

## 3. Infinity Fabric：从"性能优化"变成"攻击面"

要打 PSP，得先理解一件事：**现代 AMD 不是一颗芯片，是一堆 chiplet。**

EPYC Genoa / Bergamo / Turin（Zen 4/5）的处理器，是 CCD（CPU 复合体 die）、IOD（IO die）、PSP、内存控制器、IOMMU、PCIe root complex 等等多个 die 通过 **Infinity Fabric** 这条高速互联拼起来的。Infinity Fabric 不是一根总线，它分两层：

- **Data Fabric**：搬数据。所有 CPU 核心 → 内存控制器、PSP → DRAM、PCIe → DRAM 的读写，全走这里。它的"路由表"叫 DRAM hole / address mapping。
- **Control Fabric / SMN（System Management Network）**：配置一切。一个 **4 GB 的配置寄存器空间**，把整颗 SoC 上每一个组件的控制寄存器（内存控制器加密密钥、IOMMU 翻译表、PSP 状态机、电源管理）全部 mmap 进去。

这是教科书级别的**分层抽象**：你写数据走 Data Fabric，你配置硬件走 Control Fabric。问题在于——

> 原文（XCA Overview）："AMD designed the Infinity Fabric for performance and flexibility. In traditional deployments, the BIOS and hypervisor are trusted system software."

**这两条总线的路由规则，在传统威胁模型里是 BIOS 在启动时一次性配好、之后没人会乱动的。Infinity Fabric 没有为"BIOS 是敌人"这个场景设计。** 进了 SEV-SNP 时代，BIOS / hypervisor 全部成了敌人——但 Infinity Fabric 还在按"老剧本"运行。

这就是 XCA 攻击的母题，也是这一系列论文真正的智识贡献：**它不是又一个 bug，它指出了一个被忽略了十年的攻击面——TEE 的根硬件本身是可信的，但根硬件用来访问世界的接口不是。**

（这点其实和我之前写的[《把车里的「告密者」物理拔除：一位安全工程师的 2024 RAV4 隐私手术》](/post/good-read-rav4-modem-gps-removal-car-privacy/)异曲同工：root of trust 不重要，root of trust 旁边那根能被你切掉的天线才重要。）

## 4. Fabricked：把 PSP 的写入"扔进黑洞"

Fabricked（CVE-2025-54510）的故事，是从一个"看上去没什么大不了的设计选择"开始的。

**Infinity Fabric 的 Data Fabric 路由规则，是 BIOS / UEFI 在启动时写到一堆 DF（Data Fabric）寄存器里的。** AMD 知道这些寄存器在 SEV-SNP 启动后必须锁定——所以 PSP 在 `SNP_INIT` 这一步会触发一系列 API 调用，让 UEFI **把对应 DF 寄存器加锁**，之后任何写入都会失败。

ETH 这帮人翻 AMD 的 SEV-SNP firmware 翻出了第一个洞：

> 原文（Fabricked）："the untrusted UEFI is in charge of locking down parts of the Infinity Fabric configuration. As an attacker, we modify the UEFI to skip these API calls."

也就是说——**锁谁不锁谁，是 UEFI 自己判断的**。但 UEFI 在 SEV-SNP 威胁模型里早就是敌人了。攻击者只要换一个恶意 UEFI（fork 一份 EDK2，把那几个 lockdown 调用 NOP 掉），SEV-SNP 启动后 Data Fabric 的路由规则**仍然可写**。

这只是第一步。真正狠的是第二步：**PSP 写 RMP 的那一刻，攻击者把那段物理地址的路由改了。**

`SNP_INIT` 流程里，PSP 必须做一件事：给整张 RMP 表的每个 4KB 物理页写一条 `ImmutableEntry`，把它标成"系统页、不可被任意 hypervisor 访问"。这是 SEV-SNP 整个安全模型的水准线。

Fabricked 的攻击是：

1. 恶意 hypervisor 启动前，先用恶意 UEFI 跳过 DF 寄存器 lockdown
2. 恶意 hypervisor 给 RMP 表所在的物理页**预先写好"全部允许 hypervisor 写"的伪造内容**
3. 触发 `SNP_INIT`。在 PSP 准备把"真"RMP 条目写到 DRAM 之前，攻击者**修改 Data Fabric 的路由规则，让 PSP 写到 RMP 物理地址的事务直接 drop**（路由到一个不存在的目的地）
4. PSP 写完，认为自己初始化完成，返回成功
5. SEV-SNP 启动完成，但 RMP 表里**还是攻击者预先写好的那份"全员通行证"**

后果：之后启动的所有 CVM，RMP 检查形同虚设。Hypervisor 可以**任意读写 CVM 的物理内存**——加密保护理论上还在（PSP 用 AES-XTS 加密），但 RMP 通过后，hypervisor 可以 remap 一页明文内存进去，或者通过 [BadRAM 风格的偏移攻击](https://arxiv.org/abs/2407.16694) 让密文落到攻击者控制的地方。

更冷酷的是攻击复杂度的描述：

> 原文（Fabricked）："Fabricked operates as a fully deterministic, software-only exploit with a 100% success probability."

**100%**。不是 P50，不是"重试几次能成功"，是确定性。

## 5. BreakFAST：让 PSP 替你写它自己不愿意写的字

如果 Fabricked 是"挡住 PSP 的笔"，BreakFAST（CVE-2025-61971/72）就是"把 PSP 的手抓过来，让它替你签字"。它是一次教科书级别的 **confused deputy 攻击**——攻击者没有权限做某件事，但你说服了一个有权限的角色替你去做。

剧情：

- PSP 是少数能写整个 4GB SMN（Control Fabric）配置空间的角色——它必须能写，因为它要给内存控制器配置加密密钥、给 IOMMU 配置保护范围
- 但 Hypervisor 自己**只能写 SMN 里很少一部分**（音频控制器、风扇、电源管理这种民用寄存器），SMN 里"危险区域"（IOMMU、内存控制器、PSP 状态机）由硬件拒绝 hypervisor 写
- ETH 逆向之后发现，平台上有两个寄存器叫 `FASTREGCNTL` 和 `FASTREG`：前者是**滑动窗口的位置**（把 1MB 大小的 SMN 切片 mmap 到一个固定地址），后者是切片本身。这一对寄存器，**理论上 hypervisor 也是不能动的**

但 PSP 在执行某些 firmware 路径时，会向 DRAM 写若干字。攻击者的杠杆是：

> 原文（BreakFAST）："we first mount a confused-deputy attack against the PSP to trick it into configuring the window position for us. We achieve this by overlapping benign PSP accesses to DRAM with the location of FASTREGCNTL."

**改 Data Fabric 的路由，让 PSP 以为自己在写 DRAM、实际上是在写 `FASTREGCNTL`。** PSP 拥有"我自己写"的特权，平台不会再做权限检查。一次写完，1MB 的 SMN 窗口被攻击者控制；第二次同样的把戏，PSP 把它自己当成数据写到 `FASTREG`，攻击者就拿到了**整个 4GB Control Fabric 的任意读写**。

两个端到端 PoC：

1. **伪造 attestation**：找到 PSP 内部存放 VCEK 私钥的 RAM 区域，dump 出来，离线给任意 hypervisor-controlled CVM 签 attestation report。租户拿着报告去 AMD KDS 验，验是真的——但 VM 里跑的是攻击者的代码
2. **打开 debug 模式**：通过修改 PSP 状态机寄存器，把 production CVM 切到 debug 模式，hypervisor 直接读写它的 vCPU 寄存器

第二个尤其黑暗：**目标 CVM 启动之后再被切换**，它自己感知不到自己已经是 debug VM 了。

> 原文（BreakFAST）："BreakFAST is a fully software-based exploit requiring no physical access and no prior knowledge of the victim CVM. It achieves 100% success."

又是 100%。

## 6. 把两次攻击合起来看：XCA 是一个新的攻击家族

单独看 Fabricked，是一个 BIOS 漏洞 + 一个路由 race。单独看 BreakFAST，是一个 confused deputy + 一个隐藏寄存器。把两个放在一起，作者讲了一件更重要的事：

**Infinity Fabric 这种"为性能和灵活性设计的、把所有硬件都 mmap 进同一个地址空间的"互联架构，在 confidential computing 模型下根本没法证安全。**

> 原文（XCA Overview）："The Infinity Fabric configuration spans across dozens of SoC components, each with subtle interdependencies — a complex web of routing logic, address translation, and component interactions that cannot be exhaustively tested or formally verified at scale."

我把这句话翻译得更直白一点：

- 现代 SoC 几十个组件，每个都有自己的配置空间
- 这些空间通过 Control Fabric 互相可达
- 任意一条路由规则被改，都可能让一个组件"以另一个组件的身份"动作
- 这种组合空间，**不可能穷尽测试，也几乎不可能形式化验证**

这是非常 humbling 的一段话。它说的不是 AMD 蠢，而是 chiplet 时代的 SoC 设计哲学（最大化灵活性、复用、性能）和 confidential computing 的安全模型（最小化授信、严格分层）**有结构性矛盾**。

Intel TDX 一样吗？Arm CCA 一样吗？作者很谨慎地不下结论——他们只在 FAQ 里说"我们没有测试，但 TDX 和 CCA 的互联子系统同样庞大、同样需要 BIOS 协助配置，相似的攻击面是否存在值得社区进一步研究"。翻译：**他们也几乎肯定有，只是没人挖。**

（这点与我之前写的 [《当 part 数从 30k 涨到 160k：Cloudflare 用三个补丁，把 ClickHouse 查询规划器从一把互斥锁里救出来》](/post/good-read-cloudflare-clickhouse-mutex-contention/) 在更高的抽象层是相通的：复杂系统里的安全/性能问题，很少出在中心组件，往往出在**组件之间的协调层**。）

## 7. 编辑延伸思考：从 Spectre 到 XCA，硬件可信边界的第三次重画

我在自己的工作笔记里，把过去十年硬件安全的边界画过三次：

**第一次：2018 年，Spectre/Meltdown**。我们意识到 CPU 的"推测执行"这个性能特性会泄漏跨进程、跨权限的秘密。结论：CPU **流水线**不再是黑盒，必须暴露 [INVPCID、IBPB、SSBD 这一堆 mitigation 接口](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/best-practices/branch-target-injection-mitigation-vmm.html) 给操作系统去手动管理。

**第二次：2020-2024 年，SGX / SEV 的早期攻击**（CrossTalk、ÆPIC Leak、CipherLeaks、TLB-Leak、CacheWarp、Heckler、WeSee）。我们意识到 TEE 的**接口**——hypervisor 给 CVM 注入中断、配置 page table、做 nested paging——本身就是攻击面。结论：CVM 与 hypervisor 之间的每一条 API 都要重新审计。

**第三次：2026 年，XCA**。我们意识到，即使 TEE 的接口审计干净，**TEE 内部组件之间的总线本身**也可以被腐化。结论：以后的 TEE 设计，**互联总线必须被纳入可信边界**——要么物理隔离（PSP 不走 Infinity Fabric），要么互联本身要做认证（Authenticated Interconnect）。

后者已经有早期工作，比如 PCIe 标准里的 IDE（Integrity and Data Encryption）和 TDISP，CXL 也有相应草案。但 SoC 内部的私有互联（Infinity Fabric、Intel UPI、Arm CMN）目前几乎都是裸跑。XCA 论文的真正贡献在于：**它把"SoC 内部互联也要做 attestation"这件事，从概念论文推到了 USENIX Security 主舞台**。

而站在云厂商的角度，这件事还有一层更现实的含义：**所有 Azure Confidential VM / Google Cloud CVM / AWS Nitro Enclaves on AMD 部署的客户，过去 18 个月里相信的安全保证，事实上是有一段时间是空的。** AMD 已经发了 firmware update（AMD-SB-3030 / 3034），但实际部署的 patch 节奏从来都不是论文 embargo 解除当天就齐——这个 gap 期，是历史上每一次 TEE 漏洞都会出现的"窗口期"，也是合规审计真正需要正视的事。

如果你公司的合规框架里有一句"我们使用 SEV-SNP 来保护客户数据"，那么 2026 年 Q2 之前的所有审计报告，原则上都应该加一段脚注。

## 8. 谁应该读这篇文章

- **云厂商安全工程师**：你的 CVM 产品 SLA 里写的"硬件级隔离"，现在多了两个 CVE。补丁部署节奏、客户沟通话术、合规重审，都要重排
- **机密计算用户**（金融、医疗、政府）：你买的"加密计算"实例，过去 6 个月可能并没有给你预期的保证。问你的云厂商要 patch 时间线
- **TEE/硬件安全研究者**：XCA 是一个新攻击类，意味着接下来 12-24 个月，Intel TDX 和 Arm CCA 上的同类工作几乎必然会涌现。这是一个可以挖一系列 paper 的金矿
- **SoC / chip designer**：互联总线该怎么 attestation 化、怎么把"PSP 等可信组件"从普通 SMN 空间里隔出来，是 2027 年所有 server CPU 设计必答题
- **想理解"机密计算"到底是什么的工程师**：这篇导读 + 原 paper 是一个非常好的逆向学习路径，比从 AMD 白皮书读起更容易抓住关键概念
- **关心"信任 root 到底信什么"的哲学派**：XCA 是一次很好的提醒——root of trust 是有边界的，超出边界一寸，"可信"就成了一个比喻

## 9. 配套资料导览

本文目录下还附带四份配套资料：

- `mindmap.svg`：XCA 攻击家族思维导图，从 Infinity Fabric 两条平面到两个 CVE 的攻击路径
- `concept-cards.md`：12 张关键概念卡片，从 PSP、RMP、Attestation 到 confused deputy 攻击的概念脉络
- `glossary.md`：32 条英中术语对照表，覆盖机密计算、TEE、SoC 互联、SEV-SNP 内部组件
- `cover.svg`：本期封面

## 10. 延伸阅读图谱

### 作者其他代表作（ETH Sectrs Group / Shweta Shinde）

- **Heckler: Breaking Confidential VMs with Malicious Interrupts**（USENIX Sec'24）—— 用恶意中断打 SEV-SNP / TDX 的 CVM 控制流，是 XCA 之前对 PSP 接口攻击的重要先声
- **WeSee: Using Malicious #VC Interrupts to Break AMD SEV-SNP**（IEEE S&P'24）—— PSP 与 hypervisor 之间 #VC 异常通道的滥用
- **Aster: Bringing Confidential Computing to Android**（MobiSys'26）—— 把 confidential VM 模型搬到 Arm 移动平台
- **It's TEEtime: Bringing User Sovereignty to Smartphones**（CHES'26，获奖）—— 用户主权视角下的 TEE 设计
- **Stitch: Assertion-Guided Patching of On-Chip Protocol Implementations using LLMs**（DAC'26）—— 同组用 LLM 修 on-chip 协议实现 bug，和 XCA 揭露的攻击面正好是攻防对照

### 经典对比工作

- **CipherLeaks**（Li et al., USENIX'21）—— AMD SEV 内存加密的密文侧信道，XCA 的早期"远亲"
- **CrossTalk**（Ragab et al., S&P'21）—— Intel 跨核侧信道
- **CacheWarp**（Schlüter et al., USENIX'24）—— 同组作者 Schlüter 早期的 SEV 攻击
- **BadRAM**（USENIX'24）—— DRAM 物理地址重映射攻击 SEV-SNP，与 Fabricked 在"重新路由内存"维度上有强对比
- **ÆPIC Leak**（USENIX'22）—— Intel SGX 内存值泄漏，工业界第一次正视 TEE 接口漏洞
- **TDXDown / TDXRecycle / TDX-DOWN**（2024-2025）—— Intel TDX 早期攻击，证明 TDX 也不是金刚不坏
- **CCA-Sim / Trustee** —— Arm CCA 早期分析工作，确认互联架构是同类风险面

### 反方与不同视角

- AMD 官方公告：[AMD-SB-3030](https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3030.html)（BreakFAST 修复）、[AMD-SB-3034](https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3034.html)（Fabricked 修复）。AMD 把这两个归类为 firmware-side fix，不需要硬件 stepping 变更——但社区有人质疑这种"在恶意 UEFI 下用 firmware 自检"的做法是否真正解决根因
- Azure / GCP / AWS 三家的 patch 时间线公告（截至发稿，Azure 已确认部署，Google Cloud / AWS 时间线未公开）
- 学术圈对"XCA 是不是新攻击类"的 Twitter 讨论：有人认为 BreakFAST 本质是 confused deputy 的复刻（参见 [Schroeder 1972 confused deputy paper](https://www.cap-lore.com/CapTheory/ConfusedDeputy.html)）；Shinde 等人回应是攻击的**载体**（互联路由）才是新的

### 站内相关文章（强烈推荐合读）

- [《【好文共赏】五天，攻破 Apple 五年：Calif 团队用 Mythos 把 M5 上的 MIE 防线撕开了一道口子》](/post/good-read-calif-mie-bypass-apple-m5-kernel/) —— Apple 自家硬件可信边界的反例，与 XCA 是同一种"硬件信任假设是错的"叙事
- [《【好文共赏】2 小时审计、5 行代码：Project Zero 在 Pixel 10 VPU 驱动里挖出一个"圣杯级"内核漏洞》](/post/good-read-pixel-10-zero-click-vpu-kernel/) —— Pixel 10 VPU 驱动的零点击漏洞，关键也是"协处理器的 IOMMU 边界没被守住"
- [《【好文共赏】用咖啡和 IDA 绕过 Tesla 充电桩 anti-downgrade：Synacktiv 在 ratchet 里找到了一道顺序裂缝》](/post/good-read-tesla-wall-connector-anti-downgrade-bypass/) —— firmware 安全模型的失效叙事
- [《【好文共赏】给一块运行中的硬盘下断点：Xbox 360 黑客 Ryan Miceli 拆解 4 家 HDD/SSD 固件的反编译手记》](/post/good-read-hdd-firmware-hacking-jtag-ida/) —— 存储 firmware 的反向工程方法论，和 BreakFAST 里 PSP firmware 逆向手法是同一条手艺线

## 11. 一句话总结

XCA 不是又一个 CVE。它是一次**模型层面的提醒**：在 chiplet 时代，TEE 的"可信硬件根"如果还有任何一条总线没纳入可信边界，那条总线就是攻击者的高速公路。AMD 已经发了 firmware update，但 Intel TDX、Arm CCA、未来的 NVIDIA confidential GPU，每一个还在用相同假设、还没经过类似审计的互联子系统，都欠社区一次正视。

> 原文（XCA Overview）："Securing confidential computing requires rethinking interconnect architectures from the ground up."

——这句话，会在未来三年的硬件安全论文标题里反复出现。

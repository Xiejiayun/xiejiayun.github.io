---
title: "RISC-V 进入系统设计新纪元：当 ISA 开源遇上拼装指令集"
description: "RISC-V 正从'使能者代品'跳进'服务器级拼装主体'。RVA23 + AIA + UCIe Chiplet 生态使 fabless 初创可以跳过 ARM 授权直接拼服务器。这不是另一个 CPU 架构叙事，而是拼装时代的权力重构。"
date: 2026-05-05
slug: "riscv-system-design-chiplet-composability-era-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - RISC-V
    - Chiplet
    - UCIe
    - 服务器芯片
    - 开源硬件
draft: false
---

## 一、被忽略的拐点：RISC-V 第二阶段已经悄悄发生

过去十年，RISC-V 在公众讨论里一直被压缩成一句话：「一个开源的指令集」。这句话技术上没错，但它像把一栋大楼说成「一堆混凝土」一样毫无信息量。2026 年的真正变化不在 ISA 层面——基础整数和向量扩展早在 2019—2021 年就冻结了——而在 ISA *之上* 的系统级标准化：中断架构、IOMMU、调试规范、平台 profile、缓存一致互连、再到 Chiplet 物理接口，全部在过去十八个月里同步成型。

SemiWiki 在 2026 年的专栏《Why RISC-V System Design Is Entering a New Era》中给出了一个直白判断：RISC-V 已经走完「ISA 开源」的第一阶段，正进入「系统组件标准化 + 可拼装实现」的第二阶段[^1]。这意味着 fabless 初创公司第一次可以拿一份公开规范，就拼出一颗能跑通用 Linux 发行版、跑 Kubernetes、跑数据库的服务器级 SoC——而不必先签 ARM 架构授权，也不必等 Neoverse 路线图。

如果说第一阶段是「开源了语言」，第二阶段是「开源了语法、词典和出版社」。这是权力结构的重构，不只是技术演进。

## 二、RVA23：从「能跑代码」到「能跑发行版」

第一阶段的 RISC-V 最尴尬的地方不是性能，而是碎片化。每家实现都可以挑选不同的扩展子集，结果是 Debian、Fedora、Ubuntu 没法发布一个二进制能在所有 RISC-V 芯片上跑的 userland。这与 ARMv8-A 的「一个 profile 走天下」体验差距巨大。

RVA23 Profile 在 2024 年底批准、2025 年成为主流芯片的目标[^3]，第一次把「一组必须实现的扩展」打包成强制规范：

- **V**（向量，1.0）——SIMD 不再是可选项，编译器可以默认生成；
- **H**（Hypervisor）——虚拟化进入基线，KVM/Xen 可移植性大幅提升；
- **Zicbom/Zicboz**（缓存块管理）——给 DMA 一致性和零拷贝栈一个稳定 ABI；
- **Zacas**（原子比较交换）——无锁数据结构性能与 ARM/x86 对齐；
- **Supervisor 时钟与中断扩展**——OS 不再为每家硅片写一套时钟驱动。

RVA23 的意义远超「又加了几个扩展」：它是 RISC-V 对外发出的发行版兼容承诺。一旦上游 glibc/LLVM/GCC 把 RVA23 作为默认目标，OS 厂商就敢开始构建独立的 riscv64 二进制仓库。这对应用生态的拉动是阶跃式的，类似当年 ARMv8 让 Linaro 终于能做出统一 server stack。

## 三、AIA + IOMMU：服务器才需要的两块拼图

桌面用户看不见、嵌入式开发者用不上、但服务器架构师离了就活不下去的两块系统组件，过去是 RISC-V 的硬伤：

**AIA（Advanced Interrupt Architecture）** 在 2023 年定稿，2025—2026 年开始进入硅。它解决的是 PLIC 时代根本扛不住的事情——上百个核、几千个 MSI 中断源、虚拟机透传中断、IPI 风暴。AIA 把中断分成 IMSIC（per-hart）+ APLIC（platform）两层，语义上对齐 ARM GICv3/v4 与 x86 APIC，KVM 透传 PCIe 设备终于能正常工作。

**RISC-V IOMMU 规范** 同期定稿，提供两阶段地址转换、PCIe ATS/PRI、设备隔离与 SR-IOV。没有 IOMMU 就没有云——多租户隔离、DPDK 用户态驱动、GPU/加速器共享地址空间，全靠它。

把 RVA23 + AIA + IOMMU 三件事放在一起看，结论很清楚：**RISC-V 第一次具备了构成「服务器」一词所必需的全部系统级语义**。这之前的 RISC-V 服务器尝试（包括早期 SiFive HiFive Unmatched）都是工程演示，而不是产品。从 2026 起，缺的不再是规范，而是硅、调度器调优和软件生态深度。

## 四、CHI / AXI / UCIe：互连层的悄悄革命

CPU 核本身从来不是难点——SiFive、Andes、Alibaba 的玄铁、Tenstorrent Ascalon、Ventana Veyron 都已经能拿出乱序、宽发射、SMT 的服务器级核[^3]。真正的护城河在互连。

ARM 的 CMN-700 之所以被 Neoverse 客户绑死，不是因为它技术领先，而是因为它把核、L3、Snoop Filter、HN-F、CCIX/CXL 桥接「打包出售」，客户没有别的选择。RISC-V 世界正在出现一组替代方案：

- **TileLink**（SiFive 主推）——开源、轻量，已用于商业 SoC；
- **AMBA CHI**（ARM 公开规范，可独立实现）——已有多家 RISC-V 厂商绑定；
- **OpenCHI / 第三方 NoC IP**（Arteris、Baya Systems）——给 RISC-V 客户提供与 CMN-700 同级的服务器互连。

更深一层是 **UCIe**（Universal Chiplet Interconnect Express）。UCIe 1.1/2.0 把 die-to-die 物理层、链路层、协议层（PCIe/CXL/streaming）标准化之后，SoC 设计就从「单 die 集成」转向「接口级拼装」。这件事对 RISC-V 是结构性利好——因为 RISC-V 没有 IP 垄断者，任何 fabless 都可以把自家 RISC-V 计算 die 和别家的 IO die、HBM 控制器 die、AI 加速 die 通过 UCIe 拼起来。

## 五、一张拼装图：2026 服务器级 RISC-V SoC 长什么样

```
            ┌──────────────────────────────────────────────────────────┐
            │                  Package Substrate (UCIe)                │
            │                                                          │
            │  ┌────────────┐   ┌────────────┐   ┌────────────────┐    │
            │  │ Compute    │UCIe│ Compute   │UCIe│  AI / Vector  │    │
            │  │ Die  #0    │◄──►│ Die  #1   │◄──►│  Accel Die    │    │
            │  │ 32× RV64GC │   │ 32× RV64GC │   │ (custom ext.)  │    │
            │  │ V + H + ZC │   │ V + H + ZC │   │  bf16 / int8   │    │
            │  └─────┬──────┘   └─────┬──────┘   └────────┬───────┘    │
            │        │ CHI / TileLink coherent NoC        │            │
            │        ▼                                    ▼            │
            │  ┌──────────────────────────────────────────────────┐    │
            │  │   Shared L3 + Home Nodes + AIA (IMSIC/APLIC)     │    │
            │  └─────┬──────────────────────────────────┬─────────┘    │
            │        │                                  │              │
            │  ┌─────▼──────┐                    ┌──────▼─────────┐    │
            │  │  IO Die    │   PCIe Gen6 / CXL  │  Memory Die    │    │
            │  │  IOMMU +   │◄──────────────────►│  HBM3e ctrl    │    │
            │  │  NIC / NVMe│                    │  + DDR5 ctrl   │    │
            │  └────────────┘                    └────────────────┘    │
            └──────────────────────────────────────────────────────────┘
                       ▲                                ▲
                       │  全部通过 UCIe / BoW 物理接口  │
                       │  各 die 可来自不同 fab、不同节点
```

这张图的关键不是哪一块特别强，而是 **每一块都可替换**。Compute die 可以来自 Ventana，AI die 可以是 Tenstorrent Tensix，IO die 可以让 Astera Labs 代工——只要都接 UCIe 协议层，封装厂就能拼出来。这与 Apple M 系列那种「一家通吃」的 monolithic 哲学完全相反，是 fabless 生态的分布式胜利。

## 六、与 ARM Neoverse / x86 的对照表

| 维度 | RISC-V（RVA23 + UCIe 路径） | ARM Neoverse V/N 系列 | x86 服务器（Intel Xeon / AMD EPYC） |
|---|---|---|---|
| ISA 授权成本 | 0（规范公开） | 架构授权 + 每核 royalty | 不可授权（仅 OEM 关系） |
| 自定义扩展 | 允许，opcode 空间预留 | 受限（Custom Instructions 计划） | 不允许 |
| 可子集购买 | 是，按 die / IP 拼 | 否，CMN-700 + 核打包 | 否 |
| 服务器中断架构 | AIA（IMSIC/APLIC） | GICv3/v4 | x2APIC |
| 虚拟化基线 | H 扩展（RVA23 强制） | EL2 强制 | VMX/SVM |
| Chiplet 互连 | UCIe（开放） | UCIe / 自有 AMBA CXS | UCIe / 自有 EMIB+Foveros / Infinity Fabric |
| OS 发行版兼容 | 2026 起统一（RVA23） | 成熟 | 极成熟 |
| 路线图控制权 | 厂商自主 | 跟随 ARM 年度节奏 | 跟随 Intel/AMD |
| 适合谁 | fabless 初创、主权云、超大规模自研 | 已签授权的中大型设计公司 | 通用企业采购 |

这张表里最致命的一行是「路线图控制权」。Neoverse 客户（包括 AWS Graviton、NVIDIA Grace、Microsoft Cobalt）都得跟 ARM 的发布节奏走，自定义扩展的空间越来越小。RISC-V 客户没有这个枷锁——这是为什么阿里平头哥、Tenstorrent、Ventana、SiPearl（部分线）都把宝压在 RISC-V 上。

## 七、商业层的真正颠覆：fabless 初创的「设计权回归」

SemiEngineering 在《Designing Chips In The Context Of Rapidly Evolving AI》里指出，AI 工作负载演进速度已经超过传统 SoC 三年迭代周期，导致「为某个模型架构定制 silicon」的窗口越来越短[^2]。这把芯片设计逼向两条路：要么超大规模厂自建（Google TPU、AWS Trainium），要么 fabless 用最快路径拼出专用方案。

后者在 ARM 时代几乎不可能——一家 20 人的初创没钱付架构授权，更没人脉拿到 CMN-700。RISC-V + UCIe 把这条路重新打开：

- **设计成本**：核可以买开源（Rocket、BOOM、XiangShan）或商用（SiFive、Andes），互连可以用 TileLink 或第三方 NoC IP；
- **流片成本**：通过 chiplet 复用别家成熟 IO die，自己只流计算 die，可以把先进节点 mask 成本压到原来的 1/3—1/5；
- **产能门槛**：SemiEngineering 另一篇文章指出，先进节点产能正变成竞争壁垒[^4]——chiplet 让初创可以把计算 die 放在 N3，把 IO die 放在 N6，避开最贵节点的产能争夺。

合起来看，2026 年的事实是：一家融了 B 轮的 fabless 初创，**理论上**可以在 18 个月内拼出一颗 64 核服务器 SoC，而这件事在 2022 年是天方夜谭。

## 八、预判：2027—2028 的「二线云 RISC-V 时刻」

不要期待 AWS 或 Azure 在 2027 年发布全 RISC-V 实例——它们已经在 ARM Graviton/Cobalt 上投入了数十亿美元，转换成本是天文数字。真正的突破口在二线和主权云：

- **欧洲主权云**（OVHcloud、Scaleway、SiPearl 联合方案）——欧盟《芯片法案》补贴叠加「不依赖美国 ISA」的政治诉求；
- **中国云厂商**（阿里、字节、华为系）——平头哥已有 C910/C930 系列，2027 年出现 64 核 RVA23 服务器 SKU 的概率很高；
- **印度国家芯片计划**（Shakti / Vega 路线）——在政府订单驱动下进入电信和政务云；
- **Tenstorrent Blackhole 后继**——把 RISC-V 通用核与 AI 加速 die 拼成训练/推理一体机，绕开 NVIDIA 直接卖给二线 GPU 云。

这批客户共同特征是：性能不必跑赢 Graviton4，但要 **可控、可改、可补贴**。RISC-V 在「可控」这一项上是唯一答案。

## 九、风险清单：还没解决的硬骨头

为了不让本文变成布道，必须列出尚未解决的工程问题：

1. **软件深度**：JVM、V8、.NET CoreCLR 的 RISC-V JIT 后端虽已合并，但深度优化（向量、内联缓存、tier-up 策略）仍落后 ARM 1—2 年；
2. **性能验证基准缺失**：SPEC CPU 2017 上的公开高分 RISC-V 数据仍稀少，超大规模采购方不敢盲下单；
3. **互连标准战**：CHI vs TileLink vs 自研 NoC 仍未收敛，跨厂 chiplet 一致性域拼装在协议层还有摩擦；
4. **EDA 流程**：RISC-V 自定义扩展虽允许，但 toolchain（编译器内联、调试器、性能计数器）支持是每家自己写，复用度低；
5. **ARM 的反击**：ARM 在 2025 年开始放宽 Custom Instructions 与提供更灵活授权，护城河没那么容易被绕过。

但这些都是「能解决」的工程问题，而不是「结构性不可能」。结构性的事情——开源 ISA、可拼装 chiplet、可绕开授权——已经发生。

## 十、结语：拼装时代的权力转移

把 RISC-V 看作「另一个 CPU 架构」是过时的视角。2026 年的 RISC-V 是一场关于 **谁有权设计 silicon** 的权力重构：

- 第一阶段（2010—2020）：开源了**指令集**，让大学和嵌入式厂受益；
- 第二阶段（2023—2026）：开源了**系统级语义**（profile、中断、IOMMU、互连），让 fabless 初创第一次能拼服务器；
- 第三阶段（2026—2030）：在 UCIe + 先进封装的助力下，把「设计 SoC」这件事从巨头垄断变成 **生态拼装**。

ARM 用了二十年把 Acorn 的小核做成数据中心霸主，靠的是「一份高质量 IP + 全球授权网络」。RISC-V 不会复刻这条路，它走的是相反方向：**没有中央 IP 提供商，只有规范和接口**。这条路慢，但一旦跑通，权力分布就再也回不去了。

二线云厂商、主权计算、AI 专用 silicon——这三个方向都不需要 RISC-V 跑赢 x86，只需要 RISC-V「足够好 + 我的」。这个临界点，已经到了。

---

## 引用

[^1]: SemiWiki, *Why RISC-V System Design Is Entering a New Era*, 2026. <https://semiwiki.com/>
[^2]: SemiEngineering, *Designing Chips In The Context Of Rapidly Evolving AI*. <https://semiengineering.com/>
[^3]: RISC-V International, *RVA23 Profile Specification* 与 Tenstorrent Ascalon / Ventana Veyron 产品页. <https://riscv.org/> · <https://tenstorrent.com/> · <https://ventanamicro.com/>
[^4]: SemiEngineering, *Foundry Capacity Is Limiting Who Competes At Leading Edge Nodes*. <https://semiengineering.com/>

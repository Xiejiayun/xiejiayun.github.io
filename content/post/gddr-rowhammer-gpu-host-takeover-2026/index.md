---
title: "GDDRHammer：GPU 显存里的比特翻转，如何让攻击者接管整台主机"
description: "两个独立研究团队证明，对 NVIDIA GPU 的 GDDR6 显存发动 Rowhammer 攻击，可以跨越组件边界获取主机完整控制权。这是硬件安全的新前沿。"
date: 2026-05-07
slug: "gddr-rowhammer-gpu-host-takeover-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 硬件安全
    - Rowhammer
    - GPU安全
    - GDDR6
draft: false
---

> 2026 年 4 月，两支独立的安全研究团队在同一周内公布了针对 NVIDIA GPU 的 Rowhammer 攻击。不同于过去十年针对 CPU DRAM 的 Rowhammer 研究，这一次攻击发生在 GPU 的 GDDR6 显存中——然后跨越了 PCIe 总线，夺取了主机 CPU 的完整控制权。

## 什么是 Rowhammer，为什么 GPU 上更危险

Rowhammer 是 2014 年 Google Project Zero 首次公开披露的 DRAM 物理漏洞：反复激活（hammer）DRAM 中的某一行（row），会导致相邻行的比特发生翻转（bit flip）。在 CPU 侧，十年来的防御措施——ECC 校验、Target Row Refresh (TRR)、地址空间随机化——已经形成了多层防线。

但 GPU 侧几乎是一片空白：

| 维度 | CPU DRAM | GPU GDDR6 |
|------|----------|-----------|
| ECC 覆盖 | 服务器标配 | 消费级 GPU 无 ECC |
| 刷新策略 | TRR 已部署多代 | GDDR6 无标准化 TRR |
| IOMMU 保护 | 通常启用 | **BIOS 默认关闭** |
| 攻击面 | 需本地代码执行 | 任何 CUDA/OpenCL 程序即可触发 |

关键差异在于最后一行：GPU 的编程模型天然允许用户态程序高速、重复地访问显存地址——这正是 Rowhammer 所需要的。

## 三把钥匙：GDDRHammer、GeForge 与第三攻击

### GDDRHammer：从显存到系统内存的跨界跳跃

第一篇论文 *"Greatly Disturbing DRAM Rows — Cross-Component Rowhammer Attacks from Modern GPUs"*（Andrew Kwong 等）提出了 **GDDRHammer** 攻击：

1. **诱导比特翻转**：在 RTX 3060 上成功触发 1,171 次比特翻转，RTX 6000 上触发 202 次
2. **攻击目标**：GPU 的末级页表（last-level page table）存储在 GDDR6 中
3. **跨界升级**：通过篡改页表映射，攻击者获得对 **所有 CPU 物理内存** 的任意读写能力
4. **前提条件**：IOMMU 处于关闭状态（这是绝大多数 BIOS 的默认配置）

### GeForge：锻造 GPU 页表的另一条路径

第二篇论文 *"Hammering GDDR Memory to Forge GPU Page Tables for Fun and Profit"* 则攻击了末级页目录（page directory），而非页表本身。研究者在 RTX 3060 上演示了完整的攻击链：从一个普通用户权限的 CUDA 程序，一路打穿到 **root shell**。

### 第三攻击：IOMMU 也挡不住

2026 年 4 月 3 日披露的第三个变种更为严峻——它针对 RTX A6000，**即使启用 IOMMU 也能实现提权**。这意味着过去十年里被视为硬件级安全边界的 IOMMU，在 GPU Rowhammer 场景下被彻底绕过。

## 威胁模型：谁应该紧张

```
攻击链路:

  恶意 CUDA 程序
       |
       v
  GDDR6 Rowhammer -> 比特翻转
       |
       v
  GPU 页表/页目录被篡改
       |
       v
  GPU 获得 CPU 物理内存任意读写
       |
       v
  Root Shell / 完整系统控制
```

**最直接的受害者是多租户 GPU 云**。在 AWS、Azure、GCP 等提供 GPU 实例的环境中，如果同一物理 GPU 被多个租户共享（通过 MIG 或 vGPU），恶意租户理论上可以通过 Rowhammer 逃逸隔离边界。虽然主流云厂商通常为 GPU 实例启用了 IOMMU，但第三个攻击变种表明这道防线并不可靠。

对 AI 训练集群的影响同样不可忽视。大规模训练任务中的 **静默数据损坏（silent data corruption, SDC）** 本身就是已知问题——Meta 在 2023 年的论文中报告了 GPU 级 SDC 导致训练发散的案例。Rowhammer 将这一问题从概率性故障升级为可被主动利用的攻击向量。

## 防御困境

| 防御手段 | 有效性 | 代价 |
|----------|--------|------|
| 启用 IOMMU | 挡住前两种攻击，挡不住第三种 | 约 5-10% GPU 性能损失 |
| GDDR6 ECC | 理论有效，但消费级 GPU 不支持 | 需要硬件更新换代 |
| GDDR6 TRR | JEDEC 尚未标准化 | 需要 DRAM 厂商协同 |
| 限制 CUDA 内存访问模式 | 可检测部分 hammer 模式 | 影响合法高性能计算 |
| 硬件隔离（SR-IOV） | 增强但不能根治 | 已部署于数据中心 GPU |

核心矛盾在于：GPU 的设计哲学是 **最大化内存带宽利用率**，而 Rowhammer 防御需要 **限制内存访问模式**。这两者在架构层面存在根本冲突。

## 行业影响与判断

**短期（6-12 个月）**：NVIDIA 大概率会发布驱动层面的缓解措施，例如检测异常 hammer 模式并终止进程。云厂商将强制启用 IOMMU 并部署额外的运行时监控。

**中期（1-3 年）**：GDDR7 标准需要纳入类似 TRR 的行级刷新机制。JEDEC 的 GDDR7 规范（预计 2027 年量产）是否会包含这些安全特性，将决定下一代 GPU 是否继续暴露在 Rowhammer 风险之下。

**长期判断**：GPU 安全正在经历 CPU 安全在 2018 年 Spectre/Meltdown 之后的相同觉醒。区别在于 GPU 的攻击面更大（任何 CUDA 程序即可触发），而防御工具更少（缺乏成熟的硬件安全研究基础设施）。**GDDR Rowhammer 有可能成为 GPU 安全领域的 Spectre 时刻**。

---

**参考资料：**

1. [GDDRHammer 论文](https://gddr.fail/files/gddr.pdf) - Andrew Kwong 等
2. [GeForge 论文](https://gddr.fail/files/GeForge.pdf) - GPU 页表伪造攻击
3. [Schneier on Security - Rowhammer Attack Against NVIDIA Chips](https://www.schneier.com/blog/archives/2026/05/rowhammer-attack-against-nvidia-chips.html)
4. [Ars Technica - New rowhammer attacks give complete control of machines running Nvidia GPUs](https://arstechnica.com/security/2026/04/new-rowhammer-attacks-give-complete-control-of-machines-running-nvidia-gpus/)
5. [研究项目主页](https://gddr.fail/)

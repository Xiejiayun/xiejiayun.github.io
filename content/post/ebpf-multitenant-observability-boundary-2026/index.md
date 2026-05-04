---
title: "eBPF 在多租户运行时的可观测性边界：一把双刃剑的工程化反思"
description: "eBPF 已经成为 Linux 内核的事实可编程层，但当它被 SaaS 厂商部署到客户主机上时，'内核里的轻量探针'就变成了'权限黑洞'。本文从内核接口、JIT 验证、容器隔离三个层面分析 eBPF 在多租户场景下的真实风险与工程化边界。"
date: 2026-05-04
slug: "ebpf-multitenant-observability-boundary-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - eBPF
    - Linux内核
    - 可观测性
    - 多租户
draft: false
---

## 一、eBPF 已经赢了，但赢得太彻底

2024-2026 三年，eBPF 完成了从"性能调优工程师的小众玩具"到"云原生可观测性默认底座"的彻底转身。Cilium 拿下了过半的 K8s CNI 份额，Pixie、Coroot、Groundcover 这些 APM 创业公司全部基于 eBPF 重写、Datadog 与 Dynatrace 这些老厂也把 sidecar agent 大量替换成 eBPF 程序。

胜利的代价是：**几乎所有大型生产环境的内核里，都跑着一堆来自第三方 SaaS 厂商的 eBPF 程序**，它们以"无侵入观测"的名义获得了准 root 级别的内核可见性。这个现状在 2026 年开始引发严肃的安全与合规反弹。

## 二、为什么"内核里的轻量探针"是一个误导

eBPF 程序在用户口径里被描述成"沙箱化、有 verifier 校验、不会崩溃内核"。这三句话单独都对，组合起来却严重误导。

| 维度 | 营销叙事 | 工程现实 |
|------|----------|----------|
| 沙箱 | 不能任意访问内核内存 | 通过 helper 函数可读几乎所有进程内存 |
| Verifier | 静态证明程序终止与边界 | 复杂度增长后大量误判，被迫不断放宽规则 |
| 性能影响 | <1% | 高频 kprobe 在突发流量下可达 5-15% |
| 安全 | 需要 CAP_BPF | CAP_BPF 在多数 SaaS agent 部署模板里就是 root |
| 隔离 | per-cgroup attach | tracing 程序系统全局可见，跨 namespace |

最关键的一行是最后一行：**eBPF 的 tracing 类程序(kprobe/uprobe/tracepoint) 没有 namespace 概念**。一个被 attach 到 `do_sys_openat2` 的 kprobe，可以看到这台主机上所有容器、所有租户的文件打开行为。云原生世界辛辛苦苦用 namespace + cgroup 隔离了那么多年，eBPF 一上来就把这层隔离打穿了。

## 三、JIT 验证器的根本性困境

verifier 是 eBPF 的安全基石，它的工作是在加载时静态证明程序：(a) 一定会终止；(b) 不会越界访问；(c) 不会泄漏内核指针到用户空间。

```
   eBPF program
       │
       ▼
   ┌────────────────┐
   │  Verifier      │  指令数限制 1M
   │  路径爆炸检查  │  循环必须可证明终止
   │  指针类型追踪  │  helper 调用白名单
   └────────────────┘
       │ pass
       ▼
   ┌────────────────┐
   │  JIT 编译为    │
   │  原生机器码    │
   └────────────────┘
       │
       ▼
    内核执行 (无运行时检查)
```

困境在于：verifier 的复杂度本身已经成为内核里**最容易出 CVE 的子系统之一**。2023-2025 年仅 verifier 相关的 CVE 就超过 30 个，其中多个是可被本地用户利用提权到 root 的。每次有新 helper 函数、新 map 类型加入，verifier 都需要扩展，每次扩展都引入新的边界条件错误。

更糟的是，为了让现实业务能跑通(比如 Cilium 复杂的策略执行)，verifier 不断被放宽：bounded loops、function-by-function verification、gpl_only 限制松动。这是一条单向街——一旦放宽就很难收回，因为有用户依赖。

## 四、多租户场景下的三类真实风险

**风险一：隐私泄露。** 第三方 APM agent 用 uprobe attach 到 OpenSSL 的 `SSL_write`，号称是为了"自动 trace HTTPS 请求"。客户的明文请求体(可能包含 PII、token、医疗数据)就这样流入了 SaaS 厂商的后端。GDPR、HIPAA 在这件事上至今没有清晰判例。

**风险二：性能干扰。** 一个写得不好的 eBPF 程序 attach 到高频路径(如 `tcp_sendmsg`)，配合 perf event 上报，能让数据库的 P99 延迟翻倍。多租户环境里，A 租户的"无害观测"会让 B 租户的 SLO 崩盘，归因极其困难。

**风险三：供应链攻击。** eBPF 程序由 SaaS 厂商以 .o 字节码下发，客户几乎不可能审计。一旦厂商被入侵或员工内鬼，下发一个恶意 eBPF 程序到几千家企业的内核里，就是新一代 SolarWinds。

## 五、工程化边界的三条建议

我对正在做技术选型的架构师的建议：

1. **把 eBPF 程序加载权限收归平台团队**。绝不允许 SaaS agent 自带 CAP_BPF 在主机上随意加载。建立内部的 eBPF 程序仓库，所有第三方程序经审计、签名、白名单后才放行。
2. **强制使用 LSM hooks + KRSI**。Linux 6.x 起的 BPF LSM 可以在 program load 时拦截，结合 IMA 校验签名。这是目前唯一可落地的"防止恶意 eBPF 加载"机制。
3. **对 uprobe 用户态探针保持极度警惕**。kprobe 至少还在内核里，可观察性有限；uprobe 一旦 attach 到 OpenSSL/glibc 这类基础库，等于把整个用户态行为都暴露了。任何 SaaS 默认开 uprobe 都应该被立即拒绝。

## 六、未来 18 个月的判断

- **2026 H2** 会出现至少一起公开的"通过 eBPF 第三方 agent 实现的横向移动"安全事件，被某 APT 用作横移入口。
- 内核社区会推动 **per-namespace tracing**(已有 RFC)，但落地至少要到 2027；在这之前，多租户隔离仍是空白。
- 商业上，"eBPF 安全治理"会成为 CSPM / CWPP 厂商的下一个 SKU，Sysdig、Wiz 已经在准备相应能力。
- Cilium 与 Tetragon 的母公司 Isovalent(已被 Cisco 收购)有可能推出"eBPF marketplace"，把签名审计变成商业护城河。

## 七、结语

eBPF 是过去十年 Linux 内核最重要的演进，但任何强大的能力都需要配套的治理。当一个技术从"性能工程师的玩具"变成"运行在所有人内核里的默认探针"时，它就不再是单纯的技术问题，而是一个分布式信任与权限治理问题。我们正站在这个转折点上，下一步走错了，可观测性会变成新的攻击面。

---

### 参考资料

- Linux Kernel Documentation, "BPF Verifier" — https://docs.kernel.org/bpf/verifier.html
- Brendan Gregg, "BPF Performance Tools (2nd Edition)" — https://www.brendangregg.com/bpf-performance-tools-book.html
- ISOVALENT / Cilium Project, "Tetragon: eBPF-based Security Observability" — https://tetragon.io/
- USENIX Security 2024, "Verified Verifiers: Formal Reasoning About BPF" — https://www.usenix.org/conference/usenixsecurity24

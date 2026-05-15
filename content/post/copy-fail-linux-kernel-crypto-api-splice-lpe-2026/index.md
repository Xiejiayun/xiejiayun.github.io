---
title: "copy.fail：用 splice() 在 Linux 内核里写四个字节，就能拿到 root"
description: "copy.fail 是近五年来最严重的 Linux 本地提权漏洞之一 —— Theori 用 AF_ALG 套接字串起 splice() 的语义裂缝，把一个'四字节任意写'打成完整内核控制流劫持。本文从漏洞内核机制、利用链构造、影响面、补丁策略与未来防御方向五个维度，深度拆解这次让整个 Linux 发行版生态'抢补丁'的事件。"
date: 2026-05-15
slug: "copy-fail-linux-kernel-crypto-api-splice-lpe-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Linux 内核
    - 本地提权
    - 漏洞利用
    - splice
    - AF_ALG
    - 内核安全
draft: false
---

> **核心观点**：copy.fail 不是一个孤立的 bug，而是 Linux 内核三个独立设计决策的**语义碰撞产物** —— AF_ALG 加密套接字、splice() 零拷贝管道、SKB（socket buffer）的引用语义。任何一个单独都不致命，组合在一起就是"四字节任意写"。这意味着即使内核每个模块都通过了 fuzzing 和 KASAN，跨子系统的边界仍然是 LPE（本地提权）攻击的金矿。整个 Linux 发行版生态在 72 小时内的紧急响应，是 2020 年 BleedingTooth 以来最大规模的一次"假期取消"。

## 一、为什么这次漏洞值得专门写一篇

我们在 2024-2026 年看过太多 Linux CVE，绝大多数是某个驱动写错一个 `kfree_skb` 或者某个 ioctl 没校验 size 参数。它们都很危险，但属于**单点失误**。

copy.fail（CVE-2026-XXXX，Theori 在 4 月 29 日披露）的特殊之处在于：

- **影响所有启用 AF_ALG 的主流发行版**：Ubuntu、Debian、RHEL、Arch、openSUSE、Fedora 全部命中
- **利用稳定性极高**：Theori 公开的 PoC 在多核 / 多内核版本上一打一个准，几乎没有 ROP 的"碰运气"成分
- **修复需要重新设计 splice 与 AF_ALG 的交互**：而不是简单加个 `if` 判断
- **没有缓解措施**：SELinux/AppArmor 不挡，KASLR 不挡，SMAP/SMEP 不挡（因为是逻辑漏洞而非内存破坏起点）

Bruce Schneier 在 5 月初的评论简洁有力："**This is the worst Linux vulnerability in years**." 这话不是营销，是描述事实。

## 二、技术拆解：三个组件的"语义裂缝"

### 2.1 AF_ALG —— 被遗忘的内核加密接口

AF_ALG 是 Linux 内核 2011 年引入的特殊 socket family，让用户态进程可以通过 `socket(AF_ALG, SOCK_SEQPACKET, 0)` 调用内核加密 API。它的设计初衷很合理：

- 嵌入式设备没有 OpenSSL，但内核已经有了完整 crypto 子系统
- userspace 通过 sendmsg/recvmsg 投递数据，由内核做 AES/SHA/HMAC
- 配合硬件加密引擎可以避免数据拷贝到用户态

问题是 AF_ALG 在 2026 年的发行版里**几乎所有进程都能用**（CAP_NET_RAW 不需要、root 不需要、namespace 限制极少）。它是攻击面里"低优先级"的代码，多年没有重大审计。

### 2.2 splice() —— 零拷贝的语义假设

`splice()` 是 Linux 内核的零拷贝原语，允许在两个文件描述符之间直接传递数据**而不经过用户态**：

```c
ssize_t splice(int fd_in, loff_t *off_in,
               int fd_out, loff_t *off_out,
               size_t len, unsigned int flags);
```

内部实现是 pipe buffer（`struct pipe_buffer`）+ 页引用计数。splice 假设：

- 源端会"安全地"把页放进 pipe，源端持有页的强引用
- 目标端从 pipe 里读出页，更新引用计数
- 数据流期间，**页内容不会被原地修改**

这个假设在 socket → pipe → file 的链路里通常成立。但 AF_ALG 不是普通 socket。

### 2.3 SKB 与 crypto request 的双重身份

AF_ALG 在收到 sendmsg 数据时，会构造一个 sk_buff（SKB），把用户数据挂在 SKB 的 frags 数组里，然后**异步**发送给底层 crypto 引擎。crypto 引擎处理完会回写结果。

Theori 团队的关键发现是：

1. AF_ALG socket 实现了 `.splice_read` 操作，可以把 SKB 内容 splice 到 pipe
2. **但 splice 出去的页，仍然是 crypto request 持有的同一个页**
3. crypto 引擎完成时会**就地修改**这个页（写入加密/解密结果）
4. 此时 pipe 另一端从这个页读数据，看到的是 "crypto 正在写一半" 的状态

更狠的是：通过精心构造的 setsockopt(ALG_SET_KEY)，攻击者可以让 crypto 引擎写出**可预测、可控的字节**到目标页。这就把"裂缝"放大成了**任意写四个字节**。

### 2.4 从 4 字节写到完整提权

四个字节任意写在现代内核里已经足够 game over，标准套路：

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1 | 通过 /proc/self/stat 等信息泄露泄露 KASLR slide | 定位 modprobe_path |
| 2 | 用 4 字节写覆盖 `modprobe_path[0..4]` 为攻击者控制的路径 | 劫持 modprobe 触发点 |
| 3 | 触发未知二进制执行（socket(AF_INET, 0xffff)）让内核调用 modprobe | 以 root 权限执行攻击者 shell |
| 4 | 拿到 root | 完成提权 |

Theori 的 PoC 在 Ubuntu 24.04 LTS 默认内核上**端到端 < 2 秒**，比绝大多数 LPE 都干净。

## 三、为什么三方独立审计都漏掉了它

这是一个值得 Linux 内核社区集体反思的问题。

**syzkaller** 每天在 Google 的服务器上 fuzz 数百万次内核调用，AF_ALG 和 splice 都在它的语料库里。但 syzkaller 找不到这种漏洞，原因有三：

1. **跨子系统协议**：syzkaller 通常每条测试单独覆盖一个 socket family。要触发 copy.fail，你必须先 `socket(AF_ALG)`、`bind()`、`ALG_SET_KEY`、`accept()`、`sendmsg()` 写入数据、**同时**用另一个 fd 做 `splice()`、然后另一个 thread 触发 crypto。这种 7+ 步的协同 syzkaller 的随机化策略几乎打不出来。
2. **没有内存破坏**：KASAN/KMSAN 检测的是"读越界、写越界、UAF"。copy.fail 的所有内存访问都在合法分配的 SKB 页里 —— **每个内存访问单独看都是合法的**。
3. **时序依赖**：crypto request 的异步性质意味着漏洞依赖竞争窗口。fuzzer 的标准 oracle（崩溃、KASAN 报错）根本不会触发。

这暴露了一个更深层的问题：**Linux 内核的形式化模型不存在**。AF_ALG 和 splice 之间从来没有过共同的 invariant 文档。即使有 Murat Demirbas 倡导的 TLA+ 形式化建模，AF_ALG 也几乎不可能被覆盖 —— 因为它的状态机定义散布在 5 个文件、200 多个函数里。

Trail of Bits 在并行的 Go fuzzing 工具改进工作中也明确指出："Path constraints are hard to solve. Structured inputs usually need handmade parsing." 这是整个 fuzzing 范式当前的天花板。

## 四、影响面：到底多严重？

### 4.1 直接命中的发行版

| 发行版 | 默认启用 AF_ALG | 默认内核版本 | 补丁状态（截至 5 月 14 日） |
|--------|-----------------|---------------|------------------------------|
| Ubuntu 24.04 LTS | ✅ | 6.8 | 已发布 USN |
| Debian 12 (bookworm) | ✅ | 6.1 | 已发布 DSA |
| RHEL 9.5 | ✅ | 5.14 (backport) | 已发布 RHSA |
| Arch | ✅ | 6.14 | 已发布 |
| Alpine | ⚠️ 部分构建禁用 | 6.6 | 部分免疫 |
| Container Optimized OS | ❌（已禁用） | 6.6 | 免疫 |
| Android 通用内核 (GKI) | ✅ | 6.6 | 已发布 ASB-2026-05 |

Android 这一栏值得多说一句：通过 termux 等 app，普通应用层进程是可以打到 AF_ALG 的（视厂商配置）。这意味着 copy.fail 在移动端的"威胁面"远大于一般 Linux LPE。

### 4.2 云厂商与容器场景

云上更复杂。AWS、GCP、Azure 的虚拟机本身不直接受影响（hypervisor 隔离），但**容器场景**是重灾区：

- Docker 默认 seccomp profile **允许** socket(AF_ALG)，因为它属于 "common networking"
- Kubernetes 集群里的 sidecar 容器、untrusted workloads、CI runner 都可能被滥用
- gVisor / Kata Containers 是少数缓解方案（额外的 syscall filter 层）

GitHub Actions、GitLab CI 等共享 runner 平台在 5 月 1-5 日紧急下架了相当一批可疑 image，原因就是怀疑有人在 PoC 公开后试图通过 CI job 横向渗透。

### 4.3 Xe Iaso 的警告

独立安全研究员 Xe Iaso 在 copy.fail 公开几天后写了一篇短文《Maybe you shouldn't install new software for a bit》，里面提到至少有两个**衍生漏洞**已经被发现：

- **Copy Fail 2: Electric Boogaloo** —— 复用了同样的 AF_ALG 弱点但走不同 sink
- **Dirty Frag** —— 在 SKB fragment 处理路径上发现的并发问题

她的建议在安全圈引发了不小争议：在补丁完全收敛前，**暂缓安装非必要新软件**。这个建议听起来保守，但反映了一个现实 —— 公开 PoC + 衍生漏洞活跃期 = 供应链投毒的最佳窗口。

## 五、补丁策略与防御未来

### 5.1 上游补丁的核心思路

Greg Kroah-Hartman 在 5 月 1 日合入主线的补丁做了三件事：

1. **AF_ALG 的 .splice_read 现在会强制 copy**：通过 `skb_copy_bits()` 而非引用页指针
2. **crypto request 完成前阻塞 splice**：增加 `crypto_wait` 信号量
3. **新增 sysctl `kernel.afalg_splice_disabled`**：发行版可以选择直接禁用这条路径

第一项是"对症"，第二项是"对因"，第三项是"对未来"。三层防御组合起来才算稳。

### 5.2 缓解措施清单（运维必读）

如果你还没打补丁，按优先级建议：

```bash
# 1. 立即禁用 AF_ALG 模块加载（适用于不依赖硬件加密的服务器）
echo "blacklist algif_hash"  | sudo tee /etc/modprobe.d/disable-afalg.conf
echo "blacklist algif_skcipher" | sudo tee -a /etc/modprobe.d/disable-afalg.conf
echo "blacklist algif_rng"   | sudo tee -a /etc/modprobe.d/disable-afalg.conf
echo "blacklist algif_aead"  | sudo tee -a /etc/modprobe.d/disable-afalg.conf

# 2. 容器场景：在 seccomp profile 里禁掉 socket(AF_ALG)
# Docker: --security-opt seccomp=profile.json
# Kubernetes: PSP/PodSecurity 配合 RuntimeDefault + 自定义 profile

# 3. 监控异常 splice 调用
# auditd 规则：
sudo auditctl -a always,exit -F arch=b64 -S splice -F a0!=0 -k splice-monitor
```

### 5.3 真正需要改变的：内核子系统接口设计

copy.fail 的根因不是 AF_ALG 的 bug，而是 Linux 内核**模块化设计哲学**在 2026 年遇到的瓶颈：

> 每个子系统单独开发、单独审计，跨子系统的隐式契约从未明确写下来。

splice、io_uring、AF_ALG、io_async、page cache —— 这些子系统两两之间至少有 5-10 个隐式假设。任何一个被打破都是新的 LPE。

未来三个改进方向：

| 方向 | 现状 | 期望 |
|------|------|------|
| **跨子系统形式化建模** | 几乎没有 | TLA+ / Lean4 描述关键接口契约 |
| **AI 辅助代码审计** | 实验阶段 | 把跨函数、跨文件的数据流图喂给 LLM 做语义审查 |
| **接口"自描述"机制** | 文档分散 | 子系统注册时声明对页所有权、并发可见性的假设 |

Trail of Bits 的 Trailmark 项目（把代码解析成可查询的 call graph，再让 LLM 处理）是一个有意思的早期尝试。Murat Demirbas 关于"系统设计的两个抽象：隐藏或减少"的讨论，恰好命中这次事件的核心 —— AF_ALG 选择了"隐藏复杂度"（让应用看不到 crypto 引擎的异步性），而 splice 选择了"减少拷贝"，两者对**页所有权**的假设根本不一致。

## 六、给读者的可执行建议

不管你是开发者还是运维，从 copy.fail 你应该带走这几条：

1. **立即检查所有运行 Linux 的机器**：是否打了 5 月的内核补丁。一周内未打补丁的服务器应该视为已被入侵假设处理。
2. **容器策略需要更新**：默认 seccomp profile 该收紧的就收紧。如果你的容器不需要硬件加密引擎，**关掉 AF_ALG**。
3. **关注 Theori、Trail of Bits、Project Zero 的后续披露**：copy.fail 不是终点，是一个新研究方向的起点。AF_ALG × splice 类的跨子系统漏洞会被系统性地挖掘。
4. **重新审视 syscall 攻击面**：你的应用真的需要 splice / sendfile / io_uring / AF_ALG 吗？不需要的就用 seccomp 拒掉。
5. **如果你在做内核开发**：开始为你维护的子系统**写下来**它对外暴露的不变式（invariants），即使是粗糙的 markdown 文档。这是抵御下一个 copy.fail 的最低成本动作。

## 结语

Linux 内核已经 33 岁了。它在 2026 年面对的安全挑战，不再是"某行代码写错了"，而是"**整个系统的复杂度超过了任何单一审计者能装进脑子里的边界**"。copy.fail 让我们看清了一件事：在 fuzzing、KASAN、SMAP、KASLR 全开的现代 Linux 上，**协议层语义裂缝**才是下一代 LPE 的主战场。

防御方有形式化建模、AI 辅助审计、子系统契约文档这些武器，但都还远未成熟。在它们成熟之前，每一位运维工程师、每一家云厂商、每一个发行版维护者，都要继续在补丁星期二里熬夜。

这就是 2026 年 5 月的 Linux 现实。

## 参考来源

1. Bruce Schneier — [Copy.Fail Linux Vulnerability](https://www.schneier.com/blog/archives/2026/05/copy-fail-linux-vulnerability.html), Schneier on Security
2. Theori — Copy.Fail 原始披露报告与 PoC（2026 年 4 月 29 日）
3. Xe Iaso — [Maybe you shouldn't install new software for a bit](https://xeiaso.net/blog/2026/abstain-from-install/)
4. Trail of Bits — [Go fuzzing was missing half the toolkit](https://blog.trailofbits.com/2026/05/12/go-fuzzing-was-missing-half-the-toolkit.-we-forked-the-toolchain-to-fix-it./)（关于 fuzzing 范式的局限）
5. Trail of Bits — [Trailmark turns code into graphs](https://blog.trailofbits.com/2026/04/23/trailmark-turns-code-into-graphs/)
6. Murat Demirbas — [The Two Abstractions of System Design: Hide or Reduce](https://muratbuffalo.blogspot.com/)
7. Linux Kernel Mailing List — AF_ALG splice patches by Greg KH（2026-05-01 主线合入）
8. Ubuntu Security Notice / Debian Security Advisory / RHSA-2026 系列公告
9. Android Security Bulletin 2026-05

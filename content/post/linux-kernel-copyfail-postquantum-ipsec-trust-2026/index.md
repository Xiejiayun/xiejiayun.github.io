---
title: "Copy Fail 与后量子 IPsec：内核态信任根的双向时间旅行"
description: "同一周里，CISA 在为 30 年前的 Linux 内核内存安全漏洞 救火，Cloudflare 把后量子 IPsec 推到 GA。基础设施信任根正在两个时间方向上同时撕裂。"
date: 2026-05-05
slug: "linux-kernel-copyfail-postquantum-ipsec-trust-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Linux内核
    - 后量子密码
    - 内存安全
    - 安全架构
    - PQC
draft: false
---

## 引子：同一周，两条相反方向的新闻

2026 年 5 月初的安全圈出现了一个罕见的并列：周一，CISA（美国网络安全和基础设施安全局）发出紧急通告，要求联邦机构在三周内修补一组被研究者命名为 "Copy Fail" 的 Linux 内核漏洞——它们的根因是 `copy_from_user` / `copy_to_user` 系列函数在若干子系统中长期存在的边界检查缺失，可在普通用户态触发越界写入并最终拿到 root；周三，Cloudflare 宣布其 Magic WAN 上的 IPsec 隧道后量子加密（基于 ML-KEM-768 的混合 Kyber/X25519 密钥协商）正式 GA，所有付费用户可一键开启。

把两条新闻并排读，会有一种奇怪的眩晕感。一边，传输层在为 2030 年代才可能成熟的容错量子计算机提前布防；另一边，操作系统层还在补 1991 年 Linus 写下第一版 syscall 入口时就埋下的旧账。基础设施的"信任根"（Root of Trust）正在两个时间方向上同时被撕裂——一头朝未来跑得飞快，一头被三十年前的 C 语言惯性死死拽住。

这篇文章想梳理这种撕裂背后的结构性原因，并提出一个可操作的分层迁移策略。

## 一、Copy Fail 的解剖：一个 1995 年风格的 bug 在 2026 年要人命

`copy_from_user` 是 Linux 内核里最古老、最基础的边界 API 之一。它的契约简单到几乎"不像 API"：从用户态地址 `src` 拷 `n` 字节到内核地址 `dst`，返回未拷贝的字节数。问题是，它把"`n` 是否合法"这件事完全甩给调用者。

CISA 通告涉及的 CVE 集群（覆盖 netlink、io_uring 辅助路径、若干字符设备驱动）都是同一个反模式：

```c
// 极度简化的反模式示意
struct user_req hdr;
if (copy_from_user(&hdr, ubuf, sizeof(hdr)))
    return -EFAULT;
buf = kmalloc(hdr.len, GFP_KERNEL);          // ① hdr.len 未校验上界
if (copy_from_user(buf, ubuf + sizeof(hdr), hdr.len))  // ② 也未校验下界/整数溢出
    ...
```

上面两个 `copy_from_user` 都"成功返回 0"，但 `hdr.len` 可能是 `0xffffffff`，可能与 `sizeof(hdr)` 相加溢出，可能让后续的 `memcpy` 在 slab 上越界写。这类问题在 2003、2008、2014、2019 都曾批量爆发过，每次内核社区都加一层 hardening：`__must_check`、`copy_struct_from_user`、`check_add_overflow`、CONFIG_HARDENED_USERCOPY、KASAN……但漏洞依旧周期性地复发。

为什么补了二十年还没补完？因为 C 语言里"边界"不是类型系统的一部分，而是一种**文化约定**。每一个新写驱动的开发者、每一个被合并进主线的子系统，都要重新学习这个约定。一旦评审者疲劳，漏洞就回来了。Copy Fail 这个名字起得好——它讽刺的不是某一段代码，而是"复制"这个动作本身在内核里仍然是一种**未被类型化的危险操作**。

## 二、Cloudflare 后量子 IPsec GA：传输层的"提前三年布防"

把镜头切到另一头。Cloudflare 宣布的 PQC IPsec GA 用的是 IETF 草案 `draft-ietf-ipsecme-ikev2-pq-auth` 与 `draft-kampanakis-ml-kem-ikev2` 的组合，IKEv2 的 SA 协商阶段把 X25519 与 ML-KEM-768（NIST FIPS 203 标准化的 Kyber 变体）做混合密钥派生：最终 session key = KDF(X25519_shared || MLKEM_shared)。即使未来某天 X25519 被 Shor 算法破掉，攻击者仍需要同时破 ML-KEM 才能解密今天录下的流量——这就是所谓的 "harvest now, decrypt later" 防御。

这个动作在工程上并不戏剧性：ML-KEM-768 的公钥 1184 字节、密文 1088 字节，比 X25519 的 32 字节胖很多，但 IKE 阶段一次性开销可以容忍；CPU 开销在现代 x86 上约几百微秒，完全淹没在 IPsec 隧道建立的网络往返里。真正戏剧性的是**时间错位**：威胁要等到 2030 年代中后期 CRQC（Cryptographically Relevant Quantum Computer）出现才会兑现，但 Cloudflare 今天就把它做成默认可选项。

为什么传输层愿意提前三年甚至五年布防？因为：

1. **协议层有清晰的版本协商机制**（IKEv2 的 Transform ID），新算法可以与旧算法并存，回退成本低；
2. **密码学库与协议解耦**：libsodium / OpenSSL / BoringSSL 把 ML-KEM 实现塞进去，应用层几乎零改动；
3. **"录下来以后解"的威胁模型让监管和合规推力极强**，NSA CNSA 2.0、欧盟 ENISA、CNNIC 都在 2024–2025 年陆续公布了 PQC 迁移时间表。

传输层的迁移路径，是一条被协议、库、合规三股力量同时拉动的高速公路。

## 三、信任根栈：两个方向的撕裂

让我们把整个信任栈画出来，看看撕裂发生在哪一层：

```
┌──────────────────────────────────────────────────────────────┐
│  应用 / 业务逻辑                                              │
├──────────────────────────────────────────────────────────────┤
│  TLS 1.3 + ML-KEM 混合 (浏览器 2024 起 GA)                    │ ←─ 已 PQC
├──────────────────────────────────────────────────────────────┤
│  IPsec / WireGuard PQ (Cloudflare 2026-05 GA)                │ ←─ 刚 PQC
├──────────────────────────────────────────────────────────────┤
│  Socket / syscall ABI  (1991 设计，copy_from_user)           │ ←─ Copy Fail
├──────────────────────────────────────────────────────────────┤
│  内核 mm / fs / net 核心  (C, 约 2000 万行)                  │ ←─ 仍是 C
├──────────────────────────────────────────────────────────────┤
│  驱动层  (部分 Rust for Linux 试点)                           │ ←─ 局部 Rust
├──────────────────────────────────────────────────────────────┤
│  TEE / TPM / Secure Boot  (硬件信任根, 多数仍 RSA-2048)       │ ←─ 待 PQC
└──────────────────────────────────────────────────────────────┘
              ↑                                ↓
        未来威胁布防                     旧账尚未还清
```

撕裂点在**第三、四层之间**：上面是已经或正在 PQC 化的密码协议栈，下面是用 C 写的、仍依靠人肉边界检查的内核核心。攻击者根本不需要破密码——他直接从 syscall 进来拿 root。这就像把家门换成生物识别防爆门，但厨房窗户还是 1995 年的木框纱窗。

## 四、Rust for Linux 的进度：到边界还有多远

Rust for Linux 自 2022 年并入主线，到 2026 年已覆盖：

- Binder（Android IPC，6.10 起）
- 部分 NVMe / null_blk 驱动
- Apple AGX GPU 驱动（asahi）
- PHY 子系统抽象、misc 驱动框架

但**核心 mm、vfs、net 协议栈、调度器、io_uring 主路径仍是纯 C**。这不是技术问题，而是 review 带宽与 ABI 稳定性的问题：核心子系统每年要接受成千次补丁，把维护者群体切成"懂 Rust"和"不懂 Rust"两半，会让合并节奏崩盘。

但 Copy Fail 这类漏洞恰恰发生在**边界**：用户态 ↔ 内核态、网络包 ↔ 内核结构、设备 DMA ↔ kmalloc 缓冲区。边界子系统的特点是接口稳定（syscall 编号几乎不变）、逻辑相对独立、且**类型系统能直接消除整类漏洞**——Rust 的 `&[u8]` 自带长度，根本写不出"传一个长度参数然后忘了校验"的代码。

下表对比 C 与 Rust 在边界检查上的成本结构：

| 维度 | C 子系统 | Rust 子系统 |
|------|---------|-------------|
| 长度参数 | 显式 `size_t`，调用者负责 | `&[T]` / `&mut [T]` 内嵌长度 |
| 越界写 | 编译期不可见，KASAN 运行期捕获 | 编译期或 panic（不可达 UB） |
| 整数溢出 | 需 `check_add_overflow` 宏 | `checked_add` / `overflowing_*` 强制 |
| 用户态指针 | `__user` 注解，sparse 静态检查 | `UserSlice` 类型隔离 |
| Review 成本 | 高（人眼追踪每个 len） | 低（类型系统自动追踪） |
| 移植成本 | — | 高（生态、工具链、维护者培训） |

结论是：边界子系统的 ROI 最高。

## 五、一个分层迁移建议：内核也该有"PQC 时间表"

PQC 之所以推得动，是因为它有**清晰的分层时间表**（NIST 2024 标准化、CNSA 2.0 给出 2030/2035 截止线）。内核内存安全也应该被组织成同样的路线图，而不是任由零散的"哪个驱动维护者愿意学 Rust"自然演化。

我的提议是把内核子系统按**信任边界距离**分级：

- **L0（最高优先级）**：syscall 入口胶水代码、netlink 解析器、ioctl dispatcher、io_uring SQE 解码器。这些是攻击面最直接的边界翻译层，应在 2027 年内完成 Rust 化或形式化等价物。
- **L1**：协议解析（TCP/IP option、SCTP、Bluetooth L2CAP、USB descriptor）。历史漏洞密度最高，2028–2029 年迁移。
- **L2**：文件系统元数据解析（ext4/xfs/btrfs 的 on-disk 结构反序列化）。同样是不可信输入，2029–2030 年。
- **L3**：mm 核心、调度器、locking primitive。可以最后迁，因为接口稳定、review 群体最专精。

与此并行，密码学子系统（crypto/、KEYS、IMA、dm-crypt、fscrypt）走另一条 PQC 时间表，对齐 NIST FIPS 203/204/205。两条时间表交汇于 2030：那时内核既不再为 `copy_from_user` 漏洞救火，也不再依赖被 Shor 威胁的非对称算法。

这听起来雄心勃勃。但是想想：Cloudflare 已经做完了它那一层；浏览器 PQC 化也已基本完成。如果内核保持现在的速度，2030 年的图景将是——量子计算机还没造出来，但 Linux 服务器已经被 Copy Fail 的下一代变种打穿了无数次。

## 六、过渡期的现实主义：fuzzing 仍是最高 ROI 的防线

承认现实：核心 C 子系统在未来五年仍会是 C。在那之前，能把漏洞密度压到最低的，是**结构化 fuzzing**。Trail of Bits 在 2025 年发布的 "Extending Ruzzy with LibAFL" 把 Ruzzy（Ruby fuzzer）的 in-process 模式重写到 LibAFL 之上，拿到了一个可观察的提速：covergae 反馈 + persistent mode + cmplog，让原本一周才能复现的崩溃在几小时内浮现。

这个工作的方法论可以直接搬到内核：

- syzkaller 已经在做 syscall 序列 fuzzing，但它的结构感知（对 netlink/ioctl 二进制布局的理解）仍可大幅增强；
- LibAFL 的 cmplog（比较指令日志）可以帮 fuzzer 自动猜出 magic number、长度字段，对 Copy Fail 这种"长度字段是关键"的漏洞特别有效；
- KASAN + KCOV + LibAFL 三件套，加上每个 LTS 内核版本的持续 fuzzing 农场，应该是发行版（RHEL / SUSE / Ubuntu Pro）的合规底线，而不是"研究者的额外贡献"。

把 fuzzing 提升到合规级别——就像 PQC 迁移之于密码学——是把"靠人审"的文化转向"靠机器证伪"的文化。这是 C 内核在 Rust 化完成前唯一现实的安全网。

## 七、结语：信任根的两端，要在中间相遇

Copy Fail 与后量子 IPsec GA 出现在同一周，不是巧合，而是同一棵信任树两端开花的不同节奏。传输层用了三十年把密码学从 DES 推进到 ML-KEM，每一次迁移都靠协议协商的优雅机制完成；操作系统层用了三十年也没把 `copy_from_user` 的契约写进类型系统，因为 C 给不了它这个能力。

未来五年，真正的安全工程战场不在更前沿的密码套件，而在这条**断裂带**：

- 给边界子系统装上类型化的安全带（Rust、形式化验证、或至少更严格的 sparse 注解）；
- 给密码学子系统换上 PQC 引擎，对齐 2030 时间表；
- 给所有仍是 C 的核心子系统配上工业级 fuzzing 农场，作为过渡期的兜底。

如果这三件事能在 2030 年前完成，那时回头看 2026 年这一周，我们会说：那是基础设施信任根开始相向而行的转折点。如果完不成，下一封 CISA 紧急通告的脚注里，写的就不再是"请在三周内打补丁"，而是"请评估你的密钥是否已被记录"。

那将是另一个故事，而且不会有补丁版本号。

## 引用来源

- Tom's Hardware — CISA "Copy Fail" Linux kernel advisory coverage: <https://www.tomshardware.com/>
- Cloudflare Blog — "Post-quantum encryption for Cloudflare IPsec is generally available": <https://blog.cloudflare.com/>
- Trail of Bits — "Extending Ruzzy with LibAFL": <https://blog.trailofbits.com/>
- NIST FIPS 203 (ML-KEM) standard: <https://csrc.nist.gov/pubs/fips/203/final>
- NIST FIPS 204 (ML-DSA) standard: <https://csrc.nist.gov/pubs/fips/204/final>
- Linux Kernel CVE database: <https://cve.kernel.org/>
- Rust for Linux 项目主页: <https://rust-for-linux.com/>
- NSA CNSA 2.0 Cryptographic Suite: <https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF>
- syzkaller 项目: <https://github.com/google/syzkaller>
- IETF draft-kampanakis-ml-kem-ikev2: <https://datatracker.ietf.org/doc/draft-kampanakis-ml-kem-ikev2/>

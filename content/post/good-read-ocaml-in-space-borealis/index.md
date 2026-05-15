---
title: "【好文共赏】OCaml 第一次飞上轨道：Tarides 把 12 年 unikernel 研究塞进 5 MB 卫星载荷"
description: "Thomas Gazagnaire 的 Borealis 项目把 pure-OCaml CCSDS 协议栈送进低地球轨道，附带 ML-DSA-65 后量子 OTAR、OxCaml 把 p99.9 延迟从 29 ns 砍到 9 ns，并把 GC 完全清零。这是 2026 年关于 systems programming 的最重要一篇博客之一。"
date: 2026-05-15
slug: "good-read-ocaml-in-space-borealis"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - OCaml
    - 太空软件
    - 后量子密码
    - 形式化验证
    - Unikernel
    - 系统编程
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[O(x)Caml in Space](https://gazagnaire.org/blog/2026-05-14-borealis.html) | 作者：Thomas Gazagnaire（Parsimoni · Tarides · MirageOS 创始团队） | 发布：2026-05-14 | 阅读时长：约 18 分钟
>
> **多模评分**：Opus 9.4 / Sonnet 9.1 / Gemini 9.2（综合 **9.2 / 10**）
>
> **一句话推荐**：函数式编程 12 年 unikernel 长征的高潮——纯 OCaml 的 CCSDS 协议栈在 2026 年 4 月 23 日首次在低地球轨道运行，并且把 OxCaml 的栈分配能力、ML-DSA-65 后量子 OTAR、formally verified 密码学链路、GADT 协议状态机这些"实验室特性"一次性塞进一个 5–10 MB 的飞行二进制里。

---

## 一、为什么值得读

这是一篇你很久没有读到过的"硬核到底"博客。它的真正稀缺之处不在于"OCaml 上太空"这个噱头，而在于**它把过去十二年里散落在 ICFP/ASPLOS/USENIX Security/RFC/NIST FIPS 各个角落的研究成果，第一次串成一根能从 git push 一直拉到低地球轨道的工程线**。

读完整篇之后，你会意识到 Gazagnaire 真正在讲的故事其实有三层：

第一层是"用功能式语言去做安全敏感的协议栈"。这不是新主张——nqsb-TLS 在 USENIX Security 2015 就证过 OCaml 写 TLS reference implementation 的可行性，Nitrokey 的 NetHSM 把同一套栈量产了十年。Borealis 的贡献是把这条路从 TLS 推到 CCSDS，把"互联网协议"换成"星地协议"。

第二层是"用类型系统替代很多本来要靠运行时反射做的事"。GADT 把协议状态机的合法转移在编译期固定，schema 驱动的 ocaml-wire codec 直接对接 Microsoft EverParse 生成的 F\* 验证解析器，"functional core, imperative shell" 让同一份 `protect_bundle` 函数既是飞控代码、也是地面工具、也是测试 oracle。这套范式如果你写过 Cap'n Proto + GADT 的状态机就知道有多优雅，但能在卫星飞控这种"重 30 万美金、错一次代价百倍"的场景里**实战落地**，是另一回事。

第三层是 OxCaml 真正的工业级成熟。`exclave_ stack_` 让 p99.9 延迟从 29 ns 掉到 9 ns，394 次 minor GC 直接归零——这意味着 Jane Street 提了多年的"opt-in low-level mode system"已经被一个完全独立的团队（Tarides/Parsimoni）拿来做真实的低抖动 hot path，而不再只是 Jane Street 内部交易系统的 trick。这种"实验性编译器特性走出母体"的时刻，在过去十年也只发生过几次，比如 Rust 的 async/await、Go 的 generics。

如果你对内存安全、协议栈设计、太空软件、unikernel、OCaml 生态、或者"小团队如何在 12 年里把一篇 ASPLOS 论文撑到上轨道"这些话题中的任意一条感兴趣，这篇都值得你把咖啡端起来认真读一遍——而且作者非常体贴地把每个论断都加了引用，方便你下钻。

---

## 二、核心观点深度解读

### 1. 一个"日常 daemon"如何变成"轨道上的 daemon"

Borealis 的运行形态出奇地朴素：它是一个 5–10 MB 的 OCaml 二进制，静态链接，打包成 `FROM scratch` 的 Docker 镜像，跑在 DPhi Space 提供的 Arm Cortex-A53 ×4 / 4 GB RAM Linux SoC 上。在轨与地面之间，它说的是一套标准的客户端-服务器协议：telemetry queries、commands、responses、OTAR rekey。任何写过后端 daemon 的人看到这段代码都会觉得熟悉。

> 原文：
> > Borealis is a daemon. On both the ground and the satellite it speaks a normal client-server protocol […]. What is unusual is the wire underneath.

奇怪的事情发生在 wire 之下。DPhi 的载荷模块不给租户开放真实的 radio 接口，**只暴露一个文件系统**：你把 bundle 写到 `/uplink/`，他们在下一次过境时把这些字节流当成不透明数据转发给地面；反向同理。Borealis 把这个 filesystem 当成一个**延迟容忍网络（Delay-Tolerant Network）**——每条 telemetry、每个命令、每张相机照片，都被序列化成 BPv7（RFC 9171）bundle 写到磁盘，DPhi 看见的永远是不透明字节。

这个"文件系统即网络"的抽象，让"卫星 payload"这件事彻底民主化：只要你能写一个 Linux 上跑的 daemon，理论上就能把它送上 hosted-payload。门槛不再是"和 JPL 谈三年合同"，而是"申请一个 DPhi 账号"。这一点和 SpaceX 把发射成本砍掉的逻辑同构——**只是这次砍掉的是软件侧的进入成本**。

### 2. 为什么 OCaml，而不是 Rust 或 C

作者讲了一个非常直白的统计：根据 Microsoft MSRC 2019 和 Chromium 2020 的研究，**C/C++ 代码库里大约 70% 的严重 CVE 源自内存破坏**——缓冲区溢出、UAF、整数溢出。Borealis 跑的恰恰是密码学边界：SDLS、BPSec、OTAR 的所有解析逻辑都在处理"敌人可控的密文与密钥材料"。这正是 memory bug 杀伤力最大的地方。

> 原文：
> > Our security extensions (SDLS, BPSec, and OTAR) all handle ciphertexts and key material, which is exactly where memory bugs hurt most.

NASA 自己维护的 C 参考实现 **CryptoLib** 历史上就吃过一个典型的 bug：TC frame 解析器里的整数下溢，导致堆缓冲区溢出。如果你用 OCaml 重写这一层，"整数下溢导致下游 size 计算错误"这一类问题被**类型 + 边界检查**按构造消除掉。这不是"我们更小心"——这是"编译器拒绝这种写法"。

但作者也极其诚实地标注边界：OCaml runtime 仍然是 C，下面的 Linux kernel、bootloader 也都是 C，全都还在可信计算基（TCB）里。**memory safety helps where it helps, and is not a substitute for a trusted compute base audit.** 这种"诚实承认 TCB 边界"的克制，比"换种语言一切问题都解决"的销售辞令值钱多了。（这点与我们在[《Copy Fail 与后量子 IPsec》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/)里讨论的"内核态信任根的脆弱性"完全对齐——应用层的形式化和内核层的脆弱性是同一根问题的两端。）

### 3. 共生卫星的威胁模型：为什么单靠容器隔离没用

Borealis 跑在 hosted-payload 卫星上，这意味着**多家租户共享同一颗卫星的总线、电源、姿态控制**。每家租户的软件跑在共享 Linux 上的不同容器里。地面工程师对这种部署再熟悉不过——直到他们意识到内核态漏洞会让所有容器边界崩溃。

作者一连点了几个近年来的"容器逃逸/通用 LPE"案例：2022 年的 Dirty Pipe、2024 年的 nf_tables UAF、2026 年的 Dirty Frag 与 Fragnesia、刚刚在 2026 年 4 月末公开的"Copy Fail"——后者一击命中所有主流发行版。这些都是**结构性内核漏洞**，每隔一两年就会换一种新形式回来：

> 原文：
> > the same primitives keep resurfacing in new forms […]. On a ground server you can run the package manager and reboot; in orbit, kernel patching is its own delivery problem with its own delay, and is sometimes not possible at all.

在地面上你可以一个 `apt upgrade && reboot` 解决，但在轨道上，"打 kernel 补丁"这件事本身就是一道软件交付难题：上行带宽 KB 级、过境窗口几分钟、有些任务根本就不允许重启。**容器隔离不是真的隔离，密码学信封才是。** Borealis 的设计就是把这一点贯彻到底：每个 bundle 都被 BPSec 包成两个 extension block——一个加密 payload，一个 authenticate 整包；序列号防重放；密钥由 SDLS Security Association 提供。卫星运营商看见的永远是不透明字节，**routing path 整个被踢出 trust path**。

这种威胁模型其实在地面也越来越值钱：当我们的 microservice 之间互相调用、共享 Kubernetes 集群、共享 sidecar 网络时，"信任 mesh 不被打穿"这件事和"信任卫星总线运营商"一样脆弱。Borealis 给出的答案是冷酷而正确的——**别信任 mesh，给每个 message 自带信封**。这点与[《WebRTC 是问题本身》](/post/good-read-moq-webrtc-openai-voice-ai/)讨论的"传输协议要不要承担安全语义"形成有趣对照：前者要把安全语义往应用层推，后者也是。

### 4. OxCaml 的真实工业效果：p99.9 从 29 ns 到 9 ns

文中真正让 systems programmer 心跳加速的是这张性能表：

| 指标 | Stock OCaml 5.3 | OxCaml 5.2+ox（exclave_ stack_） |
|---|---|---|
| p50 延迟 | 与 OxCaml 相当 | — |
| **p99.9 延迟** | **29 ns** | **9 ns** |
| Minor GC 计数 | 394 | **0** |
| Throughput | 与 OxCaml 相当 | — |
| 测试规模 | 25.6 M packets，10 次运行中位数 | — |

OxCaml 是 Jane Street 维护的 OCaml 实验分支，关键是它的"mode system"——一个与传统类型系统**正交**的维度，跟踪 `locality`（值能不能逃出当前作用域）、`uniqueness`（同一资源是否只能被一个所有者使用）、`capabilities`（谁有权访问什么）。听起来抽象，但用法非常具体：

```ocaml
(* 把每包 dispatch 时用到的临时记录从堆挪到栈 *)
let dispatch hdr =
  exclave_ stack_ { apid; seq_count; data_len }
```

`exclave_ stack_` 注释告诉编译器："这个记录在调用栈上分配，不允许逃逸出 dispatch scope；消费者必须用 `@ local` 接收"。类型系统证明这个记录不会被存到外部数据结构、不会被某个 closure 捕获、不会跨线程传递——一旦证明通过，**堆分配消失、GC 没东西可收**。

> 原文：
> > Throughput is comparable; the win is jitter, and on a hosted-payload module with hundreds of microseconds of jitter budget, that is the whole game.

这是一句必须念三遍的话："the win is jitter"。throughput 大家差不多，**抖动**才是软实时系统真正的杀手。394 次 minor GC 听起来不多——但每一次都是一个不可预测的几百微秒尖峰。把它清零，等于把 hot path 的延迟分布从"有长尾"变成"几乎是常数"。

OxCaml 的意义在更宏观的层面：它把"低层手动控制"和"高层 GC 便利"这两件原本对立的事**做成了 opt-in**。你的协议栈 90% 还是普通 OCaml，享受所有 GC 友好的好处；只有那 1% 的 dispatch hot path，你用 `exclave_ stack_` 把它锤平。这种 layered intensity 的语言设计，是 Rust 的 `unsafe`、C++ 的 `constexpr`、Go 的 SIMD assembly 这些"裂口"都没能做得这么干净的事情。

### 5. 后量子 OTAR：把 NASA-STD-1006A 写进生产代码

后量子密码学（PQC）今年的关键词是"crypto agility"——你的系统要随时能换签名算法、换密钥。卫星把这件事推到了极限：一颗卫星的设计寿命是 10–15 年，**今天烧进去的签名密钥，必须撑到量子计算机有能力打破它的那一天之前还能换掉**。

Borealis 用的签名算法是 **ML-DSA-65**（NIST FIPS 204 标准化的后量子签名，相当于 Dilithium 3 的中等参数集）。NASA-STD-1006A——NASA 的太空系统保护标准——已经把"后量子命令认证"从"future option"升级为"requirement"。这是一个非常少见的"标准跑在产品前面"的时刻，因为政府客户不愿等到量子计算真正威胁现役卫星的那天才开始换。

OTAR 让密钥轮换在轨道上完成：地面把新的 PQ 公钥 + 签名传上来，卫星先放在 staging slot，校验通过后切换。Borealis 的当前固件是"收到即激活"，但协议本身支持"地面单独触发激活"的两步式安全升级——切换是 flight loop 的配置改动，**不是新代码**。这是非常老派但正确的工程：**让最危险的操作可以被验证两次**。

但作者保留了一个诚实的失败模式：**master key 没有 rotation 路径**。它是在卫星和火箭整合时烧进去的，轨道上没有比"地面整合"更受信任的通道。如果泄漏，全栈控制权丢失；如果损坏，全栈不可达。

> 原文：
> > That is the honest failure mode for a long mission with no hardware-backed key storage.

为什么不上 TPM/secure element？因为**辐照容忍的硬件信任根仍然是开放硬件问题**。Borealis 的态度是"把这件事写明白，而不是装作解决了"。这种"边界诚实"贯穿整篇文章，比所有营销文案都更让人信任作者。（这点与[《Trail of Bits 用经典计算击败 Google 量子密码分析》](/post/trail-of-bits-quantum-cryptanalysis-google-2026/)里讨论的"PQ 迁移到底要多急"形成漂亮的双向对照——PQC 的窗口期既不像 Google 量子组说的那么紧，也绝不像怀疑论者说的那么松。）

### 6. 可验证密码学链：libcrux + fiat-crypto + EverParse + GADT

Borealis 不只是"用 OCaml 重写 C"。它把**多种形式化验证工具串成一条流水线**：

- **libcrux**：Rust 实现，但用 Coq 和 F\* 验证关键原语的常数时间属性。
- **fiat-crypto**：Coq 直接生成 constant-time 域算术常数，避免侧信道。
- **EverParse**（Microsoft Project Everest 子项目）：从 typed schema 生成 F\* 验证过的 C 解析器，再嵌入到 OCaml wire codec 中。**协议解析器层面再不允许有"手写 bug"。**
- **GADT 协议状态机**：用类型参数标注当前协议状态，编译器拒绝非法转移。比如你不可能在 `Unauthenticated` 状态下调用 `send_response`，因为类型不匹配。

这条链路的强大之处不在于单个工具，而在于**它们形成了一个互相验证的网络**：schema 既驱动 OCaml 代码生成，又驱动 EverParse 的 F\* 解析器，**两边可以做 byte-for-byte 比对**。再加上 nqsb-TLS 范式的"同一份 functional core 跑在 flight / ground / oracle 三个角色"，把整个系统的"我相信的真理"压缩到极少几个地方。

```ocaml
(* 命令分发：ADT + 编译器穷尽性检查 *)
type cmd = Ping | Check | Capture | Halt

let dispatch t = function
  | Ping    -> send_response t ~prefix:"pong" "PONG"
  | Check   -> run_self_check t
  | Capture -> capture_and_send t
  | Halt    -> t.shutdown_requested <- true
```

这段代码看上去平淡无奇——但只要你加一个 `Reboot` 构造器，**编译器立刻在所有未覆盖 `Reboot` 的 dispatch 函数里给你抛错**。在轨调试一个"漏掉一个 case"的 bug 比地面贵几个量级，类型驱动的穷尽性检查在这里是真金白银。

（这一逻辑同样适用于[《当 AI 不再等你说完》](/post/good-read-thinking-machines-interaction-models/)讨论的"语言模型对话状态机"——只是那里的状态机是隐式的、训练在权重里，而 Borealis 的状态机是显式的、由类型系统强制。）

### 7. 十二年的 unikernel 弧线终于落地

ASPLOS 2013 那篇 MirageOS 论文（Madhavapeddy et al., "Unikernels: Library Operating Systems for the Cloud"）的本意是把 OCaml 编译成 sealed unikernel，去取代云上的传统 VM 镜像。十二年下来，这个想法走过了一条不直的路：

| 年份 | 节点 | 性质 |
|---|---|---|
| 2013 | ASPLOS · Unikernels paper | 学术想法 |
| 2015 | USENIX Security · nqsb-TLS | 范式验证 |
| 2017 | Nitrokey NetHSM 用 OCaml TLS 出货 | 第一次工业级生产 |
| 2022 | OCaml 5.0 multicore 发布 | 性能门槛突破 |
| 2025 | ICFP · Functional Networking for Millions of Docker Desktops | 库栈跑进 Docker Desktop |
| 2026-04-23 | Borealis 在 ClusterGate-2 首次 boot | 库栈跑进轨道 |
| 2026-05-14 | 本文发布 | 把整条弧线讲给社区 |

> 原文：
> > A decade later, the same libraries run in Docker Desktop on hundreds of millions of laptops. Now they run in space […], in places I did not predict when we first designed them.

最有意思的是，**Borealis 没有以 unikernel 的形式部署**——它是一个普通的 Linux 进程，因为 DPhi 已经提供了 Linux 主机。MirageOS 的库栈被"拆下来"以更松散的形式复用。这其实证明了 unikernel 真正的价值不是"sealed image"那种部署形态，而是**"把库 OS 拆细、按需组装"**这种设计哲学——而后者，恰恰是 Docker 在地面上 popularize 的同一个思想。

这一点对所有写"框架是不是要重新发明 OS"的工程师都有启示：**真正可移植的，不是部署单元，而是设计原语。**（这种"原语 vs 部署形态"的张力，和我在[《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/)里讨论的"AI Agent 时代的原生应用形态"是同一种问题——你的库代码值不值钱，取决于它能不能脱离原本设定的运行时活下去。）

### 8. 没解决的问题：fleet management 才是下一站

文章的结尾给了一个非常清醒的 roadmap：

> 原文：
> > Borealis is one binary in orbit. The next problem is scale: deploying and managing a fleet of specialised payload binaries across many satellites with the same one-command ease that Docker brought to Linux on the ground.

一颗卫星 = 一个 binary 已经解决；多颗卫星 + 多个 payload binary 的**签名分发、版本管理、远程证明（attestation）、租户间隔离**——才是 Parsimoni 接下来要做的事。这非常像 2014 年 Docker 已经能 `docker run` 但 Kubernetes 还没出现的状态。在地面上，我们花了大约五年才把"容器编排"做成商品；在轨道上，过境窗口和带宽约束让这个时间线只会更长。

但是**问题被认得很清楚**：他点名了三件事——signed updates、payload isolation、attestation——这三件事在地面 Kubernetes/SLSA/in-toto 生态里都有现成的对应物，只是需要在带宽/时延受限的场景下重新校准。**这一篇博客其实是在邀请整个云原生社区一起把这套工具链推到轨道上。**

---

## 三、延伸阅读图谱

### A. 作者本人的太空软件系列（2026 一整年的连续作品）

1. [Reimplementing the Space Protocol Stack from Scratch (2026-04-15)](https://gazagnaire.org/blog/2026-04-15-ccsds-protocol-stack.html) —— 把 CCSDS 整套协议族在 OCaml 里手写一遍的工程记录，是本文的"前传"。
2. [Describing Binary Formats in OCaml (2026-03-31)](https://gazagnaire.org/blog/2026-03-31-ocaml-wire.html) —— ocaml-wire 库的设计，schema-first codec 的工程动机。
3. [Apparently I Have Been Writing Flight Software All Along (2026-03-10)](https://gazagnaire.org/blog/2026-03-10-ocaml-fpp.html) —— 用 OCaml 重新实现 NASA F Prime 的 FPP（F Prime Prime）语言。
4. [Is Running Untrusted Code on a Satellite a Good Idea? (2026-02-25)](https://gazagnaire.org/blog/2026-02-25-satellite-software.html) —— 全篇威胁模型的根基。
5. [F Prime Looks a Lot Like MirageOS (but in C++) (2026-02-19)](https://gazagnaire.org/blog/2026-02-19-nasa-fprime.html) —— 把 NASA 的 C++ 飞控框架与 MirageOS 做精确对比。

### B. 相关学术论文

1. **Madhavapeddy et al., "Unikernels: Library Operating Systems for the Cloud"** (ASPLOS 2013, [doi:10.1145/2451116.2451167](https://doi.org/10.1145/2451116.2451167)) —— Borealis 思想的祖论文。
2. **Madhavapeddy et al., "Functional Networking for Millions of Docker Desktops"** (ICFP 2025, [doi:10.1145/3747525](https://doi.org/10.1145/3747525)) —— 同一套库栈如何被 Docker Desktop 复用。
3. **Kaloper-Mersinjak et al., "Not-Quite-So-Broken TLS: Lessons in Re-Engineering a Security Protocol Specification and Implementation"** (USENIX Security 2015) —— nqsb-TLS 范式的原始论文，本文的方法论祖宗。
4. **Sivaramakrishnan et al., "Retrofitting Effect Handlers onto OCaml"** (PLDI 2021) —— OCaml 5 multicore 路线图的关键里程碑。
5. **Bhargavan et al., "Everest: Towards a Verified, Drop-in Replacement of HTTPS"** (SNAPL 2017) —— Project Everest / EverParse / F\* 的总览。

### C. 工具与项目

- [**MirageOS**](https://mirage.io/) —— 库 OS 主项目。
- [**OxCaml**](https://github.com/janestreet/oxcaml) —— Jane Street 的 OCaml 实验分支。
- [**EverParse**](https://project-everest.github.io/everparse/) —— F\* 验证的二进制解析器生成器。
- [**libcrux**](https://github.com/cryspen/libcrux) —— Rust + 形式化验证的 PQ 密码库。
- [**fiat-crypto**](https://github.com/mit-plv/fiat-crypto) —— Coq 生成的常数时间域算术。
- [**NASA CryptoLib**](https://github.com/nasa/CryptoLib) —— C 写的 CCSDS 安全参考实现，本文的"反面"对照。
- [**NASA F Prime (F´)**](https://nasa.github.io/fprime/) —— JPL 的 C++ 飞控框架，被作者多次拿来对比。

### D. 标准与 RFC

- **RFC 9171** —— Bundle Protocol Version 7。
- **RFC 9172** —— Bundle Protocol Security (BPSec)。
- **NASA-STD-1006A** —— Space System Protection Standard。
- **NIST FIPS 203 / 204 / 205** —— ML-KEM / ML-DSA / SLH-DSA 后量子标准。
- **CCSDS 232.0-B / 232.1-B / 355.0-B** —— TC、COP-1、SDLS 等核心规范。

### E. 反方观点 & 对照

1. **"Why Rust for Embedded Systems"** —— 嵌入式社区的主流答案是 Rust（no GC, predictable allocation）。Borealis 用 GC + opt-in stack allocation 的路线本质上是和 Rust 路线在做不同的权衡，**值得对照阅读两边的论证**。
2. **NASA F Prime 团队的立场** —— 他们仍然认为 C++ 加严格规范 + lint + 形式化 model checking 是更现实的路径，因为整个 Aerospace 工业链对 C/C++ 工具链的认证基础设施成熟得多。
3. **"Functional Languages Don't Belong in Hard Real-Time"** —— 传统飞控工程师常见的反对意见。Borealis 用 OxCaml 的 jitter 数据正面回应：**只要 GC pressure 可控，functional 不等于不可预测。**

### F. 本博客相关文章（内部交叉引用）

- [《Copy Fail 与后量子 IPsec：内核态信任根的双向时间旅行》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/) —— Borealis 直接引用的"Copy Fail"漏洞背景。
- [《Trail of Bits 用经典计算击败 Google 量子密码分析》](/post/trail-of-bits-quantum-cryptanalysis-google-2026/) —— PQC 迁移窗口期的另一面。
- [《芯片验证的数学转向》](/post/formal-verification-chip-design-mathematical-turn-2026/) —— 形式化方法从学术走进工业的姐妹篇。
- [《【好文共赏】Mercury 把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上》](/post/good-read-haskell-mercury-production-engineering/) —— 函数式语言在生产系统的另一典型案例。
- [《【好文共赏】WebRTC 是问题本身》](/post/good-read-moq-webrtc-openai-voice-ai/) —— "应用层信封 vs 协议层信任"的同构讨论。
- [《【好文共赏】当 AI 不再等你说完》](/post/good-read-thinking-machines-interaction-models/) —— 状态机显式化 vs 隐式化的对照。
- [《【好文共赏】Emacs 化的软件世界》](/post/good-read-emacsification-of-software/) —— "可拆解可重组的原语"思想。
- [《【好文共赏】用咖啡和 IDA 绕过 Tesla 充电桩 anti-downgrade》](/post/good-read-tesla-wall-connector-anti-downgrade-bypass/) —— C 写的 ratchet 状态机如何被打穿，形成对照案例。

---

## 四、编辑延伸思考

### 1. "实验性语言特性走出母体"的稀缺时刻

我把这件事专门拎出来说，是因为它在 systems programming 的过去十年里很罕见。Rust 的 async/await 走出来花了大约六年；Go 的 generics 花了八年；C++ 的 concepts 花了十二年。每一次都是同样的模式：**先在小圈子内部用得很重，然后被一个完全独立的"严苛"场景拿去做主力**，最后社区才广泛接受。

OxCaml 的 mode system 正处在这个临界点。它在 Jane Street 内部已经用了好几年，主要驱动是低延迟交易系统的 GC 压力。Borealis 拿它去做卫星协议栈的 hot path，是一次**完全独立的、外部的、严肃的、可复现的**使用。`exclave_ stack_` 注释的效果（394 minor GC → 0）不是 Jane Street 内部 demo，是 25.6M packets 上的中位数测量。这种独立验证比任何 RFC 都更能推动一个语言特性进入主流。

我估计接下来一年里，OxCaml 会沿着这条路被更多"严苛但小众"的场景吸收：高频交易已经被 Jane Street 占了；卫星协议被 Parsimoni 占了；下一个可能是 5G/6G 基带、HFT exchange matching engine、HSM 固件、或者 K8s control plane 的某些 fast path。**OxCaml 是 systems programming 在 functional 阵营的第一次真正"严肃化"尝试，它能不能成功，取决于接下来 12 个月里类似 Borealis 这样的独立 case study 能不能再出 3-5 个。**

### 2. 太空软件的"docker 化"瞬间

值得反复琢磨的还有一点：Borealis 没有以 unikernel 形式部署。这是个**反直觉**的选择——MirageOS 全套理论就是为 unikernel 准备的，作者自己也是 MirageOS 的核心开发者。但他们选择把库栈拆下来跑在 Linux 进程里，因为：

1. DPhi 已经管好了下面的 Linux，没必要重新发明轮子。
2. 同样的二进制可以同时跑在地面调试、CI、轨道，部署成本最低。
3. **可重用性比"理论纯洁性"更重要**。

这件事的意义比"成功上轨道"更大。它在说：**云原生 12 年下来积累的"容器化、镜像化、CI/CD、observability"那一整套工程基础设施，可以一比一搬上轨道**。你不需要发明"卫星 Docker"——Docker 本身就够用，只要你愿意把 `FROM scratch` 那一层做到 5 MB、把 Linux process 当成最小调度单位。

这是 NewSpace 软件栈历史上一个真正的拐点：从"我要请 NASA/ESA 退休工程师写 RTEMS C 飞控"变成"我能把 GitHub Actions 出来的 Docker image 推上轨道"。**门槛从工业级合同变成开源工具链**。这意味着接下来两三年里，太空软件的 commit 频率、迭代速度、bug fix 周期都会指数级提升，对应的安全模型、攻防面、监管框架也会同步重写。

### 3. functional core, imperative shell 在硬实时场景的新证据

"functional core, imperative shell"是 Gary Bernhardt 在 2012 年提出的设计模式——把纯函数压缩到核心、把副作用挤到边界。十几年来这种模式主要在 web 后端和 ML pipeline 里被使用，但**它在硬实时 + 安全敏感场景的可行性**一直争议很大。传统飞控工程师的反对意见是："我承担不起 GC、我承担不起 allocation 不可预测、我承担不起 functional 的抽象开销。"

Borealis 用一组很具体的数字反驳了三件事：

- GC pressure 可以靠 `exclave_ stack_` 在 hot path 上清零。
- Allocation 可以在编译期由类型系统证明 stack-bound。
- Abstraction overhead 在 OxCaml 之后已经和 C/Rust 相当，甚至在某些 jitter 维度上更好。

更关键的是，作者用 **`protect_bundle` 是同一份代码** 这件事打开了另一个维度：**功能式核心让你的飞控代码同时也是地面调试工具、同时也是测试 oracle、同时也是 reference implementation**。这是"工程师小时数"维度的复利：你写一次，做三件事；你修一次 bug，三个地方同时被修。在卫星这种"每多写一行代码都要走一遍 V&V 流程"的场景里，**代码复用率不是省事，是省命**。

我觉得接下来五年我们会看到更多类似的"functional core 在硬实时"的案例。除了航空航天，可能的方向包括：医疗设备固件、汽车 ECU（特别是 EV 的电池管理 BMS）、机器人控制平面、工业自动化 PLC 替代。每一个都是"安全敏感 + 实时性敏感 + 长生命周期"的组合，恰好是 OCaml/Haskell/Lean 生态最擅长的舒适区。

### 4. PQ 迁移的"政府推、工业跟"模式

Borealis 的 OTAR + ML-DSA-65 设计，是一个很值得在更广 PQ 迁移讨论里参考的样本。后量子密码学过去几年最大的争议是"时间表"——量子计算到底什么时候真正威胁现役密码？乐观派说还要 15-20 年，悲观派说"harvest now decrypt later"威胁现在就在发生。

NASA-STD-1006A 把 PQ 命令认证写成 **requirement** 是一个相当有意思的政府信号：**在客户（NASA/DoD）愿意为 PQ 买单的领域，PQ 已经不是"未来选项"而是"今天必须的工程要求"**。Borealis 是这个标准落地的第一波直接受益者——他们能跑通 OTAR 不是因为商业市场要求，而是因为**军方/航天客户的合同条款**。

这种模式很可能也是地面 PQ 迁移的真实路径：先是政府关键基础设施（电网、金融、关键 SaaS）通过监管压力强制部署，然后供应链上下游传染开。Cloudflare、AWS KMS、Google Tink 这些已经在做的 PQ hybrid 部署，本质上都是被同样的力量推动。**Borealis 的价值在于它把"从标准到代码"的距离展示得非常短**——一份诚实的 in-orbit OTAR demo，比一千篇 RFC 阅读笔记都更能让其他工程师相信"我也可以做"。

### 5. 给阅读者的实用启示

如果你不是写卫星软件的工程师，这篇文章对你的日常工作仍然有几条很具体的启示：

1. **协议 schema 类型化**：不管你写 gRPC、Cap'n Proto、还是自家私有协议，**手写 marshalling 是 2026 年不可接受的做法**。从 schema 生成 codec 是基线工程素养。
2. **GADT/phantom type 锁状态机**：你的 HTTP client、WebSocket connection、payment session，本质上都是状态机。在 TypeScript、Rust、Scala 里都可以用类型把非法转移挡掉。
3. **functional core 在边界**：把纯函数压到核心，副作用集中到 edge。即使你写 Go/Java/Python，这个原则仍然适用。
4. **抓 jitter 不要只抓 throughput**：你的 SaaS 用户感知到的是 p99.9，不是 RPS。
5. **承认 TCB 边界**：明确写下"我能保证什么"和"我假设什么不出问题"。这种诚实是工程信任的起点。

---

## 五、配套资料导览

本文目录下附带以下材料，建议配合阅读：

- **`mindmap.svg`** —— 思维导图，把 Borealis 八个核心维度（为什么 OCaml / CCSDS 栈 / 威胁模型 / OxCaml 性能 / PQ 密码 / 可验证密码学 / nqsb 谱系 / unikernel 弧线）放在一张图里，适合作为"读完原文 + 主文后的快速复盘"用。
- **`concept-cards.md`** —— 15 张关键概念卡片，每张包含定义、关键数据、易错点。适合做单点突击或团队读书会的讨论起点。
- **`glossary.md`** —— 中英对照术语表，约 70 条，覆盖项目、协议、密码学、语言、系统、性能、工程、漏洞、行业、文献十类。
- **`cover.svg`** —— 封面图，包含本文核心 telemetry 数据。

---

## 六、谁应该读这篇

- **Systems / 协议栈工程师**：你会重新理解 wire format + 类型系统 + 形式化验证可以走多远。
- **关注 memory safety 的安全研究者**：Borealis 是"在 TCB 边界外能保证什么"的一个清晰样本。
- **后量子密码学落地者**：ML-DSA-65 + OTAR 的工程化范例，远比 NIST 标准文档好读。
- **OCaml / Haskell / Rust 函数式社区**：OxCaml 走出 Jane Street 的关键 case study。
- **NewSpace 软件 / 卫星运营商**：DPhi 模式 + Docker image 部署 = NewSpace 软件栈的拐点信号。
- **写 SRE / CI/CD 工具链的工程师**：fleet management 在轨道场景下被重新定义的过程，反过来会启发地面工具链设计。
- **大学 PL/Systems 课程学生**：把 unikernel、GADT、PQ crypto、formal verification 串起来的真实工程样本，比任何 textbook 例子都生动。

---

> 本期"好文共赏"到此结束。如果你觉得这种"硬核技术博客 + 多模评审 + 中文导读 + 配套思维导图/术语表/概念卡片"的形式对你有用，欢迎把它转给你身边写 OCaml、写 systems、写 PQ、或者在做 NewSpace 软件的朋友。
>
> 下一期我们会继续在 systems / security / functional / AI infra 的交叉地带打捞下一篇足以 9.0+ 评分的好文。

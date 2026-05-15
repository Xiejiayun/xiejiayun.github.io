# 概念卡片：O(x)Caml in Space · Borealis

> 配合主文《【好文共赏】把纯 OCaml 协议栈送上低地球轨道》使用。每张卡片 = 一个独立可考核的知识点。

---

## 卡片 1：Borealis 是什么

- **一句话定义**：业界首个在低地球轨道运行的、纯 OCaml 实现的 CCSDS 协议栈，由 Parsimoni（Tarides 拆出的太空软件子公司）开发。
- **关键时间**：2026-04-23 18:48:06 UTC，在 DPhi Space 的 ClusterGate-2 共生载荷模块上完成首次 boot。
- **运行形态**：5–10 MB 静态链接二进制，作为 `FROM scratch` 的 Docker 镜像在 Arm Cortex-A53 ×4 / 4 GB RAM 的 Linux SoC 上以 daemon 形式运行。
- **不是 unikernel**：作者刻意以 Linux process 形态部署，把 MirageOS 的库栈剥下来，在主机内核之上做加密信封。

---

## 卡片 2：CCSDS 协议家族

- **CCSDS** = Consultative Committee for Space Data Systems，从 1980 年代起统治"星地链路"的协议联盟。
- **层次（自下而上）**：Radio framing → Space Data Link Protocol → COP-1（command operation procedure-1，类似 TCP 的可靠传输） → CFDP（CCSDS File Delivery Protocol） → BPv7 / Bundle Protocol。
- **类比**：CCSDS 之于卫星 ≈ TCP/IP 之于地球互联网。但 BPv7 是 RFC 9171 的 delay-tolerant networking，链路可能"断开数小时"才传过去。
- **Borealis 重点**：实现了从底层 framing 到上层 BPv7 + BPSec 的完整栈，但在轨只演示上半段（因为 DPhi 的 API 把 uplink/downlink 当文件系统而非 radio）。

---

## 卡片 3：BPv7 + BPSec + OTAR 三件套

- **BPv7（RFC 9171）**：把"消息"打包成 bundle，可在 delay-tolerant 网络中转。
- **BPSec（RFC 9172）**：在 bundle 外面套两个 extension block：一个加密 payload，一个 authenticate。序列号防重放。
- **SDLS Security Association**：地面与卫星在 provisioning 阶段协商好的密钥参数（EK 加密键 + AK 认证键）。
- **OTAR（Over-The-Air Rekey）**：在飞行阶段通过受信道传入新的 PQ 签名密钥；卫星在 staging slot 验证后激活。Borealis 用 **ML-DSA-65** 做 PQ 签名。NASA-STD-1006A 已把 PQ 命令认证从"future option"升级为"requirement"。

---

## 卡片 4：威胁模型 · 为什么单靠容器隔离不够

- **共生载荷（hosted payload）卫星**：多家租户共享同一颗卫星的总线、电源、姿态控制；每个租户跑自己的 payload。
- **共享 Linux 内核 = 单点故障**。Linux 内核 LPE/容器逃逸近年滚动出现：
  - 2022 Dirty Pipe
  - 2024 nf_tables UAF（容器逃逸）
  - 2026 Dirty Frag（universal LPE）
  - 2026-04 "Copy Fail"（一次性命中所有主流发行版）
- **在轨痛点**：地面 server 可以 `apt upgrade && reboot`，在轨补丁交付要排到下一个过境窗口，有时根本做不到。
- **结论**：在 hosted-payload 环境下，**每个 bundle 自带密码学信封是唯一持久保证**。

---

## 卡片 5：为什么是 OCaml（而不是 Rust）

- **Microsoft MSRC 2019 & Chromium 2020 研究**：~70% 严重 CVE 源自内存破坏（缓冲区溢出 / UAF / 整数溢出）。
- **NASA CryptoLib 历史 bug**：C 写的参考实现也吃过整数下溢 → TC frame 解析器堆缓冲区溢出。OCaml 实现一次性"按构造"去掉这类攻击面。
- **OCaml 的独特价值**：
  - 类型系统强 + GADT 可以把协议状态机不变量编译期化。
  - 函数式核心 → 同一份代码可作飞控、地面工具、测试 oracle。
  - 性能可达 C/Rust 量级（OCaml 5 多核 + OxCaml stack allocations）。
  - 生态历史悠久：Jane Street 大规模生产用、Nitrokey NetHSM 出货十年。
- **诚实声明**：OCaml runtime / Linux kernel / bootloader 仍是 C，仍在 TCB 内；memory safety 只在应用层有效。

---

## 卡片 6：OxCaml · Jane Street 的分支

- **OxCaml** = Jane Street 维护的 OCaml 实验性 fork，与 mainline OCaml 完全兼容（"every valid OCaml is valid OxCaml"）。
- **核心特性 · 模式系统（mode system）**：
  - `locality`：标注一个值是否能逃逸出当前作用域；可以强制 stack-bound，绕过 GC。
  - `uniqueness`：编译期跟踪可变共享状态，data race → 编译错误。
  - `capabilities`：表达"谁有权访问什么资源"。
- **典型用法**：
  ```ocaml
  let dispatch hdr = exclave_ stack_ { apid; seq_count; data_len }
  ```
  消费者必须以 `@ local` 接收，类型系统保证记录无法逃出 dispatch scope。
- **效果数据（Apple M5 Max, 25.6 M packets, median of 10 runs）**：
  - p99.9 latency：29 ns → **9 ns**
  - Minor GC 计数：394 → **0**
  - Throughput 几乎相同；赢的是**抖动**，这正是 hosted-payload 软实时调度的全部痛点。

---

## 卡片 7：可验证密码学链路

- **libcrux**：Rust + Coq/F* 生态，机器验证的 PQ 原语实现。
- **fiat-crypto**：Coq 生成的 constant-time 域算术常数表。
- **EverParse**：Microsoft Project Everest 子项目；把 schema 转成 F* 验证过的 C 解析器，再嵌入到 OCaml wire codec。
- **GADT 协议状态机**：用类型参数标注当前状态，编译器拒绝非法转移。
- **nqsb-TLS 谱系**（USENIX Security 2015，Kaloper-Mersinjak 等）：用同一份功能式核心当 reference implementation，让其他实现对它做 byte-for-byte 比对。Nitrokey NetHSM 把同样的栈跑了十年。

---

## 卡片 8：Master Key 的诚实失败模式

- **现状**：master key 在卫星与火箭整合前烧入 module 内存；轨道上没有比"在地面整合时"更受信任的通道。
- **后果**：如果 master key 泄漏 → 全栈控制权丢失；如果 master key 丢失 → 全栈不可达。
- **作者的话术**：This is "the honest failure mode for a long mission with no hardware-backed key storage."
- **硬件解释**：辐照容忍 TPM/secure element 仍是开放硬件问题。Borealis 选择把 master key 留在进程内存，而把所有可用密钥保护机制集中到 BPSec + OTAR。
- **设计哲学**：宁愿明确暴露一个失败模式，也不要"假装解决"。

---

## 卡片 9：12 年的 Unikernel 弧线

| 年份 | 事件 | 含义 |
|---|---|---|
| 2013 | ASPLOS · MirageOS 论文 | "sealed, single-purpose images" 的概念被首次正式提出 |
| 2015 | USENIX Security · nqsb-TLS | 功能式核心当 TLS reference impl 的范式 |
| 2022 | OCaml 5.0 multicore 发布 | 性能门槛被攻克 |
| 2025 | ICFP · "Functional Networking for Millions of Docker Desktops" | 同一套库栈在亿级桌面跑 |
| 2026-02 | "Is Running Untrusted Code on a Satellite a Good Idea?" | 思想准备 |
| 2026-04-23 | Borealis 在 ClusterGate-2 上首次 boot | 首次轨道运行 |
| 2026-05-14 | 本文发布 | 把整个旅程总结给社区 |

**核心洞察**：硬件上轨道正在变成例行公事，**真正的新问题正在搬到太空软件里**——和云时代"机器之上才是战场"的迁移完全同构。

---

## 卡片 10：与 NASA F Prime 的对比

- **F Prime（F´）**：NASA JPL 出品的 C++ 飞控框架，2017 年开源，已驱动 Ingenuity 等任务。
- **作者观点（在 2026-02-19 旧文中详述）**：F Prime 的组件 + topology + port-based message passing 模型，本质上长得"非常像 MirageOS"——只不过用 C++ 而非 OCaml 表达。
- **Borealis 的差异点**：
  1. 内存安全在编译期强制，而非靠规约 + lint。
  2. Wire format 由 schema 生成，不靠手写 marshalling。
  3. GADT 让协议状态机的非法转移编译期就消失。
  4. 同一份代码跨"飞 / 地 / 测"三个角色，不需要维护测试桩。

---

## 卡片 11：DPhi Space 与 ClusterGate-2

- **DPhi Space**：欧洲共生载荷创业公司，把单颗卫星拆成"多个软件租户"。
- **ClusterGate-2**：他们的 payload module，给租户暴露一个文件系统抽象——租户把 bundle 写到 `/uplink`，DPhi 在下一个 ground pass 中把它当不透明字节流转发，downlink 同理。
- **对 Borealis 的好处**：Borealis 直接把这个 filesystem 当"延迟容忍网络"，BPv7 bundle 写入即"发送"，完全不需要 DPhi 介入加密/认证。
- **对开发者的好处**：任何能在 Linux 上跑的二进制，理论上都可以变成卫星 payload；门槛从"和 JPL/ESA 谈"降到"申请一个 DPhi 账号"。

---

## 卡片 12：与 Mercury Haskell / antirez DS4 / Tesla 充电桩的对照

- 这是 2026-05 一个隐含的趋势主线：**"功能式 / 类型系统在硬实时与安全敏感场景里的二次复兴"**。
- 类比 Mercury 把 200 万行 Haskell 跑在金融基础设施上：用类型系统把"不会写错"提前到编译期。
- 类比 antirez 把 GPT 5.5 当结对程序员一周写出 DS4：函数式核心 + 类型系统 = LLM 也更容易帮你做正确的事，因为错的写法过不了编译。
- 反向对照 Tesla Wall Connector 的 anti-downgrade ratchet 被 IDA 绕过：C 写的固件 ratchet 即使加 OTA 也仍然吃 IDA 拆解，而 BPSec + GADT 状态机让"非法状态"在编译期就不存在。

---

## 卡片 13：可直接借鉴的工程模式（适合地面工程师）

1. **把协议 schema 类型化**，用 ocaml-wire / capnp / Cap'n Proto 生成 codec，不要手写。
2. **GADT / phantom type 锁住状态机**：让 `send_response : t -> response_state -> _ -> _` 编译期检查。
3. **同一份 core 跨 prod/test/oracle**：把 protect_bundle 这样的纯函数当真理源。
4. **抓住 jitter 而不仅是 throughput**：对软实时系统，p99.9 比 p50 重要；GC pressure 是首要敌人。
5. **承认 TCB 边界**：清楚写出"我能保证什么"和"我不能保证什么"。

---

## 卡片 14：Borealis 没有解决的问题（作者点名）

- **舰队规模化**：一颗卫星 = 一个 binary 已经做到。**多颗卫星 + 多个 payload binary** 的部署/更新/隔离/证明（attestation）才是真正的活。
- **签名更新分发**：地面如何 sign，星上如何 verify 安装，跟"地面 CI/CD"的关键链路一模一样，但发布窗口受过境时间约束。
- **租户间隔离**：在同一颗 bus 上，A 租户的 payload 不能伤到 B 租户。Hosted-payload 的现实远比"独享卫星"复杂。
- **硬件信任根**：辐照容忍 TPM 还是开放问题；目前只能靠"出厂烧入 master key"。

---

## 卡片 15：哪些人应该读

- 想做"OCaml/Rust 落地非传统场景"的工程师。
- 关注 **memory safety vs 实时性** 权衡的 systems programmer。
- 关注 **PQ crypto agility** 的安全研究者。
- 关注 **新太空（NewSpace）软件栈** 的产品/工程经理。
- 写 protocol stack / wire format 的所有人——Borealis 是一个可学习的范本。
- 关注 **functional core, imperative shell** 设计模式在大型系统里效果的人。

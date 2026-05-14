# 概念卡片：CUBIC 死亡螺旋的 12 张速记卡

> 配套 [《【好文共赏】当"空闲"不是空闲》](./)。每张卡片 3-5 句话讲清"是什么 / 为什么重要 / 典型陷阱"。

---

## 1. CCA — Congestion Control Algorithm（拥塞控制算法）

- **是什么**：sender 端的策略，根据网络反馈调节"在飞行的字节数"。
- **为什么重要**：直接决定 TCP/QUIC 连接能用满多少带宽、抗丢包能力如何、对其它流是否公平。
- **典型陷阱**：HN 评论区原文没定义 CCA 这个缩写，连资深读者都得 google 一下——这是 IETF 缩写词膨胀的典型。

---

## 2. cwnd — Congestion Window（拥塞窗口）

- **是什么**：sender 端能"在飞行"（已发未确认）的最大字节数上限。
- **为什么重要**：所有拥塞控制算法的核心调节旋钮——调它就是调发送速率。
- **典型陷阱**：cwnd 不是真实的链路容量，它是 sender 对网络状态的**估计**。估错了，要么浪费带宽，要么把网络打死。

---

## 3. CUBIC — 默认的 loss-based 拥塞控制器

- **是什么**：用三次方曲线 $W(\Delta t) = C \cdot (\Delta t - K)^3 + W_{\max}$ 建模 cwnd 增长的算法。
- **为什么重要**：Linux 自 2.6.19 起默认，今天承担互联网绝大部分 TCP 流量。
- **典型陷阱**：把丢包当作拥塞的唯一信号——在无线网络/lossy link 上常常误判。

---

## 4. epoch — CUBIC 的曲线锚点

- **是什么**：CUBIC 三次曲线的时间原点 $t_{\text{epoch}}$，$\Delta t = \text{now} - t_{\text{epoch}}$ 决定 cwnd 应该走到曲线的哪一段。
- **为什么重要**：所有 CUBIC 内部状态都被压缩到这一个时间戳上——这是它**简洁**也是**脆弱**的地方。
- **典型陷阱**：epoch 一旦被设到未来，整个曲线就被"冻结"，cwnd 不再增长——本文 bug 的核心机制。

---

## 5. RTT — Round-Trip Time（往返时延）

- **是什么**：包从 sender 发出、到 ACK 返回所经历的时间。
- **为什么重要**：CCA 的"时钟节拍"——很多算法的状态机以 RTT 为单位推进。
- **典型陷阱**：如果某个错误现象的周期等于 RTT，bug 几乎一定锁在 ACK clock 上——这是本文最关键的诊断洞察。

---

## 6. ACK Clock — self-clocking 节奏

- **是什么**：每一轮 ACK 触发下一轮 send 的隐式节拍；TCP/QUIC 的发送由 ACK 到达自然驱动。
- **为什么重要**：理解 CCA 行为时，"ACK 到达 → 状态变化 → 再发送"这条流水线必须先在脑子里画清楚。
- **典型陷阱**：ACK clock 可以把一个**间歇性 bug** 变成一个**稳态 bug**——只要每个 RTT 都触发同样的错误判断。

---

## 7. bytes_in_flight — 在飞行字节数

- **是什么**：已发出但还没被 ACK 的字节总数。
- **为什么重要**：判断 sender 是否真的 idle 的常见信号；CCA 用它决定能否再发更多。
- **典型陷阱**：`bytes_in_flight == 0` **不等于 idle**——它可能只是 cwnd 太小、上一轮已经全部被 ACK，应用马上要发下一波。这就是死亡螺旋的入口。

---

## 8. Congestion Avoidance vs. Recovery — 两种状态

- **是什么**：CUBIC 状态机的两个主要相位。Avoidance 是日常增长，Recovery 是丢包后的休整。
- **为什么重要**：状态翻转是否健康，是 CCA 行为正确性的核心标志。
- **典型陷阱**：Recovery 时 cwnd 不增长——如果某个 bug 让 sender 永远以为自己在 Recovery，cwnd 就永远不长。这就是 999 次翻转的本质。

---

## 9. quiche — Cloudflare 的 Rust QUIC/HTTP3 实现

- **是什么**：开源的 user-space QUIC + HTTP/3 库，约 2018 开发，2019 公开 alpha，2020 起承载 Cloudflare 大量生产流量。
- **为什么重要**：Cloudflare 服务网络的核心传输层。
- **典型陷阱**：把内核 CUBIC 移植到 user-space 时漏抄了 2017 年的 follow-up commit——本文 bug 的源头。

---

## 10. qlog — QUIC 标准化日志格式

- **是什么**：IETF 草案中的 QUIC 状态日志格式，每个状态转移、包发送、ACK 处理都可以被结构化记录。
- **为什么重要**：让 QUIC 调试不再像 TCP 那样靠 pcap 推理——直接看 sender 内部状态变化。
- **典型陷阱**：默认 qlog 量很大，需要采样或裁剪；本文作者用扩展的 qlog 才看出了 999 次翻转的可视化模式。

---

## 11. BBR — Bottleneck Bandwidth and RTT

- **是什么**：Google 2016 年提出的 model-based 拥塞控制，估计瓶颈带宽和最小 RTT 来调节发送速率，不再以丢包为唯一信号。
- **为什么重要**：摆脱了 CUBIC 的"loss == congestion"假设，对 lossy 链路和大 BDP 路径有显著优势。
- **典型陷阱**：BBR 在与 CUBIC 共享瓶颈时可能不公平；BBRv2/v3 部分修复了这个问题，但仍在演化。Cloudflare 正在试点 BBRv3。

---

## 12. Adversarial Testing — 对抗性测试

- **是什么**：故意把系统逼到非正常状态（最小 cwnd、severe loss、partition、clock skew）下，观察它能否恢复。
- **为什么重要**：本文 60% 失败率的测试就是教科书级例子。控制平面 bug 几乎只能靠这种测试发现。
- **典型陷阱**：团队 review 时常把这种测试当成"不现实"否决——但正是这种"不现实"才暴露了真实世界遇到事故时系统的行为。

---

## 阅读路径建议

如果你只能记三张：**#4 epoch → #7 bytes_in_flight → #12 Adversarial Testing**。
这三张就是这次 bug 的"前因 → 触发 → 被发现"的最小完整故事。

# 术语表：QUIC / CUBIC / 拥塞控制 英中对照

> 配套 [《【好文共赏】当"空闲"不是空闲》](./)。
> 排序按英文字母顺序，括号内为本文常用译法。

| 英文 | 中文 | 简要说明 |
|------|------|---------|
| ACK | 确认 | 接收方告知发送方"我收到包了"的反馈消息 |
| ACK Clock | ACK 时钟 / self-clocking | 用 ACK 到达驱动下一轮发送的隐式节拍 |
| AIMD | 加性增、乘性减 | Reno 类算法核心：无拥塞时线性增 cwnd，有拥塞时按比例减 |
| Application-Limited | 应用受限 | sender 想发但应用层没数据；不同于网络拥塞 |
| BBR | Bottleneck Bandwidth & RTT | Google 2016 提出的 model-based CCA |
| BDP | 带宽时延积 | bandwidth × RTT，理想情况下 cwnd 应该等于 BDP |
| Bytes in Flight | 在飞行字节数 | 已发出但未 ACK 的总字节数 |
| CCA | 拥塞控制算法 | Congestion Control Algorithm 的缩写 |
| Congestion Avoidance | 拥塞避免 | CCA 退出 slow-start 之后的日常增长阶段 |
| Congestion Collapse | 拥塞崩溃 | 全网吞吐因过载塌陷的极端状态 |
| Congestion Recovery | 拥塞恢复 | 丢包后用来重建 cwnd 的过渡状态 |
| CUBIC | CUBIC | 用三次方曲线建模 cwnd 增长的 CCA |
| cwnd | 拥塞窗口 | sender 端在飞行字节的上限 |
| Death Spiral | 死亡螺旋 | sender 永远卡在最小 cwnd 的退化状态（本文核心现象） |
| Delayed ACK | 延迟确认 | 接收方合并多个 ACK 减少反向流量 |
| Epoch | 锚点时刻 | CUBIC 三次曲线的时间原点 |
| FQ-CoDel | FQ-CoDel | 公平队列 + 主动队列管理，常见于路由器 |
| HOL Blocking | 队头阻塞 | 队列首部一个慢包阻塞后续的所有包 |
| HTTP/3 | HTTP/3 | 基于 QUIC 的下一代 HTTP，2022 标准化 |
| Idle Period | 空闲期 | 连接暂停发送的时间窗口 |
| Loss-Based CCA | 基于丢包的拥塞控制 | 把丢包当作拥塞信号的算法家族（CUBIC / Reno / NewReno） |
| Min cwnd | 最小拥塞窗口 | 通常是 2 个 MTU 大小，是 sender 维持连接的下限 |
| Model-Based CCA | 基于模型的拥塞控制 | 直接估计带宽/RTT 的算法（BBR 系列） |
| MTU | 最大传输单元 | 链路层一次能传的最大字节数 |
| Pacing | 速率整形 | 把一轮 cwnd 内的包均匀铺开发送，避免突发 |
| qlog | qlog | IETF QUIC 标准化日志格式 |
| quiche | quiche | Cloudflare 开源 Rust QUIC 库 |
| QUIC | QUIC | 基于 UDP 的多路复用、低握手延迟传输协议 |
| RACK | RACK | RFC 8985 基于时间的丢包检测算法 |
| Recovery | 恢复（拥塞恢复） | 见 Congestion Recovery |
| Reno | Reno | 经典 AIMD 拥塞控制器 |
| RFC 9438 | RFC 9438 | CUBIC 算法的 IETF 标准化文档 |
| RTO | 重传超时 | Retransmission Timeout |
| RTT | 往返时延 | Round-Trip Time |
| Self-Clocking | 自时钟 | 用 ACK 节拍驱动 sender 发送的机制 |
| Slow Start | 慢启动 | 连接初期 cwnd 指数增长的阶段 |
| Sock Buffer | 套接字缓冲区 | 内核为每个连接保留的发送/接收缓冲 |
| Tail Drop | 队尾丢弃 | 路由器队列满时直接丢新到达的包 |
| TLA+ | TLA+ | Lamport 的形式化规范语言，HN 评论提到能否用它验证 CCA |
| User-Space Protocol | 用户态协议栈 | 把传统内核态协议移到应用层实现的趋势（QUIC 是代表） |
| W_max | 上次拥塞时窗口 | CUBIC 曲线锚定的另一个关键参数 |

---

## 易混淆术语小贴士

- **idle ≠ bytes_in_flight == 0**：连接 idle 是应用层没数据可发；bytes_in_flight 归零只是上一轮 ACK 全部回来。这两者**在常态下重合，在最小 cwnd 下完全不同**——这就是本文 bug 的根源。
- **CUBIC 的 "C" 不是 Congestion**：CUBIC 取自"cubic function"（三次方函数），不要把它误读成 "Cubic Congestion"。
- **quiche vs. QUIC**：QUIC 是协议，quiche 是 Cloudflare 一家的实现；其他主流实现还有 msquic（Microsoft）、quic-go（Cloudflare-adjacent）、neqo（Mozilla）、mvfst（Meta）、google QUIC。
- **Recovery 不是"修复"**：在 CCA 语境里 Recovery 是"丢包之后过渡到稳态"的状态名，不要望文生义。

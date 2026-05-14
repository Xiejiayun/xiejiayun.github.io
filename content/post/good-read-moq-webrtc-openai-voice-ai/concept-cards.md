# 关键概念卡片

> 围绕 *OpenAI's WebRTC Problem* 一文，整理 12 张概念卡片，覆盖 WebRTC / QUIC / Voice AI 的核心术语。

---

## 1. WebRTC（Web Real-Time Communication）

**一句话**：浏览器原生的实时音视频 + 数据通道 API，背后是一摞从 2000 年代初堆到今天的 ~45 个 RFC。

**关键事实**：
- 不是一个协议，而是 **ICE / STUN / TURN / DTLS / SRTP / SRTCP / SCTP / SDP / mDNS** 的合集
- 浏览器实现由 Google 主导（libwebrtc），事实上为 Google Meet 量身定制
- 2011 年 Google 开源，2017 年成为 W3C 标准

**为什么对 Voice AI 不合适**：jitter buffer 写死、丢包优先于等待、需要 8 RTT 握手、临时端口模型不亲云原生。

---

## 2. SFU（Selective Forwarding Unit）

**一句话**：一台中间服务器，接收所有参与者的媒体流，按订阅关系\"选择性\"转发——而不是混音（MCU）也不是 P2P。

**关键事实**：
- WebRTC 大规模会议的标准架构（Zoom、Discord、LiveKit、Daily 都是 SFU）
- 不解码不混音，CPU 开销低，但带宽放大（N×M 转发）
- 实现极度复杂：要同时讲 RTP、SRTP、RTCP、NACK、PLI、FIR、TWCC、REMB

**作者亲历**：他在 Twitch 用 Pion 写过一个，在 Discord 用 Rust 又写过一个。

---

## 3. Jitter Buffer（抖动缓冲）

**一句话**：把网络上\"先后顺序乱了、间隔抖了\"的音视频包，缓存后按正确时间戳重排播放的小缓冲区。

**关键事实**：
- WebRTC 的 audio jitter buffer 默认 20–200ms 范围
- 优化目标是**最小化延迟**——满了就丢包，**不重传**
- 适合双向会议，不适合\"先生成完再播放\"的 TTS 场景

**反范式**：Voice AI 场景下，可以让客户端缓冲几秒钟的 TTS 输出，反而对网络抖动免疫。

---

## 4. SDP（Session Description Protocol）

**一句话**：WebRTC 会话协商用的纯文本格式，描述\"我支持哪些 codec / 加密方式 / 端口 / IP 候选\"。

**关键事实**：
- WebRTC 用 \"Offer/Answer\" 模式互相交换 SDP
- 修改 SDP（\"SDP munging\"）是 WebRTC 工程的灰色艺术——很多调优只能这样做
- 作者吐槽：连 audio NACK 都要靠 SDP munging 才能（可能）打开

---

## 5. ufrag / ssrc

**一句话**：WebRTC 里识别\"这个包属于哪条连接\"的两个关键字段。

- **ufrag**：ICE 协议里的用户名片段，每条连接随机生成，OpenAI 用它做 STUN 路由 key。
- **ssrc**：RTP 里的同步源标识，32-bit 随机数。Discord 撞过 ssrc 碰撞——应对方案是**用所有可能的密钥都试一遍解密**。

**为什么重要**：当你把多个连接 mux 到一个端口（违反 WebRTC 规范但所有人都这么做），就只能靠这两个字段做多路复用。

---

## 6. QUIC（Quick UDP Internet Connections）

**一句话**：Google 2012 年发起、IETF 2021 年标准化的新一代传输层协议，跑在 UDP 上，原生支持 TLS 1.3、多路复用、连接迁移。

**关键事实**：
- 1 个 RTT 就能完成 \"连接 + 加密\" 握手（对比 TCP+TLS 的 3 RTT）
- HTTP/3 = HTTP over QUIC
- WebTransport = 浏览器里直接用 QUIC 的 API（绕过 HTTP 语义）

**对 Voice AI 的吸引力**：连接迁移、低握手延迟、对负载均衡极友好。

---

## 7. CONNECTION_ID

**一句话**：QUIC 协议里每个包都带的 0–20 字节标识，由\"接收方\"指定，用来识别连接。

**为什么是杀手特性**：
- 源 IP/端口改变时（手机切 WiFi → 4G），连接仍然不中断
- 负载均衡器只需看几个字节就能路由，不需要任何共享状态
- 是 WebRTC 用 ufrag/ssrc 拼命模拟的能力，QUIC 在协议第一字段就给你了

---

## 8. QUIC-LB（QUIC Load Balancing）

**一句话**：让 QUIC 后端把自己的 ID 编码进 CONNECTION_ID，使得负载均衡器**完全无状态**地路由后续所有包。

**对照 OpenAI**：OpenAI 的 STUN-only relay 用 Redis 存源 IP/port → backend 的映射，QUIC-LB 不需要 Redis。

**生产实例**：Cloudflare 全球边缘已经用这套机制做 anycast QUIC 路由。AWS NLB 也提供 QUIC LB 能力。

---

## 9. anycast / preferred_address

**一句话**：让多个服务器在 BGP 上 advertise 同一个 IP，BGP 自动把客户端路由到最近的服务器。

**QUIC 的杀手组合**：
1. 客户端用 **anycast** 地址（如 `1.2.3.4`）做握手
2. 服务器握手时用 QUIC `preferred_address` 告诉客户端\"以后发到 `5.6.7.8`\"
3. 服务器满载时撤回 anycast 通告，新连接自动飘到别处，旧连接在 unicast 上稳定

**结果**：不需要传统意义上的负载均衡器，anycast 地址本身就是健康检查。

---

## 10. Voice AI

**一句话**：以语音为主要交互界面的 AI 系统——ChatGPT Voice、Pi、Sesame、Suno Studio Voice 等。

**协议层面的独特需求**：
- 1:1 客户端到服务器，不需要 P2P
- TTS 生成速度往往快于实时播放
- 准确性 > 延迟（小幅度延迟比识别错更可接受）
- 服务端是固定 IP 的 GPU 集群

**当前现实**：几乎所有产品默认用了 WebRTC——本文论证这是\"显然但错误\"的选择。

---

## 11. MoQ（Media over QUIC）

**一句话**：IETF 正在标准化的新一代实时媒体协议，把媒体语义直接构建在 QUIC streams 之上。

**关键设计**：
- 摆脱 RTP / SRTP / SCTP 这套老协议
- 提供高层的 cache / fan-out 语义，CDN 友好
- 已有 Cloudflare 技术预览版

**对 Voice AI 的态度**：作者诚实地说，MoQ 的 cache/fanout 语义对 1:1 audio 用处不大，但 QUIC 那一层非常合适。

---

## 12. HOL Blocking（Head-of-Line Blocking）

**一句话**：当一个包丢了或晚到，后面所有包都得等它，整个流被卡住——TCP 的经典痛点。

**两面看**：
- **WebRTC 视角**：HOL 是绝对要避免的——会议场景下宁可丢一个音频包也不能停顿
- **作者观点**：在 Voice AI 场景下，**HOL 是特性不是 bug**——用户宁可多等 200ms 也不愿听到失真音频或被错误识别
- **QUIC streams**：在 stream 层无 HOL（多 stream 互不干扰），在 stream 内有 HOL，可以按需选择

---

## 学习路径建议

1. 先读 [Replacing WebRTC (2023)](https://moq.dev/blog/replacing-webrtc/) 理解作者的整体框架
2. 再读 [OpenAI's WebRTC Problem (2026)](https://moq.dev/blog/webrtc-is-the-problem/)（本文）看具体批评
3. 然后读 [QUIC's hidden Super Powers](https://moq.dev/blog/quic-powers/) 把 QUIC 那部分挖深
4. 最后读 Daniel Stenberg 的 [HTTP/3 explained](https://http3-explained.haxx.se/) 把 QUIC 标准吃透

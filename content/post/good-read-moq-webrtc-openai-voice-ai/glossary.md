# 术语对照表 / Glossary

> *OpenAI's WebRTC Problem* 一文涉及的 WebRTC、QUIC、Voice AI、网络协议相关术语，约 35 条。

| 英文 | 中文 | 简要说明 |
|------|------|---------|
| WebRTC | 网页实时通信 | 浏览器原生的实时音视频/数据通道 API，由 ~45 个 RFC 组成 |
| Voice AI | 语音 AI | 以语音为主交互界面的 AI 系统（ChatGPT Voice 等） |
| SFU | 选择性转发单元 | 实时音视频会议的中转服务器，不混音只转发 |
| MCU | 多点控制单元 | SFU 的早期替代品，在服务端混音，CPU 开销高 |
| RTC | 实时通信 | Real-Time Communication 的总称 |
| TTS | 文本转语音 | Text-To-Speech，AI 把文本合成为音频 |
| STT / ASR | 语音转文本 / 自动语音识别 | Speech-To-Text / Automatic Speech Recognition |
| ICE | 交互式连接建立 | NAT 穿透的核心协议，配合 STUN/TURN 工作 |
| STUN | 会话穿越实用工具 | 探测公网 IP/端口的服务器，UDP 协议，无状态 |
| TURN | 中继穿越 | 当 STUN 失败时通过中继服务器转发流量 |
| DTLS | 数据报传输层安全 | UDP 上的 TLS，用于 WebRTC 加密握手 |
| SRTP | 安全实时传输协议 | 加密后的 RTP，承载实际音视频数据 |
| SRTCP | 安全实时控制协议 | SRTP 的控制通道，传统计、反馈 |
| SCTP | 流控制传输协议 | WebRTC DataChannel 的底层协议 |
| SDP | 会话描述协议 | WebRTC 用来协商\"我支持哪些 codec/加密/IP\"的纯文本格式 |
| RTP | 实时传输协议 | 1996 年标准化的实时媒体协议，奠定了之后 20 年的设计 |
| RTCP | 实时控制协议 | RTP 的控制平面，反馈丢包/抖动信息 |
| mDNS | 多播 DNS | 局域网内自动发现，WebRTC 用来隐藏 IP |
| WHIP | WebRTC HTTP Ingest Protocol | 把 WebRTC 包装成 HTTP 信令的轻量协议 |
| WebTransport | Web 传输 | 浏览器里直接用 QUIC streams + datagrams 的 API |
| QUIC | 快速 UDP 网络连接 | Google 起、IETF 2021 标准化的新传输层协议 |
| HTTP/3 | 超文本传输协议 3 | HTTP over QUIC |
| HOL Blocking | 队头阻塞 | 一个包丢了，整条流被卡——TCP 的经典痛点 |
| MoQ | 媒体 over QUIC | 新一代实时媒体协议，IETF 标准化中 |
| NACK | 否定确认 | 接收方告诉发送方\"我没收到这个包\"，触发重传 |
| FEC | 前向纠错 | 发送冗余数据让接收方自己恢复丢包，不需重传 |
| Jitter Buffer | 抖动缓冲 | 缓存乱序包按时间戳重排，平滑播放 |
| TWCC | 传输级宽带阻塞控制 | Transport-Wide Congestion Control，WebRTC 拥塞反馈 |
| REMB | 接收端最大带宽估计 | Receiver Estimated Max Bitrate，已被 TWCC 取代但仍用 |
| BWE | 带宽估计 | Bandwidth Estimation 的总称 |
| Pion | Pion | Go 语言写的 WebRTC 实现库，OpenAI 用的就是它 |
| libwebrtc | libwebrtc | Google 主导的 WebRTC 参考实现，浏览器内嵌 |
| SSRC | 同步源标识 | RTP 里的 32-bit 连接 ID，会撞车 |
| ufrag | ICE 用户名片段 | ICE 协议里的随机标识符 |
| Connection ID | 连接 ID | QUIC 里 0–20 字节的连接标识，**接收方选**，免疫源 IP 变化 |
| QUIC-LB | QUIC 负载均衡 | 把后端 ID 编进 Connection ID 实现无状态路由 |
| anycast | 任播 | 多服务器共用一个 IP，BGP 自动路由到最近的 |
| unicast | 单播 | 一对一传输，与 anycast 相对 |
| preferred_address | 首选地址 | QUIC 的字段，让服务器在握手时\"把客户端导向\"另一个 IP |
| RTT | 往返时延 | Round-Trip Time，网络性能核心指标 |
| Connection Migration | 连接迁移 | QUIC 在 IP/端口变化时不重新握手就保持连接 |
| RFC | 请求评议 | 互联网协议标准文档，由 IETF 发布 |
| IETF | 互联网工程任务组 | 制定互联网协议标准的组织 |
| BGP | 边界网关协议 | 互联网骨干路由协议，anycast 的基础 |

## 缩写补充

- **DAU**：日活跃用户
- **TTFT**：Time To First Token，LLM 推理的首 token 延迟
- **CDN**：内容分发网络
- **NAT**：网络地址转换
- **MTU**：最大传输单元
- **codec**：编码器/解码器（codec = coder + decoder）
- **AV1 / VP9 / H.264 / Opus**：常见音视频编解码格式

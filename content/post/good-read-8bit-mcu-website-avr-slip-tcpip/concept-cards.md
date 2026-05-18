# 概念卡片 · 1$ AVR Web Server 全栈拆解

> 12 张关键概念卡片。每张可独立阅读，用于通勤或茶歇 30 秒掌握一个核心点。

---

## 卡片 01 · AVR Dx 系列 vs ATmega328

**问题**：为什么 Maurycy 选 AVR64DD32 而不是更出名的 ATmega328？

**答案**：
- RAM：8 kB vs 2 kB（**4 倍**，足以放 200 条 TCP 连接表）
- Flash：64 kB vs 32 kB
- 编程：单针脚 UPDI vs 6 针 ISP
- 外设：内置 OPAMP、ADC 12-bit、多个 USART
- 价格：~$1 vs ~$2（**便宜一半**）

**记忆口诀**：DD = Double Density（RAM 翻倍、Flash 翻倍、引脚使用减半）。

---

## 卡片 02 · 为什么 10BASE-T 不能 bit-bang

**问题**：8 位 MCU 跑以太网，物理上能做到吗？

**答案**：不能。10BASE-T 用 **Manchester 编码**：
- 比特 0 → 信号 "10"
- 比特 1 → 信号 "01"
- 数据率 10 Mbps，**线速 = 20 MHz toggle**

AVR I/O 引脚最高 12 MHz toggle，差一半。100BASE-TX 用 MLT-3 + 4B/5B，要求更高。

**结论**：要做 8 位 + 以太网，必须加 ENC28J60 / W5500 这种独立 MAC/PHY 芯片。

---

## 卡片 03 · SLIP 协议（RFC 1055, 1988）

**作用**：用一根串口线传输 IP 包。

**规则**（共 4 条）：
1. 包前后各加一个 `0xC0`
2. 包内 `0xC0` → `0xDB 0xDC`
3. 包内 `0xDB` → `0xDB 0xDD`
4. 不带地址、不带校验、不带错误恢复

**实现量**：MCU 端约 60 行 C；Linux 端零代码（内核内建 `net/slip`）。

**今日意义**：现代 Linux 仍支持 SLIP，是把 MCU 接入网络最便宜的方式。

---

## 卡片 04 · IPv4 头部最小必要字段

**完整 IPv4 头**有 20+ 字节 + 可选项。Maurycy 实际处理的字段只有：

| 字段 | 作用 | 实现 |
|---|---|---|
| Version | 必须 = 4 | 检查 |
| IHL | header 长度 | 固定 5 |
| Total Length | 包总长 | 写入 |
| TTL | 跳数 | 重置 64 |
| Protocol | 上层协议 | 6=TCP / 1=ICMP |
| Source IP | 源 | 与 Dest 互换 |
| Dest IP | 目的 | 与 Source 互换 |
| Checksum | 校验 | 重算 |

被砍掉：fragmentation、IP options、DSCP/ECN（设 0）。

---

## 卡片 05 · IP Checksum 的 8 位实现技巧

**协议规定**：16-bit one's complement sum over header，再取反。

**在 8 位 CPU 上的高效写法**（RFC 1071）：
1. 把每两字节当作 uint16，累加到 uint32 中
2. 累加完毕后，把 uint32 的高 16 位反复加回低 16 位，直到没有 carry
3. 取反得到 checksum

**为什么是 8 位平台最快**：避免每次加都检测 carry，把 carry 推到最后一次性处理。

---

## 卡片 06 · TCP 状态机最小子集

Maurycy 的 TCP 实现支持的状态：

```
CLOSED → LISTEN → SYN_RECEIVED → ESTABLISHED → FIN_WAIT → CLOSED
```

每条连接需要保存：
- remote_ip (4B)
- remote_port (2B)
- local_port (2B)
- state (1B)
- snd_seq (4B)
- rcv_seq (4B)
- last_active (4B 时间戳)

**总计 ~21 字节/连接**。`MAX_CONNS=200` → 4.2 kB（一半 RAM）。

**砍掉**：Nagle 算法、SACK、ECN、Window Scaling、Timestamp option、Persist Timer、Karn's algorithm。

---

## 卡片 07 · 为什么"硬编码 HTTP 响应"是对的

**前提**：你的网站只有 **一个 URL**。

**那么**：
- 不需要 parse Method（永远是 GET）
- 不需要 parse Path（永远是 /）
- 不需要 parse Header（除了 `\r\n\r\n` 边界）
- 不需要 routing、middleware、content negotiation

**节省**：约 5–10 kB Flash + 不可计的开发时间。

**教训**：**约束驱动设计** > 通用框架。当你的需求是 1，做 1 即可。

---

## 卡片 08 · WireGuard 在此处的角色

**误解**：WireGuard 是 VPN（"翻墙"工具）。

**真相**：在本项目中，WireGuard 是 **NAT 穿透 + 加密专线**。
- UDP-only → 易过 NAT
- 静态密钥 + Curve25519 → 配置简单
- roaming endpoint → 家里 IP 变了不掉线
- 内核态实现 → 接近 wire speed

**拓扑**：
```
[AVR] -- SLIP --> [家庭 Linux] -- WireGuard UDP --> [赫尔辛基 VPS] -- nginx /mcu --> [公网]
```

---

## 卡片 09 · 反向代理同时是三个角色

VPS 上的 nginx `location /mcu` 配置同时承担：

1. **路由器**：把公网 URL 映射到内网 WireGuard 地址
2. **TCP 终止器**：客户端的 TCP 与 MCU 的 TCP 是 **两条独立连接**，nginx 在中间转发
3. **SYN flood 缓冲器**：恶意 SYN 不会到达 MCU 的简陋 TCP 栈

**类比**：与 Cloudflare 在 edge 终止 QUIC 同构，只是尺寸缩小一万倍。

---

## 卡片 10 · "MAX_CONNS=200" 的内存账

| 项目 | 字节 |
|---|---|
| `pkt_in[MTU]` (MTU=1500) | 1500 |
| `pkt_out[MTU]` | 1500 |
| `conn[200]` × 21 字节 | 4200 |
| 全局/中断/栈 | ~500 |
| **总计** | ~7700 |

8192 - 7700 = **492 字节余量**。这是 8 位 MCU 上典型的"极限榨干"，但也是为什么这种代码不能扩展——再加一个特性 RAM 就爆。

---

## 卡片 11 · 经典对照：uIP / lwIP / smoltcp

| 实现 | 作者/语言 | 典型 ROM | 典型 RAM | 风格 |
|---|---|---|---|---|
| **Maurycy 自写** | C, 2026 | ~10 kB | ~8 kB | 单文件、教学品 |
| **uIP** | Adam Dunkels, 2001, C | ~6 kB | ~2 kB | protothreads |
| **lwIP** | Adam Dunkels et al, C | ~40 kB | ~10–20 kB | 主流 RTOS 标配 |
| **smoltcp** | Rust, no_std | ~50 kB | 可配置 | 静态分配、Redox |

**结论**：Maurycy 的实现是 **教学品 / 文章伴侣**，不是 lwIP 的替代品。

---

## 卡片 12 · IPv6 的家庭普及问题（彩蛋）

原文最后一句怒气十足：

> 原文：This whole problem wouldn't exist if we could just get our stuff together: IPv6 has existed for thirty years but most people still don't have access.

**事实清单**：
- IPv6 1995 年标准化（RFC 1883），1998 年定稿（RFC 2460）
- 2026 年仍有 ~40% 全球家庭无原生 IPv6
- 主要瓶颈：CGNAT 既能用且更便宜 → ISP 没动力
- 若有 IPv6：每个 MCU 都能拿到全球唯一地址，不需要 WireGuard、不需要反代

**与 [Mullvad 那篇](/post/good-read-mullvad-exit-ip-fingerprinting/) 的连接**：IPv4 地址池的稀缺 + CGNAT 共享 = 出口指纹更易追踪。

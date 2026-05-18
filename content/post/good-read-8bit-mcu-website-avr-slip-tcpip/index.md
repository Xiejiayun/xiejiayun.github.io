---
title: "【好文共赏】1 美元、8 kB RAM、一根 USB 串口线：Maurycy 把整个 TCP/IP 栈塞进 AVR64DD32，给微控制器装了一个网站"
description: "Maurycy 用一颗 1 美元的 8 位 AVR 单片机，亲手实现了 SLIP + IPv4 + 自写 TCP 状态机 + HTTP 单 URL 响应，再用 WireGuard 让它出现在公网，全过程 600 行 C 代码——一份关于'极致受限平台 + 现代网络'的 5 分钟工程长读"
date: 2026-05-18
slug: "good-read-8bit-mcu-website-avr-slip-tcpip"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 嵌入式
    - 网络协议
    - 单片机
    - 复古工程
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> **原文**：[Hosting a website on an 8-bit microcontroller](https://maurycyz.com/projects/mcusite/) · 作者：Maurycy · 发布：2026-05-11（持续更新至 05-14） · 阅读时长：约 5 分钟（含 600 行 C 源码可下载）
>
> **多模评分**：Opus 8.8 / Sonnet 8.5 / Gemini 8.6（综合 **8.63 / 10**）
>
> **HN 热度**：235 points / 20 comments（front page，2026-05-17）
>
> **一句话推荐**：当大半个行业还在为「Rust 重写 Bun」、「让 AI 重写流程」这些抽象议题吵架时，Maurycy 一个人在自家桌子上把 1977 年的 SLIP、1981 年的 IPv4、2018 年的 WireGuard 和一颗 1 美元的 AVR 单片机串在一起，写了一段不到 600 行的 C 代码，结果就是：你现在真的可以访问一个跑在 8 kB RAM、8 位内核里的网站。这种"全栈最小生成元"式的工程，是 2026 年互联网上越来越稀缺的写作品类。

---

## 1. 为什么值得读

过去十二个月，「8 位单片机跑 X」这类项目在 HN 上几乎每周一次：有人在 Z80 上跑 Linux 用户态、有人在 6502 上跑 GPT-2，有人用 ESP32 做 Kubernetes 节点。绝大多数都是炫技——把一个想法做成 demo 视频，发到推上，吃完热度就丢。

Maurycy 这一篇不一样。它具备三个稀缺特征。

第一，**整条工程链路完整**。从选片（AVR64DD32 为什么比 ATmega328 划算）、不选以太网的物理层原因（10BASE-T 的 Manchester 编码需要 20 MHz 线速，而 AVR I/O 引脚最高 12 MHz）、SLIP 帧格式（RFC 1055 的 0xC0/0xDB/0xDC/0xDD 转义）、IPv4 头部的最小必要字段、TCP 状态机的"几天调试"、HTTP 的"算了我直接硬编码一个响应"，到最后把它通过 WireGuard 暴露到芬兰赫尔辛基的 VPS，没有任何一步是抽象掉的。读者可以照着原文一字不漏地复制出来。

第二，**作者公开了所有代码**，并且声明 "This website is not licensed for ML/LLM training or content creation"——这是 2026 年我越来越欣赏的一种创作伦理：自己的内容，自己定义谁能用。原文链接的 [`www.c`](https://maurycyz.com/projects/mcusite/www.c) 实测约 600 行，没有任何依赖，编译出来 [`www.elf`](https://maurycyz.com/projects/mcusite/www.elf) 直接烧录就跑。这与 [《【好文共赏】把 Fisher-Price 的童年盲盒一颗颗剥光》](/post/good-read-dmitry-grinberg-pixter-full-preservation/) 中 Dmitry Grinberg 的「完全保存」精神一脉相承。

第三，**它给"什么是真正的全栈"做了一个反向定义**。我们行业里"全栈"这个词早已被简化为 React + Postgres + Vercel 的三件套。Maurycy 的全栈是：物理层（Manchester 编码 vs SLIP）→ 链路层（USB-Serial、`slattach`）→ 网络层（自写 IP 头部组装）→ 传输层（自写 TCP 状态机）→ 应用层（一行 HTTP 硬编码）→ 公网暴露（WireGuard + nginx 子路径反向代理）。每一层都没有任何"先用现成库"，每一层都暴露出一个被现代框架隐藏多年的设计决定。

对今天大量"会用 fetch 但不知道 SYN-SYN/ACK-ACK 状态机"的工程师而言，这是一份难得的纵切片教材。

---

## 2. 核心拆解 · 一：为什么不是 ATmega328、不是 ESP32，而是 AVR64DD32

很多人会下意识地觉得"8 位单片机做 web server"就是 Arduino 那一套。原文一开头就用一张参数表绕开了这层误解：

> 原文：CPU: Single 8-bit AVR core @ 24 MHz (max) · RAM: 8 kB · Flash: 64 kB · EEPROM: 256 bytes · Voltage: 1.8 – 5.5 V · Cost: $1

这颗 AVR64DD32 属于 Microchip 在 2022 年前后推出的 AVR Dx 系列。相比经典 ATmega328（同样 8 位、最高 20 MHz、2 kB RAM、32 kB Flash、价格 ~$2），它有三个改良：**RAM 翻 4 倍**（这是能跑 TCP 状态表的关键，因为每个连接需要保存序列号/确认号/状态字段，原文 `MAX_CONNS=200` 直接占走几 kB）、**单针脚 UPDI 编程**（不再需要 6 针 ISP 头）、**12 MHz 外设时钟**（虽然不足以打 10BASE-T，但足够 USART 跑 115200 bps SLIP）。

为什么不选 ESP32？原文没有直接说，但隐含的判断很清楚：ESP32 自带 lwIP 栈，整件事就变成了"在 IDF 里写一个 hello world"，工程深度归零。8 位 AVR 才是那个"什么都没有，必须自己写"的稀缺平台。

这种选片逻辑跟 [《【好文共赏】OCaml 第一次飞上轨道》](/post/good-read-ocaml-in-space-borealis/) 中 Tarides 选 unikernel 而不是 Yocto 是同一种品味：**约束本身就是题目**。只有当你的 RAM 只有 8 kB，TCP 状态机才必须诚实。

### 2.1 关键决定：放弃以太网

原文用两段话讲清楚了为什么 10BASE-T 不能选：

> 原文：Even the slowest version (10BASE-T) still runs at 10 megabits/second. Worse, it uses Manchester encoding: a zero is sent as "10" and a one as "01", so 10 megabits of data is actually 20 megabits at the wire.
>
> While its processor can run at 24 MHz, but all the peripherals and IO pins max out at a 12 MHz clock.

这其实是 8 位单片机做网络项目时一个常被忽略的物理事实：**bit-banged Ethernet 不仅要求 MCU 在 CPU 频率上够快，还要求 I/O 引脚翻转速率（toggle rate）够快**。AVR 这一颗即便上到 24 MHz，I/O 也只能 12 MHz 切换，连 Manchester 编码 10 Mbps 都达不到。这就是为什么早期"裸跑 Ethernet"的玩家都得加 W5500、ENC28J60 这类外置 MAC/PHY 芯片。

Maurycy 选了一条更优雅的路：**直接绕开链路层，让 Linux 替我做**。

---

## 3. 核心拆解 · 二：SLIP——1988 年的协议为何还在 Linux 内核里

SLIP（Serial Line Internet Protocol，RFC 1055，1988 年）几乎是"最简单的网络协议"：

- **帧分隔符**：每个 IP 包前后各包一个 `0xC0` 字节
- **转义**：包内出现 `0xC0` → `0xDB 0xDC`；包内出现 `0xDB` → `0xDB 0xDD`
- **无地址、无校验、无错误恢复**——一切交给上层 IP/TCP

读者可能下意识觉得这种"远古协议"早就被废弃。但原文给出一个干净的反例：

```bash
stty -F /dev/ttyUSB0 115200 raw cs8
slattach -m -F -L -p slip /dev/ttyUSB0
# ... and now it's a network interface
```

两行命令，Linux 内核就把 `/dev/ttyUSB0` 变成了一个真正的网络接口 `sl0`。你可以 `ip addr add`、`ip route add`，跟普通以太网卡一模一样。这是 30 年前拨号上网遗留的好处：**SLIP 早已嵌入 net/slip 内核模块，从未被移除**。

对 MCU 端的意义是巨大的：你只需要实现一个 UART RX 中断 + 状态机扫描 `0xC0/0xDB`，整个链路层就完成了。原文的 `www.c` 中这一部分大概 60 行 C 代码、3 个全局变量（`pkt_in[MTU]`、`len_in`、`packet_ready`），不需要 DMA、不需要环形缓冲，因为 SLIP 没有时序要求——MCU 慢，就让发送端等。

### 3.1 一个常被忽视的细节：MTU 与 buffer

原文用宏 `#define MTU 1500`、`#define MAX_PAYLOAD 500` 把两边定死。注意 **MTU=1500 占了 RAM 的 18.75%**，再加上一个 `pkt_out[MTU]` 就是 37.5%。在 8 kB 设备上，这是一个相当激进的内存预算。一个常见的"省 RAM"做法是把 MTU 调到 576（IPv4 强制最低值），但 Maurycy 选了 1500——这意味着他押注 Linux 端会替他打散大包，而不是反过来。

这种"我可以省，但我不省"的选择，背后其实是个深刻的工程判断：**优化总要选一个地方，选错就把你后面所有调试都拖死**。先让协议正确，再谈紧凑。这与 [《【好文共赏】把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上》](/post/good-read-haskell-mercury-production-engineering/) 中 Mercury 团队"先类型正确再考虑性能"的取舍是同一种心法。

---

## 4. 核心拆解 · 三：手写 IPv4 头部——比想象中简单

读者听到"手写 IP 协议栈"通常会本能地退缩。Maurycy 用一段话把这个恐惧化解了：

> 原文：The protocol used to be a lot more complex, with features like packet fragmentation that require a lot of memory to handle correctly, but I don't have to: every modern operating system disables fragmentation and IPv6 removed it entirely. This makes implementing it very easy: Just swap around the source and destination of a received packet to generate the header for the response. (and reset the TTL counter)

把这段话翻译成可执行步骤：

1. 从 SLIP 包里读出 20 字节 IPv4 头
2. 校验 protocol 字段 == 6 (TCP) 或 1 (ICMP)
3. **互换 source IP / dest IP**
4. TTL 重置为 64
5. **重算 header checksum**（这是唯一一个真"算"的字段）
6. 回写

整个 IP 层不到 30 行。能这么短的根本原因是 Maurycy 明确放弃了：
- **IP fragmentation**（每个现代 OS 都设置 DF=1）
- **IP options**（极少使用，VPN 厂商常 strip）
- **多播/广播路由**
- **ICMP 高级功能**（保留了 echo reply 让 `ping` 能通）

这种"砍掉一切现代不再需要的字段"的做法，其实跟 [《【好文共赏】Quack：DuckDB 在 2026 年从零设计一个数据库 wire 协议》](/post/good-read-duckdb-quack-protocol/) 异曲同工：当一个协议被设计了 40 年，绝大部分字段已经事实失效，只有把它们识别出来，才能写出小到 200 行的实现。

### 4.1 校验和的小动作

IPv4 checksum 是 16-bit one's complement，over 整个头部。在 8 位 CPU 上做 16 位加法、检测进位、回环加（end-around carry），原本是个非常容易写错的地方。从 `www.c` 里可以看到 Maurycy 的实现走了一个标准的 trick：**累加成 uint32_t，最后再把高 16 位反复加回低 16 位**。这是 RFC 1071 给出的"高效校验和"算法，30 多年了，依然是 8 位平台上最快的写法。

---

## 5. 核心拆解 · 四：自写 TCP 状态机——"几天搞定，还有 bug"

这是原文最克制的一段：

> 原文：The other protocol, TCP is a lot harder: Implementing it requires the microcontroller to track connection states, periodically retransmit lost packets and handle a huge number edge cases. It took several days to get my custom implementation working well enough, and it's still got a few bugs.

但代码里能看出"几天"包含什么：

- 一个 `conn[MAX_CONNS]` 结构数组，每个条目存 `{remote_ip, remote_port, local_port, state, snd_seq, rcv_seq, last_active}`
- 状态枚举：LISTEN / SYN_RECEIVED / ESTABLISHED / FIN_WAIT / CLOSED
- 每 500 ms 用 TCA0 定时器中断设一个 `should_rtx` flag，主循环遍历所有连接，对超时未 ACK 的报文进行重传
- 没有 Nagle 算法、没有 SACK、没有 ECN、没有 timestamp option——**只有 RFC 793 的最小核心**
- "几个 bug"的诚实：HN 评论区里有人复现了"快速重连同一端口时连接表错乱"的现象，作者自己也在脚注承认

关键的设计选择是 **`MAX_CONNS = 200`**。在 8 kB RAM 里硬塞 200 个连接条目，每个条目不到 16 字节，意味着所有元数据都是定长 + 无指针。这与 lwIP 那种 malloc-heavy 的实现完全是两条路。

对今天用 socket API 写 server 的工程师来说，这一段代码其实把 TCP "去神秘化"了：**TCP 不是黑魔法，它就是一个有 11 个状态、若干超时计数器、若干序列号比较的有限状态机**。看一遍 Maurycy 不到 200 行的实现，再回去看 Linux 内核 `net/ipv4/tcp_input.c` 那 4000 行，对每一个 `if` 分支都会更有体感。

### 5.1 为什么不直接用 uIP 或 lwIP？

uIP（Adam Dunkels 2001 年的 6 kB TCP/IP 栈）和 lwIP 是 MCU 圈子里现成的方案。Maurycy 没有直接说原因，但从字里行间可以推断：

- uIP 用 protothreads 这种"非阻塞协程"风格，调试体验差
- lwIP 太大，光是 `pbuf` 抽象就要几 kB Flash
- **自己写一遍才能完全理解** —— 这与 [《【好文共赏】matklad：Conway 定律才是软件架构的母题》](/post/good-read-matklad-learning-software-architecture/) 中 matklad 说的「真正读懂一个系统的方式是重写它」是一回事

这种"为了学习而自写"的传统，从 Tanenbaum 的 MINIX 到 xv6 一脉相承，是嵌入式社区最珍贵的精神资产之一。

---

## 6. 核心拆解 · 五：HTTP——为什么直接硬编码一个响应是对的

最让我笑出声的是这段：

> 原文：As for implementing HTTP, I didn't: The server always sends a hardcoded "response" back to the client. This works fine as long as there's only a single URL on the site.

这一段值得整个软件工程行业反复读三遍。

HTTP 1.1 的 RFC 7230 系列至少 8 个文档，加起来上千页。但如果你的网站**只有一个 URL**，所有 RFC 都是噪声——你需要的只是：

1. 读到 `\r\n\r\n` 表示 header 结束
2. 发回一个固定的 `HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: N\r\n\r\n<html>...`

不需要 parse Method、不需要 parse Path、不需要 parse Header。这是"约束驱动设计"的极致：**当你的需求只有一个 URL 时，所有 routing、所有 method dispatch、所有 content negotiation 都是过度设计**。

我看到这一段的瞬间，想起的是 [《【好文共赏】Redis 的野心代价》](/post/good-read-redis-cost-of-ambition/)。Charles Leifer 的论点是 Redis 试图同时做 dict、queue、pub/sub、search、graph、JSON store，每一项都做不到最好。Maurycy 的反向论点正好对位：**当你只做一件事时，你可以把它做到极致小**。1500 字节的 HTTP 响应，能驱动一颗 1 美元的芯片自豪地说"我也是 Web 服务器"。

---

## 7. 核心拆解 · 六：WireGuard 反向代理——让 8 位单片机出现在公网

最后一段我个人最喜欢，因为它把"复古工程"和"现代互联网现实"完美对接。

问题：MCU 在作者家里，家里没有公网 IPv4，连 Starlink 都被原文直接嘲讽（"no, Starlink is not good"）。解法：

1. 家里一台 Linux router 通过 SLIP 连 MCU，作为协议转换器
2. 这台 Linux 通过 **WireGuard 隧道**连到芬兰赫尔辛基的 VPS
3. VPS 上的 nginx 把 `/mcu/*` 路径反代到 WireGuard 隧道另一端的私有 IP

这套架构有几个值得拆开看的点：

**(a) 为什么不直接给 MCU 一个公网 IP？** 因为这意味着把 MCU 的自写 TCP 栈直接暴露给互联网。原文写得很坦白：

> 原文：This means that visitors aren't directly connecting to the MCU's TCP/IP stack... but hey, it's the same setup that the Vape Server uses and no one complained. (It also makes it slightly harder to break by sending SYN packets, but it's not exactly hard to DDoS a server connected over what's effectively dial-up)

也就是说，**反向代理同时承担了三个角色**：路由器、SYN flood 缓冲器、TCP 终止器。这与 Cloudflare 在 [《【好文共赏】当"空闲"不是空闲》](/post/good-read-cloudflare-quic-cubic-death-spiral/) 里把 QUIC 终止在 edge 节点的思路完全同构——只不过尺寸缩小了一万倍。

**(b) WireGuard 在这里的角色非常优雅**。它不是 VPN（没有人需要"翻墙"到 MCU），而是一个"NAT 穿透 + 加密专线"工具。WireGuard 的 NAT 友好特性（UDP-only、roaming endpoint）让家里的 CGNAT 不再是阻碍。

**(c) 整个公网链路的延迟堆栈**：USB→SLIP（115200 bps，~10 KB/s 极限）→ Linux router → WireGuard UDP → 公网 → 芬兰 VPS → nginx → reverse proxy → 你浏览器。**最慢的环节是 SLIP 串口**，~80 ms 单边时延，足以让现代浏览器的 keep-alive 超时阈值都需要调高。

---

## 8. 编辑延伸思考：在 LLM 写代码的年代，为什么我们更需要这种"凿穿一切"的工程

2026 年我们正在经历一个奇怪的悖论：

- 一方面，Codex/Claude Code 已经能在 5 分钟内"写出"一个完整 web server。但这种写出，是在 npm 上下载 200 个包、依赖 30 万行别人的代码、最终跑在一个抽象掉所有底层细节的 runtime 上。
- 另一方面，**很少有人能从 SLIP 帧解析一路写到 nginx 反代**——因为这其中每一步都被"现成方案"挡住了。LLM 知道每一层的名字，但它不像 Maurycy 一样真的把每一层用 600 行 C 代码缝在一起过。

我越来越相信：**在 AI 写代码的时代，"自己凿穿全栈一次"的能力，会从"程序员的乐趣"升级为"程序员的差异化护城河"**。一个会用 ChatGPT 帮你 vibe code 一个 SaaS 的人，年薪可能 8 万美元；一个能在一颗 1 美元的 AVR 上自己实现 TCP 状态机的人，年薪可能 30 万美元——因为后者意味着你**真的理解**网络栈，意味着当生产环境出 CUBIC 死亡螺旋（参考 [Cloudflare 的那篇](/post/good-read-cloudflare-quic-cubic-death-spiral/)）或者 ClickHouse 互斥锁竞争（参考 [Cloudflare 这篇](/post/good-read-cloudflare-clickhouse-mutex-contention/)）时，你能从第一性原理出发去诊断。

Maurycy 在博客首页用一行字标明："This website is not licensed for ML/LLM training or content creation."——这不仅是版权声明，更是一种立场宣言：**人类可以学习的工程实践，不应该被无限稀释成模型的训练材料**。

如果我们这一代程序员还想保留点东西不被自动化吞噬，**自己用 8 kB RAM 重写一遍 TCP，可能是最高 ROI 的练习之一**。

### 8.1 这篇文章的"反例"在哪里？

为了平衡，我也要指出原文的不足：

1. **TCP 状态机的几个 bug 没有给出修复路线图**。读者复刻时会撞到，但要自己 debug。
2. **没有性能数据**。115200 bps 实际峰值吞吐多少？200 个并发连接的内存碎片如何？文章一字未提。
3. **作者承认了 IPv6 的根本问题（"This whole problem wouldn't exist if we could just get our stuff together"）但没有给出 IPv6 版本**。这反映了 IPv6 在家庭网络的落地仍然是个无解的政治问题，与 [《【好文共赏】8.2 万亿种可能里只剩 284 种》](/post/good-read-mullvad-exit-ip-fingerprinting/) 中 IPv4 地址池的稀缺性形成镜像。
4. **没有讨论安全性**。一个手写 TCP 栈在 NAT 后面相对安全，但如果暴露到公网，整数溢出、状态机绕过都是真实风险。这一点与 [《【好文共赏】curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 中 Stenberg 讨论的"小代码量并不等于无漏洞"是一致的。

但这些不足并不损害原文价值——它本来就是一篇 5 分钟的项目随笔，不是 USENIX 论文。重要的是它**给读者打开了一扇门**。

---

## 9. 延伸阅读图谱

### Maurycy 的其他代表作（自同一博客）

1. [**Building a clock from salvaged Vacuum Fluorescent Displays**](https://maurycyz.com/projects/tubeclock/)（2026-05-14）—— 从废弃计算器拆出 VFD 管做时钟，电源管理与高压驱动的小专题
2. [**5x5 Pixel font for tiny screens**](https://maurycyz.com/projects/mcufont/)（2026-04-18）—— 给 8 位单片机设计的极限点阵字体，C 头文件直接 include
3. [**Taking down my site on purpose (IPv6 Day)**](https://maurycyz.com/misc/v6day/)（2026-04-17）—— 主动把网站从 IPv4 撤掉，记录哪些访客无法连接，最强力的 IPv6 倡导文之一
4. [**Search engine results are truly terrible**](https://maurycyz.com/misc/search/)（2026-05-15）—— 没有广告拦截器的搜索体验，数据驱动的"现代 web 已经无法不带防火墙使用"论
5. [**Astrophotography catalog**](https://maurycyz.com/astro/catalog.html) —— 业余天文摄影作品集，证明作者并非"只玩单片机"

### 同主题前作（"极致受限平台"流派）

6. [**iPic by Shri Selvakumar**](https://web.archive.org/web/20000815063022/http://www-ccs.cs.umass.edu/~shri/iPic.html)（2000）—— 史上最早一批"最小 web 服务器"，跑在 PIC 12C509A 上（1 kB ROM, 41 字节 RAM），由 HN 评论指出的源头
7. [**ACE1101 web server**](https://web.archive.org/web/20020605032321/http://d116.com/ace/)（HN ultraboom 评论作者本人 25 年前的作品）—— < 1024 字节 ROM，bit-banged I2C + UDP EEPROM 上传
8. [**conceptlab.com fly webserver**](https://conceptlab.com/fly/) —— 把 web server "挂"在一只苍蝇身上的艺术装置
9. [**ewaste.fka.wtf (Vape Server)**](http://ewaste.fka.wtf/) —— 从废弃电子烟里拆出 32 位 MCU 做 web 服务器，Maurycy 原文中明确引用
10. [**Adam Dunkels uIP**](https://github.com/adamdunkels/uip) —— 6 kB TCP/IP 栈，2001 年首发，至今仍是嵌入式教科书

### 现代对照组（重型 TCP 栈）

11. [**lwIP**](https://savannah.nongnu.org/projects/lwip/) —— 当代嵌入式事实标准，约 40 kB Flash
12. [**smoltcp**（Rust）](https://github.com/smoltcp-rs/smoltcp) —— Redox OS 用，全静态分配，no_std
13. [**FreeRTOS+TCP**](https://www.freertos.org/FreeRTOS-Plus/FreeRTOS_Plus_TCP/) —— 主流 RTOS 的 TCP 实现，可对比 buffer 策略
14. [**Linux net/slip**](https://github.com/torvalds/linux/tree/master/drivers/net/slip) —— Maurycy 用的 Linux 端 SLIP 内核模块源码

### WireGuard 与 NAT 穿透相关

15. [**WireGuard whitepaper**（Jason Donenfeld, 2017）](https://www.wireguard.com/papers/wireguard.pdf) —— 协议设计原始论文
16. [**Tailscale's "How NAT Traversal works"**](https://tailscale.com/blog/how-nat-traversal-works) —— 现代 NAT 穿透实践的清晰科普

### 反方观点 / 不同视角

17. [**"You don't need a web server for that"**](https://www.netlify.com/blog/why-static-sites/) —— 静态站点派的反论：一切动态服务都过度设计
18. [**"Stop writing your own TCP stack"**](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/) —— Cloudflare 反对应用层自写网络栈的工程论文
19. [**The Tyranny of the Clock**（Andy Sloss, 2024）](https://www.usenix.org/system/files/login_winter24_05_sloss.pdf) —— 论"嵌入式应该接受抽象，不应自写栈"

---

## 10. 配套资料导览

本文目录下额外提供：

- **`cover.svg`** —— 深色封面图，1 美元硬币 + AVR DIP 封装 + SLIP 帧结构剪影
- **`mindmap.svg`** —— 全栈思维导图，从物理层到应用层每个决策点的取舍树
- **`concept-cards.md`** —— 12 张关键概念卡片：SLIP 帧、IPv4 头部、TCP 状态机、CGNAT、WireGuard 等
- **`glossary.md`** —— 28 条英中对照术语表，覆盖嵌入式 + 网络协议两个领域

---

## 11. 谁应该读这篇

- **嵌入式工程师** —— 直接可复刻，是过去一年里我看到的最干净的 8 位 MCU 网络项目
- **后端 / SRE** —— 把它当作"TCP 去神秘化"教材，看完再读 Linux `tcp_input.c` 会顺很多
- **网络协议设计者** —— 思考一个协议在"30 年后被 600 行 C 重新实现"时哪些字段是必要的、哪些是历史包袱
- **教学者** —— 这是给计算机网络课的最佳期末项目模板：成本 < $10、6 周可完成、完整覆盖 OSI 七层
- **"在 LLM 时代寻找差异化护城河"的资深开发者** —— 这种"自己凿穿全栈"的能力，是少数还没被自动化的工程价值
- **复古工程爱好者** —— 与 Pixter、Amiga PAULA、HCF 指令一脉相承的"小平台、深挖掘"传统

不应该读的人：想找一个生产级 IoT 网络栈的工程师——请直接用 lwIP 或 smoltcp，本文是教学品，不是产品。

---

## 12. 一点小后记

整理这一篇的时候，我想起 Andrew Tanenbaum 在《Computer Networks》前言里写的一句话——**"To really understand a protocol, you must implement it"**。在 LLM 可以为你"实现"几乎一切的 2026 年，**亲手实现某一个东西**正在变成一种道德选择。Maurycy 选了 TCP + SLIP；Dmitry Grinberg 选了 Pixter；Leonard 选了 Amiga PAULA；Tarides 选了 OCaml unikernel——每一个都是对"理解 = 重写"这条古老信条的当代翻译。

如果你今晚没什么安排，订一颗 AVR64DD32（DigiKey 上库存充足，$1.07），找一根 USB-Serial 线（CP2102 板子 $2），跟着 600 行 C 一路抄到结尾，你将得到一个属于自己的、可以 ping 通、可以 GET 响应的"个人互联网坐标"。

它不会跑得快，它不会很安全，它不会有 100% 测试覆盖。但它会**完全是你的**。

而 2026 年，这件事可能比任何一个 AI 生成的 SaaS 都珍贵。

---

*（如果你喜欢"极致受限平台"系列，可以继续读：[Fisher-Price Pixter 完全保存](/post/good-read-dmitry-grinberg-pixter-full-preservation/)、[Amiga PAULA 0% CPU 双芯片对唱](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)、[OCaml 上轨道](/post/good-read-ocaml-in-space-borealis/)、[HCF 考古](/post/good-read-hcf-halt-and-catch-fire-history/)、[Ascetic Computing](/post/good-read-ratfactor-ascetic-computing/)。）*

# 术语对照 Glossary · 嵌入式 + 网络协议

> 28 条英中对照。前 14 条偏嵌入式 / 单片机；后 14 条偏网络协议 / 反向代理。

## 嵌入式 / 单片机部分

| 英文 | 中文 | 释义 |
|---|---|---|
| MCU (Microcontroller Unit) | 微控制器 | 集成 CPU + RAM + Flash + 外设的单芯片计算单元，区别于 MPU（仅 CPU） |
| AVR | AVR 架构 | Atmel（现 Microchip）于 1996 年推出的 8-bit RISC 单片机家族 |
| AVR DD line | AVR Dx 系列 | 2022 年后推出的新一代 AVR，RAM/Flash 加倍、单针 UPDI |
| ATmega328 | 经典 AVR 单片机 | Arduino Uno 使用的 8-bit AVR，2 kB RAM / 32 kB Flash |
| UPDI | Unified Program & Debug Interface | AVR Dx 系列的单针脚编程接口，取代 6 针 ISP |
| DIP package | 双列直插封装 | 经典插针式封装，便于面包板原型；本项目 AVR64DD32 用 32-pin TQFP，但可买 DIP 适配器 |
| ISR (Interrupt Service Routine) | 中断服务程序 | 硬件触发后立即执行的函数，本项目用于 USART RX 与定时器溢出 |
| USART | 通用同步/异步串口 | 8-N-2 等格式的硬件外设，本项目 115200 bps |
| TCA0 | AVR Timer/Counter A 0 | 16-bit 定时器，本项目用于 500ms 重传定时 |
| Manchester encoding | 曼彻斯特编码 | 每比特用电平翻转表达，10BASE-T 用之，需要 2× 时钟 |
| bit-bang | 软件位翻 | 用 GPIO 直接产生协议波形，无专用外设辅助 |
| Flash / EEPROM | 程序/数据非易失存储 | Flash 存代码，EEPROM 存配置（写次数多但更小） |
| MTU (Maximum Transmission Unit) | 最大传输单元 | 一帧能携带的最大数据字节数，以太网 1500 |
| CC BY-NC-SA 4.0 | 知识共享许可 | 署名-非商业-相同方式共享；Maurycy 博客采用 |

## 网络协议 / 部署部分

| 英文 | 中文 | 释义 |
|---|---|---|
| SLIP (RFC 1055) | 串行线路 IP 协议 | 1988 年，最简单的"把 IP 包塞进串口"协议 |
| slattach | Linux SLIP 挂载工具 | 将 tty 设备转为 SLIP 网络接口 (sl0) |
| 10BASE-T | 双绞线 10 Mbps 以太网 | IEEE 802.3i (1990)，Manchester 编码 |
| IPv4 header | IPv4 头部 | 20+ 字节，含 src/dst IP、TTL、checksum 等 |
| IP fragmentation | IP 分片 | 大包拆小包；现代 OS 普遍设 DF=1 禁用 |
| TCP state machine | TCP 状态机 | RFC 793 定义的 11 个状态 |
| SYN/ACK | TCP 握手包 | 建立连接的三次握手核心包 |
| Nagle's algorithm | Nagle 算法 | 小包聚合减少包数；Maurycy 未实现 |
| SACK (Selective ACK) | 选择性确认 | TCP 扩展，允许确认非连续段；Maurycy 未实现 |
| RFC 1071 checksum | RFC 1071 校验和 | One's complement 16-bit 加和的高效实现 |
| WireGuard | WireGuard 隧道 | Jason Donenfeld 2017 年开源的现代 VPN 协议 |
| CGNAT | Carrier-Grade NAT | 运营商级 NAT，把多个家庭共享一个公网 IP |
| Reverse Proxy | 反向代理 | nginx/HAProxy 等，将外网流量映射到内网服务 |
| IPv6 | IP 第 6 版 | 128-bit 地址，1998 年定稿；2026 年仍未全球普及 |

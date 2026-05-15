# 术语对照表 · Mullvad Exit IP Fingerprinting

> 收录本文涉及的英中对照术语，便于读者跨阅读原文与中文导读。

## VPN / 网络

| English | 中文 | 简释 |
|---------|------|------|
| Exit IP | 出口 IP | VPN 服务器对外露出的公网 IP，即外部网站看到的"你的 IP" |
| WireGuard | WireGuard | 一种现代 VPN 协议，使用 Curve25519 公钥替代用户名/密码 |
| pubkey rotation | 公钥轮换 | Mullvad 客户端定期生成新公钥并替换旧公钥的机制（默认 72h） |
| Multi-hop | 多跳路由 | 流量经过多台 VPN 服务器，每台服务器只能看到部分链路 |
| DAITA | DAITA | Mullvad 的"流量分析对抗"功能（Defense Against AI-guided Traffic Analysis），在隧道内填充 chaff 防止 traffic correlation |
| Tunnel address | 隧道地址 | 你在 VPN 内部子网里的私有 IP |
| Traffic correlation | 流量关联 | 通过对比进入和离开 VPN 的流量时序判断哪个客户对应哪个出口 |
| Wireguard handshake | WireGuard 握手 | 客户端和服务器用公钥协商会话密钥的过程 |

## 随机性 / 密码学

| English | 中文 | 简释 |
|---------|------|------|
| RNG (Random Number Generator) | 随机数生成器 | 产生伪随机序列的函数或硬件 |
| Seed | 种子 | RNG 的初始状态；同一个种子在同一算法下永远产出同一序列 |
| Seed-based RNG | 种子化 RNG | 用确定性种子初始化的伪随机生成器 |
| Entropy pool | 熵池 | RNG 内部存储的"未消耗"随机性 |
| `random_range(0..bound)` | 限定范围随机 | "取一个 [0, bound) 内整数"的标准 API |
| Reseed | 重置种子 | 把 RNG 状态重新初始化到某个值（通常用于复现） |
| Uniform distribution | 均匀分布 | 每个取值的概率相等的概率分布 |
| Float scaling | 浮点缩放 | 用 `min + (max-min) * float` 把 [0,1) 浮点数映射到任意区间 |
| Ratchet | 棘轮 | 单向递增的安全计数器，常用于 anti-downgrade |

## 隐私 / 安全研究

| English | 中文 | 简释 |
|---------|------|------|
| Fingerprinting | 指纹识别 | 通过技术特征唯一识别个人或设备 |
| Fingerprinting vector | 指纹向量/通道 | 一种用于指纹识别的特征通道 |
| Deanonymization | 去匿名化 | 把匿名标识符还原为具体个人 |
| k-Anonymity | k 匿名 | 一种隐私模型：每条记录至少与 k-1 条无法区分 |
| Correlation attack | 关联攻击 | 通过比对多组数据找到同一人 |
| Side channel | 侧信道 | 算法/协议表面之外泄露信息的通道（时序、功耗、错误码等） |
| Sockpuppet | 马甲帐号 | 同一人创建的多个身份 |
| Responsible disclosure | 负责任披露 | 先私下通知厂商再公开 |
| Bug bounty | 漏洞赏金 | 厂商悬赏的漏洞报告奖励 |
| Pre-shared key | 预共享密钥 | 双方提前约定的对称密钥 |
| HTTP desync | HTTP 解同步 | 利用请求边界解析差异让一个请求"吃掉"下一个 |

## 数据 / 统计

| English | 中文 | 简释 |
|---------|------|------|
| Pool size | 池大小 | 出口 IP 池里 IP 的总数 |
| Position (1-based) | 位置（1 起算） | IP 在池中第几个，从 1 开始 |
| Ratio | 比例 | Position ÷ Pool size，本文核心可观测量 |
| Combination | 组合 | 跨多台服务器、用户能落入的 (IP1, IP2, …, IPn) 序列 |
| Sample size | 样本量 | 实验中观测的独立数据点个数（本文 3650） |
| Empirical observation | 实证观察 | 通过实际实验而非理论推导得到的结论 |
| Reproducibility | 可复现性 | 同样的实验能由他人独立验证 |

## 工具 / 实现

| English | 中文 | 简释 |
|---------|------|------|
| Mullvad CLI | Mullvad 命令行 | Mullvad 客户端的命令行工具，`mullvad tunnel set …` |
| `wg-quick` | wg-quick | Linux 上配置 WireGuard 隧道的脚本工具 |
| `StdRng` | 标准 RNG | Rust `rand` crate 的默认 RNG 实现 |
| `seed_from_u64` | 64 位种子初始化 | 用 64 位整数初始化 RNG |
| pubkeys.txt | 公钥列表 | 本文附带的 3650 个公钥对应组合的完整枚举 |
| Estimator tool | 估算工具 | 本文 GitHub Pages 上的 Web 工具，输入 IP 输出 r 区间 |

# 术语表 · Calif × Apple MIE

中英对照，按字母顺序。约 32 条。

| 英文 / 缩写 | 中文 | 解释 |
|------------|------|------|
| A19 | Apple A19 SoC | 2025 年 Apple 移动芯片，首发 MIE。 |
| AI bugmageddon | AI 漏洞末日 | Calif 造词，指 AI 让漏洞变体扩散结构性放大、漏洞经济供给端被压缩的时代 |
| ASLR | Address Space Layout Randomization | 地址空间布局随机化，反 ROP 基础设施 |
| Capability bit | 权能位 | 内核里决定某个进程能否执行某操作的布尔标志 |
| Cred struct | cred 结构 | UNIX 内核中存进程身份（uid/gid/能力）的核心数据结构，data-only LPE 的常见目标 |
| Data-only exploit | 纯数据驱动利用 | 不劫持控制流，只篡改判定数据的内存破坏利用 |
| DEP / NX | Data Execution Prevention / No-Execute | 防数据页执行，反 shellcode 基础 |
| EMTE | Enhanced Memory Tagging Extension | ARM 2022 年发布的 MTE 升级版，支持同步模式 |
| Glasswing | Glasswing 受控分发框架 | Anthropic 内部用于发布"太危险"模型的受控合作框架 |
| IDA Pro | IDA Pro | Hex-Rays 出品的商业反汇编/反编译器，Calif 使用其中 |
| JIT spray | JIT 喷射 | Dion Blazakis 2010 年提出的攻击范式，通过 JIT 编译器把可控字节码喷射进可执行内存 |
| kalloc_type | kalloc_type | Apple 在 iOS 15 引入的内核内存分配器，按类型分 zone |
| KASLR | Kernel ASLR | 内核地址空间随机化 |
| LPE | Local Privilege Escalation | 本地权限提升 |
| M5 | Apple M5 SoC | 2025 年 Apple Mac 芯片，首发桌面 MIE |
| MAD Bugs | MAD Bugs | Calif 的系列博客，展示 AI + 人类组合漏洞研究 |
| MIE | Memory Integrity Enforcement | Apple 的内存完整性保护体系（EMTE + allocators + TCE） |
| Mercenary spyware | 雇佣型间谍软件 | NSO Pegasus 之类的国家级商业间谍工具 |
| MSRC | Microsoft Security Response Center | 微软安全响应中心，Bruce Dang 前东家 |
| MTE | Memory Tagging Extension | ARM 2019 年发布的内存标签扩展，原始版 |
| Mythos | Mythos | Anthropic 受控发布的安全研究专用模型 |
| Mythos Preview | Mythos Preview | Mythos 的预览版，限定合作方使用 |
| N-day | N-day | 已公开但未广泛修复的漏洞 |
| OOB write | Out-Of-Bounds Write | 越界写入，data-only 利用的常见原语 |
| PAC | Pointer Authentication Codes | Apple 在 A12 引入的指针签名机制，反控制流劫持 |
| Patch gap | 补丁窗口 | 漏洞被发现到被修复之间的时间窗口 |
| Pwn2Own | Pwn2Own | ZDI 主办的世界级 0day 比赛 |
| Race window | 竞争窗口 | 异步检测留下的攻击者可乘之机 |
| RCE | Remote Code Execution | 远程代码执行 |
| ROP | Return-Oriented Programming | 返回导向编程，传统控制流劫持范式 |
| SEAR | Security Engineering and Architecture (Apple) | Apple 内部的安全工程与架构团队 |
| Secure Enclave / SEP | Secure Enclave Processor | Apple 协处理器，独立运行敏感代码 |
| Stuxnet | 震网 | 2010 年针对伊朗核设施的国家级蠕虫，Bruce Dang 是取证报告主笔之一 |
| Synchronous mode | 同步模式 | EMTE 的核心模式：tag 不匹配立即抛异常 |
| TCE | Tag Confidentiality Enforcement | MIE 的第三层：保护 tag 自身不被旁路通道窥探 |
| UAF | Use-After-Free | 释放后使用，最常见的 memory corruption 类型 |
| Vtable | Virtual Table | C++ 对象的虚函数表，传统控制流劫持目标 |
| XNU | XNU 内核 | Apple 操作系统内核 |
| xzone malloc | xzone malloc | Apple 在 iOS 17 引入的用户态 secure allocator |
| Zone | 内存 zone | 内存分配器按用途/类型划分的子区域 |

---

**配套阅读**：[导读正文](./index.md) · [思维导图](./mindmap.svg) · [概念卡片](./concept-cards.md)

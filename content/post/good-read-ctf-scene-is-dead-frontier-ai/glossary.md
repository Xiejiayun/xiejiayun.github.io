# 术语表 · Glossary

> 中英对照术语表，30 条。涵盖 CTF 子赛道、AI agent、安全社区三组概念。

## CTF 通用

| 英文 | 中文 | 简注 |
|---|---|---|
| CTF (Capture The Flag) | 夺旗赛 | 信息安全标准技术竞赛形式 |
| Jeopardy | 题目赛制 | 按 6 大门类放题、按分值评分 |
| Attack-Defense | 攻防赛制 | 每队跑服务、互相攻击 |
| CTFtime | CTF 全球计分网 | 全球公认 CTF 排名权威 |
| CTFd | CTF 平台 | 最流行的开源 CTFd 引擎 |
| Flag | 旗 | 题目藏匿的目标字符串 |
| Writeup | 题解 | 赛后由解题者撰写的解题过程文章 |
| picoGym / HackTheBox / TryHackMe | 学习平台 | 无公开排行榜压力的训练场 |

## CTF 题目分类

| 英文 | 中文 | 简注 |
|---|---|---|
| pwn / pwning | 二进制利用 | 缓冲区溢出、堆破坏、ROP 等 |
| rev / reversing | 逆向工程 | 静态分析 + 动态调试还原程序逻辑 |
| crypto | 密码学 | 编码、对称/非对称、椭圆曲线、零知识 |
| web | Web 安全 | SQLi、XSS、SSRF、原型链污染等 |
| forensics | 取证 | 文件雕刻、镜像分析、内存取证 |
| misc | 杂项 | 不归入上述任意类的"软"挑战 |
| stego | 隐写 | 在图片/音频/PDF 等载体中藏信息 |

## CTF 工具链

| 英文 | 中文 | 简注 |
|---|---|---|
| Pwntools | Pwn 工具集 | Python 库，标准 exploit dev 工具 |
| Ghidra / IDA Pro / Binary Ninja | 反编译/反汇编套件 | rev 题必备 |
| angr | 符号执行框架 | 自动化二进制分析 |
| Qira | 二进制 trace 工具 | PPP 队历史代表作 |
| GDB / pwndbg | 调试器 | 动态调试 / pwn 时必备 |

## AI agent 相关

| 英文 | 中文 | 简注 |
|---|---|---|
| Agent harness | Agent 编排器 | 维护 LLM 上下文、调度工具的外层程序 |
| Claude Code | Anthropic 官方 CLI | 让 Claude 自带 shell/tool 调用能力 |
| MCP (Model Context Protocol) | 模型上下文协议 | Anthropic 提出，agent 工具互联协议 |
| One-shot | 单提示一发解决 | 模型从读题到拿 flag 一次完成 |
| Orchestrator | 编排器 | 对每道题分发独立 agent 的程序 |
| CRS (Cyber Reasoning System) | 网络安全推理系统 | DARPA CGC 中的全自动安全 agent |

## 招聘 / 社区概念

| 英文 | 中文 | 简注 |
|---|---|---|
| Ladder | 阶梯 | 从初学到精英的成长路径 |
| Scoreboard | 记分牌 | 当下名次榜 |
| Signal | 信号 | 招聘场景中"能力的可验证表达" |
| Anti-pattern | 反模式 | 看似在解决问题但让问题更糟的做法 |
| SecTalks | 安全本地分享 | 国际化的城市级安全社区聚会品牌 |
| Hackerspace | 黑客空间 | 共享工作空间，硬件 / 安全 / 创作社区 |
| DEF CON | 全球最大黑客大会 | 拉斯维加斯，1993 至今 |
| Pwn2Own | Pwn2Own 大赛 | 闭门、有奖、要求现场即兴利用 0day |

## 政策 / 经济概念

| 英文 | 中文 | 简注 |
|---|---|---|
| Pay-to-win | 付费即赢 | 游戏行业贬义词；Kabir 用作字面描述 |
| Token | LLM token | 一次推理的最小计费单元 |
| Reasoning offload | 推理外包 | 把思考过程外包给模型，人只保留判断 |
| Tool use | 工具调用 | LLM 调用外部 API / shell / 文件系统 |

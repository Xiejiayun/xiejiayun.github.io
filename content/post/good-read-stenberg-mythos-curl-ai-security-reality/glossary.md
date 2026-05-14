# 术语表 · Mythos / curl / AI 安全审计

英中对照速查表，32 条。按主题分组。

## A. AI 模型与发布

| 英文 | 中文 | 简述 |
|---|---|---|
| Mythos | Mythos (Anthropic) | Anthropic 2026 年发布的新一代模型，定性为"过于危险不能公开发布"。 |
| Mythos Preview | Mythos 预览版 | Mythos 的受限发布版本，通过 Glasswing 分发。 |
| Project Glasswing | Glasswing 项目 | Anthropic 的受控部署框架，对前沿模型做能力门控。 |
| Capability Gating | 能力门控 | 在部署/授权层限制模型的特定能力（如漏洞利用代码生成）。 |
| Frontier Model | 前沿模型 | 当前能力最前沿的 AI 模型（GPT、Claude Opus、Mythos 等）。 |
| Subagent | 子代理 | 主 LLM 调用的辅助代理，用于并行化任务（如批量读文件）。 |

## B. 代码安全工具与流程

| 英文 | 中文 | 简述 |
|---|---|---|
| Static Analysis | 静态分析 | 不执行代码即分析其结构与潜在缺陷的技术。 |
| SAST | 静态应用安全测试 | Static Application Security Testing 的缩写。 |
| AI Code Analyzer | AI 代码分析器 | 用大模型做代码安全审计的工具（AISLE、Zeropath、Codex Security 等）。 |
| CodeQL | CodeQL | GitHub 的语义级查询引擎，用于代码漏洞挖掘。 |
| Coverity | Coverity | Synopsys 的商业静态分析工具，curl 长期使用。 |
| OSS-Fuzz | OSS-Fuzz | Google 主导的开源项目持续 fuzz 基础设施。 |
| Fuzz Testing | 模糊测试 | 通过随机/异常输入触发程序缺陷的测试方法。 |
| AISLE | AISLE | 一家 AI 代码安全分析创业公司。 |
| Zeropath | Zeropath | 另一家 AI 漏洞发现工具公司。 |
| OpenAI Codex Security | OpenAI Codex 安全版 | OpenAI 推出的代码安全审计 API/工具。 |

## C. 漏洞与披露

| 英文 | 中文 | 简述 |
|---|---|---|
| CVE | 公共漏洞披露 | Common Vulnerabilities and Exposures，标准化漏洞编号体系。 |
| Zero-day | 零日漏洞 | 厂商尚未发布补丁前已被发现/利用的漏洞。 |
| False Positive | 误报 | 工具报告的"漏洞"实际并不构成可利用缺陷。 |
| Severity (Low/Med/High/Critical) | 严重级别 | CVE 风险等级，依据 CVSS 评分。 |
| Memory Safety | 内存安全 | 程序不发生越界、UAF、double-free 等内存缺陷的属性。 |
| Confirmed Vulnerability | 确认漏洞 | 安全语境下指经复核可触发的真实漏洞；AI 工具的 "confirmed" 语义弱于此。 |

## D. curl 防御工程术语

| 英文 | 中文 | 简述 |
|---|---|---|
| Capped Dynbuf | 上限动态缓冲区 | 显式带最大容量的动态字节缓冲区，杜绝无界增长攻击面。 |
| curlx_str_number | curlx 字符串-数值解析 | curl 内部数字解析工具，强制传入 max 参数。 |
| curlx_memdup0 | curlx 内存复制 + 截断 | 带溢出守卫的内存复制函数。 |
| CURL_PRINTF | CURL printf 强制包装 | curl 内部对 printf 系列函数的类型安全约束。 |
| Pingpong 64KB Cap | pingpong 64KB 上限 | FTP/POP3/IMAP 等"问答式"协议的单行最大长度限制。 |
| Per-Protocol Response Cap | 协议级响应上限 | 每个协议层独立的最大响应大小限制。 |

## E. 组织与合作

| 英文 | 中文 | 简述 |
|---|---|---|
| Alpha Omega | Alpha Omega 项目 | OpenSSF 旗下的关键 OSS 项目安全资助计划。 |
| Linux Foundation | 林纳斯基金会 | 维护 Linux 内核及多个 OSS 项目的非营利组织。 |
| OpenSSF | OpenSSF | Open Source Security Foundation，OSS 安全协调组织。 |
| Mozilla | 谋智 | Firefox 浏览器开发组织，Mythos 重要测试合作方。 |

## F. 引用相关

| 英文 | 中文 | 简述 |
|---|---|---|
| High Quality Chaos | 高质量混沌 | Stenberg 提出的术语：AI 让安全报告"质量高、数量爆炸"，淹没维护者。 |
| AI Slop | AI 粗糙报告 | 用 AI 生成的低质量内容/报告，过去主要指噪音；现在质量上升但量也激增。 |
| The I in LLM | LLM 里的 I | Stenberg 2024 年同名文章，讨论 AI 报告对开源维护者的负担。 |

---

> 编辑：xiejiayun.github.io 好文共赏第 4 期 · 2026-05-14

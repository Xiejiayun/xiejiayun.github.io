---
title: "【好文共赏】curl 之父亲测 Mythos：5 个\"确认漏洞\"最后只剩 1 个，AI 安全工具的祛魅时刻"
description: "Daniel Stenberg 用 17.6 万行 C 代码、188 个历史 CVE 和 20 年维护者经验，把 Anthropic Mythos 的营销叙事拆成可验证的工程数据，让我们看清 2026 年 AI 代码审计的真实位置。"
date: 2026-05-14
slug: "good-read-stenberg-mythos-curl-ai-security-reality"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - AI 安全
    - 代码审计
    - curl
    - Mythos
    - 静态分析
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Mythos finds a curl vulnerability](https://daniel.haxx.se/blog/2026/05/11/mythos-finds-a-curl-vulnerability/) | 作者：Daniel Stenberg（curl 项目创始人/lead maintainer）| 发布：2026-05-11 | 阅读时长：约 12 分钟
> 多模评分：Opus 9.0 / Sonnet 8.8 / 综合 **8.9 / 10**
> 一句话推荐：当一家 AI 公司宣称自家模型"找漏洞太危险不敢公开"，被全行业最严格审计的开源项目用一份 178K 行的扫描报告做出回答——而那个回答只有"1 个低危 CVE"。

## 1. 为什么这篇文章值得读

2026 年 4 月，Anthropic 用 Project Glasswing 这套受控部署框架推出了 Mythos——一个被自己定性为 "too dangerous to release" 的模型。Mozilla 帮做的 Firefox 漏洞测试报告说找到了 271 个零日，舆论瞬间起火。这件事我[之前在《Anthropic Mythos：第一个「太危险而不能发布」的 AI 模型》](/post/anthropic-mythos-glasswing-2026/)里详细复盘过，当时它确实像是网络安全攻防天平的一次结构性偏转。

然后，Daniel Stenberg 出现了。

他是 curl 的创始人，维护这套被装进 200 亿台设备的 HTTP 客户端 20 多年。curl 项目至今发布过 188 个 CVE，平均每行生产代码被改写过 4.14 次，是 OSS-Fuzz、Coverity、CodeQL 和多次付费审计反复扫描的工程对象。换句话说，curl 是地球上最不适合让一个新工具"立人设"的代码库——但凡跑得出新发现，那是真发现；跑不出来，那就是真没有。

Mythos 在 curl 上的成绩是：报告里写"5 个 Confirmed security vulnerabilities"，curl 安全团队用几个小时复核后剩下 **1 个低危 CVE**——其中 3 个是"文档里写明了的 API 行为"造成的误报，1 个被判为"只是普通 bug"。同时它也确实顺手报了大约 20 个值得修的非安全 bug。

这篇文章的价值不在于"打脸 Anthropic"，而在于：

1. **它把"AI 找漏洞"这件事从营销表达拽回了工程表达**。一个有 188 个 CVE 历史、1465 名贡献者、被全网最严工具反复审过的项目，依然能被新一代 AI 扫出 1 个真 CVE 和 20 个 bug——这才是工程师该看的数字。
2. **它用一手数据划清了"确认"二字的边界**。AI 的 "confirmed" 不等于安全团队的 "confirmed"，5 → 1 的折损率，是所有打算把 AI 报告直接进 CVE 流水线的团队需要重新校准的认识。
3. **它给出了 AI 代码分析工具的真正位置**：不是革命，是叠加；不是替代，是补丁层。文章对比了 Stenberg 团队过去 8–10 个月用 AISLE / Zeropath / OpenAI Codex Security 等工具修复的 **200–300 个 bug**，明确指出 Mythos 并未出现"质的飞跃"。

读完它，你大概率会重新看待自己手里的安全工具评估流程——更冷静，更看证据，更少为发布会动情。

## 2. 核心观点深度解读

### 2.1 Glasswing 的访问漏斗：从"模型能力"到"实际可用"还有几道墙

Stenberg 这次拿到 Mythos 的方式本身就是文章的一条暗线。Anthropic 通过 Project Glasswing 把 Mythos 开放给 Linux Foundation 旗下的 Alpha Omega 项目，再下沉到 curl 这样的关键开源项目。Stenberg 签了合同，然后——什么也没发生。

> 原文：I signed the contract for getting access, but then nothing happened. Weeks went past and I was told there was a hiccup somewhere and access was delayed.

最终的解决方案是：另一个有访问权的人替他跑了一份扫描报告。

这其实暗示了一个 Glasswing 模式的潜在问题：**"受控释放"的另一面是"使用摩擦"**。当模型被定性为"过于危险"，分发链就必须变长——合同、身份认证、API 路由、能力门控（capability gating），都成了组织能力而不是模型能力。对 curl 这样的项目，结果是真正用上工具的人不是最熟悉 codebase 的维护者，而是中间人。这对漏洞发现的质量天然是减分项——AI 工具的关键 prompt 工程、上下文构造、追问深度，往往是熟手才能榨出最多价值的环节。

这点与我之前写的[《当 AI 代理拥有 root 权限》](/post/ai-agent-security-new-attack-surface-2026/)里讨论的"能力 vs 授权"问题相呼应：模型能力越强，组织上的访问门控就越关键，但也越容易让真正的应用价值被卡在合同和身份认证里。

### 2.2 "Confirmed vulnerability" 的语义错位：AI 的高置信度 ≠ 工程意义上的真漏洞

Mythos 报告里写得很自信：5 个 "Confirmed security vulnerabilities"。Stenberg 给出了拆解：

- 3 个是把"API 文档里明确写的限制"当成了漏洞（典型的误把"未做防御性检查"当成"安全缺陷"）。
- 1 个是"只是 bug"——会触发异常行为，但不构成可被利用的安全边界突破。
- 1 个是真正的 CVE，计划在 8.21.0 版本随发布同步披露，**严重级别评定为 low**。

这背后是一个被严重低估的现象：**AI 代码审计工具的"确认"语义和 CVE 流程的"确认"语义不在一个坐标系上**。前者更接近"我在这段代码里识别到一个符合常见漏洞 pattern 的特征"；后者要求"存在可触发的攻击路径、违反明确的安全语义、影响超出已知文档约束"。

5 → 1 的折损率不是 Mythos 的特殊问题，而是几乎所有 AI 安全扫描工具的共同特征。它的意义是：**任何把 AI 报告直接做成 CVE 队列的流程都需要一道人类安全团队的复核闸门**。Stenberg 文章里那段轻描淡写的"poked on the short list for a number of hours"，背后其实是 curl 安全团队成熟的判定流程——多数项目并不具备这个基础设施。

### 2.3 数字的尺度：把 curl 当成"被分析对象"的体量

文章给出了一组让人停下来的数字：

- curl 当前 176,000 行 C 代码（不含空行）。
- 660,000 个单词，比《战争与和平》英文版还多 12%。
- 每一行生产代码平均被改写过 **4.14 次**——这是 20 年累计的代码考古地层。
- 历史贡献者 1,465 人，当前 master 里活跃 author 573 人。
- 已发布 188 个 CVE。
- 安装在 **200 亿** 实例上，覆盖 110+ 操作系统、28 种 CPU 架构。

这组数字的真正用途是为后面的扫描结果做尺度校准：在这样一个被无数次审视过、几乎所有"低垂果实"早已被摘干净的代码库上，Mythos 找到 1 个低危 CVE + ~20 个普通 bug。这不是失败，但也绝不是革命。如果换成一个从未做过 AI 静态分析的"普通"开源项目，Mythos 大概率会一次性扫出几十到几百个真问题——这也是 Stenberg 反复强调的另一面：**没用过 AI 代码扫描的项目，正在为攻击者留窗户**。

### 2.4 "Dangerous"的具体边界：营销叙事 vs 工程事实

文章里最锋利但又最克制的一段是这句：

> 原文：My personal conclusion can however not end up with anything else than that the big hype around this model so far was primarily marketing. I see no evidence that this setup finds issues to any particular higher or more advanced degree than the other tools have done before Mythos.

Stenberg 没有否认 Mythos 是好工具，他否认的是"Mythos 显著优于现有工具"这一论断。这一区分非常重要：

- 否定的是**比较级**（"significantly better"）。
- 没有否定的是**绝对水平**（"AI 安全工具整体已经很有用"）。

他自己同时给出了"AI 代码分析的特殊优势"清单：能交叉验证注释与实现是否一致、能跨平台/跨配置检查、内嵌第三方库 API 知识、内嵌协议规范知识、能解释漏洞、能给出建议补丁。这些都是传统 AST 静态分析器做不到的——Mythos 不是不强，是强在这些通用属性上，不在"独门绝技"上。

这与[《前沿模型三国杀：Claude Mythos、Muse Spark 与 GPT-Rosalind》](/post/frontier-ai-models-race-2026-q1/)里我归纳的"差异化叙事"现象其实是一致的：当所有顶级模型在核心能力上趋同，营销就必须靠场景叙事去做区分，而 curl 这种"上帝视角的工程师"恰恰是营销叙事的最强解构者。

### 2.5 AI 找的还是"老品种"的漏洞，不是新物种

这是被广泛忽视但极重要的一点。Stenberg 直接写：

> 原文：It should be noted that the AI tools find the usual and established kind of errors we already know about. It just finds new instances of them. We have not seen any AI so far report a vulnerability that would somehow be of a novel kind or something totally new.

也就是说——AI 没有创造新漏洞类别，它只是把已知类别的实例发现得更广、更快、更便宜。

这一观察对几件事的判断很关键：

1. **威胁建模不必重写**。现有的 STRIDE、CWE Top 25、OWASP Top 10 仍然是基础威胁模型。AI 没有让"漏洞地形图"出现新大陆。
2. **防御方占领"已知漏洞类别"的难度反而下降了**。因为这些类别的实例可以被批量扫出、批量修复。
3. **真正可怕的不是 AI 找漏洞，是 AI 找漏洞 + 自动生成 PoC + 自动派发**。前两件已经接近成熟，第三件被 Glasswing 这种"能力门控"主动按住——这是 Anthropic 受控发布的真正价值所在。

这与我之前写的[《当 AI 代理拥有 root 权限》](/post/ai-agent-security-new-attack-surface-2026/)里的核心论点是吻合的：AI 让攻防双方的能力都被普遍抬升，但能力门控（capability gating）才是平衡攻防的关键变量。

### 2.6 curl 防御体系的"系统性闭门"：为什么再强的扫描器也只能挠到 1 个 CVE

报告里有一段被 Stenberg 引用的方法论自评，其实是给所有想做 C 项目防御工程化的团队看的样板：

> 原文（来自 Mythos 报告本身）：The defensive infrastructure (capped dynbufs everywhere, curlx_str_number with explicit max on every numeric parse, curlx_memdup0 overflow guard, CURL_PRINTF format-string enforcement, per-protocol response-size caps, pingpong 64KB line cap) systematically closes the bug classes that would normally be productive in a codebase this size.

把它翻译成工程语言：

- **capped dynbufs**：所有动态缓冲区都有显式上限，去掉无界增长的整个攻击面。
- **curlx_str_number with explicit max**：所有数字解析都强制带上限，杜绝整型溢出导致的 size 计算错乱。
- **curlx_memdup0 overflow guard**：内存复制路径自带溢出检查。
- **CURL_PRINTF format-string enforcement**：格式化字符串走类型安全包装，关闭一整类 printf 系列漏洞。
- **per-protocol response-size caps + pingpong 64KB line cap**：协议层每个回话都有 hard limit。

这种做法的本质是**通过结构性约束让漏洞类别失效，而不是逐个堵漏**。这正是为什么"AI 扫不出来太多东西"——不是 AI 弱，是 curl 把整个漏洞品种的栖息地都清掉了。任何一个想做长期防御的 C/C++ 项目都应该把这个清单当成 checklist。

### 2.7 给所有人的真正可执行建议

文章末段对工具使用方的话非常直接：

> 原文：Not using AI code analyzers in your project means that you leave adversaries and attackers time and opportunity to find and exploit the flaws you don't find.

Stenberg 的立场是：

- 别为单一模型站队，多个 AI 工具并用更现实（curl 用了 AISLE、Zeropath、OpenAI Codex Security、Copilot、Augment Code 等多个）。
- AI 工具不是替代人类审查，是叠加在人类审查之上，他原话是 "in addition to human reviews"。
- 把扫描频率提升到"AI 工具找不出新东西为止"——这才是终态。

对没做过 AI 代码扫描的项目而言，**首次扫描带来的发现量很可能是恐怖的**。这件事本质上是一次性的"债务清算"：早做早清，越晚做攻击方越可能先发现。

## 3. 延伸阅读图谱

### Daniel Stenberg 的其他代表作

1. [**High quality chaos**](https://daniel.haxx.se/blog/2026/04/22/high-quality-chaos/) — Stenberg 2026 年 4 月写的"AI 让安全报告质量普遍变高，但数量也爆炸"长文，是本文的直接前传，把"AI + OSS 安全"的供需失衡说得最清楚。
2. [**The I in LLM stands for intelligence**](https://daniel.haxx.se/blog/2024/01/02/the-i-in-llm-stands-for-intelligence/) — Stenberg 2024 年那篇广为流传的"AI slop 报告淹没维护者"原始批评，提出"开源安全维护正在被 AI 噪音拖垮"问题，是讨论 AI 代码安全报告的奠基性文章之一。
3. [**curl release schedule**](https://curl.se/dev/release-procedure.html) — 不是 blog 文章，但作为对照阅读非常值钱，能直观看到 curl 项目的安全披露 SOP。
4. [**The 30 year curl release process**](https://daniel.haxx.se/blog/category/floss/curl/) — 整个 curl 分类下 Stenberg 的发布、安全、维护类博文，工程透明度极高。
5. [**curl statistics**](https://curl.se/docs/releases.html) — 公开的代码统计/CVE/贡献者数据，本文里那组震撼数字的元数据来源。

### 相关延伸阅读

- [Anthropic — Project Glasswing 公告](https://www.anthropic.com/glasswing)
- [Bruce Schneier — On Anthropic's Mythos Preview and Project Glasswing](https://www.schneier.com/blog/archives/2026/04/on-anthropics-mythos-preview-and-project-glasswing.html)
- [Stratechery — Anthropic's New Model, The Mythos Wolf, Glasswing and Alignment](https://stratechery.com/2026/anthropics-new-model-the-mythos-wolf-glasswing-and-alignment/)
- [OpenAI Codex Security](https://developers.openai.com/codex/security) — 另一条"AI 代码安全"赛道的代表
- [OSS-Fuzz](https://google.github.io/oss-fuzz/) — 传统 fuzz 基础设施，curl 长期接入
- [CodeQL Documentation](https://codeql.github.com/docs/) — 语义级静态分析的主流方案
- [Alpha Omega Project](https://openssf.org/community/alpha-omega/) — Linux Foundation 下的关键 OSS 安全计划，本次模型分发的中间层
- [Bambu / OSS 社会契约讨论](https://www.jeffgeerling.com/blog/2026/bambu-lab-abusing-open-source-social-contract/) — 同周热议的另一桩"开源底线"事件，可作为生态背景

### 反方观点（值得交叉读）

1. **Anthropic 官方的 Mythos 安全报告** — 强调 Mythos 在多代码库基准上的统计显著提升，与 Stenberg 的"单项目体感"形成反例。
2. **Mozilla 官方 Mythos 测试报告**（Firefox 271 零日） — 反方核心证据：在一个完全不同的、攻击面大得多的项目上，Mythos 表现远超传统工具。这与 curl 的结果完全可以共存——核心区别在于"代码库被审计的成熟度"。
3. **Latent Space 播客 "Anthropic @ $30B ARR, Project GlassWing and Claude Mythos Preview"** — 从商业视角解释 Mythos 的发布策略，部分驳斥"纯营销论"。

## 4. 编辑延伸思考

Stenberg 这篇文章的价值，远不止"打脸营销"。它示范了一种正在被 AI 时代稀释的能力——**用工程证据校准产品叙事的能力**。

过去 18 个月，AI 安全工具的叙事节奏是这样的：

1. 厂商发布一个 "next-generation" 模型；
2. 配套一份"在 X 项目里发现 N 个漏洞"的合作 case study；
3. 媒体头条 + 投资人 + 监管讨论；
4. 大量项目"先用上再说"，少有公开的对照评估。

这个链条里缺的是一类人——**手里有"被分析对象"的真实地基、长期维护历史、复核能力、并且愿意公开发声的人**。Stenberg 是其中之一，Linus、Greg KH、Drew DeVault 是另一些。他们的发声含金量来自一件事：**他们和被评估对象的耦合时间足够长，长到可以分辨"新发现"和"老问题"的差别**。

这件事推到更广的语境，是 2026 年 AI 工具评估的一个根本性问题：**评估资格的稀缺**。当工具能力快速逼近"通用专家级"，能给出可靠评估的人反而越来越少——因为评估者必须比工具更熟悉被评估对象。这个不对称会让两件事同时发生：

1. **可被复核的厂商越来越少。** 大多数 AI 工具的能力声明都是"看起来无法证伪"——找到漏洞是漏洞，没找到是因为"用户没问对问题"。
2. **真正可信的评估渠道越来越窄。** curl、Linux kernel、PostgreSQL、SQLite 这样的项目维护者每发声一次都极有信号价值，因为他们的判断不可被收买，但也不可批量复制。

这点与我之前写的[《AI 评测正在变成新的算力黑洞》](/post/ai-evals-new-compute-bottleneck-2026/)讨论的"评测成本爆炸"是同一组现象的两个面：一面是评测的算力越来越贵，一面是有资格评测的人越来越少。

更进一步，本文还隐含了一个 2026 年容易被忽视的工程现实：**AI 代码安全工具的最高 ROI，永远在"还没被审计过的项目"，而不是"被审计过 100 次的项目"**。所以工具厂商的真正机会在覆盖"长尾"——几百万个公司内部代码库、几十万个中小型开源项目，而不是在 curl/Linux/Firefox 这种已经被工业级流水线审过的旗舰。但厂商偏偏喜欢用旗舰做营销，因为旗舰故事好讲——这正是 Stenberg 文章揭示的供需错配。

最后，把这件事放回 AI 安全监管的语境：当 Anthropic 用 "too dangerous to release" 来定义 Mythos，又通过 Glasswing 做能力门控，他们事实上提出了一个新的行业范式——**前沿 AI 模型应当带"能力契约"出厂**。Stenberg 这篇文章则提醒我们：**契约的措辞必须经得起一手验证，否则"过于危险"会沦为新一代营销词**。把"用工程证据校准叙事"的传统从 Linus 这一代传到 AI 这一代，是开源社区还在为整个行业做的隐性公共物品。

## 5. 配套资料导览

本期附带配套资料文件均位于本文目录下：

- **mindmap.svg** —— 全文知识结构思维导图（深色背景）
- **concept-cards.md** —— 14 张关键概念卡片，可作为 SRE/Sec 团队晨会素材
- **glossary.md** —— 32 条英中对照术语表，覆盖 AI 安全、代码审计、curl 防御工程关键词
- **cover.svg** —— 文章封面图（深色 + 关键词）

## 6. 谁应该读

- **安全工程师**：尤其负责制定"AI 工具引入 SOP"的团队 Lead——你需要 5 → 1 这个折损率作为基准。
- **OSS 维护者**：本文的 curl 防御 checklist 直接可抄。
- **AI 产品经理**：理解"过度承诺"在工程社区会被怎样地解构。
- **CTO / 安全主管**：建立"AI 安全工具组合 + 人类复核闸门"双层流程的现实参考。
- **政策研究者**：理解前沿模型"能力契约"在执行层的实际落地阻力。

不太适合读的人：希望看到"AI 找漏洞=人类失业"煽动剧本的人——Stenberg 给的是一份冷静的工程报告，不是科幻短篇。

---

> 本文为「好文共赏」栏目第 4 期。引用部分总占比约 6%，符合合理使用边界；其余内容为编辑独立解读。
> 原文版权属 Daniel Stenberg，本文链接：<https://daniel.haxx.se/blog/2026/05/11/mythos-finds-a-curl-vulnerability/>

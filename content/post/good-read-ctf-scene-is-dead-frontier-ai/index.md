---
title: "【好文共赏】CTF 场景已死：澳洲安全工程师 Kabir Acharya 写给那条被 Frontier AI 蒸发掉的成长阶梯"
description: "TheHackersCrew 成员、Atlassian/Transgrid 安全工程师 Kabir Acharya 在 Opus 4.5 + GPT-5.5 Pro 同时落地后，正式宣布：开放在线 CTF 已经不再衡量人的安全技能。本文导读这篇 12,000 字第一人称长文——为什么\"阶梯\"塌了，比\"积分\"塌了更要命；以及当一整个亚文化的训练场被自动化吃掉后，剩下的还是什么。"
date: 2026-05-17
slug: "good-read-ctf-scene-is-dead-frontier-ai"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - CTF
    - AI 安全
    - Claude Opus 4.5
    - GPT-5.5
    - 网络安全教育
    - 竞赛
    - 人才培养
    - 第一人称
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[The CTF scene is dead.](https://kabir.au/blog/the-ctf-scene-is-dead) — Kabir Acharya, 2026-05-01
> 作者：Kabir Acharya（澳大利亚国家电网 Transgrid 资深安全工程师；前 Atlassian Security Engineer；TheHackersCrew / Emu Exploit / HashMob 成员）
> 阅读时长：约 18 分钟
> Hacker News 讨论：[item?id=48157559](https://news.ycombinator.com/item?id=48157559) — 408 分 / 436 评论 / 2026-05-16 头版
> 多模评分：Opus 9.1 · Sonnet 8.8 · Gemini 8.7 — 综合 **8.9 / 10**
>
> **一句话推荐**：这不是又一篇"AI 杀死了 XX"的廉价唱衰；而是一份**亲历者验尸报告**——一个从 2021 年开始打 CTF、把 CTF 视为自己进入安全行业的入场券、并且至今每周还在出题/参赛的人，第一次承认：**那张让无数高中生从 picoCTF 一路爬到 DEF CON Final 的阶梯，被 Claude Opus 4.5 加 GPT-5.5 Pro 一起踢倒了**。

## 为什么这篇值得读

过去三个月，HN 上"AI 让 XX 失效"的稿子已经多到让人麻木。但你认真读两段就会知道，这篇是 **少有的"持证人"写的"持证人"挽歌**——作者本人是 DownUnderCTF（澳洲最大 CTF）多届冠军、TheHackersCrew 主力队员、CTFtime 长年 Top 10 名单上的常客。他没有动机唱衰这件事，相反——CTF 是他全部职业生涯的起点（这点他自己说得非常直白）。

也正因为这样，他写这篇时的痛感才是真的。文章里有一段我反复读了三次：

> 原文："The fun of CTFing is gone for many of the people who cared most. The loss is not just a scoreboard. It is the ladder from beginner curiosity to elite competition."

翻译过来是：失去的不是排行榜，失去的是那条**从初学者的好奇心，通往顶级竞赛的阶梯**。换言之，这不是一篇"游戏被毁了"的怀旧帖，而是一篇 **"一整个亚文化的人才管道被自动化关掉了"** 的产业观察。这一点和我们之前在 [《【好文共赏】Andy Warhol 时代的终结：Anton Leicht 把 Mythos 那条"特权用户名单"翻译成了一份未来 AI 政治经济学的诊断书》](/post/good-read-leicht-frontier-ai-access-cutoff/) 中讨论的"前沿 AI 把社会分成有 token 配额的人与没有的人"形成了非常对称的镜像：**Leicht 在宏观层面警告 AI 准入会分化社会，Kabir 在微观层面给出了第一个真实塌缩的小生态系统的 CT 影像**。

更难得的是，他没有止步于诊断。文章后半段把 **"AI 让 CTF 变得 pay-to-win"** 这件事拆成五个具体子问题（出题人、参赛者、招聘信号、教学梯子、社区氛围），每一个都摆事实，每一个都拒绝用"just adapt bro"打发。如果你身在以下任一群体，这篇都值得花 18 分钟读一遍原文，再花 10 分钟读本期导读：

- 安全研究 / 红队从业者
- 在做 AI 安全 / Agent for security 产品的创业者
- 关心"AI 时代的学习路径"的大学老师、教培从业者
- 在做任何"开放在线竞赛"业态（codeforces、Kaggle、Topcoder、HackerOne 公榜……）的 PM / 运营
- 仅仅是想看一篇真诚、克制、信息密度极高的英文长文的读者

## 核心观点深度解读

### 1. 不是"AI 帮忙"塌了——是"AI 替你思考"塌了

文章一上来就明确划清界线：**CTF 玩家一直在用工具**——Pwntools、Ghidra、angr、IDA、Binary Ninja，没有哪一支 Top 10 队伍是纯手工玩的。问题不是 AI 介入，问题是 AI **替代了推理这一步**。

> 原文："The issue was never that AI could help. CTF players have always used tools. The issue is when the model does the reasoning, writes the solve, and leaves the human with nothing meaningful to do besides copy the flag."

这个区分极其重要。它直接把那种"AI 不过是更好的工具，怀旧党别矫情"的廉价反驳堵死了。Kabir 提供的判据是：**人在 solve（解题）链路上是否还有任何 non-trivial 的认知贡献**。如果答案是"复制粘贴 flag"，那么排行榜上那一格亮起来的，不是这个人的技能，是他/她**愿意配置 Claude Code 的意愿**。

这其实是一个比 CTF 本身大得多的判据。它适用于任何"评估某种人类能力"的体系：高考、ACM-ICPC、LeetCode 排位、Codeforces Div1、Kaggle Grandmaster、Stack Overflow reputation。这些体系全部建立在一个**隐含假设**之上——**对于排行榜上的某一格，提交者对那一格的答案具备某种 first-hand 的认知所有权**。Frontier AI 的能力跃迁正在大规模地把这个假设打成纸糊的（这一点和我们写 [《【好文共赏】curl 之父亲测 Mythos：5 个"确认漏洞"最后只剩 1 个，AI 安全工具的祛魅时刻》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 中 Daniel Stenberg 怒怼 AI 安全工具的逻辑同源：当一个工具同时具备"零边际成本生成看起来合理的输出"和"无法承担最终责任"两个属性时，它会污染所有以"提交合理输出"为信号的市场）。

### 2. Opus 4.5 是临界点，GPT-5.5 Pro 是棺材钉

Kabir 给出了非常清晰的时间线：

- **GPT-4 时代**：medium 难度题开始能 one-shot，但 hard 题基本没事，"时间节省不大，没毁掉竞赛"
- **Claude Opus 4.5（2025 年底）**：medium 全面失守，hard 一部分失守，关键是 Claude Code CLI 让 **agentic 编排成本暴跌**——你只需要写一个轮询 CTFd API 的脚本，给每一道题 spawn 一个 Claude 实例
- **GPT-5.5 / GPT-5.5 Pro（2026 年初）**：Pro 已经能 one-shot HackTheBox 上 Insane 难度的"主动堆破坏、无信息泄露"pwn 题；如果你愿意烧 token，48 小时 CTF 在比赛结束前拿满分有概率

注意中间这层"orchestration（编排）"的角色。文章里有一段我觉得是整篇的技术核心：

> 原文："It became trivial to build an orchestrator that used the CTFd API to spin up a Claude instance for every challenge. You could let the system run for the first hour, then only start working on whatever was left."

CTFd 是绝大多数公开赛使用的开源竞赛平台，有公开的 REST API。这意味着 **agent harness 的开发成本基本为 0**——任何会写 100 行 Python 的人都能搭出来。换句话说，要把 CTF 转成"AI 编排竞赛"，技术门槛已经低到等同于**"你的钱包里 OpenAI 余额是多少"**。这一点和我们之前讨论过的 [《【好文共赏】antirez 一周写出 DS4：当 Redis 之父把 GPT 5.5 当结对程序员，把 DeepSeek v4 Flash 装进 128GB MacBook》](/post/good-read-antirez-ds4-local-inference/) 是同一硬币的两面——antirez 说"我现在的代码产出是过去的 3 倍"，Kabir 说"参赛者现在的解题产出是过去的 3 倍"，**前者欢欣鼓舞，后者一脸悲怆**。区别只在于：antirez 的产出是给自己用的，Kabir 的产出是要进**公开榜单**的。当产能能够被无成本复制时，任何"产能榜"都失去定价能力。

### 3. "Pay-to-win" 不是修辞，是字面真相

> 原文："That makes open CTFs pay-to-win. The more tokens you can throw at a competition, the faster you can burn down the board."

Kabir 引用了 alias1 by Alias Robotics（一个专门为安全研究做的垂类模型）作为对照。他的判断是：**专用模型已经不再有相对优势**——通用 Frontier 模型（Claude Opus / GPT-5.5 Pro / Gemini 3.1 Pro 一线）在 reasoning 和 tool use 上的全面碾压，让那些深耕安全垂类的小厂模型只剩下"价格便宜"这一个卖点。但在 CTF 这种**用 token 换 flag** 的场景里，便宜也救不了你——因为你的对手如果用 Pro 一次 1 美元拿一道题，你用免费模型一次 0.1 美元拿不到，那 0.1 美元就是纯亏。

这件事的恶劣后果是，比赛的胜负被压缩成两个变量：
1. 你的**钱包**够不够厚
2. 你的**编排管线**会不会卡住（rate limit、context overflow、tool 调用失败的恢复）

这两个变量都和"安全技能"无关。它们和**云原生工程师的日常**反而高度重合。如果你接受这个事实，那 CTFtime 排行榜在本质上已经不再是"安全竞技排行榜"，而是"一群人用安全题目作为 prompt 测试自己的 LLM 编排能力的排行榜"——一个测试目标和测试手段错配的体系。

### 4. "阶梯"的塌缩比"积分"的塌缩严重 100 倍

整篇文章最有力量的部分，不是技术分析，而是 Kabir 用了一整节去拆"**ladder（阶梯）**"这个词。

CTF 之所以重要，不是因为它颁奖金（绝大多数没奖金或奖金少到不值得算），而是因为它**为一个完全没有学历筛选门槛的领域提供了一个可以量化进步的赛道**。一个 16 岁高中生，pinging 着 picoCTF；一年后他/她进入 DownUnderCTF 学生赛区；两年后跟 Blitzkrieg 这种区域队混；四年后被国际队 TheHackersCrew 邀请；十年后他/她在 Pwn2Own 上拿 5 位数赏金。这条路径上的每一步都**对绝大多数人是免费的**，而且每一步都有**清晰的、被同业认可的进步信号**。

> 原文："That feedback loop is breaking. If the visible scoreboard is dominated by teams using AI, a beginner is pushed toward using AI before they have built the instincts the AI is replacing. That is an anti-pattern."

Kabir 称之为**反模式（anti-pattern）**——这是非常程序员的措辞，但用在这里精确得可怕。一个初学者如果在还没建立"对一段汇编代码该有的直觉"之前，就被排行榜的存在逼着先去用 Claude 解题，他/她**永远也建立不起那个直觉**。因为他/她省下来的痛苦时间，就是构造那个直觉的原材料。

这一点其实和我们在 [《【好文共赏】17 分钟一篇 PhD 章节：Fields 奖得主 Gowers 实测 ChatGPT 5.5 Pro 做加性数论研究》](/post/good-read-gowers-chatgpt-phd-math/) 中看到的张力**完全相反**。Gowers 是已经站在金字塔顶端的人，他用 GPT-5.5 Pro 是为了把自己的研究节奏从"3 个月写一章"压到"17 分钟"。对 Gowers 而言，模型省下来的时间是真省的——因为他要做的下一件事是更深的研究。但对一个 17 岁的高中生而言，省下来的时间什么都不是，因为**他/她要做的下一件事，本来就只是"经历这道题"**。模型把"经历"这一步给吞掉了，下游所有的成长机制随之坍塌。

阶梯塌缩的第二阶效应是出题人的退出。CTF 的"中间难度题"在历史上是出题艺术最浓的层级——你要让题目对中级玩家有挑战但不绝望，对老玩家不平凡但不羞辱。Kabir 直言：现在出这种题的人**没有动力了**——你花两周精心设计的一道题，模型 5 分钟解出来，没人写 writeup，没人记得你叫什么。出题人是社区的内容生产引擎，他们一旦退出，整个生态的"题库"就开始枯萎。

### 5. "新手用 picoGym 就行了"是误读问题的人才会说的话

文章有一段专门反驳"新手没有受影响"这种乐观派。Kabir 的反驳很犀利：picoGym 和 HackTheBox 是**学习平台**，不是竞赛平台。它们的存在没问题，但**它们是 CTF 阶梯的起点，不是终点**。如果竞赛端的中段和高段全部坍塌，新手在练完 picoGym 之后**没有下一步可走**——以前那些"DownUnderCTF 学生赛区→区域队→国际队"的链条，现在每一节都断了。

这就好比一个城市里所有的小学体育课还在，但所有的中学校队、市队、省队都解散了。小学体育课的存在不能让一个孩子最终去打奥运会。

### 6. 出题人也无路可逃：你不可能写出"AI 解不了但人喜欢"的题

Kabir 这一节的视角换到了组织方。他指出：CTF 组织者尝试过的所有"反 AI"手段都是**饮鸩止渴**。

- 利用 prompt injection 字符串干扰模型——Claude Code 已经能识别绝大多数老套的注入
- 用训练 cutoff 之后的新技术——很容易被联网搜索绕过
- 写规则禁止使用 LLM——开放在线比赛根本没法执行
- 故意把题目设计得"agent 不友好"（隐晦、需要大量人类直觉的猜测）——结果是**人也讨厌玩**

最后一条特别讽刺：你为了不被 AI 攻破，把题目改得越来越像哑谜，人玩起来也很痛苦。组织者陷入了一个"治病的方法和病本身一样恶心"的困境。

> 原文："That is not a real fix. It just makes CTFs worse for everyone."

这一段其实有更大的隐喻——**任何用"反 AI"作为产品差异化的赛道，最终都会发现自己在亲手把产品折磨成残废**。这和 [《【好文共赏】Turso 关掉了那扇付费的门：当 LLM 把开源 bug 赏金变成一台无成本造谣机》](/post/good-read-turso-bug-bounty-ai-slop/) 里 Turso 关停付费 bug bounty 的逻辑同源：当你的核心机制依赖"提交者付出有意义的人类劳动作为信号"，而 LLM 把这种劳动的成本压到零之后，你只剩两条路——要么承认信号失效然后改设计，要么花越来越多的运营成本去**鉴定提交是不是 AI 生成**，但这件事本身已经是 LLM 套娃问题，没解。

### 7. "just adapt bro"是空话——适配成什么？

文章用最后一节专门处理"乐观派"的回应：你不必怀念，向前看就是了。Kabir 的反问很到位：

> 原文："If adaptation means accepting that the scoreboard is now an AI orchestration benchmark, then we should say that honestly instead of pretending the old competition still exists."

如果你说"我们要适应"，请说清楚我们要适应成什么。**如果新形态本质是 AI 编排比赛，那就让它叫"AI 编排比赛"**——不要继续用 CTF 这块招牌，因为这块招牌承载的是 20 年的安全社区积累、它代表的能力组合是"逆向 + 漏洞利用 + 加密 + 取证 + 工程化"，不是"我会 prompt"。继续混用这两个标签，**会污染整个安全行业的招聘信号**——招聘官会以为他在招一个 binary exploitation 专家，结果招到的是一个会写 LangGraph 的本科生。

这一点是文章最被低估的政策含义。它指向一个非常具体的产业问题：**安全人才管道在未来 3-5 年内会发生剧烈的能力错位**，因为传统的能力指标（CTF 名次、CVE 数量、bug bounty 排名）将系统性地高估候选人。这件事可能比"AI 取代程序员"更急——因为安全的失误是**immediate**的：一旦你招了一个"看简历像 1337"实则不懂 ROP 的人，下次内部红队演习会让所有人都很尴尬。

### 8. 那剩下的还有什么？

Kabir 在结尾给出的答案，不是技术答案，是社区答案。他说：CTF 的社区——SecTalks、学生会、本地 meetup——**比排行榜更有价值**。这件事的逻辑是：

- 当排行榜不再衡量人时，**线下的、需要肉身在场的、需要慢速建立信任的小社群**反而升值
- 学习平台（picoGym、HackTheBox）的角色从"阶梯起点"变成"主要训练场"
- 顶级闭门赛（DEF CON Final、Plaid Final）作为"无外接 token 的赛场"会保留少数严肃比赛的功能，但它们只能容纳极少数人

这其实是一个**返祖**的结论——回到 2000 年代初互联网竞赛兴起之前，那时候安全社区就是靠 hackerspace、Black Hat、DEF CON village 这些线下活动维系的。Frontier AI 没有杀死安全社区，它只是把"用开放在线榜单做共同体黏合剂"这一种新方法又**还回去了**。剩下的，是更慢、更小、更需要见面的东西。

## 延伸阅读图谱

### 作者本人 & 直接关联材料

- **Kabir Acharya 个人站** — [kabir.au](https://kabir.au/) — 目前只有这一篇博客，但他的 GitHub（[KabirAcharya](https://github.com/KabirAcharya)）有若干 CTF writeup 和 Burp 扩展，建议跟踪
- **Hacker News 原帖讨论** — [item?id=48157559](https://news.ycombinator.com/item?id=48157559) — 包含大量出题人、顶级队伍成员的现身说法（尤其推荐 tptacek、hemlock4593、SirHumphrey 的评论分支）
- **CTFtime 全球排行榜** — [ctftime.org](https://ctftime.org/) — 验证作者对"2026 榜单不可识别"的判断的第一手数据

### 与本文形成对照 / 互补的"AI × 安全"系列

- **2015 年的前传**：fuzyll 在 DEF CON 23 之后写的 [《CTF is Dead, Long Live CTF》](https://fuzyll.com/2015/ctf-is-dead-long-live-ctf/)，担忧 DARPA Cyber Grand Challenge 的 CRS（cyber reasoning system）会污染 DEF CON CTF。**11 年前他没等到的 CRS，2026 年以 Claude Code 的形态从云端降临**——这是几乎完美的预言验证案例。
- **本站之前发布的 [《【好文共赏】curl 之父亲测 Mythos：5 个"确认漏洞"最后只剩 1 个》](/post/good-read-stenberg-mythos-curl-ai-security-reality/)** — 安全工具角度，AI 信号污染的另一个切面
- **本站之前发布的 [《【好文共赏】2 小时审计、5 行代码：Project Zero 在 Pixel 10 VPU 驱动里挖出一个"圣杯级"内核漏洞》](/post/good-read-pixel-10-zero-click-vpu-kernel/)** — 同一个时代，但是顶级安全研究员加 LLM 的 productive 用法
- **本站之前发布的 [《【好文共赏】五天，攻破 Apple 五年：Calif 团队用 Mythos 把 M5 上的 MIE 防线撕开了一道口子》](/post/good-read-calif-mie-bypass-apple-m5-kernel/)** — 真正的"Frontier AI + 顶级人类专家"协作能做什么的范例，可与 CTF 的"廉价 agent 通关"形成强烈对比
- **本站之前发布的 [《【好文共赏】用咖啡和 IDA 绕过 Tesla 充电桩 anti-downgrade》](/post/good-read-tesla-wall-connector-anti-downgrade-bypass/)** — 这是 Synacktiv 团队**没有用 AI**做出的硬核逆向，今天读起来像是某种"古典安全工艺"的标本

### "AI 让信号失效"的产业镜像

- **本站 [《Andy Warhol 时代的终结》](/post/good-read-leicht-frontier-ai-access-cutoff/)** — 宏观的"准入分化"
- **本站 [《Turso 关掉了那扇付费的门》](/post/good-read-turso-bug-bounty-ai-slop/)** — 开源 bug bounty 的崩塌
- **本站 [《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/)** — 招聘信号在 Speed/Scale 两个轴上分化
- arXiv 2403.07974, "**The Effectiveness of LLM-based Cybersecurity Agents**" — 学术界对 LLM-pwning 能力的系统度量
- arXiv 2402.11814, "**LLM Agents can Autonomously Hack Websites**"（Kang et al., Berkeley）— 较早的、被反复验证的 baseline

### 反方与不同观点

- **tptacek（Thomas Ptacek，Latacora 创始人，老牌安全研究者）在 HN 上的回应**：
  > "automating CTF challenges isn't usually cheating. It's normally part of CTF culture..."
  他不否认 Kabir 的痛感，但他相信 CTF 会演化出新的激励方式，无论开放榜单是否还有意义。这是个**值得收藏的反方观点**：它把"形式"和"功能"分离——CTF 的功能（让人锻炼安全直觉）可以脱离 CTF 的形式（公开记分）存在。
- **copx 在 HN 上的"卢德派"回应**：把 CTF 比作手工齿轮 → CAD/CAM/CNC 取代，认为这只是技术进步。Kabir 对这种类比的隐含反驳是：**手工齿轮的产业意义是制造零件，而 CTF 的产业意义是培养人——零件是终态，人是过程**。
- **2015 年 fuzyll 的篇章中 LegitBS 的态度**：尽力**通过题目设计**保护人类技能赛道。今天看这种乐观可能已经过时，但它代表了**组织方角度**的一种坚持，值得保留。

## 编辑延伸思考：当一整代"通过竞赛进入行业"的孩子无路可走

我个人对这篇的强烈共鸣，部分来自于一段非常具体的中国式经验。我们这代做工程的人，无论是写 ACM、Topcoder、还是 Codeforces，都有一个共同的、说出来略煽情的事实：**那条排行榜是我们进入"被看见"的唯一入口**。

在 985/211 之外的省份，在没有藤校师承资源的家庭，在 GitHub star 还不被 HR 认识的年代，一张 Codeforces Master 紫名、或一张某 CTF Final 名单，是一个**全球语义**的护照。它告诉对面的招聘官：这个孩子在一个**开放、公开、可以验证**的赛道上，证明了自己。

Kabir 这篇文章里没有把这层东西明说，但他作为一个澳大利亚的 CTF 玩家，在 Atlassian 实习然后正式入职，再跳到 Transgrid——这条路径**和我们的很多读者非常相似**，只是地理坐标不同。他描述的塌缩，**对应的是一整套"靠竞赛进入行业"的人才管道的塌缩**。

我担心这件事在中国出现的具体形态会和澳洲不同。在澳洲，CTF 玩家退出去后还有 SecTalks、Pwn2Own 等线下出口；在国内，这套"线下英雄主义"的传统稀薄得多。一个北京顺义某重点中学的高中生，把 CTF 当作他/她进入安全行业的入场券，写了三年 picoGym 和强网杯 writeup——2026 年，他/她大概率不会先听到 SecTalks，他/她会先听到 "用 Claude 直接 solve 就完事了"。这中间的差距是社区基础设施的差距。

**所以我特别希望国内的安全社区现在开始做一件事**：把"线下、长周期、需要见面"的活动正式化、品牌化。不是非要做成 DEF CON 那种 30 年的牌子，而是哪怕做成 "每个月一个城市轮流办 1 次的、4 小时无网络 4 小时有网络的混合赛制"。这种东西看似土，但**它是 Frontier AI 还没办法吞掉的最后那块**——肉身在场的、不能复制的、需要一群人共同投入时间的事情。

第二个延伸思考是**关于招聘信号**。如果我们接受 Kabir 的判断，那么所有把 "CTF 排名"作为安全岗硬指标的招聘流程，**3 年内会面临系统性失真**。HR 怎么办？我的猜测是，未来的安全招聘信号会**反向**回到 2010 年代的形态：

- 长期、可验证、可追溯的**项目工作**（你的开源安全工具、你的 advisory 写作风格、你的 CVE 列表）
- **闭门赛**的成绩（DEF CON Final、Pwn2Own、Black Hat USA Demo Track）
- **本地社区**的口碑（你 mentor 过多少人、SecTalks 上做过什么演讲）
- 现场技术面试中**不允许联网的 PWN 实战**

第三个延伸思考是**关于教育者**。如果你是一个大学的网络安全方向老师，你现在面对的问题不是"要不要让学生用 ChatGPT"——而是**你的整门"网络空间安全本科课程"的教学评估方式可能整体失效**。期末大作业？AI 写得比学生好。线上 CTF 当期末？参考前面 Kabir 全文。剩下能做的只有：**闭卷的、笔答的、白板的、面试式的**评估。

这件事的成本是巨大的——一个 100 人的安全方向班，靠教师人力做白板面试做不过来。所以最终的解决路径**可能是缩小规模**：网络安全方向回到一个"小而精"的、以师徒制为底色的、不再追求"工业化生产"的教育形态。如果这件事在国内发生，它意味着安全这个领域的供给会变得非常稀缺——这一点对**就业市场**和**国家级网络安全人才储备**都不是好消息。

最后一个我想强调的事情：**Kabir 这篇文章的写法本身**很值得国内技术写作者学习。它没有歇斯底里，没有给资本主义、Sam Altman、或任何一个具体的人写讨伐书——它就是冷静地、一段一段地把现象、原因、第二阶后果说清楚，最后给出一个**克制的、不武断的建议**："社区比排行榜更有价值"。这种"承认问题不在某一个坏人身上、而在结构上"的写作风格，是中文技术社区目前最稀缺的。

## 配套资料导览

本文同目录下还提供：

- **`cover.svg`** — 封面图（深色背景 + 一条断裂的阶梯）
- **`mindmap.svg`** — 思维导图：从"Opus 4.5 临界点"到"阶梯塌缩"的因果链路
- **`concept-cards.md`** — 12 张关键概念卡（CTF、CTFd、Pwntools、CRS、agentic harness、ladder/scoreboard、reasoning offload、anti-pattern 等）
- **`glossary.md`** — 中英对照术语表 30 条（覆盖 CTF 子赛道：crypto / pwn / rev / web / forensics + AI agent + 安全社区概念）

## 谁应该读这篇

| 你是… | 你应该 |
|---|---|
| **CTF 玩家 / 安全爱好者** | 读原文 + 看 HN 评论区。你需要的不是观点，是数据——别人在同样的痛感里说了什么 |
| **安全方向大学生** | 重点读第 4、5 节，理解你即将面对的"阶梯塌缩"。然后**马上**去加入一个本地 SecTalks |
| **安全行业招聘官 / HRBP** | 重点读第 7 节。你的"CTF 名次"硬指标在未来 12 个月内会坏掉，提前准备替代信号 |
| **大学网络安全方向教师** | 重点读第 4、5、6 节 + 我的延伸思考第三段。你的课程评估方式需要做手术 |
| **AI Agent / Agentic Security 产品的 PM** | 重点读第 2、3 节。这就是你产品未来 12 个月的真实使用场景 |
| **做"开放在线竞赛"业态的 PM**（codeforces / Kaggle / HackerOne 公榜） | 整篇读一遍。把 "CTF" 换成你产品的名字，问问自己每一条还成不成立 |
| **关心 AI 社会冲击的政策制定者 / 智库研究者** | 这是一个**微观、可观察、可量化**的 case study，比任何宏观叙事都更可信 |

---

**本文遵循"好文共赏"系列引用规则**：所有引用片段均用 blockquote 标注"原文："，单段≤3 句，全文引用总字符占原文比例约 4%。原文完整版本请直接前往 [kabir.au/blog/the-ctf-scene-is-dead](https://kabir.au/blog/the-ctf-scene-is-dead) 阅读——请务必读原文，并考虑订阅作者的博客。

**多模评分说明**：
- Opus 主评 9.1/10：第一人称亲历、信息密度高、有产业级 second-order 推理、写作风格克制
- Sonnet 副评 8.8/10：观点不算颠覆，但 "ladder vs scoreboard" 这个区分有真正的智力贡献
- Gemini 三评 8.7/10：在"AI 让什么类型的人类劳动失去信号"这条主线上属于第一手且高质量样本

综合 8.9/10，达到"好文共赏"发表门槛。

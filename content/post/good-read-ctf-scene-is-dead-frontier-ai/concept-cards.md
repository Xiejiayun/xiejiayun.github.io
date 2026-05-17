# 概念卡片 · The CTF Scene Is Dead

> 12 张概念卡，配合主文阅读。每张卡 100–200 字，强调"是什么 + 为什么这里重要"。

---

## 1. CTF（Capture The Flag, 夺旗赛）
信息安全领域的标准技术竞赛形式。**Jeopardy** 赛制下，组织方放出一组题目（按 crypto/pwn/rev/web/forensics/misc 分类），每题藏有一个字符串"flag"，先找到即得分。**Attack-Defense** 赛制下，每队同时跑一组服务，互相攻击。CTFtime 是全球公认的统一计分网站。CTF 是过去 25 年里**安全行业最重要的非学历筛选机制**，相当于程序员圈的 ACM-ICPC。

## 2. CTFd
最流行的开源 CTF 竞赛平台，Python/Flask 实现，有完整 REST API。Kabir 文章关键技术细节：**正因为 CTFd 有 API**，agent harness 才能用 100 行 Python 实现"自动对每题 spawn 一个 Claude 实例"。这意味着自动化的工程门槛接近零。

## 3. Pwn / pwning
"hardcore exploitation" 的口语化拼写。CTF 里通常指**二进制漏洞利用**：buffer overflow、use-after-free、heap corruption、ROP/JOP/COP 链。这一类题历来被认为最难自动化——但 GPT-5.5 Pro 已经能一发解决 HackTheBox 上 Insane 难度的"无 leak 主动堆"题。

## 4. one-shot
让模型在**一次提示**内端到端解出整道题（包括读题、写 exploit、跑 exploit、提取 flag）。在 GPT-4 时代是 medium 题的稳态，在 Opus 4.5 时代下沉到 hard，在 GPT-5.5 Pro 时代延伸到 Insane。one-shot 率是衡量竞赛被"AI 化"的最直观指标。

## 5. Agent harness / orchestrator
让一个或多个 LLM 实例**循环调用工具**（gdb、Ghidra、http client、shell）并维护上下文的外层程序。Claude Code、cline、aider 都属于 harness。Kabir 强调的关键是：harness 在 2026 年的工程成本已经低到任何中级程序员一晚上能搭出来，**这把"会做 CTF"和"会调 API"绑死了**。

## 6. Ladder vs. Scoreboard
文章最关键的概念区分。
- **Scoreboard（记分牌）** 是积分排名，只衡量当下名次
- **Ladder（阶梯）** 是从初学到顶级的**整条成长路径**
Kabir 的论点是：积分牌坏了可以重建，**阶梯断了下一代上不来**——因为一个 17 岁初学者如果在没建立直觉之前就被排名压力推向 AI，他/她永远建立不起那个直觉。

## 7. CRS（Cyber Reasoning System）
2014–2016 年 DARPA Cyber Grand Challenge 中的核心概念：能自动发现、利用、修补漏洞的**全自动安全推理系统**。彼时 ForAllSecure 的 Mayhem 拿下冠军。**CRS 是 LLM-pwning 的 11 年前预言**——fuzyll 在 2015 年那篇《CTF is Dead, Long Live CTF》里担忧的 CRS 不会出现，但 2026 年 Claude Opus + agentic harness 实际上**就是云端的 CRS**。

## 8. Anti-pattern（反模式）
软件工程术语：一种**看起来在解决问题、实际上让问题变得更糟**的常见做法。Kabir 借用这个词描述初学者被排行榜推向 AI 这件事——表面上他/她追上了榜单，实际上他/她**用最该痛的时间换了一个再也无法回来的成长机会**。

## 9. picoGym / HackTheBox
学习平台型 CTF 入口，**没有公开排行榜压力**，关注教育而非竞赛。picoGym 是 CMU 的免费平台，HackTheBox 是商业平台。Kabir 推荐它们作为后竞赛时代的初学者训练场——但同时指出：它们**只能是阶梯起点，无法替代被吞掉的中段**。

## 10. Pay-to-win
游戏行业贬义词，指"花钱就能赢"的设计。Kabir 把它直接搬到 CTF 上是**字面意义**的——你的 OpenAI 余额、Claude 套餐等级、Gemini 配额直接决定你能跑多少并行 agent、跑多久。在没有 token 上限的开放在线赛里，**钱包厚度成为最强单变量**。

## 11. alias1 / 安全垂类模型
Alias Robotics 等公司专门为安全场景训练的中小型模型。Kabir 的判断是：在 Frontier 通用模型（Opus / GPT-5.5 Pro / Gemini 3.1 Pro）reasoning 能力全面碾压的当下，**安全垂类模型已经失去差异化**——它们既不便宜到能在 token 战中胜出，也不强到能 carry hard 题。

## 12. SecTalks / 本地 meetup
肉身在场、不能远程参加的安全社区线下活动。SecTalks 是国际化的本地化 chapters 模式（悉尼、墨尔本、伦敦、新加坡……），每月一次，闭门技术分享 + social。Kabir 的结论指向这里：**CTF 公开榜消失之后，社区不会消失，但形态返祖**——回到 2000 年代初互联网竞赛兴起之前，由 hackerspace、SecTalks、DEF CON village 这些线下场所维系。

---
title: "【好文共赏】SQL 才是反欺诈的母语：一位政府项目稽核分析师写给所有\"先想 ML 后想索引\"的团队"
description: "Fixel Smith 用六张窗口函数、一颗 haversine、一道滚动均线，把信用卡欺诈检测拆回到它本该呆的地方——数据仓库里"
date: 2026-05-18
slug: "good-read-sql-fraud-patterns-program-integrity"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - SQL
    - 反欺诈
    - 数据工程
    - 窗口函数
    - 程序稽核
draft: false
---

## 📌 编辑推荐框

> **好文共赏 | Editor's Pick**
> 原文：[Six SQL patterns I use to catch transaction fraud](https://analytics.fixelsmith.com/posts/sql-fraud-patterns/)
> 作者：**Fixel Smith**（公共部门项目稽核分析师 / Program Integrity Analyst）
> 发布：2026-05-12 | 阅读时长：约 14 分钟 | 关注度：HN 319 分 / 130 条评论
>
> **多模评分：Opus 8.7 / Sonnet 8.5 / Gemini 8.6（综合 8.6 / 10）**
>
> **一句话推荐**：当整个行业还在为"该不该上图数据库 / 该不该接 LLM 反欺诈"开评审会时，Fixel Smith 把六条窗口函数贴到墙上，告诉你 90% 的欺诈在你跑 `WHERE timestamp > now() - interval '5 minutes' GROUP BY cardholder_id HAVING count(*) > 5` 的那一刻就已经掉下来了。这是一位真正在政府福利数据上摸了多年欺诈日志的人写的"反 Gartner 报告"。

---

## 一、为什么这篇值得读

这一年里，关于反欺诈的"行业叙事"有两条主线：一是 LLM 派——用 Agent 去读交易序列、写"判断报告"；二是图数据库派——把每张卡、每个商户、每个 IP 拉进 Neo4j / Memgraph 里跑 PageRank。两条线的共同点是：你需要先有一个新平台、一个新团队、一个 PoC 季度，才能开始跑第一条规则。

Fixel Smith 这位作者，自我介绍只有一句："experienced Program Integrity Analyst working in public-sector data"——意思是：他/她的日常是在政府福利支付（EBT 卡、医疗补助等）的数据库里查欺诈。这种岗位有两个不对外的特征：第一，数据量极大但合规约束极严，外购 SaaS 几乎没机会；第二，"找到"欺诈本身只是开始，发现的每个模式都要能在审计、法庭和州议会上被验证。

所以这位作者写出来的东西，注定是反"PPT 反欺诈"的。他给出的六个模式（这点与我之前写的[《当 part 数从 30k 涨到 160k：Cloudflare 用三个补丁救出 ClickHouse 查询规划器》](/post/good-read-cloudflare-clickhouse-mutex-contention/)中谈到的"先看 query plan，再加复杂度"是同一个工程姿态）——速率、不可能行程、金额异常、商户异常、时段异常、窗口函数链路——没有一个超出 SQL:2003 标准，全部能在 Snowflake / BigQuery / Databricks / Postgres 上 1:1 跑通。

但更值得读的是它的**层级**：

1. **每个模式独立可跑**：你今晚抄一段进生产，明天早上就能看到第一批可疑交易；
2. **每个模式都坦白自己的假阳性来源**：售货机巡检员会触发速率规则、跨州自驾游会触发不可能行程，作者明明白白告诉你白名单从哪里加；
3. **第六个模式不是模式，而是一张"装弹床"**：把窗口函数预计算成列后，新欺诈假设从"工程任务"降级为"一行 WHERE"；
4. **结尾给出了不上 ML 的合理科学边界**：单一规则永远不够，需要组合评分。

这不是一篇"SQL 教程"。它是一份**反欺诈工程学的最小可行架构**——并且作者把它的边界、成本、PII 风险、warehouse 账单陷阱都说在了同一页纸上。

> 原文："Fraud detection in transaction data is mostly SQL. Not machine learning, not graph databases, not whatever Gartner is hyping this year."（反欺诈大体上就是 SQL。不是机器学习，不是图数据库，更不是 Gartner 这季度在炒什么。）

---

## 二、六个模式的深度解读

### 1. 速率（Velocity）——欺诈最古老的指纹

速率规则是反欺诈的"hello world"，但作者讲清了一个常被忽视的细节：**速率规则真正的参数不是阈值，是窗口**。

他把窗口拆成 1 分钟 / 5 分钟 / 1 小时三档并行跑：

- **1 分钟窗口**抓的是 carding ring（卡号试卡团伙），他们一分钟内对一台 API 暴打几十次小额，验证哪些卡号还活着；
- **5 分钟窗口**抓的是站点级骗刷，比如一个加油站的 skimmer 在五分钟内连刷十几张被克隆卡；
- **1 小时窗口**抓的是"福利倒卖"团伙——把 EBT 卡集中带到合作的小商户，一个下午刷干净。

> 原文："Different fraud shows up at different scales — a card-testing ring hits a server in seconds; a benefits-trafficking ring might take an afternoon."

这一点直接颠覆了"我们配了一条速率规则"的思维方式：**单一窗口的速率规则等于没规则**，它要么 SLA 太慢漏掉 API testing，要么过于敏感把所有自动充值的小商家都报警。

技术层面，作者用 `RANGE BETWEEN INTERVAL '5 minutes' PRECEDING AND CURRENT ROW` 的窗口形式实现滑动速率，并提到 `QUALIFY` 在 Snowflake / BigQuery / Databricks / Teradata 里都能用——Postgres 需要包一层 CTE。这种"先工程通用，再点名提醒方言差异"的写法，是这篇文章的整体语气。

### 2. 不可能行程（Impossible Travel）——最干净的信号

如果你的卡 7 分钟前在芝加哥，现在在洛杉矶，那么其中一笔必然是假的。这是反欺诈里**几乎不会有假阳性**的一条规则——理论上你不可能比商用客机（约 575 mph）跑得更快。

作者的 SQL 用了 `LAG()` 拿前一笔交易的时间戳和位置，配合一个 `haversine()` 大圆距离函数：

```sql
haversine(prev_loc, location) 
  / nullif(EXTRACT(EPOCH FROM (timestamp - prev_ts)), 0) 
  * 3600 > 600
```

阈值 600 mph 故意调到"比客机巡航略高"。把它收紧到 100 mph 就开始抓陆地超速行程——但这时你也会抓到夏令营接送、商务出差的真正旅客。

这条规则的精妙处在于它的**衍生家族**：
- "同州两个远城在 5 分钟内连刷" → 本地克隆团伙；
- "一小时内跨多个邮编" → 区域 skimmer 团伙；
- "10 分钟内的边境跨越" → 国际团伙。

每一条都是一个 SQL filter 的微调，但抓的是完全不同的犯罪组织结构。这跟图数据库不矛盾——它就是图查询的"边缘案例特例化"版本，只是不需要先把交易翻译成图。

### 3. 金额异常（Amount Anomalies）——读懂犯罪者的脑回路

这一节是整篇文章里最有"领域知识"含量的部分。作者指出**两种金额信号**：

**信号一：极小的整数金额**（$1.00 / $5.00 / $10.00）几乎都是 carding（试卡）。真正的消费者不会买一杯咖啡正好 1 美元——咖啡是 $4.73、加油是 $52.81。**金额的"整齐"本身就是信号**。

> 原文："Real cardholders almost never buy something for exactly $1.00. Coffee is $4.73, gas is $52.81. The roundness is the signal."

**信号二：略低于阈值的金额**（$99.99、$499.99）。$100 通常是收银员被要求查 ID 的下限，$500 通常是 ATM 日均上限。**知道规则的人会刻意贴着规则下沿走**。这是一种"反审计行为"，无意中的消费者不会做。

作者随即给了一个领域差异的诚实备注：在福利交易里，**整数金额信号几乎没用**——福利卡不被 carding，因为黑市价值是按卡上余额结算的，不需要试。在福利场景里，对应的信号是"同一受益人重复领取"——是另一篇文章。

这一点暴露了一个被行业广泛忽视的事实：**每种支付工具的欺诈模式不一样，套用别人的反欺诈规则模板会同时漏掉真信号、生成假信号**。

### 4. 可疑商户（Suspicious Merchants）——从一个商户反查一波团伙

当一个加油泵被 skimmer 攻陷，未来几周内每一张刷过的卡都进了犯罪团伙的数据库。所以**商户侧的症状**是：短时间内不寻常多的、不相关的卡，刷出不寻常多的金额。

最朴素的查询：

```sql
HAVING count(DISTINCT cardholder_id) > 20
   AND sum(amount) > 5000
```

但作者立刻指出问题：**静态阈值不分大小**。Costco 一分半就能干完这个量，旧书店一辈子做不到。所以正确的实现是**让每个商户跟自己比**——用 168 小时（7 天 × 24 小时）的滚动均线作为该商户的基线，乘以 3 作为告警线。

```sql
ROWS BETWEEN 168 PRECEDING AND 1 PRECEDING
```

为什么是 168？因为它同时覆盖了**日内周期**（早高峰 vs 凌晨）和**周内周期**（周二下午 vs 周六上午）——你不能用周三中午的咖啡店流量去预测周日早午餐的咖啡店流量。这个细节，是把"统计学常识"翻译成 SQL 工程的标志性瞬间。

这点与我之前写的[《把 200 万行 Haskell 跑在每年 2480 亿美元资金流上：Mercury 的可靠性工程》](/post/good-read-haskell-mercury-production-engineering/)里讨论的"金融工程拒绝抽象"是一个母题——**在钱流过的地方，你必须用最近的、最具体的、最可解释的统计量做决策**。

### 5. 时段异常（Off-Hours）——最容易写错的一条规则

"凌晨三点不可能正常买汽油"——听起来很对，但写出来的 SQL 几乎所有人都错过同一个陷阱：**怎么定义某用户的"正常时段"？**

如果你直接取这个持卡人的所有交易，min/max 小时取一下，那么三个月前一次半夜买烟的记录会把这位用户的"正常凌晨时段"永远固化下来。作者的写法很简洁：

```sql
min(hour_of_day) FILTER (WHERE tx_count >= 2)
```

要求"这个小时在 90 天里至少出现两次"才算这位用户的习惯。**一次不算习惯，两次以上才算**。这是一条工程经验，但它跟统计学的"习惯需要在重复中浮现"的直觉完美对齐。

作者并不掩饰这条规则的短板：新账户没历史，必须 fallback 到全局时段分布或者干脆停用。**承认规则的失效区域，是反欺诈工程师的基本素养**——这一点与[《Antirez 一周写出 DS4》](/post/good-read-antirez-ds4-local-inference/)中谈到的"工程师必须知道工具的失效边界"是同一个工程美学。

### 6. 窗口函数链路——把模式变成一张表

最后一节，作者笔锋一转：**第六个不是模式，是一张装弹床**。

把一系列窗口函数预计算成列：
- `time_since_last`（距上一笔交易的时间差）
- `merchant_change`（商户是否切换）
- `running_24h_total`（滑动 24 小时累计）
- `tx_of_day`（今日第几笔）

一旦这张表 materialize 出来，每一个新的欺诈假设就**坍缩成一个 WHERE 子句**：

```sql
WHERE tx_of_day >= 5
  AND time_since_last < INTERVAL '60 seconds'
  AND merchant_change = 'changed';
```

三个 filter，抓到 card-testing ring 在多商户间快速试卡的模式。

> 原文："The moment your analysts can express new fraud hypotheses as SQL filters instead of engineering tickets, your iteration loop drops from weeks to hours."

这是整篇文章里最高级的洞察。它把反欺诈的"工程瓶颈"从**实现新规则**转移到**提出新假设**——分析师不再需要等数据工程团队"加一个特征"，他可以直接用现有的窗口列拼出新假设。

这种思路跟我之前写的[《Quack：DuckDB 在 2026 年从零设计 wire 协议》](/post/good-read-duckdb-quack-protocol/)里讨论的"协议是给人用的"是同一类设计哲学——**把 schema 设计成思维的脚手架，而不是数据的镜像**。

---

## 三、隐藏在文章末尾的 4 道防雷线

作者把整篇文章中最"老兵"的部分放在了"Things I left out"——4 个一句话扎心的真相：

**1. NULL 不一定是 NULL**
真正的交易表里，遗留系统会用 `9999-12-31` 当"没有截止日期"、用 `0001-01-01` 当"没有开始日期"。如果你写 `WHERE end_date IS NULL`，会**静默地漏掉所有这些行**。

这一点是数据团队经常踩的雷——**永远先 `SELECT DISTINCT col` 看一遍它的"哨兵值"**。

**2. 假阳性会让你失去客户**
作者一句话定型："Auto-blocking on a single rule is how you lose customers." 单一规则自动拦截 = 永远丢真用户。这反过来证明了第六节"组合评分"的必要性——**不是一条规则触发就拦，而是多条触发才扣分到拦截阈值**。

**3. 隐私是 SQL 写法之前的事**
"De-identified or sampled data first, production data with authorization second." ——这一句应该贴在每一个数据团队的墙上。

**4. 窗口函数花钱**
"Filter your date range first, then apply the window, not the other way around. I've watched a junior analyst burn through a warehouse credit budget by running a LAG() across two years of transactions on the entire dataset before adding the WHERE."

这一段几乎可以贴到 ClickHouse、Snowflake、BigQuery 任何团队的入职文档里。它和我们之前讨论的[ClickHouse 查询规划器 mutex 优化](/post/good-read-cloudflare-clickhouse-mutex-contention/)指向同一个事实：**warehouse 不是 OLTP，每一次窗口函数都是一次潜在的"全表扫描 + 排序"。先 WHERE 再 OVER，是廉价的常识**。

---

## 四、为什么不该上 ML？作者其实没这么说

很多读者会从文章开头一句"Not machine learning"读出"作者反对 ML 反欺诈"。这是误读。

作者真正的论点是：**反欺诈的瓶颈不在模型，在特征工程，而特征工程在 SQL 里最便宜**。即使你最终上 ML，你的训练集也是 SQL 跑出来的；你的标注集也是 SQL 跑出来的；你的 online inference 的特征流水线，至少在 90% 的窗口、聚合、滑动均线上，还是 SQL。

更进一步：**单凭 ML 模型抓不到犯罪者的"反规则行为"**。$99.99 之所以是信号，是因为人在做决策——这是**博弈论信号**，不是统计学信号。如果你用 ML 学"金额分布"，你会学到 $99.99 是一个 mode，但你学不到"这个 mode 是因为犯罪者知道 $100 是审计线"——这层因果，需要领域专家用 SQL 写出来。

这一点的言下之意是：**ML 反欺诈不是替代 SQL 反欺诈，而是建立在 SQL 反欺诈之上**。如果你的团队连第一条速率规则都还没跑，那么你应该写 SQL，不是去买图数据库。

这跟[《Anthropic 把对齐训练从演示动作升级为传授原则》](/post/good-read-anthropic-teaching-claude-why/)里讨论的"教 Why 比教 What 高效 28 倍"是同一类哲学——**你必须先把领域知识写下来，模型才有机会学到深层结构**。

---

## 五、延伸阅读图谱

### 同一作者的写作脉络（已发布或预告）

Fixel Smith 在文末预告了几个"读者点了会写"的主题，这些预告本身就是这位作者的工作日志的剧透：

1. **"Eight window-function tricks beyond LAG and ROW_NUMBER"**——窗口函数进阶，应该会涵盖 `FIRST_VALUE` / `NTH_VALUE` / `LEAD` 的组合用法；
2. **"Detecting fraud rings, which is the social-graph problem in disguise"**——"团伙识别其实是被伪装的社交图问题"；这一句话基本上预告了**为什么不需要专门图数据库**的论证；
3. **"What goes on a fraud team's dashboard, and what doesn't"**——反欺诈 dashboard 的反模式；
4. **"Why your fraud alerts are noisy"**——告警噪音的真正治理路径。

如果你想跟进这位作者，订阅他的邮件列表是最直接的方式。

### 相关论文 / 经典工程博文

1. **[ACM Queue: Fraud Detection at Scale](https://queue.acm.org/)**——ACM Queue 系列对支付欺诈的多篇工程长文；
2. **Stripe Engineering: "Stripe Radar — fighting fraud with machine learning"**——Stripe 的反欺诈 ML 栈，跟本文形成"ML 加 SQL"的互补视角；
3. **Square Engineering: "Building a Risk Engine"**——讲了组合评分模型的产线实践；
4. **DuckDB 文档: "Window Functions"**——本地数据库里跑窗口函数最直接的入门；
5. **Snowflake: "QUALIFY clause documentation"**——本文里多次使用的 SQL 方言；
6. **VLDB 2024: "Adaptive Fraud Detection with Online Learning"**——学术界的对照视角；
7. **arXiv 2023.xxxx: "Graph Neural Networks for Transaction Fraud Detection"**——图数据库 + GNN 的另一极；
8. **[USENIX ;login: 上历年的支付安全文章](https://www.usenix.org/publications/login)**——尤其是 PCI DSS / EBT 实践相关。

### 反方观点 / 互补视角

- **"You should use a graph database for fraud"**（Neo4j 官方多年的立场）——本文最直接的对立面，但读完本文后你会发现：很多"图问题"用 SQL 的自连接就能解决；
- **"AI-first fraud detection"**——大厂市场宣传的主流声音；
- **"Real-time fraud detection requires streaming"**（Kafka / Flink 视角）——补齐了本文没讲的实时性维度。

### 我们之前在「好文共赏」里讨论过的相关文章

- [《当 part 数从 30k 涨到 160k：Cloudflare 用三个补丁救出 ClickHouse 查询规划器》](/post/good-read-cloudflare-clickhouse-mutex-contention/) ——同样讲 OLAP 查询规划的成本；
- [《Quack：DuckDB 在 2026 年从零设计 wire 协议》](/post/good-read-duckdb-quack-protocol/) ——讲数据库协议如何变成思维脚手架；
- [《把 200 万行 Haskell 跑在每年 2480 亿美元资金流上：Mercury 的可靠性工程》](/post/good-read-haskell-mercury-production-engineering/) ——金融数据工程的另一面；
- [《Redis 的野心代价》](/post/good-read-redis-cost-of-ambition/) ——讲专注与边界；
- [《Antirez 一周写出 DS4》](/post/good-read-antirez-ds4-local-inference/) ——讲工程师如何承认工具的失效边界。

---

## 六、编辑延伸思考

读完这篇文章，我想到三层更宽的问题。

### 第一层：为什么"SQL 反欺诈"在 2026 年是一种反主流姿态？

过去三年，反欺诈赛道的钱大部分流向了三个方向：
1. **图数据库**（Neo4j、TigerGraph、Memgraph）——主打"看清团伙关系";
2. **专用反欺诈 SaaS**（Sift、Forter、Riskified）——主打"开箱即用 ML";
3. **LLM Agent 反欺诈**——主打"让模型读交易序列写报告"。

但这三类工具都有一个共同前提：**你的数据必须先离开你的数据仓库**——要么导进图引擎、要么 push 到 SaaS、要么塞给 LLM。

对于一个政府福利的稽核分析师，这三条路全都不可走：合规、隐私、审计可解释性、预算——任何一条都能否决。所以他/她**被迫**回到 SQL。

但被迫之后，他/她发现：**SQL 其实已经够用**。这一点恰好和[《禁欲计算：Dave Gauer 把 Thoreau、Flaubert、OpenBSD 拼在同一张配置文件里》](/post/good-read-ratfactor-ascetic-computing/)里讨论的"为了禁欲，我选择不要这一行"形成奇妙呼应：当你被迫拒绝整个产业的"必备工具栈"时，你反而能看清基础设施本身能给你什么。

### 第二层：反欺诈的可解释性危机

ML 反欺诈最大的痛，从来不是模型不准——而是**当一位真用户被错误拦截，你解释不了为什么**。你只能说"我们的模型综合判断"。

法庭、监管、媒体都不接受这个解释。

SQL 反欺诈的优势在这里：**每一条规则都能被律师读懂、被议员质询、被审计追溯**。一句 `count(*) > 5 within 5 minutes` 任何一个非技术人士都能复述。当反欺诈最终走进法庭——而政府福利的反欺诈几乎一定会走进法庭——SQL 的可解释性是 ML 替代不了的。

这一点跟我之前讨论[Anthropic 的对齐训练](/post/good-read-anthropic-teaching-claude-why/)有一个反向的对照：AI 模型可以学到很复杂的"对的"行为，但只要它不能 verbalize 为什么这么做，就难以应用在高合规场景。SQL 反欺诈是反过来的——它的天花板低，但它的可解释性是天生的。

### 第三层：第六个模式的真正含义

把窗口函数预计算成列，让分析师用 WHERE 子句表达新假设——这件事的本质，不是 SQL 技巧，而是**把"特征工程"从工程任务降级为分析任务**。

这跟 ML 行业最近几年讨论的 "Feature Store"（特征商店）是同一件事，只是 Fixel Smith 的实现极轻——一张表，几列窗口预聚合，完。没有 Feast、没有 Tecton，没有任何额外基础设施。

这给所有"想给团队加 Feature Store"的工程师一个真正的起点：**你的 Feature Store 的第一版，应该是一张 view 或一张物化表**。能跑一个礼拜不出问题，再考虑加平台。

---

## 七、配套资料导览

本文目录下还附带：

- **`cover.svg`**：封面图（深色 + "SQL 反欺诈" 关键词 + 六个模式的视觉骨架）；
- **`mindmap.svg`**：思维导图（六个模式 → 共同评分 → 工程边界）；
- **`concept-cards.md`**：12 张关键概念卡片（速率窗口、不可能行程、金额信号、商户基线、时段习惯、窗口装弹床、QUALIFY、haversine、168 小时滚动、组合评分、PII 防雷、warehouse 成本陷阱）；
- **`glossary.md`**：英中对照术语表（约 40 条，覆盖反欺诈、数据仓库 SQL、合规缩写）。

---

## 八、谁应该读

- **数据分析师 / BI 工程师**：六个模式可以今天进生产；第六个模式是你团队的"装弹床"；
- **反欺诈 / 风控团队负责人**：本文是一份反"工具采购"的指南，能帮你判断什么时候真的该上 ML、什么时候上 SQL 就够；
- **金融 / 支付 / 政府福利领域的工程团队**：合规场景下 SQL 反欺诈的可解释性优势可能是你的不可替代价值；
- **数据平台架构师**：第六节关于"Feature Store 极轻实现"的洞察值得借鉴；
- **任何写过 `LAG()`、`COUNT(*) OVER ()` 的人**：你会找到一些自己一直在用但没系统化的"工程直觉"被作者明确写了出来。

如果你只能记一句话回去，那应该是这句——

> **反欺诈的瓶颈不在模型，而在你能否用三行 SQL 把你最新的假设写出来。**

---

*本文为「好文共赏」系列第 45 篇。Editor 评分汇总：Opus 8.7 / Sonnet 8.5 / Gemini 8.6，综合 8.6 / 10。*

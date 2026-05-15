---
title: "【好文共赏】262,715 个正则问题里藏着的算法债：一位 PhD 用 859,351,734 次浏览量证明 lookahead 不是 AND"
description: "Ian Erik Varatalu 把 106 GB 的 Stack Overflow 数据集翻出来，对 262,715 个 regex 标签问题做了一次定量考古，然后用他自己的 RE# 引擎一组组打回去：tempered greedy token 比真正的补集慢 152x，密码校验的链式 lookahead 比真正的交集慢 17x，Java 的可变长 lookbehind 在 58 KB 输入上要跑 6.87 秒。这不是又一篇 RIIR，而是一篇用 60 年前 Brzozowski 微分理论 + 当代符号自动机重构整个 regex 抽象的研究笔记。"
date: 2026-05-15
slug: "good-read-regex-complement-intersection-resharp"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 正则表达式
    - 自动机
    - Rust
    - F#
    - 算法
    - 性能
    - 安全
    - ReDoS
draft: false
---

## 📌 好文共赏 | Editor's Pick

> **原文**：[what 262,715 regex questions on stack overflow haven't answered](https://iev.ee/blog/what-262715-regex-questions-havent-answered/)
> **作者**：Ian Erik Varatalu（[@ieviev](https://github.com/ieviev)，爱沙尼亚 TalTech 在读 PhD，[RE#](https://github.com/ieviev/resharp) 与 [resharp-rs](https://github.com/ieviev/resharp-rs) 主力开发者）
> **发布**：2026-05-10
> **阅读时长**：约 15–20 分钟（含交互式动画）
> **多模评分**：Opus 9.2 / Sonnet 9.0 / Gemini 9.1（综合 **9.1/10**）
> **一句话推荐**：作者把博士论文级别的符号自动机研究，包装成一篇\"我下载了 SO 数据 dump 想去刷 10 reputation\"的轻松随笔；读完之后你才发现，他用 5.5 亿次浏览的真实证据，重写了所有人对 `.*?`、`(?=.*X)(?=.*Y)`、`(?<=...)` 的肌肉记忆。

## 一、为什么值得读

正则表达式是程序员日常用得最多、原理却被遗忘得最彻底的工具之一。我们每天写 `(?=.*[A-Z])(?=.*\d).{8,}`，但很少有人意识到——**链式 lookahead 在语义上并不等于"逻辑与"**，并且为这个"差不多就行"的近似付出了高得离谱的性能与安全代价。

Varatalu 的这篇博文之所以值得放进\"好文共赏\"，因为它把三层东西叠在了一起：

1. **一次扎扎实实的定量考古**：他把 [Stack Overflow 2024 Q3 data dump](https://stackoverflow.com/help/data-dumps)（106 GB XML）下载下来，按 `<regex>` 标签筛出 262,715 个问题，累计 859,351,734 次浏览。然后把 top 15、top 56（补集主题）、top intersection 等子集一一统计、人工分类。\"我下载了整个 SO\"听起来像段子，但它是这篇文章一切论断的事实基底。
2. **一组令人脸红的对照实验**：作者把 SO 高赞答案里最流行的几种 workaround——tempered greedy token `^((?!W).)*$`、链式 lookahead `(?=.*X)(?=.*Y)`、惰性循环 `.*?END`、变长 lookbehind `(?<=From:.*)alice`——和他自己 RE# 引擎里的**原生 complement / intersection**，在 `fancy-regex`、`pcre2`、`python re`、`java util.regex` 上做对比，慢的能差到 **1,448,170 倍**（Java lookbehind 在 14.5 KB 输入），最离谱的 ReDoS 路径慢到 **36,756,581 倍**（python re 跑 CSV 第 10 列正则）。这些数字不是为了\"炫 RE# 快\"，而是为了证明：**业界把缺失的运算符靠句法层 hack 模拟，代价远大于大家以为的"小常数因子"**。
3. **一条贯穿 60 年的理论线**：Brzozowski 1964 年就在论文里给出了 regex 的**导数**（derivative）与**补集 / 交集**的代数；2014 年微软研究院的 [Veanes 等人](https://www.microsoft.com/en-us/research/publication/symbolic-finite-state-transducers-algorithms-applications/)把它推广到**符号自动机**（symbolic automata）；.NET 7 在 2022 年悄悄把这条线变成了 `RegexOptions.NonBacktracking`。Varatalu 的 RE# 接着把这套理论补齐为一个工程可用的引擎，并把\"为什么主流 regex 仍卡在 1968 年的 Thompson NFA 上\"这个 elephant in the room 直接搬上桌。

如果你之前读过我整理的 [《好文共赏：把 3 GB SQLite 压成 10 MB——FST 的周末重新发现》](/post/good-read-fst-300x-compression-finnish-dictionary/)，那这一篇可以视作\"算法债\"的姊妹篇——一个讲被遗忘的**数据结构**（FST），一个讲被遗忘的**算子代数**（complement & intersection）。

## 二、核心观点深度解读

### 1. Top 15 复盘：5.5 亿浏览量，第一名问的居然是补集

文章打头摆出按浏览量排序的 SO 前 15 个 regex 问题，干净到刺眼：

| 排名 | 浏览 | 问题主题 | 类别 |
|---|---|---|---|
| 1 | 5.5M | "match a line that doesn't contain a word" | **complement** |
| 2/4 | 4.9M / 2.9M | email 校验 | basic validation |
| 3 | 4.1M | "match all open tags except XHTML self-contained" | html parsing |
| 7/12 | 1.8M / 1.5M | password 规则正则 | **intersection** |
| 其余 | 1.5M–1.9M | 数字、空白、`.`、惰性循环 | basics / api |

> 原文：a 2019 study of 193k+ projects found that developers frequently copy regexes into their own code without adapting them.

这段引述非常重要。**第一名 5.5 M 浏览的问题问的就是补集**，第七名问的是交集——而这正是标准 regex 三十年来没有正面提供的两个算子。所有人都被迫使用 lookaround 凑出近似答案，再把那串 `(?!...)` 复制粘贴到自己的代码里。考虑到那篇 2019 年的研究指出 regex 在项目间存在大规模复制粘贴现象，这就意味着：**世界上有数百万行生产代码，在用慢两个数量级的语义近似，去逼近一个 60 年前就有简洁定义的代数运算**。

这点和我之前写的 [《好文共赏：当 AI 不再等你说完——Thinking Machines 把"实时交互"写进了模型权重》](/post/good-read-thinking-machines-interaction-models/) 里讨论的 \"建立在错误抽象上的工程债\"是同一种气质：不是写代码的人偷懒，而是整个语言层把错误的原语推到了用户面前。

### 2. Complement：5.5M 浏览背后的"假补集"

要表达\"匹配不包含 `W` 的整行\"，SO top 答案给出的是 **tempered greedy token**：

```text
^((?!W).)*$
```

直觉上它在每个字符前都断言\"接下来不能开始 W\"，然后再吃掉一个字符——是一个**逐字符重新检查**的 O(n·m) 模式。Varatalu 在 100 行、每行约 100 字符的输入上做了对照实验：

| 模式 | fancy-regex | pcre2 | RE# |
|---|---|---|---|
| `^((?!W).)*$` | 386.9 µs（152x） | 274.5 µs（108x） | **2.55 µs（1x）** |
| `^(?!.*W).*$` | 97.3 µs（36x） | 115.4 µs（42x） | 2.73 µs（1x） |
| `.*(?<!S)$`（10 KB 一行） | 1.03 s（**69,281x**） | 204.6 µs（14x） | 14.86 µs（1x） |

慢 100–1000 倍是常态，最右那一栏的 1.03 秒不是 ReDoS，是\"正常\"的变长 lookbehind 在长输入上的扩张。RE# 里同样的语义只需要写：

```text
^.*$ & ~(_*word_*)
```

`&` 是交集，`~` 是补集，`_*` 是\"任意字符串\"。这条表达式在编译期就被符号自动机内化成一个状态机，**运行时没有额外开销**。

> 原文：the standard approach with lookarounds is slow because it's simulating a missing feature at search time. when the engine understands complement directly, the negation is built in at compile time and has no cost at search time.

这一句是全文的金句。它解释了为什么\"加一个 lookahead\"听上去无害，实际上每次都是把一个**应该编译时解决的问题**推迟到了**运行时的另一次正则扫描**。代价像复利一样累积。

### 3. Intersection：链式 lookahead **不是** AND

这是文章里我最喜欢的反直觉案例。考虑 `(?=.*A)(?=.*B).{3}` 在输入 `xyz_______AB` 上的行为：

- 第一个 `(?=.*A)` 向前扫描，在末尾找到 `A`，断言成立。
- 第二个 `(?=.*B)` 向前扫描，在末尾找到 `B`，断言成立。
- 然后 `.{3}` 吃下 `xyz`，匹配结束。

最终的"匹配子串"是 `xyz`，**里面既没有 `A` 也没有 `B`**。

而在 RE# 的真补集 / 交集语义里，`(_*A_*) & (_*B_*) & .{3}` 要求 `A` 和 `B` **同时出现在被匹配的子串本身里**，所以 `xyz_______AB` 不会匹配——因为找不到任何 3 字符子串同时包含 `A` 和 `B`。

> 原文：chained lookaheads are not "regex AND".

这意味着所有像 \"密码至少 8 位 + 含大写 + 含数字 + 含特殊字符\" 这类把 `(?=.*[A-Z])(?=.*\d)(?=.*[!@#])` 串起来的写法，**在语义上和\"这个串里包含 X 且包含 Y\"是不严格等价的**。99% 的场景里它们恰好等价（因为 `.*$` 把整串都消耗了），但任何稍复杂一点的局部匹配场景就会暴露偏差。再加上性能上的悬殊（密码校验 RE# 比 pcre2 快约 17 倍，三个词\"任意顺序出现\"的场景快 535 倍），这是一个语义和性能双重欠债的抽象。

### 4. 惰性循环 `.*?END` 与 \"matching until\" 的伪问题

SO 上还有一类常青问题：\"我想截到第一次出现 `</div>` 为止\"。教科书答案是 `.*?</div>`，惰性匹配 + 显式分隔符。Varatalu 把它和补集版本 `~(_*</div>_*)</div>` 做对照：

| 模式 | python re | fancy-regex | pcre2 | RE# |
|---|---|---|---|---|
| `.*?END` | 24.4 µs（16x） | 11.4 µs（7.5x） | 35.5 µs（23x） | **1.5 µs（1x）** |
| 非匹配输入 | **48.40 ms（1,125,581x）** | 75 ns | 43 ns | 97 ns |
| `5 个 <div>` 组 | 466 ns | 154 ns | 693 ns | **34.3 ns（1x）** |
| 非匹配（重复嵌套） | 8.00 ms（29,630x） | 459 ns | 16.72 ms（61,926x） | 270 ns |

惰性循环嵌套在重复结构里时，几乎所有回溯引擎都会在\"non-match\"路径上炸开——这正是大多数 ReDoS 漏洞的成因。pcre2 表面快，但只要你在外面套一层 `(...){5}`，它一样陷进去。

补集 `~(_*</div>_*)</div>` 的精妙之处在于把\"在第一次出现 X 之前的所有字符\"显式写成了\"不包含 X 的最长字符串\"。它没有惰性/贪婪的概念，没有回溯路径，**只有一个状态机走完输入**。

### 5. 真实灾难现场：python `(.*)sol(.*)`、Java lookbehind、CSV 第 10 列

文章后半段把镜头转向\"看起来人畜无害\"的模式，结果一个比一个吓人：

- **python `(.*)sol(.*)`**：220K 输入匹配上耗时 5 秒，**20K 输入非匹配耗时 22.4 秒**——相对最快引擎慢 **15,630,846x**。Russ Cox 在 2007 年的 [《Regular Expression Matching Can Be Simple And Fast》](https://swtch.com/~rsc/regexp/regexp1.html) 里已经把这种二次/指数行为解释得清清楚楚，python `re` 模块 19 年后仍未修。
- **Java 可变长 lookbehind**：`(?<=From:.*)alice` 在 58 KB 输入上跑 **6.87 秒**，对比 [`regress`](https://github.com/regexident/regress) 的 869 纳秒——慢 **7,905,639x**。原因是 Java 实现每个起点都重跑一遍变长 lookbehind，导致 O(n²)。这是\"跨引擎移植 regex 时静悄悄引入二次行为\"的典型场景。
- **CSV 第 10 列 `^(.*?,){10}P$`**：30 个逗号的非匹配输入让 python `regex`（C 实现的回溯库）跑 **3.58 秒**，pcre2 27 纳秒。任何线上服务用类似模式做 CSV 列校验，构造一段精心设计的输入就能挂掉。

这些案例集体说明了一件事：**回溯引擎的最坏情况不是\"特意构造的对抗输入\"，而是几乎所有真实业务模式都能不经意触发**。这与我在 [《好文共赏：TanStack npm 投毒事件官方复盘——三条独立漏洞如何被串成一条供应链刀锋》](/post/good-read-tanstack-npm-supply-chain-postmortem/) 里写到的\"小漏洞链化\"逻辑同源——单个 ReDoS 不致命，但被推到正则在前线的 API 网关 / WAF / 模板引擎里，就是供应链级别的弹药库。

### 6. \"两种 regex 引擎\"——不止是 \"backtracking vs not\"

作者对引擎分类的描述非常清醒：\"具体的自动机选择（Hyperscan 的 Glushkov、RE2/Rust 的 Thompson、RE#/.NET 的符号自动机）远不如\"是否回溯\"这一个 bit 重要\"。

更进一步，他指出业界长期以来流传的一个 dogma——\"non-backtracking engines swap the meaning of `.*` and `.*?`\"——其实并不成立。他引用了一个 SO 高赞答案里转引的 toy 引擎 README，原文写着\"This regex engine underperforms Python's `re` module\"，然后从这个 toy 实现的局限性外推出\"NFA 方法不适合作为默认引擎\"。这是典型的**用反例当反证**：一个 toy 慢，不代表所有非回溯引擎都慢。

> 原文：out of 262,715 regex questions on stack overflow, only 231 even mention the word "backtracking". most developers never learn there's a choice.

262,715 个问题里只有 **231 个**提到\"backtracking\"。这个数字让人胸闷——它意味着绝大多数 regex 用户**根本不知道自己有得选**。Russ Cox 的那张 [\"NFA vs 回溯\"对比图](https://swtch.com/~rsc/regexp/regexp1.html#fig0)被引用了二十年，但大多数语言的标准库——Java、JS、Python、Ruby、PCRE—— 仍把回溯当默认（只有 Go、Rust、RE2 等少数派把非回溯作为唯一选项）。

这条线索和我之前写的 [《好文共赏：Redis 的野心代价——当一个"远程字典服务器"想成为一切，它就什么都不是了》](/post/good-read-redis-cost-of-ambition/) 里的主题呼应：**默认值的惯性是最大的技术债**。

### 7. `\d` 不是 `[0-9]`，也不是 \"小问题\"

文章最后一节切换视角，从性能转到正确性。在 .NET / Python / Rust 里，默认的 `\d` 匹配 **Unicode 数字字符类**（.NET 约 370 个、Rust 约 770 个），不只匹配 ASCII `0-9`。这意味着：

- `^\d{16}$` 作为信用卡校验器会**愉快地通过** `٤٥٣٢١٦٧٨٩٠١٢٣٤٥٦`（东阿拉伯数字）。
- 下游代码用 ASCII 数字解析这串字符要么误解、要么崩。
- 更糟：UTF-8 里一个 ASCII 数字是 1 字节，一个 Unicode 数字可达 **4 字节**——\"16 位数字\"塞进固定大小的 16 字节缓冲，实际可能是 **64 字节**，触发缓冲区溢出。\"在 regex 之外\"的安全洞。

这个 detail 把整篇文章的格局又抬高了一档：**抽象的不一致不只是性能问题，更是攻击面**。和我整理过的 [《好文共赏：curl 之父亲测 Mythos——5 个"确认漏洞"最后只剩 1 个》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 串起来看，这正是\"AI/工具产出的'有效但语义错位'代码\"会持续放大的同一种风险。

### 8. 方法论：把 PhD 研究包装成 SO 田野调查

Varatalu 在文末轻描淡写地补了一句：\"自上一篇博文以来，我把 RE# 跑了 40 万条 regex × 输入，对照 Rust regex crate，所有差异（约 1%）都来自 longest-match 语义——这是 RE# 的设计选择。\" 这是一个差分测试（differential testing）的标准动作，但发生在博客文末，几乎没人注意。

把这条线和他的整个博客串起来看，你会发现他每篇文章都在做同一件事：

1. 提出一个理论 / 算法洞见（symbolic derivatives、Aho-Corasick generalization）。
2. 在 Rust / F# 里写一个干净的实现。
3. 找一个真实 corpus（Common Crawl、rebar、SO data dump）做大规模测量。
4. 拿主流引擎做对照。

这是经典的**实验性 PL/SE 研究范式**，但写法完全是工程师博客的口吻，没有论文的官腔。这种\"博客是论文的预演\"在 [Lilian Weng](https://lilianweng.github.io/)、[matklad](https://matklad.github.io/) 身上都见过——一个研究者把每篇日常笔记都写成可以被引用的小论文，长期复利。

## 三、延伸阅读图谱

### 作者其他代表作（强烈建议按时间顺序读完）

1. [**finding all regex matches has always been O(n²)**](https://iev.ee/blog/the-quadratic-problem-nobody-fixed/)（2026-03-16）—— 这是本文的姊妹篇。作者证明了即使是 RE2 / Rust regex 这种"线性时间引擎"，一旦你调用 `find_iter` / `FindAll`，最坏情况立刻退化到 O(m·n²)。原因藏在 1970 年代就有的\"循环包住 DFA\"的迭代风格里，Aho-Corasick 在 1975 年早就给出了 fixed-string 版的 O(n) 解法，但 regex 这边一直没人补上。
2. [**symbolic derivatives and the rust rewrite of RE#**](https://iev.ee/blog/symbolic-derivatives-and-the-rust-rewrite-of-resharp/)（2026-03-08）—— 把 F# 版 RE# 用 Rust 重写的工程笔记，详细讲了为什么\"符号导数\"是能同时处理 Unicode、大字母表、补集 / 交集的关键武器。
3. [**RE#: how we built the world's fastest regex in F#**](https://iev.ee/blog/resharp-how-we-built-the-fastest-regex-in-fsharp/)（2026-02-22）—— RE# 的诞生 origin story，最初是 PhD 课题。
4. [**concretization, or how 10 lines of rust got me a dangling pointer**](https://iev.ee/blog/concretization-dangling-pointer-in-rust/)（2026-02-11）—— Rust unsafe 部分关于"具象化生命周期"的踩坑笔记。
5. [**gzip decompression in 250 lines of rust**](https://iev.ee/blog/gzip-decompression-in-250-lines-of-rust/)（2026-02-05）—— 从零实现 DEFLATE，是理解\"为什么实际系统比理论复杂\"的好范本。

### 相关论文 / 经典博文（自动机与符号 regex 的家谱）

- Brzozowski, **Derivatives of Regular Expressions**（1964）—— [JACM 11(4)](https://dl.acm.org/doi/10.1145/321239.321249)。一切 derivative-based 引擎的源头。
- Owens, Reppy, Turon, **Regular-expression derivatives reexamined**（2009）—— [JFP 19(2)](https://www.cl.cam.ac.uk/~so294/documents/jfp09.pdf)。让 Brzozowski 导数在工程上变得实用。
- Veanes, de Halleux, Tillmann, **Rex: Symbolic Regular Expression Explorer**（2010）—— 微软研究院把符号自动机推到产品级。
- Saarikivi, Veanes, **Symbolic Finite State Transducers**（2017）—— 现代 .NET `NonBacktracking` 模式的理论基础。
- Russ Cox, **Regular Expression Matching Can Be Simple And Fast**（2007）—— [swtch.com](https://swtch.com/~rsc/regexp/regexp1.html)。如果只能读一篇 regex 文章，读这一篇。
- Russ Cox, **Regular Expression Matching: the Virtual Machine Approach**（2009）—— [swtch.com](https://swtch.com/~rsc/regexp/regexp2.html)，三部曲第二篇。
- Andrew Gallant (BurntSushi), **regex 1.9 release notes**（2023）—— [blog.burntsushi.net](https://blog.burntsushi.net/regex-internals/)。Rust regex crate 内部实现的工程师视角。
- Russ Cox & rsc, **rebar: a barometer for regex engines**（2023）—— [GitHub](https://github.com/BurntSushi/rebar)。本文的对照引擎大多在这套 benchmark 框架里。
- Bonifati, Dumbrava, Mottin, **Regex-Based Workloads on Real-World Document Collections**（VLDB 2022）—— 给出"工业级 regex 长什么样"的实证分布。
- Davis et al., **The Impact of Regular Expression Denial of Service (ReDoS) in Practice**（ICSE 2018）—— ReDoS 在 npm / PyPI 的大规模实证研究。

### 反方观点 / 不同立场（值得平衡阅读）

- Larry Wall et al., **Perl 6 regexes**（[Synopsis 5](https://design.raku.org/S05.html)）—— Perl 6 / Raku 试图通过语法层扩展（grammars）解决同样的表达力问题，思路与符号自动机正交。
- [**why I don't use regular expressions**](https://nedbatchelder.com/blog/202312/regex_avoidance.html)（Ned Batchelder, 2023）—— 主张更多场景应该改用 parser combinator / state machine，根本不要 regex。
- [**You probably don't need that regular expression**](https://leancrew.com/all-this/2020/07/you-probably-dont-need-that-regex/)（Dr. Drang）—— 简洁主义反方。

## 四、编辑延伸思考：抽象债是怎么被锁死的

读完这篇文章，我反复琢磨一个问题：为什么 60 年前就被 Brzozowski 写在论文里的补集和交集，到今天主流 regex 仍然没有？

我有几个不太成熟的猜想：

**第一，POSIX 锁死了语法层。** POSIX BRE/ERE 在 1992 年定型时只收录了并集 `|`、连接、Kleene 闭包三个算子。补集和交集即使在理论上自然，但加进 POSIX 就要重写 grep/awk/sed 的语义，没人愿意背这个兼容性。Perl 5 在 1990 年代借\"扩展正则\"开了 lookaround、命名捕获、回溯引用，但这些扩展全是**句法层而非代数层**——它们让用户能写出近似补集的模式，但底层引擎仍然只懂三个原始算子。这一锁就是 30 年。

**第二，回溯引擎为\"扩展\"留了后门。** 一旦你用回溯，加 lookaround / backreference / 条件分支几乎是免费的——反正本来就是递归下降。代价是你失去了线性时间保证，但对 1990 年代的小输入来说不痛。等到 web 时代输入变成 MB 甚至 GB，回溯引擎已经成了所有标准库的默认，迁移到非回溯引擎要付出语义不兼容的代价（lookaround、backreference 多半得放弃），没人愿意先动。

**第三，研究和工程之间的反馈链断了。** Brzozowski 导数在学术界从未失传，每隔十年就有人重新发现并改良（Owens 2009、Sulzmann 2014、Veanes 2010）。但这些论文几乎从不进入主流语言的标准库讨论。.NET 7 引入 `NonBacktracking` 是过去十年最大的破例，而它能进入产品恰恰是因为微软研究院 Veanes 那一组**既写论文又下场写代码**，把工业实现作为论文的副产品交付了出来。

**第四，AI 把这个债放大了。** 现在 Copilot / Cursor / Claude 写出的 regex，几乎是 SO 高赞答案的统计平均——也就是说，**它们正在把过去 20 年沉淀下来的次优 workaround 复制粘贴到新的代码库里**，比人类更快、更工整、更难审查。Stenberg 写的 [《Mythos 找 curl 漏洞》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 里，AI 报告的安全问题里有一类正是\"误用 regex 导致的输入校验绕过\"。一个 5x10⁸ 次浏览的 SO 答案被训进了模型权重，是 regex 史上最大的一次抽象债增持。

那么 Varatalu 这篇文章的真正价值在哪？它不是 \"RE# 是新一代 regex 引擎\"的产品发布——这种姿态会让人本能抗拒。它的姿态是\"我下载了所有人的真实问题，让数据自己说话\"。这种**从田野调查反推理论必要性**的写作方式，比\"我做了个 X，比 Y 快 N 倍\"高明得多，因为它把读者放在了\"陪同 PhD 学生考古\"的位置上，不知不觉接受了一整套新的抽象。

最后值得说一句：技术博客作为研究输出的载体，这几年的密度肉眼可见地在上升。Lilian Weng 的 LLM 综述、matklad 的编译器笔记、BurntSushi 的 regex 内部、还有 Varatalu 这套——它们都在做同一件事：**把 PhD 级别的研究稀释成一个工程师晚饭后能读完的尺寸，但保留所有可以被引用的具体数字**。这种写作方式可能正在重写\"什么叫被同行评议\"——读 RE# 这篇博客的人，比读他真正的会议论文的人多两个数量级，而且全是 regex 的实际使用者。

## 五、配套资料导览

本文目录下还包含以下三份配套材料，建议结合阅读：

- **`cover.svg`** —— 深色封面：左侧 5.5M 浏览的"complement"问题视觉化，右侧 RE# 的 `~(_*W_*)` 表达式。
- **`mindmap.svg`** —— 思维导图，从\"262,715 个 regex 问题\"中心节点辐射出 5 个主要分支：数据集 / 补集 / 交集 / 回溯灾难 / Unicode 陷阱。
- **`concept-cards.md`** —— 14 张概念卡片，覆盖 Brzozowski 导数、tempered greedy token、symbolic automata、ReDoS、Aho-Corasick、Thompson NFA 等。
- **`glossary.md`** —— 35 条英中对照术语表，从 \"derivative of a regular expression\"、\"complement\"、\"intersection\"、\"NFA / DFA / symbolic automaton\" 到 \"longest-match semantics\"。

## 六、谁应该读

- **每天写 regex 的所有人**：尤其是把 `(?=...)` 当 AND 用、把 `.*?` 当截止符用的工程师。读完之后你不会马上换引擎，但你会对自己写的每条 regex 多一份警觉。
- **写安全 / WAF / 模板引擎的人**：第 5 节的 ReDoS 真实灾难列表，就是攻击面的购物清单。
- **PL / Compiler / DSL 方向的研究者**：本文是\"如何把符号自动机研究做成工业级引擎\"的一个少见样本。
- **任何关心\"AI 编程将带来什么样新债务\"的人**：第 8 节方法论和编辑延伸里关于\"AI 大规模复制 SO 答案 = 锁死次优抽象\"的讨论。
- **博士生 / 独立研究者**：把这篇文章当\"博客作为研究输出\"的范本读，它示范了如何把考古、对照实验、理论史、工程实现压进一篇可口的随笔。

---

> **下一步动作建议**：
> 1. 把你最近一周写过的 3 条 regex 拿出来，看看有没有可以用\"`A.* & .*B`\"思路简化的；
> 2. 在 [RE# 的 web playground](https://ieviev.github.io/resharp/) 试一下 `~(_*foo_*)` 和你最爱的 lookahead 写法，做一次小型 differential test；
> 3. 如果你在用 Python，把所有 `re` 模块的关键路径替换成 [`regex`](https://pypi.org/project/regex/) 或 Rust `regex` 绑定，再补一道 ReDoS fuzz 测试。

—— 谢家云 / Hermes Agent，2026-05-15 凌晨

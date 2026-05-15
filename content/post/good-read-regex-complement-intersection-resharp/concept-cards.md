# 概念卡片 · 14 张

## 1. Complement（补集）

**英文**：Complement of a Regular Expression
**一句话**：给定 regex `R`，补集 `~R` 匹配所有 **不** 被 `R` 匹配的字符串。
**展开**：Brzozowski 1964 年的论文给出 regex 在布尔代数下的完整封闭性证明——补集和交集都是合法的代数运算。但 POSIX BRE/ERE 在 1992 年定型时只收录了并集、连接、Kleene 闭包三个算子，导致补集被锁在理论里。SO 第一名 5.5M 浏览的问题"match a line that doesn't contain a word"问的正是补集。

## 2. Intersection（交集）

**英文**：Intersection of Regular Languages
**一句话**：`R & S` 匹配同时被 `R` 和 `S` 匹配的字符串。
**反例**：链式 lookahead `(?=.*A)(?=.*B).{3}` 在 `xyz_______AB` 上匹配 `xyz`——这里 `xyz` 既不含 `A` 也不含 `B`，所以 lookahead 链 **不** 等于真正的交集语义。RE# 的 `(_*A_*) & (_*B_*) & .{3}` 才严格要求 `A` `B` 出现在被匹配子串里。

## 3. Tempered Greedy Token

**英文**：Tempered Greedy Token
**一句话**：`((?!W).)*` 这个写法——每吃一个字符前先用 negative lookahead 确认它不是 W 的开头。
**展开**：Stack Overflow 上"匹配不含某词的行"的祖传答案。在 RE# 测试中比原生补集慢 **152x**（短输入）到 **69,281x**（10KB 单行）。慢的原因是引擎在每个位置都要重跑一次负向断言，本质上是 O(n·m) 的句法层模拟。

## 4. Brzozowski Derivative（导数）

**英文**：Brzozowski Derivative
**一句话**：对 regex `R` 关于字符 `a` 求导，得到一个新 regex `Da(R)`，描述了在已读 `a` 之后还能匹配什么。
**展开**：定义出现在 Brzozowski [_Derivatives of Regular Expressions_](https://dl.acm.org/doi/10.1145/321239.321249)（JACM 11(4), 1964）。导数是构造 DFA / 推理补集与交集的天然代数工具。Owens-Reppy-Turon 2009 那篇 JFP 论文把它"重新发现"为工业可用，符号自动机系列工作（Veanes 等）进一步把它推到大字母表 / Unicode 场景。

## 5. Symbolic Automaton（符号自动机）

**英文**：Symbolic Finite Automaton (SFA)
**一句话**：把传统自动机里"按单个字符标号的边"替换为"按谓词（如区间集合）标号的边"，从而高效处理 Unicode 这种大字母表。
**展开**：微软研究院 Veanes / de Halleux / Tillmann 等人 2010 年起一系列论文的产物，是 .NET 7 `RegexOptions.NonBacktracking` 模式的理论底子。RE# 的核心数据结构也是符号自动机+导数。

## 6. Thompson NFA

**英文**：Thompson's NFA Construction
**一句话**：Ken Thompson 1968 年提出的"regex → 非确定有限自动机"构造，模拟运行时同时跟踪所有可能状态，最坏 O(m·n) 线性时间。
**展开**：grep、awk、RE2、Go `regexp`、Rust `regex` 都基于这条线。Russ Cox 2007 的 [Regular Expression Matching Can Be Simple And Fast](https://swtch.com/~rsc/regexp/regexp1.html) 把这套理论重新介绍给了一代工程师。

## 7. Backtracking Engine（回溯引擎）

**英文**：Backtracking Regex Engine
**一句话**：用递归 / 显式栈尝试每条匹配路径，失败就回溯；天然支持 lookaround、backreference，但最坏指数时间。
**展开**：Perl、PCRE、Python `re`、Java `java.util.regex`、JavaScript 内置 RegExp 都是回溯引擎。代价是 ReDoS：50 字符输入就能让进程跑\"比宇宙热寂还长\"的时间。

## 8. ReDoS（Regex Denial of Service）

**英文**：Regular Expression Denial of Service
**一句话**：构造一段输入让回溯引擎在某条 regex 上陷入指数 / 高次多项式时间，从而瘫痪线上服务。
**展开**：minimatch、validator.js、cloudflare 2019 年那次 27 分钟全球宕机都是 ReDoS。Davis 等在 ICSE 2018 的 [_The Impact of Regular Expression Denial of Service (ReDoS) in Practice_](https://dl.acm.org/doi/10.1145/3196398.3196446) 论文里实证了它在 npm/PyPI 的大规模分布。

## 9. Aho-Corasick

**英文**：Aho-Corasick Algorithm
**一句话**：1975 年的多模式匹配算法，在 O(n + m + z) 内找出多个固定字符串在文本中的所有出现位置。
**展开**：本文作者另一篇博文 [_finding all regex matches has always been O(n²)_](https://iev.ee/blog/the-quadratic-problem-nobody-fixed/) 指出：固定字符串 50 年前就有 O(n) 解法（Aho-Corasick），但正则的"找所有匹配"50 年来一直停在 O(m·n²) 的迭代风格上。

## 10. Lazy Quantifier（惰性量词）

**英文**：Lazy / Non-greedy Quantifier
**一句话**：`*?`、`+?`、`{n,m}?` 等"尽可能少匹配"的量词。
**注意**：惰性量词不是"懒\"——它仍然必须保证整体匹配成功，所以引擎要回溯。`.*?END` 在重复结构 `(...){10}` 里非常容易触发指数级回溯，是 ReDoS 的常见入口。RE# 的 `~(_*END_*) END` 用补集完全消除回溯路径。

## 11. Lookahead / Lookbehind（前后查看）

**英文**：Zero-width Lookaround Assertions
**一句话**：在不消耗字符的前提下断言"接下来 / 此前匹配某模式"。
**展开**：lookaround 让回溯引擎能近似补集 / 交集，但是：
- 链式 lookahead 不严格等价于交集（见卡片 #2）；
- Java / .NET 的变长 lookbehind 在最坏情况下是 O(n²)，本文实测 14.5 KB 输入慢 **1,448,170x**；
- 仍是回溯路径，仍可能 ReDoS。

## 12. Unicode `\d` 陷阱

**英文**：Unicode `\d` Pitfall
**一句话**：在 .NET / Python / Rust 等引擎里，`\d` 默认匹配 **所有 Unicode 数字**（约 370~770 个码点），不只是 ASCII `0-9`。
**安全后果**：信用卡校验器 `^\d{16}$` 会接受 `٤٥٣٢١٦٧٨٩٠١٢٣٤٥٦`（东阿拉伯数字），下游 ASCII 解析崩；UTF-8 下一个 Unicode 数字最多 4 字节，"16 位数字"塞 16 字节缓冲 → 64 字节缓冲区溢出。

## 13. Differential Testing（差分测试）

**英文**：Differential Testing
**一句话**：用两个或多个实现跑同一组输入，对比输出来发现 bug。
**展开**：作者把 RE# 与 Rust regex crate 在 40 万组 regex × 输入上做差分测试，所有差异（~1%）都来自 longest-match 语义——这是 RE# 的设计选择。这是把博客文章升级为工业级声明的关键动作。

## 14. Longest-Match Semantics（最长匹配语义）

**英文**：Leftmost-Longest Match
**一句话**：当存在多个匹配选择时，取"最左 + 在该位置上能匹配的最长子串"。
**展开**：POSIX ERE 和 awk 用 leftmost-longest，Perl / PCRE / Python 用 leftmost-first。RE# 选择 longest-match 是为了和符号导数代数自然对齐，但这是与主流 Python regex 行为差异的来源（约 1%）。理解这点对跨引擎移植 regex 至关重要。

# 术语对照表 · 35 条

| 英文 | 中文 | 简注 |
|---|---|---|
| Regular Expression | 正则表达式 | 描述字符串模式的形式语言 |
| Regular Language | 正则语言 | 能被有限自动机识别的语言族 |
| Derivative of a Regex | 正则表达式的导数 | Brzozowski 1964 提出，对字符求"已读后剩余可匹配什么" |
| Complement | 补集 | `~R` 匹配所有 `R` 不匹配的字符串 |
| Intersection | 交集 | `R & S` 匹配同时被 `R` 和 `S` 接受的字符串 |
| Union / Alternation | 并集 / 选择 | regex 的 `\|` 算子 |
| Concatenation | 连接 | regex 的隐式连接 `RS` |
| Kleene Star | 克莱尼闭包 | `R*` 表示零次或多次重复 |
| Lookahead | 前向断言 | `(?=R)` 不消耗字符地断言后续匹配 R |
| Negative Lookahead | 负向前向断言 | `(?!R)` 断言后续 **不** 匹配 R |
| Lookbehind | 后向断言 | `(?<=R)` 断言此前匹配 R |
| Variable-length Lookbehind | 变长后向断言 | 长度可变的 `(?<=R)`，Java / .NET 实现常退化为 O(n²) |
| Tempered Greedy Token | 节制贪婪 token | `((?!W).)*` 模拟"不含 W 的字符串"的常见 hack |
| Lazy / Non-greedy Quantifier | 惰性量词 | `*?`、`+?`，尽可能少匹配 |
| Greedy Quantifier | 贪婪量词 | `*`、`+`，尽可能多匹配 |
| Backreference | 反向引用 | `\1` 引用前面捕获的子串，超出正则语言能力 |
| Capture Group | 捕获组 | `(...)` 记录匹配的子串 |
| Non-capturing Group | 非捕获组 | `(?:...)` 只分组不捕获 |
| NFA (Nondeterministic FA) | 非确定有限自动机 | 同一输入可同时处于多状态 |
| DFA (Deterministic FA) | 确定有限自动机 | 每个状态对每个输入只有唯一转移 |
| Symbolic Automaton (SFA) | 符号自动机 | 用谓词（区间集合）标号边，高效处理 Unicode |
| Thompson NFA Construction | Thompson NFA 构造 | 1968 年的 regex→NFA 算法，O(m·n) |
| Glushkov NFA | Glushkov NFA | 另一种 regex→NFA 构造，Hyperscan 等引擎采用 |
| Backtracking Engine | 回溯引擎 | 用递归尝试匹配路径，最坏指数时间 |
| Non-backtracking Engine | 非回溯引擎 | 基于 NFA/DFA 模拟，最坏 O(m·n) |
| ReDoS | 正则拒绝服务 | 构造输入让回溯引擎陷入指数时间 |
| Catastrophic Backtracking | 灾难性回溯 | 嵌套量词触发的指数级回溯 |
| Aho-Corasick Algorithm | Aho-Corasick 算法 | 1975 多模式固定字符串匹配，O(n) |
| Leftmost-First Match | 最左优先匹配 | Perl/PCRE 默认语义 |
| Leftmost-Longest Match | 最左最长匹配 | POSIX ERE 与 RE# 默认语义 |
| Find Iter / FindAll | 迭代查找 / 查找全部 | "找所有匹配"的 API，几乎所有引擎最坏 O(m·n²) |
| Differential Testing | 差分测试 | 多实现对比寻找语义偏差 |
| Fuzzing | 模糊测试 | 用随机或半随机输入暴露漏洞 |
| Unicode `\d` | Unicode 数字字符类 | 在多数现代引擎中包含约 370~770 个码点，**不等于** `[0-9]` |
| POSIX Character Class | POSIX 字符类 | 如 `[[:digit:]]`、`[[:alpha:]]`，跨平台兼容性较好 |
| Code Point | 码点 | Unicode 标量值，可对应多字节 UTF-8 编码 |
| UTF-8 | 8 位 Unicode 转换格式 | 变长 1~4 字节编码 Unicode 码点 |
| Buffer Overflow | 缓冲区溢出 | 写入超出缓冲容量，本文示例由 Unicode `\d` 引发 |
| Tag Mining / Tag Survey | 标签挖掘 / 标签调研 | 从 SO data dump 按 `<tag>` 统计常见问题 |
| Stack Overflow Data Dump | Stack Overflow 数据转储 | 公开发布的 SO 全量 XML，本文用约 106 GB 的版本 |

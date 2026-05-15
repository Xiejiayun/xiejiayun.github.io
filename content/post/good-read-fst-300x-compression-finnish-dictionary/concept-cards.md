# 概念卡片 · 关键数据结构与术语

> 配合主文《把 3 GB SQLite 压成 10 MB》一起看，每张卡片对应一个独立可掌握的概念。建议按顺序阅读。

---

## 卡片 1：Trie（前缀树）

**一句话**：一棵把字符串按字符摊开成树的有根多叉树；从根到任意节点的路径就是一个字符串前缀。

**核心性质**
- 查询某个 key 的时间是 O(|key|)，与字典里有多少 key 无关。
- 共享前缀但不共享后缀。`kadun` 和 `kaduille` 共享 `k-a-d-u`，但后面分叉后各自独立。
- 适合 4–6 位数 key 量。10 万级以上的自然语言词库会爆内存。

**典型用法**：自动补全（IDE、搜索框）、最长公共前缀、IP 路由表的初版实现。

---

## 卡片 2：DAFSA（有向无环有限状态自动机）

**别名**：DAWG（Directed Acyclic Word Graph）、Minimal Acyclic FSA、MA-FSA。

**一句话**：把 trie 的所有"结构相同的子树"合并成同一个 DAG 节点，于是同时共享前缀**和**后缀。

**和 trie 的差别**
- Trie 是树：每个节点恰好一个 parent。
- DAFSA 是 DAG：多个 parent 可以共用同一个子图。

**对自然语言为什么有用**：芬兰语 4000 万词形里，"以同一组屈折后缀结尾"的词共享同一条尾巴。Trie 把每条尾巴存 4000 万次，DAFSA 存一次。

**经典应用**：Scrabble 词典、英文拼写检查、压缩词频表。

---

## 卡片 3：FST（Finite State Transducer，有限状态转换器）

**一句话**：在 DAFSA 的边上挂可累加的"权值"，于是从开始状态走到接受状态时，不仅识别了一个字符串，还**输出**一个数字或字符串。

**核心抽象**
- DAFSA = 集合：能告诉你 `kadun` 是不是合法词。
- FST = 映射：能告诉你 `kadun → katu`（lemma）或 `kadun → 47823`（dictionary ID）。

**权值的限制**：必须是**幺半群**（monoid）——有结合律 + 单位元的二元运算。最常用的是 `u64` 加法、字符串拼接。

**实现里的优雅**：Daciuk 等人 2000 年的增量最小化算法在 O(N) 时间构造 minimal FST，前提是 key 流已排序。

**为什么不能 in-place 更新**：插入新 key 要求重新检查所有"已固化"的状态是否仍是 minimal，复杂度退化到 O(N²)。所以 FST 是 **batch build + read-only** 的。

---

## 卡片 4：BurntSushi/fst（Rust crate）

**一句话**：Andrew Gallant（也是 ripgrep 作者）2015 年写的 Rust FST 实现，目前生态里最完整的版本。

**特性**
- 流式 API：可以增量构造 GB 级数据结构而不爆内存。
- `Levenshtein` automaton：FST 与编辑距离自动机求交集 → 模糊查询。
- 正则匹配：FST 与有限自动机求交集 → 复杂查询。
- 集合运算：union、intersection、difference 在 FST 层面就能流式做。
- mmap-friendly：FST 文件可以直接 mmap 进进程，无需反序列化。

**经典测试集**：Common Crawl 2015 年 7 月 archive 里的 16 亿条 URL（134 GB）。BurntSushi 在 8 GB RAM 的机器上构造，花了几个小时，最终二进制 30 GB 左右。

---

## 卡片 5：Levenshtein Automaton（编辑距离自动机）

**一句话**：把"所有与某个目标字符串编辑距离不超过 K 的字符串"编码成一个 NFA / DFA。

**和 FST 的组合**：如果字典是 FST，查询字符串构造一个 K-Levenshtein automaton，**两者求交集**就得到字典里所有"模糊匹配"的词。整个过程是流式的，不需要枚举字典里的每个词去比较。

**算法源头**：Schulz & Mihov 2002, "Fast string correction with Levenshtein automata"。

**实际意义**：你输入 `Homer Simpsom` (有 typo)，FST 在毫秒级返回字典里所有编辑距离 ≤ 2 的合法词。这是搜索框 "did you mean" 的底层。

---

## 卡片 6：黏着语（Agglutinative Language）

**一句话**：通过把表示语法功能的词缀**像积木一样依次拼接**到词根上，来表达复杂语义的语言。

**例子（芬兰语）**
```text
talo               房子
talo-ssa           房子-内格 ("在房子里")
talo-i-ssa         房子-复数-内格 ("在房子们里")
talo-i-ssa-mme     房子-复数-内格-我们的
talo-i-ssa-mme-kin 房子-复数-内格-我们的-也 ("在我们的房子们里也")
```

**反面例子**：英语（屈折型 + 分析型）、汉语（孤立型）。屈折型不"贴标签"而是改变词的形态：`amō → amās → amat`。

**对数据结构的启发**：黏着语的词形组合数 = 词根数 × 后缀链数量，但**后缀链是有限可枚举的**。这正是 FST 通过 suffix sharing 大杀四方的领域。

**其他黏着语**：土耳其语、日语（部分）、匈牙利语、斯瓦希里语、韩语。

---

## 卡片 7：Consonant Gradation（辅音弱化）

**一句话**：芬兰语 / 爱沙尼亚语等语言里，词干的辅音根据后续音节的开闭而发生交替的现象。

**例子**
- `katu`（街道，主格）→ `kadun`（属格）：`t → d`，因为加 `-n` 让音节闭合。
- `tappaa`（杀，第一动词类）→ `tapan`（"我杀"）：`pp → p`。

**为什么数据结构难处理**：直接用规则就能"算出"，但词典必须包含所有变体（因为很多词的弱化是不规则的）。这就是为什么 tsk 必须显式把所有 inflection 装进字典而不能"运行时算"。

---

## 卡片 8：Vowel Harmony（元音和谐）

**一句话**：词缀的元音必须和词根的元音"同类"——前元音 (a, o, u) vs 后元音 (ä, ö, y) 不能在同一个词里混。

**例子**
- 内格后缀有两种变体：`-ssa`（后元音词）vs `-ssä`（前元音词）。
- `talo` + `-ssa` = `talossa` ✓
- `kylä` + `-ssä` = `kylässä` ✓ （不能用 `-ssa`）

**对 FST 的影响**：每个变体后缀都是独立路径，但他们共享中段。FST 的 suffix sharing 在这里仍然有效，因为是从词根的"最后一个变化点"开始合并。

---

## 卡片 9：mmap-as-Deserialization

**一句话**：把数据结构序列化成一个"自描述的内存布局"二进制文件，运行时用 `mmap()` 直接映射进进程地址空间，**省掉解析/反序列化步骤**。

**前提**
- 文件里只用 fixed-width 整数和偏移量（不能有指针）。
- 字节序固定（通常 little-endian）或在 header 标注。
- 所有内部"指针"是相对偏移而非绝对地址。

**优点**
- 启动时间 O(1)：不读盘也不解析。
- 多进程共享同一物理内存：N 个进程读同一字典，只占用一份 RAM。
- 操作系统 page-out 友好：冷数据自动被换出。

**FST 文件**：BurntSushi/fst 的 .fst 文件就是 mmap-friendly 的。10 MB 的字典在内存占用上几乎可以忽略。

**反面例子**：Pickle / Protocol Buffers / JSON。都需要先读到内存再解析。

---

## 卡片 10：Zequals 方法

**一句话**：英国数学普及作者 Rob Eastaway 提出的"心算估计法"：所有数字都圆到**一位有效数字**，让估算结果走得到位、记得住。

**Quinn 在文章里的用法**：所有数字都用 zequals 取过，比如 "10 MB" 实际是 7 MB，"300x" 实际是约 280–320x，"50 MB" 实际是约 47 MB。

**为什么重要**：让读者**记住论点骨架而不是数字细节**。读完文章你会记住"某个独立开发者用 FST 把字典压了 300 倍"，而不是 "from 3,072 MB to 9.7 MB"。这是 Quinn 作为科普写作者的功夫。

**适用场景**：博客、教学、产品 OKR、第一次提案。**不适用**于会计、金融、医学。

---

## 卡片 11：Caplanian / "Reinvent a few wheels"

**一句话**：经济学家 Bryan Caplan 在《The Case Against Education》里的论点——学校教育大多是 signaling 而非 skill transfer。技能主要靠"在已有 sense 的领域刻意重做几次问题"来获得。

**Quinn 的应用**：你需要重新造**几个**轮子，才能走到"造轮子"知识的边缘——不是几千个，也不是零个。

**对工程师的启示**：
- "已被解决的问题" 不是停止学习的理由，是开始学习的标记物。
- LLM 给了我们"读完前人成果"的便利，但代替不了"亲手重做一次"才能积累的肌肉记忆。
- 经验密度 = 重做次数 / 单位时间。Quinn 一个周末把 v1 → v2 重做一次，密度极高。

---

**配套阅读**：主文《把 3 GB SQLite 压成 10 MB》第 2-6 节会反复使用以上术语；BurntSushi 的 [transducers 博文](https://burntsushi.net/transducers/) 会把卡片 1-5 用 Rust 代码完整演示一遍。

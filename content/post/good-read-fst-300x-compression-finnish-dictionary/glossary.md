# 英中对照术语表 · FST 与黏着语形态学

> 主文与延伸阅读中涉及的关键词。涵盖数据结构、形态学、Rust 生态三大门类。

## 数据结构与算法

| English | 中文 | 注解 |
|---|---|---|
| Trie | 前缀树 / 字典树 | 多叉树结构，共享前缀。 |
| DAFSA (Directed Acyclic Finite State Automaton) | 有向无环有限状态自动机 | 又称 DAWG。共享前缀和后缀。 |
| DAWG (Directed Acyclic Word Graph) | 有向无环词图 | DAFSA 的别名。 |
| Minimal Acyclic FSA | 最小化无环有限状态自动机 | DAFSA 的"最小"版本，状态数最少。 |
| FST (Finite State Transducer) | 有限状态转换器 | 边带权值的 DAFSA，能识别 + 输出。 |
| FSA / FSM | 有限状态自动机 / 有限状态机 | 通用术语。 |
| Acceptor / Recognizer | 接受器 / 识别器 | FSA 的角色——只判断 yes/no。 |
| Transducer | 转换器 | FST 的角色——输入字符串 → 输出值。 |
| Determinization | 确定化 | 把 NFA 转换为 DFA 的过程。 |
| Minimization | 最小化 | 合并等价状态以减小自动机规模。 |
| Daciuk Algorithm | Daciuk 算法 | 2000 年的增量最小 FSA 构造算法。 |
| Levenshtein Automaton | 编辑距离自动机 | 接受所有"与目标距离 ≤ K"字符串的自动机。 |
| Levenshtein Distance | 编辑距离 | 把字符串 A 变成 B 所需的最少插入/删除/替换次数。 |
| Suffix Sharing | 后缀共享 | DAFSA/FST 的核心压缩机制。 |
| Prefix Sharing | 前缀共享 | trie 的核心压缩机制。 |
| Common Suffix | 共同后缀 | 多个字符串末尾相同的子串。 |
| Path Compression | 路径压缩 | 把单链节点合并以节省空间。 |
| Patricia Trie | 帕特里夏树 | 路径压缩的二进制 trie。 |
| Radix Tree / Radix Trie | 基数树 | 路径压缩的 trie 变体。 |
| LOUDS | 层序一元退化串编码 | 一种简洁数据结构，常用于压缩 trie。 |
| Marisa-trie | 玛丽萨树 | 基于 LOUDS 的静态 trie 实现。 |
| FTS (Full Text Search) | 全文检索 | SQLite/Postgres 等数据库的索引扩展。 |
| Inverted Index | 倒排索引 | 搜索引擎的核心数据结构。 |
| Posting List | 倒排表 | 倒排索引中"每个词指向哪些文档"的列表。 |
| Term Dictionary | 词项字典 | Lucene 中存储所有 term 的索引。 |
| mmap (Memory-Mapped File) | 内存映射文件 | 把文件映射进进程地址空间。 |
| Zero-Copy | 零拷贝 | 不在用户态/内核态间复制数据。 |
| Monoid | 幺半群 | 代数结构，FST 边权必须是幺半群。 |

## 形态学与语言学

| English | 中文 | 注解 |
|---|---|---|
| Agglutinative Language | 黏着语 | 通过堆叠词缀表达语法功能的语言。 |
| Inflectional Language | 屈折语 | 通过改变词形表达语法功能的语言（如拉丁语）。 |
| Analytic Language | 分析语 / 孤立语 | 依靠词序和虚词的语言（如汉语）。 |
| Morphology | 形态学 | 研究词的内部结构的语言学分支。 |
| Lemma | 词根 / 词目 | 词典中的标准形（如 "go" 是 "went" 的 lemma）。 |
| Inflection | 屈折变化 | 一个词根的所有合法形式。 |
| Declension | 名词变格 | 名词/形容词的格变化。 |
| Conjugation | 动词变位 | 动词的时态/人称变化。 |
| Case | 格 | 名词的语法范畴（主格、宾格、内格等）。 |
| Nominative | 主格 | 主语用的格。 |
| Genitive | 属格 | 表示"的"的格。 |
| Inessive | 内格 | "在...里" 的格（芬兰语 `-ssa/-ssä`）。 |
| Possessive Suffix | 物主后缀 | 表示"我的/你的"等的后缀（芬兰语 `-ni/-si/-nsa`）。 |
| Clitic | 附着词 / 助词 | 像后缀一样附着但语法独立的词（如芬兰语 `-kin` "也"）。 |
| Consonant Gradation | 辅音弱化 / 辅音交替 | 芬兰语中辅音随音节开闭变化的现象。 |
| Vowel Harmony | 元音和谐 | 词缀元音必须与词根元音同类。 |
| Front Vowel / Back Vowel | 前元音 / 后元音 | 元音和谐的两个对立类别。 |
| Orthography | 正字法 / 拼写规则 | 一种语言的书写规范。 |
| Morpheme | 词素 | 最小的有意义的语言单位。 |

## Rust 与工程生态

| English | 中文 | 注解 |
|---|---|---|
| Crate | Rust 包 | Rust 的代码分发单元。 |
| Cargo | Rust 包管理器 | Rust 的官方构建工具。 |
| MUSL | 静态 libc 实现 | 用于编译完全静态链接的 Linux 二进制。 |
| Static Linking | 静态链接 | 把所有依赖编译进单一二进制。 |
| Cross-Compilation | 交叉编译 | 在 A 平台上编译 B 平台的可执行文件。 |
| RIIR (Rewrite It In Rust) | "用 Rust 重写一下" | 社区梗，常用于嘲讽过度重写。 |
| TUI (Terminal User Interface) | 终端用户界面 | 在终端里运行的图形界面。 |
| FFI (Foreign Function Interface) | 外部函数接口 | 跨语言调用的机制。 |
| Bindgen | 绑定生成器 | Rust 自动生成 C 库绑定的工具。 |

## 重要人物与项目

| English | 中文/角色 | 注解 |
|---|---|---|
| Andrew Quinn | 文章作者 | 住芬兰的工程师，Taskusanakirja / Siilikuin 创始人。 |
| BurntSushi (Andrew Gallant) | Rust 数据结构权威 | ripgrep、fst crate、xsv 等众多明星项目的作者。 |
| Mike McCandless | Lucene 核心开发者 | 推动 Lucene 4.0 采用 FST 作为 term dictionary。 |
| Jan Daciuk | 波兰计算语言学家 | Minimal acyclic FSA 增量构造算法的提出者。 |
| Rob Eastaway | 英国数学普及作家 | "zequals" 估算方法的提出者。 |
| Bryan Caplan | 美国经济学家 | The Case Against Education 作者，"reinvent a few wheels" 思想的源头之一。 |
| ripgrep | Rust 命令行工具 | grep 的 Rust 重写，BurntSushi 作品。 |
| Lucene | Java 搜索引擎库 | Elasticsearch / Solr 的底层。 |
| Common Crawl | 公共网络爬虫数据集 | BurntSushi 用来测试 1.6 亿 URL 的源数据。 |
| Taskusanakirja (tsk) | 芬兰语词典软件 | Quinn 的项目，本文主角。 |

---

**编纂说明**：本表服务于主文导读，未尝试穷尽。如需更专业的形态学术语，参考 [WALS](https://wals.info/) 或 [Glottolog](https://glottolog.org/)；如需更专业的 FST 文献，参考 [OpenFst 项目](https://www.openfst.org/)。

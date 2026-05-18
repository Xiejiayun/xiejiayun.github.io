# 术语表 · The Third Hard Problem · Glossary

英中对照术语表，按字母序排列。涵盖文章中出现的所有核心术语、相关概念与人物。

| 英文 | 中文 | 简要说明 |
|---|---|---|
| Abstract Syntax Tree (AST) | 抽象语法树 | 编译器将源码 token 序列组织成的树结构；空间组织器的典型例子。 |
| AppKit | Apple 桌面 UI 框架 | macOS 原生应用框架；Kashitsyn 未提，但与 bundle 哲学相关。 |
| Bazel | 谷歌开源构建工具 | 从 Google Blaze 演化而来；专为按项目切的 monorepo 设计。 |
| BeFS | BeOS 文件系统 | Be 操作系统的 web 化文件系统实验，引入数据库式属性查询，但未流行。 |
| Blaze | Google 内部构建工具 | Bazel 的前身；按项目（而非语言）组织代码的构建系统。 |
| Bundle | 应用包 | macOS .app / Snap / Flatpak 的形式；把一个应用相关的所有文件聚成一个目录。 |
| B-tree | B 树 | 数据库中组织有序键空间的平衡树。 |
| Buck | Buck 构建工具 | Facebook 开源的 Bazel 风格构建系统。 |
| Cache invalidation | 缓存失效 | Phil Karlton 双难之一；缓存何时该被推翻、刷新的难题。 |
| Cephalopod | 头足类 | 章鱼、乌贼所属类群；其相机型眼与脊椎动物趋同进化。 |
| Christopher Alexander | 克里斯托弗·亚历山大（1936-2022） | 建筑师 + 数学家；*A Pattern Language* 与 *A City is not a Tree* 的作者。 |
| Cladistics | 支序分类学 | 现代生物分类法，依据共同祖先（基因继承）而非可见性状切分。 |
| Conway's Law | Conway 定律 | 系统结构镜像设计该系统的组织沟通结构。 |
| Convergent evolution | 趋同进化 | 不同物种独立演化出相似性状（如头足类与脊椎动物的眼）。 |
| DAG (Directed Acyclic Graph) | 有向无环图 | 比树更一般、比图更窄的结构；依赖图的真实形态。 |
| Design doc | 设计文档 | 软件工程中的技术设计稿；本质是 web → tree → string 的写作过程。 |
| DOM | 文档对象模型 | 浏览器中 HTML 的树形表示。 |
| Flatpak | Linux 应用打包格式 | bundle 哲学在 Linux 上的实现之一。 |
| Forge | 锻造、构造 | 引申为代码托管平台（如 Forgejo）。 |
| Galois connection | Galois 连接 | 范畴论 / 序理论中的成对映射；Kashitsyn 用它形式化"好名字"。 |
| Hierarchy | 层级 / 层次 | 树形结构的同义词；人类大脑组织信息的默认形式。 |
| Horizontal gene transfer | 水平基因转移 | 物种间（而非亲子之间）的基因传递；让支序分类学也不能完美。 |
| Incremental computation | 增量计算 | rust-analyzer 等现代 IDE 后端的核心模型——只重算被影响的部分。 |
| k-d tree | k-d 树 | 多维空间索引结构，常用于图形与最近邻搜索。 |
| Karlton (Phil) | 菲尔·卡尔顿 | Netscape 工程师，提出"两个 hard things"俏皮话。 |
| Lattice | 格 | 序理论结构；每对元素都有上确界和下确界。 |
| Levittown | 莱维敦 | 美国战后规划郊区代表；Alexander 的"人造城市"典型。 |
| LSP | 语言服务器协议 | IDE 后端与编辑器之间的通用协议。 |
| Make-believe | 假装游戏 | 字面"假装相信"；学校工程课的婉转贬义。 |
| Monorepo | 单体仓库 | 多项目集中在一个 git 仓库的开发模式。 |
| Morphological taxonomy | 形态学分类 | 旧式生物分类法，基于可见性状（有无脊椎、是否飞行等）。 |
| NSTextView | macOS 原生文本视图 | Cocoa 的富文本组件。 |
| Object ownership graph | 对象所有权图 | Rust 借用检查器关心的对象间所有权关系；理想形态是树。 |
| ORM (Object-Relational Mapping) | 对象关系映射 | 把对象图压成关系表的工具；又一次 tree mapping 灾难。 |
| Package manager | 包管理器 | npm / pip / cargo / apt；都要做依赖图的某种 tree 化或 DAG 化决策。 |
| Pants | Pants 构建工具 | Twitter / Foursquare 出来的 Bazel 风格构建系统。 |
| Phylogeny | 系统发生 / 演化树 | 物种演化的关系树。 |
| Please | Please 构建工具 | Thought Machine 出品的 Bazel 风格构建系统。 |
| Plug'n'Play (PnP) | 即插即用 | yarn berry 的依赖解析模式，替代 node_modules tree。 |
| Pinker (Steven) | 史蒂芬·平克 | 哈佛认知科学家；*The Sense of Style* 作者。 |
| Reptilia | 爬行纲 | 传统分类中的爬行动物纲；现代系统发生学下不再被视为单系群。 |
| Rust borrow checker | Rust 借用检查器 | Rust 编译器的核心；强制把对象交互 web 压成所有权 tree。 |
| Semilattice | 半格 | 允许重叠的偏序结构；Christopher Alexander 给"natural city"的数学结构。 |
| Shred-everything | 散落式打包 | Linux 经典做法——把应用文件按类型散落到 /usr/lib、/etc 等。 |
| Siena | 锡耶纳 | 意大利古城；Alexander 的"自然生长城市"典型。 |
| Skeumorph | 拟物 | 数字界面模仿物理对象（如文件夹图标模仿纸质文件夹）。 |
| SLIP (Serial Line Internet Protocol) | 串行线 IP | RFC 1055；古早的 IP over serial 协议。 |
| Snap | Linux 应用打包格式 | Canonical 出品，bundle 哲学在 Linux 上的另一实现。 |
| String | 字符串 / 线性序列 | Pinker 写作三元组的最低层级——读者眼中看到的词流。 |
| Tag-based system | 标签系统 | 替代树形分类的多对多组织方式；web 化的近似。 |
| Tree | 树 | 无环连通图，每个节点有唯一父节点；空间组织器的典型形式。 |
| Tree mapping | 树映射 | 本文核心术语——把图嵌入到树的过程。 |
| Wilkins (John) | 约翰·威尔金斯 | 17 世纪英国学者，尝试设计哲学语言；Borges 讽刺对象。 |
| WinFS | Windows Future Storage | 微软在 Longhorn 时代规划的"基于关系数据库的文件系统"；未发布。 |
| `node_modules` | Node 依赖目录 | npm 把 DAG 实例化为完整树时产生的庞大目录，体积是 tree mapping 的物理证据。 |
| `Rc<RefCell<T>>` | Rust 共享所有权 + 内部可变性 | 在 Rust 中手工还原一条"非树边"的标准组合。 |
| `Arc<Mutex<T>>` | 跨线程共享所有权 + 互斥 | 同上的多线程版本。 |
| `catch_unwind` | Rust panic 捕获 | 在 panic 边界手工切分隔离域；rust-analyzer 用它隔离单功能崩溃（见 matklad 系列）。 |

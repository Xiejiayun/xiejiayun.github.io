# 概念卡片 · The Third Hard Problem · Tree Mapping

12 张可独立阅读的核心概念卡片。每张卡片：**定义 → 出处 → 在工程中的体现 → 工程含义**。

---

## 卡片 1｜Tree Mapping（树映射）

- **定义**：把一张图（web / lattice / general graph）嵌入到一棵树（hierarchy / tree）的过程，必然伴随信息丢失或结构扭曲。
- **出处**：Roman Kashitsyn, *The Third Hard Problem* (mmapped.blog #48, 2026-02-28)。
- **在工程中**：文件系统目录、monorepo 结构、ORM、类继承、Rust 所有权图、Agent 上下文窗口——几乎所有"组织信息"的工程实践都是 tree mapping 的一次具体实例。
- **工程含义**：当你为系统设计卡住时，不要怪自己，承认这是一个**没有最优算法解**的问题；并对自己提出三问——What web is being flattened? Which links are sacrificed? Must the target be a tree?

---

## 卡片 2｜Phil Karlton's Two Hard Things（命名 + 缓存失效）

- **定义**：计算机科学的"古典两难"——naming things 与 cache invalidation。
- **出处**：Phil Karlton 口耳相传，被 Martin Fowler 在 bliki/TwoHardThings 收录。
- **在工程中**：API / 变量 / 文件命名；CDN / Redis / CPU 缓存的失效策略。
- **工程含义**：这两件事都"没有算法可解"，需要 empathy 与 systems thinking；Kashitsyn 的工作是把 tree mapping 加入这张清单。

---

## 卡片 3｜Web of Ideas vs Tree of Phrases vs String of Words

- **定义**：Steven Pinker 关于写作本质的三层映射——作者头脑中的概念网（web）→ 用句子的树（tree）组织 → 输出为读者眼中的词语链（string）。
- **出处**：Steven Pinker, *The Sense of Style* (2014)。
- **在工程中**：写设计文档、技术博客、代码注释，本质都在做这次"网 → 树 → 链"的有损三层压缩；这就是写作痛苦的来源。
- **工程含义**：当你下笔卡住，不是文笔差，是拓扑嵌入难——给自己更多耐心。

---

## 卡片 4｜Semilattice（半格）vs Tree（树）

- **定义**：半格（semilattice）是允许两个集合"重叠"而不要求一个包含另一个的偏序结构；树是严格不允许重叠的特殊半格。
- **出处**：Christopher Alexander, *A City is not a Tree* (1965)。
- **在工程中**：自然生长的城市（Siena、Kyoto）是 semilattice；规划出来的城市（Levittown、Chandigarh）是 tree。
- **工程含义**：当你的系统让用户感到"压抑"或"功能割裂"，多半是你把一个本该是 semilattice 的关系压成了 tree。

---

## 卡片 5｜Cladistics（支序分类学）

- **定义**：现代生物分类法，以**共同祖先 / 基因继承**为切分依据，取代传统的形态学（按可见性状切）。
- **出处**：Willi Hennig, *Phylogenetic Systematics* (1966)。
- **在工程中**：与"按真实存在的、不可分割的边切"对应——比如优先按依赖关系而不是按命名空间切代码库。
- **工程含义**：Tree mapping 选轴时，**优先保留那些真实、不可分的边**；让可选属性变成 tag / index / metadata。

---

## 卡片 6｜Conway 定律（Conway's Law）

- **定义**：系统结构最终镜像设计该系统的组织的沟通结构。
- **出处**：Melvin Conway, *How Do Committees Invent?* (1968)。
- **在工程中**：monorepo 按团队切 vs 按语言切的本质冲突；Google 选择 Bazel 是因为他们必须支持组织拓扑。
- **工程含义**：tree mapping 是纵向（信息嵌入），Conway 定律是横向（组织映射）——两者在同一份代码库里同时发生作用。

---

## 卡片 7｜Borges 的中国百科全书

- **定义**：Jorge Luis Borges 在《约翰·威尔金斯的分析性语言》里虚构的一本中国百科全书，把动物按荒谬的轴分类——"属于皇帝的"、"被熏制的"、"远看像苍蝇的"……
- **出处**：J.L. Borges, *The Analytical Language of John Wilkins* (1942)；Foucault《词与物》序言。
- **在工程中**：任何"看起来怪"的分类法，其实只是 tree mapping 选了一组陌生的轴；没有客观正确的分类轴。
- **工程含义**：在评审分类方案时，先问"我们为什么选这个轴"，再问"什么是被这个轴牺牲掉的"。

---

## 卡片 8｜Bundle vs Shred-Everything

- **定义**：应用打包的两种哲学——bundle 把所有相关文件放在一个目录里（macOS .app、Snap、Flatpak）；shred-everything 按文件类型分散（Linux 经典 /usr/lib + /usr/man + /etc/）。
- **出处**：本文，对比 macOS / Windows 与 Linux。
- **在工程中**：bundle 对用户友好，shred 对工具友好；Linux 桌面通过 Snap/Flatpak 在向 bundle 漂移。
- **工程含义**：你选哪一种取决于"哪条边更重要" —— 用户视角的"这个东西是什么应用" vs 系统工具视角的"这个文件是什么类型"。

---

## 卡片 9｜Monorepo 的双轴困境

- **定义**：多语言项目目录必须在"按组件切"（/payments/{ts,rs}）vs "按语言切"（/{ts,rs}/payments）之间选一种。
- **出处**：本文，Kashitsyn 的 monorepo 案例。
- **在工程中**：Google 用 Bazel 强制按项目切；Node.js 社区按语言切（package.json）；混合项目通常用 Nx / Turborepo / Pants。
- **工程含义**：Bazel 之类的语言无关构建工具存在的根本原因，是为了让"按组件切"的人类直觉，能从"按语言切"的工具世界里被解救出来。

---

## 卡片 10｜Borrow Checker 的本质

- **定义**：Rust 借用检查器的本质工作，是强迫程序员把对象交互图（web）压成对象所有权树（tree）。
- **出处**：本文结尾段，Kashitsyn 直接点名。
- **在工程中**：`Rc<RefCell<T>>`、`Arc<Mutex<T>>`、weak references——都是用 runtime 手段恢复 tree mapping 丢掉的非树边。
- **工程含义**：Rust 学习曲线的真相不是"内存安全难学"，而是"我必须把脑子里的 web 重新规划成 tree"。

---

## 卡片 11｜node_modules 与依赖图的 web 性

- **定义**：JavaScript 依赖图本质是 DAG（有向无环图），但 npm 历史上把它实例化为完全嵌套的 tree（每个包带自己的依赖子树）。
- **出处**：本文结尾段；pnpm / yarn berry PnP 的背景。
- **在工程中**：npm 的 hoisting 算法、pnpm 的 symlink 内容寻址、yarn berry 的 Plug'n'Play——都是用不同手段让依赖图重新变回 web。
- **工程含义**：当你看到 node_modules 体积异常，知道那是 tree mapping 留下的物理痕迹。

---

## 卡片 12｜Be Intentional（核心方法论）

- **定义**：Kashitsyn 给出的唯一普适建议——在做 tree mapping 时，不要因为习惯而下意识选择，要明知地选择。
- **出处**：本文结论段。
- **在工程中**：每次做 schema 设计、目录结构调整、类继承设计、API 资源建模时，**先停下来，把"被压扁的 web 是什么"画出来**。
- **工程含义**：三问——What web is being flattened? Which links are sacrificed? Must the target medium be a tree in the first place?

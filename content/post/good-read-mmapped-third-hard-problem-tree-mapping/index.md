---
title: "【好文共赏】第三个难题：Roman Kashitsyn 把\"树映射\"提升为继命名与缓存失效之后的计算机科学第三难"
description: "mmapped.blog 的 Roman Kashitsyn 写了一篇横跨文件系统、写作、城市规划、生物分类与 Rust 借用检查器的元论文，把\"把一个图嵌入到一棵树\"这件每天都在悄悄折磨我们的事——命名为 tree mapping，与 Phil Karlton 的命名和缓存失效并列，封为第三个 hard problem。"
date: 2026-05-18
slug: "good-read-mmapped-third-hard-problem-tree-mapping"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 计算机科学
    - 抽象建模
    - 数据结构
    - 软件架构
    - 信息组织
    - Christopher Alexander
    - Conway定律
draft: false
---

## 📌 好文共赏 | Editor's Pick

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[The Third Hard Problem](https://mmapped.blog/posts/48-the-third-hard-problem)
> 作者：Roman Kashitsyn（DFINITY 系统工程师，mmapped.blog 站长，前 Google）
> 发布：2026-02-28（2026-05-14 在 HN 重新引爆：144 分 / 62 评论）
> 阅读时长：原文约 12 分钟（中文导读约 35 分钟）
>
> 多模评分：Opus **9.0** / 交叉评审 **8.8** / 综合 **8.9 / 10**
>
> 一句话推荐：当大多数工程文章在比 GPU 利用率、token 价格和 BPF 字节码时，Kashitsyn 安静地拿起一把更古老的尺子——**"我们总是被迫把一个图揉进一棵树里"**——量遍了文件系统、写作、城市规划、生物分类、ORM 与 Rust 借用检查器，并把它命名为 **tree mapping**，与 Phil Karlton 的"命名"和"缓存失效"并列封为计算机科学的第三个 hard problem。

---

## 一、为什么这篇短文值得读

Phil Karlton 的那句"计算机科学只有两个难题——命名与缓存失效"已经被印在了 T 恤、马克杯、HN 评论框的 placeholder 上。它好笑、好背、看似把这门学科最玄学的两件事都吃掉了，于是过去 25 年我们一边重复这句俏皮话，一边没人补第三条。

Roman Kashitsyn 这篇 ~12 分钟的文章，第一次让我读到一个**配得上被排进那张清单的候选**。他的提议是：

**第三个难题，是 tree mapping——把一个一般的图（web / lattice）嵌入到一棵树（hierarchy）里。**

为什么这件事配得上"难题"这个称呼？因为它满足 Karlton 那两个原始项的共同结构：

- **没有算法可解**——好名字要靠共情，缓存失效要靠系统思考，而把一个有交叉关系的概念网压成一根目录路径，同样没有通用解；
- **几乎无处不在**——文件系统、目录、章节、组织架构、数据库设计、类继承、所有权图、依赖图、cookbook 章节顺序……一旦你认出这个模式，就再也看不见别的；
- **它的痛苦是结构性的，不是工具性的**——换一个数据库、换一个编辑器、换一种语言都不能根治；你只能选择"扭曲哪一根边"。

而这篇文章罕见的地方在于：作者把这一抽象命题，**用五个完全不同领域的具体例子撑了起来**——Linux 包结构 vs macOS bundle、monorepo 按组件还是按语言切、写作里"把意念之网压成词语之链"、Christopher Alexander 1965 年那篇《A City is not a Tree》、生物学的形态学分类 vs 进化树（cladistics），最后落回 MongoDB、Rust 借用检查器和 `node_modules`。

它**不是一篇技术博文**，它是一篇**元论文（meta-essay）**——讨论的不是"如何更好地用 Rust 写一个 LSP 服务器"，而是"为什么我们写任何 LSP 服务器时都会在同一个地方流血"。

这一点与我之前写的 [《matklad：Conway 定律才是软件架构的母题》](/post/good-read-matklad-learning-software-architecture/) 形成一种几何上的对位：matklad 告诉你**社会拓扑会复刻到代码拓扑**（Conway 定律是横向的），Kashitsyn 告诉你**所有"组织"的天然形式是树，而所有"内容"的天然形式是网**（tree-mapping 是纵向的）。两篇文章像同一张二维码的横/纵扫描线，合起来才能解出"为什么我们在 2026 年还在为目录结构吵架"。

## 二、第一刀：trees 是空间的语言，webs 是思想的语言

Kashitsyn 起手就抛出一个看似平淡、其实极锋利的观察：**人脑的空间感是为物理世界优化的——而物理世界的特征是 hierarchical、localized**。

> 原文："One of the defining features of a physical space is its hierarchical, localized structure. We perceive each bit of space as self-contained and interacting only with nearby bits."

为什么我们一谈"组织信息"就先想到目录、章节、taxonomy？因为我们的大脑就是这么进化出来的——它已经为"原子组成分子、分子组成身体、身体组成种群、种群构成生态"这种**层级嵌套**的世界优化了数百万年。

但**信息不是这样的**。一篇维基百科页面会指向几百篇别的页面；一个数学概念在三本教材里有三种"起源"；你家牙医的账单同时属于"医疗"、"今年税务"、"年度档案"和"X 月份家庭支出"。Kashitsyn 用了一个直接的隐喻：**ideas form intricate webs that penetrate rigid boundaries**——思想织成的网会刺穿任何僵硬的边界。

而计算机科学里**最常用的数据结构**——B-tree、k-d tree、AST、目录树、DOM——**全是树**。Kashitsyn 一句话点透了为什么：

> 原文："Trees are intimately related to spaces as they are universal space organizers."

树之所以好用，正因为它是**空间组织器**：B-tree 组织有序键空间，k-d 树切多维空间，AST 组织线性 token 序列。但当我们试图用同一把工具去组织**非空间的东西**——意义、关系、引用、所有权——树就开始变形扭曲，**而我们却以为是自己的设计能力不够**。

Tree mapping 这个名字之所以精准，是因为它直接点出了**问题不在树本身、也不在图本身，而在那个"映射"动作里**：你必须扭曲一些东西、丢弃一些边、复制一些节点，才能把一张 N 维的网压进一棵一维深度的树。

## 三、第二刀：文件系统是 1980 年代留下来的考古层

第一个具体战场是文件系统。Kashitsyn 拿出一个所有人都遇到过的场景：

> 原文："Imagine receiving a bill from your dentist. How do you file it? In a common archive folder? In a more specific 'medical' folder? In the XXXX year taxes project folder for future tax returns? Or copy it and choose all the options at once?"

Dropbox 时代了，你依然只能把那张牙医账单放进一个目录。"选哪个"这个问题在维多利亚时代的绅士书信整理桌上是有意义的——纸只能放进一个抽屉——**但在 2026 年这是个完全自我强加的限制**。我们的分布式文件系统在用户接口层"继承了物理世界的几乎所有约束"。

接下来 Kashitsyn 把这把刀从用户场景滑向了工程师每天面对的两个具体战场：

**战场 A：操作系统的应用打包**

- macOS / Windows 选择了 **bundle**：一个 `.app` 目录里塞下二进制、库、资源、配置——文件按"它属于哪个应用"切；
- Linux 历史上选择了 **shred-everything**：库去 `/usr/lib`、文档去 `/usr/man`、配置去 `/etc/`——文件按"它是什么类型"切。

两种切法**各自都是把那张"应用-类型"双轴的网压成树时丢掉了一根轴**。Linux 这种切法让 `man` 命令只需要看一个固定路径，但代价是软件管理变成噩梦；于是 macOS 风格的 bundle 思想又通过 **Snap 和 Flatpak** 反向渗透了 Linux 桌面。

**战场 B：monorepo 的目录结构**

一个有 TypeScript 前端 + Rust 后端的项目，你目录里应该写 `/acme/payments/index.ts` + `/acme/payments/main.rs`（按组件切），还是 `/acme/ts/payments.ts` + `/acme/rs/payments.rs`（按语言切）？

Kashitsyn 一针见血地指出：**按组件切对人友好，因为它反映了组织结构**（这里他直接挂了一个 Conway 定律的链接）；但绝大多数构建工具不支持这种切法，所以**工具的强力会把你拽回按语言切的世界**。

> 原文："Slicing by component is easier for humans because it reflects the organizational structure, but most tools don't support this setup, forcing a technology-centric approach."

只有 Google 这种规模的工程组织咬牙啃下这块骨头：他们用 `/search`、`/shopping`、`/maps` 这种**按项目切**的 monorepo，代价是要发明一整套 language-agnostic 的构建工具，这就是 **Blaze → Bazel** 以及它的衍生家族（Pants、Buck、Please）的来源。

读到这里你会突然意识到一件事：**Bazel 之所以存在，从根上是因为人类的工程组织拓扑（按团队 / 按产品）与编译工具偏好的拓扑（按语言）打架**——Bazel 是为了把"按组件切"的人类直觉，从"按语言切"的工具世界里救出来。

这里 Kashitsyn 留了一个极有意思的暗扣：BeFS 和 WinFS 都试过把文件系统改成 web 形态，最后都没能改变现状；但他暗示在 tags 和 links 渐渐成为公共词汇的时代，**文件系统终究可能向 web 化演化**。读到这里我立刻想起 [《DuckDB 在 2026 年从零设计一个数据库 wire 协议》](/post/good-read-duckdb-quack-protocol/) 里 DuckDB 团队的论证——数据系统的 wire 协议同样在被迫从"行/列树"转向"列簇 + 元数据图"，是同一个 tree → web 漂移的另一个截面。

## 四、第三刀：写作就是把一张概念网压成一根句子链

第二个战场是文学。Kashitsyn 引用了 Steven Pinker 的一句话，几乎可以独立成一个章节：

> 原文（Pinker）："the writer's goal is to encode a web of ideas into a string of words using a tree of phrases."

注意这句话的三层结构：

| 输入 | 媒介 | 输出 |
|---|---|---|
| **web** of ideas | **tree** of phrases | **string** of words |

写作就是一次三层映射：作者头脑里那张密集的概念网 → 章节-段落-句子的树状结构 → 最终落到读者眼睛上的线性单词序列。每一步都丢信息：

- web → tree：丢掉横向交叉；
- tree → string：丢掉并行性。

读者反过来要做三层重建。**而写作之所以痛苦，正是因为这三层压缩 + 重建是 lossy 的**。Kashitsyn 顺手丢出 Gene Fowler 那句被引用了一百年的笑话："Writing is easy. All you do is stare at a blank sheet of paper until drops of blood form on your forehead."——读到这里你会突然理解，那滴血**不是因为找不到词，而是因为你在做一次没有最优解的拓扑嵌入**。

最致命的一击在数学教材这一段：

> 原文："Math might seem like a Lego brick tower with simple concepts at the foundation and complexity gradually increasing toward the top. ... Yet, the choice of foundational blocks is often arbitrary."

数学看起来是树——从公理生定理，从简单到复杂，从 Euclid 到 Bourbaki 这种连贯叙述都遵循这个模板。**但作为"地基"的那个砖是可以任选的**——你可以从集合论起步，可以从范畴论起步，可以从直觉主义起步——**因为底下的数学概念本身就是一张网，不是一棵树**。

Kashitsyn 在一个脚注里写了一句让我合上电脑发了几分钟呆的话：他说自己学完实分析几个月后，**因为后来在学常微分方程，才突然真正理解了"极限"是什么**——他甚至说**自己对"自然数"的理解都会随着每本新读的教材而变化**。

这条脚注道出了 tree mapping 的最深一层痛感：**当一个概念在网里有多条路径连接到其他概念时，从不同方向接触它，会得到不同的它**。教科书的"目录"必须选一条路径来呈现，于是每一本教科书都构造了一个不同的"数学"。

> 原文："The next time you sit down to an empty design doc and don't know where to start, be kind to yourself. You're solving a hard problem."

对所有写过 RFC、设计文档、技术博客的人，这句话价值千金——**你卡住不是因为你笨，是因为你在做一次没有保证存在最优解的拓扑嵌入**。

## 五、第四刀：Christopher Alexander 1965 年就吵过的架

到了第三战场——城市规划——Kashitsyn 调出了一篇 1965 年的传奇论文：建筑师 + 数学家 Christopher Alexander 的 **《A City is not a Tree》**。

Alexander 把城市分成两类：

- **设计出来的城市**（artificial cities）：Levittown、Chandigarh——居住区、学校、商场被规划进互相隔离的"邻里单元"，**结构是树**；
- **长出来的城市**（natural cities）：Siena、Kyoto——工作、生活、娱乐互相交叠，**结构是 semilattice（半格）**。

Alexander 的核心论断：**人造城市感觉"压抑、缺少某种秘密成分"，而长出来的城市让人感到"生活与舒适"——这种差别的源头是底层数学结构的不同**。

读到这里你会发现：**Alexander 在 1965 年解决的，本质上就是一个 tree mapping 问题**——人类社会关系（一个半格 / 一张网）必须被嵌入到一个具体地形上的具体建筑布局（一棵物理实体的树）里，而**没有 canonical mapping**。

Alexander 自己也承认：

> 原文（Alexander 转述）："I must confess that I cannot yet show you plans or sketches. It is not enough merely to make a demonstration of overlap — the overlap must be the right overlap."

也就是说，Alexander 本人都拿不出一张"半格城市"的设计图，因为**没有算法能告诉你哪些 overlap 是对的 overlap**。

这里 Kashitsyn 给"工程师"递了一支烟——**这不是计算机科学专有的难题**。建筑学被这个问题折磨了至少 60 年，仍然没有"解"。我们今天在 monorepo / ORM / 类继承里挣扎的，是同一组困境在另一个媒介上的投影。

（这一点也让我重新理解了我之前推过的 [《Quack：DuckDB 在 2026 年从零设计一个数据库 wire 协议》](/post/good-read-duckdb-quack-protocol/) 与 [《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/)——这些都是同一个 web → tree 嵌入问题在不同抽象层的不同变种：wire protocol 要把"列簇关系图"嵌入"字节流序列"，Emacs 化的世界要把"用户工作流图"嵌入"按文件组织的源代码树"。）

## 六、第五刀：生物分类学的两次革命

第四战场最让人惊讶——Kashitsyn 突然把镜头切到生物分类学。

历史上的**形态学分类（morphological taxonomy）**是按看得见的性状切：有没有脊椎、是否哺乳、是否飞行……但这种方法的问题在于 **convergent evolution（趋同进化）**——头足类的眼睛和脊椎动物的眼睛长得几乎一样，但**它们的共同祖先大概是一只眼点感光的盲虫**。

> 原文："If camera-type eyes defined a biological group, its members would be a weird bunch."

历史上真的犯过这样的错：

- 真菌一度被归类为植物，直到 20 世纪中才被独立为一个界；
- 鳄鱼曾被归在 Reptilia，鸟在 Aves，是两个并列的纲——**但实际上鳄鱼与鸟的亲缘关系，比与其他爬行动物近**。

Kashitsyn 把这件事直接挑明：**形态学分类是另一种 tree mapping**——性状是属性，属性集合形成的"概念们"之间的包含关系是 lattice，**强行压成树就一定有人被错分**。

然后他放了 Borges 的那段经典讽刺——《约翰·威尔金斯的分析性语言》里那本虚构的中国古代百科全书：

> 原文（Borges）："the animals are divided into: (a) belonging to the Emperor (b) embalmed (c) trained (d) piglets (e) sirens (f) fabulous (g) stray dogs (h) included in this classification (i) trembling like crazy (j) innumerables (k) drawn with a very fine camelhair brush (l) et cetera (m) just broke the vase (n) from a distance look like flies"

任何一个"看起来荒谬"的分类法，本质上都是把一张关系网压成树时**选了一组奇怪的轴**——并不比"按生境/按食性/按形态"更荒谬，只是我们对后者更习惯。

而**支序分类学（cladistics）** 的革命之所以伟大，正是因为它换了一个映射规则：**不按性状切，按共同祖先切**——这本质上是把"那张物种关系网"的一组**真实存在的边**（基因继承）保留下来作为树骨架，再让其他属性自由飘移。

> 原文："Even though this mapping is imperfect due to horizontal gene transfer, it's more accurate and revealing than the traditional classification because it preserves existing connections rather than imposing artificial ones."

读到这里我意识到——**这其实给了所有"该按什么切"的工程师一个具体的指导**：**优先保留那些"真实存在的、不可分割的"边**（继承、依赖、所有权），让"可选的、属性化的"边变成 tag / index / metadata。这个原则同时回答了文件系统、monorepo、ORM、bug tracking、产品分类的问题。

## 七、第六刀：Rust 借用检查器是 tree mapping 在编译器里的化身

文章倒数第二段是给程序员的礼物。Kashitsyn 一行接一行地点名：

> 原文："Now that you know about the problem, you won't have any trouble spotting it everywhere. It lurks in database modeling challenges (I'm looking at you, MongoDB), dooms object-oriented class hierarchies, and underpins struggles with Rust's borrow checker (**object ownership graphs are trees, but object interactions are webs**)."

这一句把过去十年关于 Rust 的所有争论压成了一个等式：**borrow checker 的痛苦本质，是它强制你把一张交互网压进一棵所有权树**。

这就是为什么 Rust 里频繁出现 `Rc<RefCell<T>>`、`Arc<Mutex<T>>`、`weak references`——它们都是**手工修复 tree mapping 的副作用**：当真实业务里需要一条"非树边"（multiple owners、cyclic reference、shared mutable state）时，我们不得不引入 runtime 引用计数 / 借用检查来手动管理那条**被树映射丢掉的边**。

这同时解释了为什么 Rust 学习曲线极陡：**新手以为 borrow checker 是在检查内存安全，其实它在强迫你把一张 web 重新规划成一棵 tree**。而几乎所有 OOP 程序员的脑子里，对象之间从来都是 web 形态的。

Kashitsyn 顺手又点名了几个：

- **MongoDB 的"灵活 schema"** 实际上是在逃避一次 tree mapping 决策——但代价是查询时必须重新做一次；
- **OOP 类继承** 是 tree mapping 失败的经典灾难——这就是为什么 Go 用 interfaces、Rust 用 traits、所有现代语言都在背离 Java/C++ 风格的深继承；
- **`node_modules` 的体积**——他用"大小"做了一个反讽——是因为依赖图是 web，但 npm 长期以来用 tree 形态实例化（每个包带自己的子依赖树），所以**同一个底层库可能被压扁实例化几十遍**。pnpm 和 yarn berry 的 PnP 模式之所以革命，正是因为它们让 node_modules 终于变回了**带共享子树的 DAG**——重新承认那张依赖图本来就是 web。

读到这里我想起我们之前写的 [《资深开发者为何"说不清"自己的价值：Speed 与 Scale 的两个循环》](/post/good-read-senior-developer-speed-scale-decoupling/)——资深开发者直觉里反复"重写目录结构"、"反对深继承"、"质疑 ORM"，这些看似随机的偏好，其实**都源于他们在反复直面 tree mapping 这个不可见的难题**。Kashitsyn 给了这种直觉一个名字，于是它从"经验"升格成"知识"。

## 八、文章的真正力量：一种命名行为

读完这篇文章，最让我感到震动的，并不是其中任何一个具体例子——所有例子我都见过。**真正的力量在于"命名"本身**。

这正好暗合了 Karlton 那句俏皮话的第一条："naming things"。Kashitsyn 写了一篇关于第三个 hard problem 的文章，**而这篇文章的核心动作就是把第一个 hard problem（naming）应用到了第三个 hard problem 上**——他把一个我们每天遇到、从未取名的痛苦，命名为 **tree mapping**。

> 原文（结尾）："The primary strategy for dealing with tree mapping is to be intentional. We reach for hierarchies instinctively, and we often don't notice that we're making a choice. We must stop and ask: **What web is being flattened? Which links are sacrifices? And, most importantly, must the target medium be a tree in the first place?**"

这三个问题应该被印在每一份系统设计文档、每一个数据库 schema 评审、每一次组织架构调整的封面上：

1. **被压扁的是什么 web？**——逼自己说出那张原本的图；
2. **被牺牲了哪些边？**——明确丢掉了哪些 invariant 与可达性；
3. **目标真的必须是树吗？**——质问那个被当作前提的"我们要做一个目录树"。

这三句话之所以有力，是因为它们把一种**幽灵般的不适感**（"我说不出为什么，但我感觉这里设计错了"）转译成了一组**可以在设计评审上提问的句子**。这种"把直觉变成议程项"的能力，是好文章的标志。

## 九、延伸阅读图谱

### Roman Kashitsyn 的其他代表作（mmapped.blog 50 篇精选）

1. **[Compilation is communication](https://mmapped.blog/posts/45-compilation-is-communication.html)**（#45，An ode to M-x compile）：把"编译"重新理解为"程序员与编译器之间的对话循环"——一篇关于工具与人的关系的小论。
2. **[Good names form Galois connections](https://mmapped.blog/posts/26-good-names-form-galois-connections.html)**（#26）：把"如何起一个好名字"这个 Karlton 第一难题，从范畴论的 Galois connection 角度形式化——和"第三难"形成有趣的姊妹篇。
3. **[Enlightenmentware](https://mmapped.blog/posts/28-enlightenmentware.html)**（#28）：列举那些"让你成为更好的程序员的软件"——一份经过深思的工具学清单。
4. **[Effective design docs](https://mmapped.blog/posts/31-effective-design-docs.html)**（#31）：他自己关于"如何写设计文档"的实操指南，可与本文"design doc 卡住时请对自己温柔点"那段对读。
5. **[Static types are for perfectionists](https://mmapped.blog/posts/38-static-types-perfectionism.html)**（#38）：关于静态类型与编程哲学的小品文，里面的"perfectionism"母题与 tree mapping 的"choose a sacrifice"母题暗通款曲。

### 同一母题的相关文献

1. **Christopher Alexander, *A City is not a Tree* (1965)**——本文最重要的思想来源，建筑学与系统理论的交叉里程碑。
2. **Steven Pinker, *The Sense of Style* (2014)**——"writer's goal is to encode a web of ideas into a string of words using a tree of phrases" 的出处。
3. **David Weinberger, *Everything Is Miscellaneous* (2007)**——把"标签 vs 目录"提升到信息哲学层面的早期开火。
4. **Jorge Luis Borges, *The Analytical Language of John Wilkins* (1942)**——"中国百科全书"那段讽刺的原文，是 Foucault《词与物》序言的灵感来源。
5. **Phil Karlton 的原句**（无明确出处的口耳相传）——"There are only two hard things in Computer Science: cache invalidation and naming things." 通常被 Martin Fowler 在 [bliki/TwoHardThings](https://martinfowler.com/bliki/TwoHardThings.html) 收录。
6. **Conway, *How Do Committees Invent?* (1968)**——Conway 定律原文，把组织结构与系统结构联系起来的最早论文。
7. **Pieter Hintjens, *Social Architecture* (2014)**——讨论 OSS 项目的社会拓扑如何决定代码拓扑。
8. **Manuel Lima, *The Book of Trees* (2014)** & **The Book of Circles** (2017)**——视觉化呈现"人类几百年来用树形 / 网形组织信息"的历史。

### 反方观点

1. **平台派**：Linus Torvalds 等系统派认为 Linux"按类型切"的设计是正确的，因为它强迫一致性、减少重复——他们会反对 Kashitsyn 隐含的"bundle 更友好"立场。
2. **MongoDB 派 / Document-DB 派**：会反驳说他们不是"逃避"tree mapping，而是把它推迟到读时去做——并附上对关系派几十年正则化教条的批评。
3. **代码即数据派（Lisp / Smalltalk 传统）**：他们会说真正的解法是**抹掉 tree 与 web 的区别**——一切都是图，目录只是一种 view。代表作如 Ted Nelson 的 *Computer Lib* / Xanadu。

## 十、编辑延伸思考：为什么 2026 年是 tree mapping 重新被点名的时刻

Kashitsyn 这篇文章发布于 2026 年 2 月，但真正在 HN 引爆是 5 月——三个月延迟，这种"沉睡 → 突然引爆"在 HN 上往往不是巧合。**我猜引爆它的，是 AI Agent 时代对组织结构的二次冲击**。

过去三年，我们在 [《Agent Memory Architecture 与 Technical Debt》](/post/agent-memory-architecture-technical-debt/)、[《Context Engineering 与 Agent Memory》](/post/context-engineering-agent-memory/) 里反复讨论的话题，本质上都是 tree mapping 的新变种——

- **Agent 的工作记忆**：是一张概念图（任务 / 文件 / 函数 / 对话），但 LLM 的上下文窗口是一根线性 token 序列——这是 web → string 的一次硬映射；
- **MCP (Model Context Protocol) 的资源组织**：把"工具 / 资源 / 提示 / 文件"压成几个固定 schema 的树——但每个工具的真实关系是 web；
- **Code Agent 的 codebase 视图**：理想中是符号图（call graph + type graph + dependency graph），现实中却只能通过文件目录 + grep + AST 局部树切片来访问——这就是为什么 [《Google IDE 编年史》](/post/good-read-history-of-ides-at-google/) 里 Cider V 之类的 IDE 试图把整张 codebase 都建成语义图。

换句话说，**LLM 时代加剧了 tree mapping 的痛苦**，因为：

1. 我们要把更多更复杂的 web（业务知识、工具、对话历史）灌进越来越严格的 token 序列里；
2. AI Agent 自动化了"做 tree mapping 决策"的过程——但 LLM 本身就是基于 tree 化的训练语料学习的，它**继承了我们 50 年来的所有 tree mapping 偏见**；
3. 当所有人都用 AI 写代码时，**那些"边"的损失被加倍**——AI 倾向于按它见过的、被树化的样本输出，于是 cycle、shared ownership、跨层关系**进一步被压扁**。

这就引出一个深远的猜想：**未来真正的 IDE 与代码组织革命，可能正是因为我们必须重新让"代码"承认自己是 web 而不是 tree**。这与 [《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/) 那篇关于 AI 让每个人都能写自己的原生应用的预言、与 [《GGUF 不只是权重》](/post/good-read-gguf-beyond-the-weights/) 那篇关于本地模型文件格式如何承载模型 + 工具 + 元数据图的讨论，恰好构成了 2026 年 5 月这批"好文共赏"里的一组隐线。

Kashitsyn 没有提 LLM，但**他的文章给了 2026 年的 AI 工程师一根尺子**：你可以用 tree mapping 这个词，去解释为什么你的 Agent 系统不好用、为什么你的 MCP 工具树永远在重构、为什么你的代码 RAG 找不到上下文——**不是模型不够强、不是工具链不够好，是你在做一次没有解的拓扑嵌入**。

而真正的进步，从来不是发明更好的工具，是**先承认问题的形状**。Kashitsyn 这篇文章送给整个行业最大的礼物，就是这个形状的名字。

## 十一、谁应该读

- **系统架构师 / 数据库设计师**：每天与 schema 打交道的人，本文给你一组永久有用的提问框架；
- **写技术博客 / 设计文档的工程师**：第三章那段"writing is tree mapping"会让你重新理解自己卡住的瞬间；
- **OOP 与 Rust 程序员**：第七章那句"object ownership graphs are trees, but object interactions are webs"是过去 10 年关于继承 vs 组合争论最干净的总结；
- **产品 / UX 设计师**：第二章关于文件系统与第四章关于 Christopher Alexander 的部分，对"信息架构 / 导航树设计"是直接的弹药；
- **AI / LLM 应用工程师**：第十章"延伸思考"是为你写的——理解 Agent / MCP / Code RAG 卡在哪里，先要理解 tree mapping。

## 十二、配套资料导览

本文目录下还包含：

- **`mindmap.svg`**：文章五个战场（filesystems、writing、architecture、biology、code）与核心命题（tree mapping）的思维导图。
- **`concept-cards.md`**：12 张核心概念卡片，涵盖 tree mapping、cladistics、semilattice、Borges taxonomy、Conway 定律、borrow checker 等。
- **`glossary.md`**：30+ 条中英对照术语表。
- **`cover.svg`**：本文封面图。

---

> 编辑按：Roman Kashitsyn 的 mmapped.blog 是 2026 年系统工程社区少见的"哲学型"博客——他的论题往往看似抽象，但每一篇都能精确落到具体工程决策上。这种"高抽象 + 高落地"的双 high 写作，在快餐化、demo 化的技术内容生态里越来越罕见，值得被认真订阅。

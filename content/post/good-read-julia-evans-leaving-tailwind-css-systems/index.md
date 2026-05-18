---
title: "【好文共赏】Julia Evans 把 Tailwind 拆成九个抽屉：八年之后，她终于敢说 CSS 是一门技术"
description: "从 2018 年那篇\"终于不用写 CSS 了\"，到 2026 年这篇\"我搬走了所有 Tailwind\"——jvns.ca 用九个系统级抽屉，把 utility-first 的隐性课程整理成一份给 LLM 时代的 CSS 成熟度模型"
date: 2026-05-18
slug: "good-read-julia-evans-leaving-tailwind-css-systems"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - CSS
    - 前端架构
    - Julia Evans
    - Tailwind
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Moving away from Tailwind, and learning to structure my CSS](https://jvns.ca/blog/2026/05/15/moving-away-from-tailwind--and-learning-to-structure-my-css-/)
> 作者：Julia Evans（jvns.ca）｜发布：2026-05-15｜阅读时长：约 12 分钟
> 多模评分：Opus 9.0 ／ Sonnet 8.5 ／ Gemini 8.7（综合 **8.7 / 10**）
> 一句话推荐：八年用户、一周迁移、九个抽屉——一位资深 backend/SRE 把 Tailwind 当成"看不见的 CSS 老师"，把它教过自己的所有东西重新拆解再亲手实现一遍，顺便提出一个 LLM 时代前端最该警惕的问题：**当工具帮你藏起的知识恰好是你这一行业的护城河，你还要不要把它藏到底？**

---

## 1. 为什么这篇值得读

如果只看标题，这又是一篇"我离开 X 框架"的迁移日志。但当你读完会发现，Julia Evans 真正在做的事情远比"骂 Tailwind"复杂得多：她在做一件许多资深工程师做过、却很少有人写出来的事——**把一个高层框架反向蒸馏回它所封装的基础抽象**。

Julia Evans 是谁不需要太多介绍。她写了多年的 [`b0rk` 漫画系册子](https://wizardzines.com)，把 Linux 内核、HTTP、DNS、Git 这些"看似简单实则深邃"的基础设施画成几十页 zine，每一本都成了从业者书架上的常客。她有一个非常特别的写作角度：**永远以"我也是被它绊倒过的人"的姿态去写**，但写出来的东西却让你意识到——她对底层的尊重和耐心，恰恰是大多数中高级工程师在堆栈往上爬之后丢掉的。

这次她写 CSS，是把这套方法论又用了一遍。文章的明线是迁移：把多个个人项目从 Tailwind v2 搬回 vanilla CSS。但暗线，也是更重要的那条线，是她整理出了**九个"任何一个 CSS 代码库都必然要回答"的系统级问题**：

1. reset（重置）
2. components（组件）
3. colours（颜色体系）
4. font sizes（字号刻度）
5. utilities（工具类）
6. base（全局基线）
7. spacing（间距）
8. responsive design（响应式）
9. build system（构建系统）

这九个问题不是她发明的，是 Tailwind 用 utility-first 这一句话**替你回答了**的全部问题。而当你把 Tailwind 拆下来，每一格抽屉里都掉出来一团你以为自己不需要懂的知识。她做的事，是把每一格的"我现在打算怎么填"诚实地写下来——而且明确告诉你：**很多格子，她直接复制了 Tailwind 的答案**。

这种诚实在前端世界稀缺得令人吃惊。绝大多数"我离开 X"的文章是为了立"我现在用 Y 更好"的牌坊；Julia Evans 立的牌坊是："Tailwind 教了我很多，我现在意识到自己在用它的同时学会了 CSS。"——这是一种几乎反工业写作惯性的、非常 craft 的姿态。

而文章最后那段关于 *Tailwind and the Femininity of CSS* 的引用，把整篇文章从工程笔记拔高到了一个**LLM 时代的从业伦理问题**：当大模型可以输出任何 utility-class 堆砌的 div soup，**人类把"如何把 CSS 写得有结构、有语义"这件事真正学会，是不是比以往任何时候都更重要？** 这一笔，是把文章从 9 分推到 9.5 分的那一刀。

这也是为什么这篇文章在 Hacker News 上以 657 分、370 条评论登顶——它不是又一次的框架圣战，而是一份**面对成熟工程师的、关于"工具到底教了你什么"的反思练习**。

## 2. 抽屉一与抽屉二：reset 与 components——为什么她坦白"我直接抄了前 200 行"

Julia 在 reset 这一节做了一件很多人不敢做的事：她**承认自己直接复制了 Tailwind 的 preflight 前 200 行**。

> 原文：*"I just copied Tailwind's 'preflight styles' by going into `tailwind.css` and copying the first 200 lines or so."*

为什么她不重新写一份？因为她对 Tailwind 的 reset 已经形成了"肌肉记忆"——`* { box-sizing: border-box; }`、`html { line-height: 1.5; }` 这些规则她在写 CSS 时**默认假设它们存在**，没了反而无法工作。她说："我相信 Tailwind reset 里还有很多我已经潜意识依赖、但根本意识不到的设置。"

这是一个非常诚实、也非常重要的认知：**框架真正的杀伤力不是"用起来快"，而是它把一组隐性约束烧进了你的直觉**。当你迁移走的时候，你不是从零开始，而是带着一组你自己都说不清楚的偏好。承认这一点，比假装"我现在从一张白纸开始"要专业得多。

紧接着的 components 抽屉，是整篇文章里**对工程化最有借鉴价值的一节**。她给了三条规则：

- 每个 component 有一个唯一的 class
- 一个 component 的 CSS 永远不覆盖另一个 component 的 CSS
- 每个 component 一个独立的 CSS 文件

然后用 nested selector 把变体（`.zine.horizontal`、`.zine.vertical`、`:hover`）收在一个块里。这本质上是**轻量 BEM**——但她没有引入 BEM 的命名仪式，只是借用了 BEM 的核心约束：**变更局部化**。

她明确说自己没有用 `@scope`、没有用 web components、没有任何编译期保证——只有"约定 + 尽力"。但即便如此，这套约定已经让她在改一个 100 行组件时**只需要思考那 100 行**。这点跟我们之前写过的 [《matklad：Conway 定律才是软件架构的母题》](/post/good-read-matklad-learning-software-architecture/) 里讨论的"局部推理（local reasoning）"是完全同源的——架构的本质从来不是工具，而是**你愿意为"我改这里不会炸那里"付出多少自律**。

## 3. 抽屉三与抽屉四：颜色与字号——设计 token 的私人化版本

Julia 把所有颜色塞进 `colours.css` 的 `:root` 变量里，唯一的约定是："**这个网站用到的所有颜色都必须出现在这个文件里**"。她坦言自己不打算在这次重构里碰颜色——因为"颜色真的很难"。她在前一篇 [《Links to CSS colour palettes》](https://jvns.ca/blog/2026/05/04/css-colour-palettes/) 里专门列了她喜欢的几个调色板（uchū、flexoki、reasonable colours），这也是这次迁移的伏笔。

字号那一节更具示范性。她**直接从 Tailwind 偷了 `text-xs / sm / lg / xl / 2xl` 的字号刻度**，但用 CSS 变量重写：

```css
--size-xs: 0.75rem;
--line-height-xs: 1rem;
--size-sm: 0.875rem;
--line-height-sm: 1.25rem;
```

然后用 `font-size: var(--size-lg); line-height: var(--line-height-lg);` 这种比 Tailwind 啰嗦一点、但完全可控的方式调用。

这背后是一个非常关键的设计哲学：**设计 token 这件事 Tailwind 没有错，错的只是它要求你必须通过它的 build system 才能使用**。Julia 把 token 抽出来变成 CSS 变量后，整个系统对工具链零依赖——浏览器原生支持 `@import` 和嵌套选择器后，连构建步骤都可以省。

这一点跟最近 OKLCH、`color-mix()`、`@property` 这些原生 CSS 特性的成熟形成了完美呼应：**Tailwind 在 2018 年填补的设计 token 真空，2026 年的原生 CSS 已经可以填上了**。这不是 Tailwind 的失败，是 web 平台的胜利。

## 4. 抽屉五到抽屉八：utilities、base、spacing、grid——一组从"妥协"到"激进"的渐变

接下来的四个抽屉，呈现出一个非常有意思的渐变：从对 Tailwind 完全妥协，到几乎完全反叛。

**Utilities（妥协）**：她保留了一组 utility class，包括从 Tailwind 抄来的 `.sr-only`（屏幕阅读器专用）。这一节她写得非常克制：「这一节很小，我对在这里做改动很谨慎。」

**Base（半妥协）**：全站基础样式她只敢写两条——`<section>` 的居中布局和 `<a>` 的颜色。她明确说："**我准备 bottom-up 地工作——先让 base 几乎是空的，等我从 components 里发现真正全局复用的东西，再往上抽。**" 这跟 Rich Hickey 的 "Simple Made Easy" 里那个核心原则一模一样：**不要为了 DRY 而过早抽象**。

**Spacing（探索中）**：她坦言这一格她还没想清楚。但她引用了两个非常 craft 的资源：

- [The Owl Selector（`* + *`）](https://every-layout.dev/layouts/stack/)：用 `section > * + * { margin-top: 1rem; }` 让父容器掌控子元素间距。
- ["No outer margin"](https://mxstbr.com/thoughts/margin/)：永远不在 component 外缘加 margin，让外层布局负责间距。

这两条规则合起来是一个非常有力的设计原则：**间距的责任永远向上委托给外层布局**。这跟 React 社区"组件不应该知道自己出现在哪里"的论断完全同构。

**Responsive design（激进反叛）**：这一节是整篇文章最技术性的一节。她明确说："**我现在尝试一种和 Tailwind 完全不同的方式——用更灵活的 CSS Grid 布局，少用 breakpoints。**" 她给的样例是：

```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(min(100%, 400px), max-content));
justify-content: center;
```

这一行 grid 配合 `auto-fit` + `minmax`，在大屏上自动两列、小屏上自动一列，**根本不需要任何 `@media` 查询**。这是 Tailwind 的 `md:` 前缀语法**做不到**的事，因为 `md:` 本质上是把 media query 编码到 class name 里——你的 breakpoint 是离散的、绝对的。

而真正的现代 CSS 提供了一种**连续的、内禀的响应式**：容器大就两列、容器小就一列，没有 768px / 1024px 这种武断阈值。她还提到了 `grid-template-areas`——一个让你用 ASCII art 描述布局的功能，Tailwind 同样做不到。

这一节的潜台词是：**Tailwind 把响应式简化成"在每个尺寸下应用不同的 utility"，而原生 CSS 的响应式哲学是"让布局本身有弹性"**——这是两种根本不同的思维模式。

## 5. 抽屉九：build system——原生 CSS 已经长大了

最后一格抽屉是 Julia 这次迁移的真正决定性因素之一。她写道：

> 原文："**In development, I don't need a build system: CSS now has both built in import statements [...] and built in nested selectors.**"

CSS 原生 `@import` 已经存在很久，但**原生嵌套选择器（CSS Nesting）2023 年才在主流浏览器全面支持**。这个时机点很重要——Julia 这次迁移并不是孤立事件，而是**原生 CSS 在最近两三年补齐了 SCSS/Less 的核心能力**之后的自然回潮。

生产环境她用 esbuild bundle CSS：

```bash
esbuild style.css --bundle \
  --loader:.svg=dataurl \
  --loader:.woff2=file \
  --outfile=/tmp/out.css
```

她明确说："**我通常避免使用 CSS 和 JS 构建系统，但我不介意用 esbuild——因为它基于 web 标准，而且它是一个静态 Go 二进制。**" 这个表态跟我们写过的 [《Rust 的边界在哪里：Black Hat Rust 作者 Kerkour 写给\"想抄 Cloudflare 作业\"的团队》](/post/good-read-kerkour-limits-of-rust/) 里那个核心判断同源——**工具的复杂度必须有边界，越过边界的优化等于复杂度税**。

她为什么不能再用现代 Tailwind？答案藏在她的"妥协诚实学"里：Tailwind v3 之后基本上**必须**走 build system；她一直在用 v2，因此项目里堆了 2.8MB 的 `tailwind.min.css`（gzip 后 270K）——她自己说"感觉有点傻"。这是一个非常具体的、可量化的迁移成本：**为了用一个让前端"看起来快"的工具，她付出了一个静态站点 270K 的体积代价。**

## 6. 那段被很多人忽略的尾声：CSS 是一门技术，不是一个发泄对象

整篇文章真正的高潮在最后一节。Julia 引用了一篇三年前的博文 *Tailwind and the Femininity of CSS*，并大段引用了其中一段：

> 原文："*They've heard it's simple, so they assume it's easy. But then when they try to use it, it doesn't work. It must be the fault of the language, because they know that they are smart, and this is supposed to be easy.*"

然后她写了整篇文章里最重的一段自我剖析——她承认自己曾经也带着这种"CSS 不就那么回事"的姿态进入这个领域，而在十年之间，她**主动选择了反方向**：把 CSS 当作一门值得严肃对待的技术，把"居中很难"这种沮丧当成是**CSS 在解决一个真正困难的问题**的证据。

> 原文："*CSS is hard because it's solving a hard problem!*"

接着是那一刀——也是这篇文章在 LLM 时代真正的政治姿态：

> 原文："*Especially in this time of LLMs where it feels more important than ever to value humans' expertise.*"

这句话翻译过来是："**正因为我们身处 LLM 时代，'尊重人类专业能力'这件事比以往任何时候都更重要。**" 她明确说，Tailwind 在文化层面**贬低了 CSS 专业性**，而她不想做这件事的同谋。

这一笔为什么重要？因为它把一个工程问题（用什么写 CSS）抬到了一个文化层面（你是否愿意承认 CSS 是一门有 craft 的技艺）。在大模型可以五秒输出三百行 utility-class 堆砌的 div soup 的今天，**一个真正懂得"为什么要用 `<section>` 而不是 `<div>`"、"为什么 owl selector 比逐个加 margin 优雅"的人，反而是稀缺的**。

这跟我们之前写过的 [《资深开发者为何"说不清"自己的价值：Speed 与 Scale 的两个循环》](/post/good-read-senior-developer-speed-scale-decoupling/) 是同一个母题：**当工具让"看起来快"变得便宜，"真正懂"的价值就会被重新定价。**

## 7. 延伸阅读图谱

### 作者其他代表作（精选 5 篇）

- **[How HTTPS works (zine 在线版)](https://wizardzines.com/zines/https/)** — Julia 的看家本领，用 30 页漫画把 TLS 握手讲透。读完这本，你不会再害怕 SSL 证书报错。
- **[How a JIT compiler works (zine)](https://wizardzines.com/zines/jit/)** — 同样是把"听起来很高深"的东西画成 zine 的代表作。
- **[Recursive DNS Servers I Have Loved (2017)](https://jvns.ca/blog/2017/02/11/recursive-dns-servers/)** — DNS 系列的第一篇，奠定了她"在公开学习中讲解基础设施"的风格。
- **[How to be a -10x engineer (2017)](https://jvns.ca/blog/2017/04/16/become-a-10x-engineer/)** — 一篇神级讽刺，写工程师如何**让团队变慢**。讽刺背后是对协作本质的洞察。
- **[Some questions about file systems (2020)](https://jvns.ca/blog/2020/06/12/some-questions-about-file-systems/)** — "我也不懂，但我列出来一个清单" 的代表作，启发了无数后来者写"诚实的问题清单"。

### 相关博文与论文（精选 8 篇）

- **[A Whole Cascade of Layers — Miriam Suzanne (2022)](https://www.miriamsuzanne.com/2022/09/06/layers/)** — Julia 文中明确点名的灵感来源。Suzanne 是 CSS 工作组成员，`@layer` 提案的主要推动者。
- **[How I write CSS in 2024 — Jacob Brennan](https://jacobb.nyc/writing/how-i-write-css-in-2024)** — 另一篇 Julia 引用的影响来源，给出了一份现代 vanilla CSS 的完整组织方案。
- **[Every Layout: The Stack](https://every-layout.dev/layouts/stack/)** — Heydon Pickering & Andy Bell 的 owl selector 系统化教科书。
- **[CSS Tricks: A responsive grid layout with no media queries](https://css-tricks.com/responsive-grid-layout-no-media-queries/)** — Julia 文中提到的 `auto-fit + minmax` 技术的原始来源。
- **[Tailwind and the Femininity of CSS — Jason Schuller](https://jasonsf.medium.com/tailwind-and-the-femininity-of-css-7d36b0a37cf0)** — 那篇被 Julia 引用的、改变她对 CSS 文化态度的关键文章。
- **["No outer margin" 原则](https://mxstbr.com/thoughts/margin/)** — Max Stoiber 的间距哲学经典。
- **[CSS Nesting — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting)** — 浏览器原生嵌套的官方文档，理解 Julia 为什么现在可以放弃 SCSS。
- **[`@scope` at-rule — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/At-rule/@scope)** — Julia 提到"想试试"的下一代 CSS 隔离方案。

### 反方观点（精选 2 篇）

- **[Adam Wathan on why Tailwind exists（多篇）](https://adamwathan.me/css-utility-classes-and-separation-of-concerns/)** — Tailwind 作者的原始论证。值得一读，因为他真正想解决的"separation of concerns 在组件化时代变成了 separation of technologies"，至今依然成立。
- **["I love Tailwind" 类长文（HN 评论代表）](https://news.ycombinator.com/item?id=48158400)** — HN 那 370 条评论里有大量资深工程师为 Tailwind 辩护，核心论点是"团队协作中 utility-class 比 BEM 更稳定"。这一观点不应被忽视——Julia 写的是**个人项目**的故事，团队场景的权衡完全不同。

## 8. 编辑延伸思考：当一个框架的最高赞美是"它教会了我不需要它"

我读 Julia 这篇文章时，反复想到的一个概念是 **"脚手架性框架"（scaffolding framework）** 与 **"基础设施性框架"（infrastructure framework）** 的区分。

**脚手架性框架**的成功标志，是用户最终**不再需要它**。Tailwind 是脚手架——它教你 spacing scale、color palette、reset 这些设计 token 的概念，等你内化了，你可以走。Rails 在 2010 年代教 Java 工程师 convention over configuration，也是脚手架，很多用户后来转去了 Sinatra/Hanami 甚至 Go。

**基础设施性框架**的成功标志，是用户**永远离不开它**。Linux 内核、PostgreSQL、TCP/IP 协议栈是基础设施——它们的成功在于让上层应用根本不去想它们的存在。

这两类框架的健康判据是相反的：脚手架性框架如果**让用户离不开**，就开始变成债务；基础设施性框架如果**用户能感觉到它**，就说明它没设计好。

Tailwind 的有趣之处在于，它一直在两者之间摇摆。早期它清晰地定位为脚手架（utility-first 是为了让你**少写 CSS**），但随着 v3/v4 引入越来越多的编译期魔法、JIT、preset 系统，它正在向"基础设施"的方向漂移——你越来越离不开它的 build pipeline。Julia 这次迁移的真正触发点（"v2 之后必须用 build system"），其实就是她感知到了这种漂移。

这背后还有一个更大的产业模式问题：**前端工具链的复杂度天花板正在被 LLM 重置**。当 GitHub Copilot 可以生成完美的 Tailwind class、Cursor 可以一键 refactor 整个 design system，"工具是否容易上手"这个 Tailwind 当年的核心卖点正在被 AI 蒸发掉。剩下的核心问题就成了：**哪一种代码更容易被 AI 维护？是 utility-class 堆出来的 div soup，还是有清晰语义和组件边界的 vanilla CSS？**

我倾向于认为是后者。这跟我们写过的 [《GGUF 不只是权重：一个本地推理引擎作者眼里，单文件模型格式还缺什么》](/post/good-read-gguf-beyond-the-weights/) 里讨论的"自描述格式比依赖外部工具的格式更耐久"是同一个判断——**代码的可读性、语义性、自包含性，在 AI 协作时代是会被加倍奖励的**。

最后，回到 Julia 的那一刀。"In this time of LLMs, it feels more important than ever to value humans' expertise"——这句话不只是关于 CSS。这是一整代资深工程师正在被迫面对的问题：当大模型能输出任何"差不多对"的代码，**你那些"看起来不太能直接用"的深度知识，到底是债务还是护城河？**

Julia 给的答案非常清晰：**护城河，而且要继续挖。** 一个能在十年里耐心把 CSS 学到真正尊重它的程度的工程师，是不会被 utility-class 一键生成器替换掉的。

## 9. 配套资料导览

- **`cover.svg`** — 文章封面（深色 + "好文共赏" + 关键词）
- **`mindmap.svg`** — 九抽屉思维导图：以 reset / components / colours / font / utilities / base / spacing / responsive / build 为分支
- **`concept-cards.md`** — 12 张关键概念卡片，覆盖 owl selector、CSS Nesting、`@layer`、`@scope`、`auto-fit + minmax`、design tokens 等
- **`glossary.md`** — 30 条英中对照术语表

## 10. 谁应该读

- **正在维护任何 utility-class 项目的前端工程师**：这篇是一份"如果哪天你想搬走"的迁移路线图。
- **CSS 半懂半不懂的全栈/后端工程师**：Julia 整理的九个抽屉，是你重建 CSS 心智模型的最快路径。
- **技术决策者 / Tech Lead**：里面对"框架什么时候变成债务"的判断，可以直接复用到任何技术选型场景。
- **写技术文章的人**：这篇文章本身就是"诚实地承认自己抄了哪些东西、还没想清楚哪些东西"的写作示范——比绝大多数"我离开 X"的圣战文好十倍。
- **关心 AI 与人类专业关系的人**：最后那一段关于"LLM 时代为什么要尊重人类专业能力"的论述，值得反复读。

---

> **版权声明**：本文为读者笔记 / 深度导读，所有引用均标注原文出处，单段引用不超过 3 句，总引用低于全文 10%。原文版权归 Julia Evans 所有，强烈建议读者阅读 [原文全文](https://jvns.ca/blog/2026/05/15/moving-away-from-tailwind--and-learning-to-structure-my-css-/) 与 Julia 的 [CSS 系列](https://jvns.ca/categories/css/)。

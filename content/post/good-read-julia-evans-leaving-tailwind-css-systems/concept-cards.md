# 关键概念卡片 · Concept Cards

> 配套于《Julia Evans 把 Tailwind 拆成九个抽屉》读者笔记。每张卡片独立可读，便于日后查阅。

---

## 卡片 01 · Utility-First CSS

**定义**：一种 CSS 编写范式，主张直接在 HTML 上堆叠语义最小的、单一职责的 class（如 `p-4`, `text-lg`, `bg-blue-500`），由此把所有样式表达力推到 markup 上，几乎不写自定义 CSS。Tailwind 是其代表实现。

**核心论证**（Adam Wathan）：CSS 的 "separation of concerns" 在组件化时代已经过时——真正的关注点是 component，而不是 "HTML vs CSS"。

**反方论证**：utility-class 堆砌往往伴随语义贫乏的 div soup，可访问性和长期可维护性双输。

---

## 卡片 02 · CSS Reset / Preflight

**定义**：一组在所有元素上强制重置浏览器默认样式的规则，目的是消除跨浏览器差异，给后续 CSS 一个干净的起点。

**经典例**：Eric Meyer Reset（2007）、Normalize.css（2011）、Tailwind Preflight（2019+）。

**Julia 的做法**：直接复制 Tailwind preflight 的前 200 行——承认自己已经对 `box-sizing: border-box`、`line-height: 1.5` 等设置形成肌肉记忆。

---

## 卡片 03 · BEM (Block · Element · Modifier)

**定义**：Yandex 在 2010 年前后提出的 CSS 类命名约定：`.block__element--modifier`，目的是用命名约定隔离样式作用域。

**核心约束**：一个 block 的 CSS 永远不应影响另一个 block。

**Julia 的轻量版**：不强制命名规范，但保留核心约束——"一个 component 的 CSS 永远不覆盖另一个 component"，靠 nested selectors 和"每文件一组件"的目录结构来落地。

---

## 卡片 04 · Design Tokens

**定义**：把设计系统中的所有原子决策（颜色、字号、间距、半径等）抽成命名变量，作为 design 和 code 之间的唯一真相源。

**载体**：CSS 自定义属性（`--pink: #fea0c2`）、Style Dictionary、Tailwind config 等。

**Julia 的做法**：用 `colours.css` + `:root { --pink: ...; }` 模式，把所有颜色集中登记；font sizes 同样用 `--size-xs / sm / lg` 抽出。这是不依赖任何 build pipeline 的 "纯 CSS design token"。

---

## 卡片 05 · CSS Nesting (原生嵌套)

**定义**：CSS 4 标准的一部分，允许在 CSS 中直接嵌套选择器：
```css
.zine {
  color: white;
  &.horizontal { ... }
  &:hover { ... }
}
```

**重要性**：原生嵌套（2023 年主流浏览器支持完成）替代了 SCSS/Less 在这一点上的核心价值，使得 vanilla CSS 再次成为足够工程化的选项。**Julia 这次能放弃构建系统，关键就是它**。

---

## 卡片 06 · Owl Selector (`* + *`)

**定义**：由 Heydon Pickering 在 2014 年推广的间距模式：
```css
section > * + * { margin-top: 1rem; }
```
"两眼瞪着的猫头鹰"——选中所有除第一个之外的兄弟元素，统一加上顶部间距。

**优势**：让父容器掌控子元素间距，单一规则代替分散在子组件里的 margin 散落。

**进阶**：Every Layout 的 `.stack` 组件就是 owl selector 的系统化封装。

---

## 卡片 07 · `auto-fit` + `minmax` Grid

**定义**：一种"无需 media query 的响应式"模式：
```css
display: grid;
grid-template-columns:
  repeat(auto-fit, minmax(min(100%, 400px), max-content));
```

**机制**：
- `auto-fit`：根据容器宽度自动决定列数
- `minmax(min(100%, 400px), max-content)`：每列最小宽度为 "100% 或 400px 取小者"，最大为内容宽度

**结果**：大屏自动多列、窄屏自动一列，**容器响应而非视口响应**，与 container queries 异曲同工。

---

## 卡片 08 · `@layer` (Cascade Layers)

**定义**：CSS 2022 标准引入的级联层机制，允许显式声明样式层的优先级顺序：
```css
@layer reset, base, components, utilities;
```
后声明的 layer 永远胜过先声明的，与选择器特异性解耦。

**作用**：彻底解决 "为什么我的样式被覆盖了" 的世纪难题。Julia 文中"我还想试试"的下一步特性之一。

**来源**：Miriam Suzanne 在 2022 年的文章 *A Whole Cascade of Layers*。

---

## 卡片 09 · `@scope`

**定义**：CSS 新提案，允许显式定义样式的作用域：
```css
@scope (.card) {
  h2 { color: red; }
}
```
其中的规则只对 `.card` 内部的 `h2` 生效，与 Shadow DOM 类似但无需 web component 机制。

**意义**：终于让"组件 CSS 不会泄漏"成为语言级保证，而不是命名约定。Chrome 已支持，Firefox/Safari 跟进中。

---

## 卡片 10 · 脚手架性框架 vs 基础设施性框架

**脚手架性框架 (Scaffolding Framework)**：成功的标志是用户**最终不再需要它**。Tailwind、Rails 早期阶段属于此类。

**基础设施性框架 (Infrastructure Framework)**：成功的标志是用户**永远离不开**，且感觉不到它存在。Linux Kernel、PostgreSQL、TCP/IP 属于此类。

**健康判据相反**：脚手架性框架"让人离不开"是债务；基础设施性框架"被用户感知到"是 bug。

**Julia 的潜在论点**：Tailwind 正在从脚手架向基础设施漂移（v3+ 必须用 build pipeline），这是她离开的真正触发因素。

---

## 卡片 11 · CSS 在 LLM 时代的护城河

**问题**：当 LLM 可以在五秒内生成三百行 utility-class 堆砌的 div soup，"懂 CSS" 还有价值吗？

**Julia 的回答**：**正因如此，懂得"为什么用 `<section>` 而不是 `<div>`"、"为什么 owl selector 比逐个 margin 优雅"的人变得更稀缺**。代码的语义性、可读性、自包含性，在 AI 协作时代是被加倍奖励的。

**延伸**：这跟 GGUF 单文件格式、matklad 的 Conway 定律论一样，都指向同一个判断——**自描述、有语义、有边界的工件**在 AI 时代更耐久。

---

## 卡片 12 · CSS 是"难"还是"被低估"

**经典误区**：因为 CSS "看起来简单"，所以新手期望它"用起来容易"；当它不符合期望时，归咎于语言本身。

**真相**：CSS 解决的是 layout、typography、cross-device rendering、accessibility 这一组**真正困难**的问题。"居中难"不是 bug，是因为"居中"在 inline / block / flex / grid / writing-mode 等不同上下文里有不同含义。

**Julia 的姿态**：把"CSS 难"解读为"它在解决难问题"的证据，主动选择尊重它、深入它。这是这篇文章的灵魂论点，也是她写"为什么 LLM 时代要尊重人类专业能力"那句话的前置思想准备。

---

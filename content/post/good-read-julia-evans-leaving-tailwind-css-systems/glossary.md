# 术语对照表 · Glossary

> 30 条英中对照术语 + 一句话解释，配套《Julia Evans 把 Tailwind 拆成九个抽屉》读者笔记。

| 英文 | 中文 | 一句话解释 |
|---|---|---|
| Utility-First CSS | 工具优先 CSS | 在 HTML 上堆叠单一职责 class（如 `p-4`）以代替自定义 CSS 的范式 |
| Tailwind Preflight | Tailwind 预飞行重置 | Tailwind 自带的 CSS reset，统一浏览器默认样式 |
| CSS Reset | CSS 重置 | 一组覆盖浏览器默认样式的规则，给后续 CSS 一个干净起点 |
| Vanilla CSS | 原生 CSS / 纯 CSS | 不借助任何预处理器或 utility 框架的标准 CSS |
| BEM (Block-Element-Modifier) | 块-元素-修饰符命名约定 | Yandex 提出的 CSS 命名规范，用 `.block__el--mod` 形式隔离作用域 |
| Design Token | 设计 token / 设计令牌 | 设计决策（颜色、字号等）的命名抽象，作为设计与代码的桥梁 |
| CSS Custom Properties | CSS 自定义属性 | `--name: value;` 形式的 CSS 变量，支持运行时继承与覆盖 |
| CSS Nesting | CSS 嵌套 | 允许在 CSS 中直接嵌套选择器，2023 年成为主流浏览器原生特性 |
| Owl Selector | 猫头鹰选择器 | `* + *` 模式，选中所有非首个兄弟元素，用于统一间距 |
| Cascade | 级联 | CSS 决定多条规则冲突时谁胜出的核心机制 |
| Specificity | 选择器特异性 | CSS 级联中根据选择器复杂度决定优先级的算法 |
| `@layer` / Cascade Layers | 级联层 | 2022 年 CSS 标准，允许显式声明样式优先级层，绕过特异性 |
| `@scope` | 作用域规则 | CSS 新提案，让样式只在指定容器内生效，类似无 Shadow DOM 的隔离 |
| `@import` | 导入规则 | CSS 原生模块导入语法，无需构建工具即可拆分文件 |
| `auto-fit` | 自动填充 | grid-template-columns 配合 `repeat` 时让列数随容器宽度自适应 |
| `minmax()` | 最小最大函数 | grid 列定义里指定列宽的下限与上限 |
| Container Query | 容器查询 | 基于父容器宽度而非视口宽度做响应式，CSS 2023 主流支持 |
| Subgrid | 子网格 | 允许嵌套 grid 沿用父 grid 的轨道定义，2024 年广泛支持 |
| Media Query | 媒体查询 | `@media (min-width: 768px) { ... }` 形式的视口条件样式 |
| Breakpoint | 断点 | 响应式设计中切换布局的视口宽度阈值（如 768、1024） |
| `grid-template-areas` | 网格模板区域 | 用 ASCII art 命名 grid 区块的布局语法，可读性极高 |
| Sass / SCSS | Sass 预处理器 | 历史上最流行的 CSS 预处理器，提供变量、嵌套、mixin 等 |
| PostCSS | PostCSS | 基于插件的 CSS 转换工具链，Tailwind 等框架的底层 |
| esbuild | esbuild 打包器 | Go 编写的极速 JavaScript/CSS 打包工具 |
| Build Pipeline | 构建管线 | 从源码到生产产物的工具链（打包、压缩、tree-shaking 等） |
| Tree Shaking | 树摇 | 构建期移除未使用代码以减小产物体积 |
| Semantic HTML | 语义 HTML | 使用 `<section>`/`<article>`/`<nav>` 等表达文档结构含义的 HTML |
| Accessibility (a11y) | 无障碍访问 | 让残障用户（视觉、听觉、运动等）能正常使用网页的设计实践 |
| `.sr-only` | 屏幕阅读器专属类 | 视觉上隐藏但屏幕阅读器可读的 utility class |
| ARIA | 可访问富互联网应用 | 为辅助技术（screen reader 等）提供语义补充的 HTML 属性集 |
| Local Reasoning | 局部推理 | "改这里不会炸那里" 的可维护性属性，软件架构核心目标之一 |
| Separation of Concerns | 关注点分离 | 经典原则：不同关注点（如 HTML 结构 vs CSS 样式）分开存放 |
| Component-Driven | 组件驱动 | UI 以可复用、可组合的组件为基本单元的开发范式 |
| Div Soup | div 浓汤 | 大量无语义 `<div>` 嵌套堆砌而成的不可访问 HTML |
| Mythical Man-Month | 人月神话 | Fred Brooks 1975 年经典著作，"加人不能让晚的项目变早" |
| The Goal (TOC) | 目标 / 约束理论 | Goldratt 同名小说，提出"瓶颈应得到可预测高质量输入"原则 |
| Femininity of CSS | CSS 的女性化标签 | 2023 年 Jason Schuller 的文章，指出工程界对 CSS 的轻视带有性别偏见色彩 |

---

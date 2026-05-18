# 英中术语对照表 — Browser Quirks 主题

> 配套于《浏览器源码里那张藏起来的"大客户名单"》。共 38 条。

| 英文 | 中文 | 说明 |
|---|---|---|
| Quirks | 兼容怪癖 / 怪癖补丁 | 浏览器为特定站点写的硬编码特殊处理 |
| Quirks Mode | 怪癖模式 | 与 Quirks 不同——文档头缺失时浏览器退回旧 IE 行为；属历史概念 |
| Site Intervention | 站点干预 | Mozilla 对 Quirks 的官方称呼，一份 JSON 对应一个站点 |
| `about:compat` | Firefox 兼容性页面 | 用户可见的、可开关的"为本站启用了哪些干预"清单 |
| User-Agent String | 用户代理字符串 | 浏览器在 HTTP 请求中自报家门的字符串 |
| User-Agent Sniffing | UA 嗅探 | 服务端根据 UA 提供差异化代码路径，被广泛认为是反模式 |
| User-Agent Override | UA 覆盖 / UA 伪装 | 浏览器主动声称自己是另一种浏览器以躲避歧视 |
| User-Agent Reduction | UA 信息削减 | Chrome 主导的减少 UA 字符串细节项目 |
| Living Standard | 活规范 / 持续规范 | 没有版本号的规范模式，HTML / DOM / Fetch 都采用 |
| Willful Violation | 故意违反 | 规范主动声明不跟随实际浏览器实现的条目 |
| Interop | 互操作 | 各家浏览器对一组目标特性达成实现一致性的年度项目 |
| Implementation-Defined Behavior | 实现自定义行为 | 规范允许各家自由决定的行为，事实上 Chrome 选了就是行业标准 |
| Vendor Prefix | 厂商前缀 | 如 `-webkit-`、`-moz-`、`-ms-`，已基本退出 CSS 世界 |
| Feature Detection | 特性检测 | 用 `@supports`、`if ('foo' in obj)` 判断能力的现代做法 |
| WebKit | WebKit 内核 | Apple 维护的浏览器引擎，是 Safari 的基础 |
| Blink | Blink 内核 | Google 从 WebKit fork 的引擎，是 Chromium / Chrome / Edge 的基础 |
| Gecko | Gecko 内核 | Mozilla 维护的浏览器引擎，是 Firefox 的基础 |
| Chromium | Chromium 项目 | Blink + V8 的开源浏览器项目 |
| Picture-in-Picture (PiP) | 画中画 | 视频元素脱离页面悬浮的浏览器能力 |
| Touch Bar | 触控栏 | 部分 macOS 笔记本曾搭载的辅助触摸条，是 Quirks.cpp 中的一类来源 |
| Magnifier Lens | 放大镜组件 | Amazon 商品页的图片放大器，WebKit 为它写了专门的触摸事件分支 |
| Picture-in-Picture Quirk | 画中画兼容补丁 | WebKit 对 Facebook/X/Reddit 暂停滚出视口视频的特殊处理 |
| Browser Sniffing | 浏览器嗅探 | UA Sniffing 的同义词 |
| Compatibility Layer | 兼容层 | 浏览器/操作系统中专门用来"承接旧代码"的子系统 |
| Frontend Engineering | 前端工程 | 浏览器侧 UI / UX 实现的工程实践 |
| Web Compatibility Project | Web 兼容性项目 | Mozilla 主持的开放兼容性问题报告平台 |
| WHATWG | Web 超文本应用技术工作组 | 由浏览器厂商主导的规范组织，制定 HTML / DOM / Fetch 等 |
| W3C | 万维网联盟 | 传统的 web 标准组织，与 WHATWG 历经多次冲突与合并 |
| Browser Market Share | 浏览器市场份额 | 决定 quirks 经济学的根本变量 |
| Chrome Hegemony | Chrome 霸权 | 学术/评论用语，描述 Chrome 在 web 平台上的事实垄断地位 |
| Single-Engine Web | 单引擎 Web | 整个 web 实际上只有 Chromium 一种渲染实现的状态 |
| DMA (Digital Markets Act) | 数字市场法案 | 欧盟反垄断法案，迫使 Apple 在 iOS 上允许第三方浏览器引擎 |
| Hardcoded Domain | 硬编码域名 | 在源码字符串字面量里写死的某个具体域名 |
| Source Code Archaeology | 源码考古 | 通过翻浏览器仓库历史来发现行业事实的方法论 |
| Bugzilla | Bugzilla | Mozilla 的 bug 追踪系统，所有 Firefox 干预 JSON 都引用 Bugzilla 编号 |
| rdar:// | rdar 链接 | Apple 内部 Radar bug 追踪系统的 URI，WebKit 注释中大量出现 |
| Outreach Attempt | 主动联系 | 浏览器工程师尝试联系站点让对方修代码，但常常失败 |
| Five-Line Workaround | 五行变通 | Den Odell 原文里对"加一段 Quirks 修一个站点"的工作量描述 |

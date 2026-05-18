# 关键概念卡片 — Browsers Treat Big Sites Differently

> 配套于《浏览器源码里那张藏起来的"大客户名单"》。每张卡片 80-160 字。

---

## 卡片 1：Quirks（兼容怪癖）

浏览器为了让某个**具体网站**正确渲染或运行，在源码里加入的**域名级特殊处理代码**。和"quirks mode"（HTML 文档头缺失时退回 IE 5.5 渲染模式）不是同一回事。本文里 quirks 特指**对实名站点的源码补丁**，比如"如果 `host == 'seatguru.com'`，就特殊处理样式"。

---

## 卡片 2：WebKit `Quirks.cpp`

苹果维护的 WebKit 内核源文件，路径为 `Source/WebCore/page/Quirks.cpp`，截至 2026-05 共 **4048 行 C++**。文件里集中了所有面向具体站点的渲染、事件、视频、UA 处理分支。文件本身是公开的——任何人都能在 GitHub 上看到 Safari 在为哪些公司加班。

---

## 卡片 3：Firefox `webcompat/data/interventions/`

Mozilla 维护的 site-specific 补丁目录。每个干预是一个独立 JSON 文件，文件名以 Bugzilla 编号开头（如 `1944727-linkedin.com.json`）。截至 2026-05 共 **372 个文件**。Firefox 把这些干预作为一个内置 WebExtension 加载，用户可以在 `about:compat` 里逐个关掉。

---

## 卡片 4：`about:compat`

Firefox 地址栏专用 URL。打开后会看到所有"针对你正在访问的网站启用的兼容性干预"，每条都有开关。这是浏览器世界里非常罕见的"对用户透明"的设计——Chrome 没有等价物。把它和 `chrome://flags` 放在一起对比，可以感受到两家公司对"用户应该知道什么"的哲学差异。

---

## 卡片 5：User-Agent Sniffing & UA Override

UA Sniffing 是站点根据浏览器 User-Agent 字符串提供不同代码路径的做法。本应在 2010 年代被特征检测取代，但实际上从未消失。**WebKit 和 Firefox 都在源码里内置了一份伪装 Chrome 的 UA**，专门对那些只认 Chrome 的站点使用。这是一种"为了上网，自我矮化"的反讽。

---

## 卡片 6：Living Standard

WHATWG 维护的 HTML 规范的特殊形态：没有版本号，持续更新，规范文本以"实际浏览器实现"为基准。听起来很务实，但隐藏代价是：**当主导浏览器的实现先于规范变化时，规范就会被自动重写以匹配主导浏览器**。Den Odell 文章指出，这把规范变成了 Chrome 的"事后注释"。

---

## 卡片 7：Willful Violation

HTML 规范中"故意违反实际浏览器实现"的条目（少数）。规范主动声明"我们知道浏览器都这么做，但规范说不行"。这是 WHATWG 哲学里少有的反例——规范偶尔确实会要求所有浏览器改变，而不只是描述。但这种条目极少见。

---

## 卡片 8：Interop 项目

Apple / Google / Mozilla / Microsoft 联合发起的年度项目（Interop 2022/2023/2024/2025/2026），约定一组目标 web 特性并集体推进各家实现一致性。可以理解为浏览器厂商对 quirks 内卷的"集体反扑"。**但 Interop 不解决 80% 长尾站点的 quirks 问题**，它只解决新特性的兼容。

---

## 卡片 9：Site-Specific Intervention

Mozilla 对其 webcompat 干预的官方称呼。每个 intervention 通常包含：触发条件（URL 模式）、注入的 CSS / JavaScript / UA override、相关 Bugzilla 链接、有效期。Firefox 把它们集中成一个数据驱动的目录，是一种"工程债务管理"的工业化做法。

---

## 卡片 10：UA Reduction（Chrome）

Chrome 自 2022 起推动的"减少 UA 字符串信息量"项目，让浏览器版本号、操作系统等不再精确披露。看起来是反 UA sniffing 的好事，但**实际效果是让非 Chrome 浏览器更难伪装成 Chrome**——因为 UA 字符串里能识别"真假 Chrome"的细节少了。这是 Chrome 单方面把规则定下的另一个案例。

---

## 卡片 11：iOS WebKit-Only 政策

iOS 上所有浏览器（包括 Chrome、Edge、Firefox iOS 版）都必须使用 WebKit 作为渲染引擎——这条苹果规则被欧盟 DMA 推翻只是部分。iOS 这块土地是 WebKit 的"避难所"：在这里 Chrome 反而是受 quirks 待遇的那个。所以"用户会换浏览器"的市场逻辑在 iOS 上完全不成立——这是 Den Odell 文章未展开的角度。

---

## 卡片 12：Implementation-Defined Behavior

规范用语，指"规范允许浏览器自由决定的行为"。在理论上各家可以不同，但实际上 Chrome 选择什么、整个行业就跟什么。**这是 Quirks 出现的另一个根源**——其他浏览器为了让"事实上 Chrome 的选择"在自家也能跑通，必须 quirk。一份完整的"web 实际规范"，今天其实是"HTML + CSS + Chrome implementation-defined choices"。

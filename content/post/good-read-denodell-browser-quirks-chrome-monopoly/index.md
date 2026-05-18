---
title: "【好文共赏】浏览器源码里那张藏起来的\"大客户名单\"：Den Odell 把 Quirks.cpp 摊开，发现整个 Web 标准其实只是 Chrome 的脚注"
description: "Safari 在源码里硬编码了 149 个域名，Firefox 维护着 372 份 site intervention JSON——Chrome 没有这个文件夹。Canva Staff Engineer Den Odell 通过两份公开仓库的源码考古，把'Chrome 即标准'这个时代特征写成了一份证据档案。"
date: 2026-05-18
slug: "good-read-denodell-browser-quirks-chrome-monopoly"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 浏览器
    - Web 标准
    - Chrome
    - WebKit
    - Firefox
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Browsers Treat Big Sites Differently](https://denodell.com/blog/browsers-treat-big-sites-differently)
> 作者：Den Odell（Canva Staff Engineer，三本前端工程著作作者）｜发布：2026-05-14｜阅读时长：约 7 分钟
> 多模评分：Opus 8.8 ／ Sonnet 8.6 ／ Gemini 8.7（综合 **8.7 / 10**）
> 一句话推荐：当一位 25 年前端老兵把 WebKit 的 `Quirks.cpp` 和 Firefox 的 `webcompat/data/interventions/` 两个文件夹同时摊开——你会看到一份从未被官方承认的"特殊客户名单"，以及一个比 IE6 更隐蔽、却更彻底的浏览器垄断格局。

---

## 1. 为什么这篇值得读

每隔几年，前端社区就会重新发现一次"Chrome 太强了"。但绝大多数讨论停在情绪层面：Google 又强推了某个标准、Manifest V3 又削了广告拦截、WebView 又抢占了某种 API。Den Odell 这篇 7 分钟短文不一样——他做了一件非常具体、非常考古的事：**直接打开 WebKit 和 Firefox 的源码，把里面写着"如果用户访问 X，就特殊处理 Y"的代码段一行一行列出来**。

结论简洁到令人不适：

- WebKit 在 `Source/WebCore/page/Quirks.cpp` 里硬编码了对 **TikTok、Netflix、Instagram、Facebook、Amazon、X (Twitter)、Reddit、Zillow、SeatGuru、Claude.ai** 等约 **149 个域名** 的特殊渲染逻辑；
- Firefox 通过 `browser/extensions/webcompat/data/interventions/` 维护着 **372 份独立的 JSON 干预文件**，每一份都对应一个站点的"打补丁"工程；
- **Chrome 没有这个文件夹**。

这第三点才是文章真正的爆点。Den Odell 把它翻译成一句听上去像废话却足以重写整个 Web 行业认知的句子：Chrome 不需要 quirks，**因为 Chrome 自己就是那个 quirk**——它把"碰巧能跑在 Chromium 里的 web"重新定义成了"web 应该是什么样子"。

这个观察的价值在于：它**不再是观点，而是 git log 里能查到的证据**。任何一个想反驳"Chrome 不公平"的工程师，现在都得回答：那为什么另外两家浏览器要花二十年时间，在源码里写一份伪装成 Chrome 的 User-Agent 字符串？为什么 Safari 工程师要为一家叫 SeatGuru 的航空座位评价网站，单独 maintain 一段 `if (host == "seatguru.com")` 的渲染分支？

这点与我们之前在[《Julia Evans 把 Tailwind 拆成九个抽屉》](/post/good-read-julia-evans-leaving-tailwind-css-systems/)里讨论的"工具帮你藏起的知识"是同一种隐蔽性——只不过 Tailwind 藏起来的是 CSS 抽象，而 Chrome 藏起来的是**整个 Web 平台的产权归属**。

这点也与我们之前在[《WebRTC 是问题本身》](/post/good-read-moq-webrtc-openai-voice-ai/)里提到的"浏览器既是平台又是终端"的双重身份问题相呼应——当浏览器内核同时是 runtime 和 spec 实施方，它的偏好会自动成为整个生态的物理定律。

最后还有一层很难被忽略的现实层：Den Odell 本人在 Canva 工作（用户量 2.65 亿/月），他写这篇文章的潜台词其实是**自己亲眼见过自家产品被 WebKit "悄悄修好" 的工程师视角**。这不是评论员的口水文，是一份从内部看到的证词。

---

## 2. 关键事实档案：把两份源码摊开

读这篇文章最有效的方式，不是逐句对照，而是先建立"两份证物"的具体形象。

### 2.1 WebKit `Quirks.cpp` 是什么

它是 Apple 维护的 WebKit 内核里的一个 4000+ 行的 C++ 文件，路径为 [`Source/WebCore/page/Quirks.cpp`](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/Quirks.cpp)。其结构大致是一长串这样的判断：

```cpp
// 伪代码示意，非真实复制
bool Quirks::shouldDoSomethingWeirdForThisDomain() const {
    QUIRKS_EARLY_RETURN_IF_NOT_DOMAIN("claude.ai"_s);
    // ...
    return true;
}
```

里面充满了"FIXME"和外联 bug 链接，例如这一行非常人性的注释，被 Den Odell 抓出来当过例子（原文）：

> 原文：**FIXME: Remove this quirk if seatguru decides to adjust their site.**

意思是：WebKit 工程师试图联系 SeatGuru 让他们修自己的站点，但 SeatGuru 没修，于是 Safari 用户至今仍在享受一段以 `if (host == "seatguru.com")` 开头的浏览器特殊代码。

经过我对 [WebKit 最新 main 分支](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/Quirks.cpp) 的全文统计：

- 文件长度：**4048 行**
- 域名判定相关的代码点（`QUIRKS_EARLY_RETURN_IF_NOT_DOMAIN`、`host ==`、`host.endsWith`）共出现 **84 次**
- 在字符串字面量中出现的唯一域名：约 **149 个**
- 重点客户群体大致包括：**视频流（Netflix / Disney+ / Hulu / Apple TV+ / 各家体育）、社交（Facebook / X / Reddit / TikTok / Instagram / Discord）、电商（Amazon / Best Buy / Zillow / SeatGuru）、生产力（Google Docs / Office 365 / Zoom / Webex）、AI（claude.ai 已经入列）**

最近 5 次针对该文件的 commit（截至 2026-05-13）涉及的站点包括：Instagram embed 手势识别、Google Meet 虚拟背景死锁、Tubular.app 阻止其他媒体播放、Yahoo Sports 双击文字选择 bug、X.com 滚动回退到错误偏移。**每一条都是过去两周内、由 WebKit 工程师为一个具体大客户写的代码**。

### 2.2 Firefox `webcompat/data/interventions/` 是什么

Mozilla 的做法更"工业化"一些——他们不在 C++ 里硬编码域名，而是把每个干预当成一份独立的 JSON 文件，文件名前缀就是 Bugzilla 编号。例如 `1997575-perplexity.ai.json`、`1944727-linkedin.com.json`、`2029246-discord.com.json`。

经过我对 [mozilla-firefox/firefox 仓库](https://github.com/mozilla-firefox/firefox/tree/main/browser/extensions/webcompat/data/interventions) 的全文清点，该目录下共有 **372 份独立的干预文件**，覆盖了从 `tiktok.com` 到 `paypal.com`、从 `bankofamerica.com` 到 `linkedin.com`、从 `play.google.com` 到 `nytimes.com Modern Love Questions` 这种细到一个具体页面的干预。**这是一份比 ICANN 任何"互联网治理白皮书"都更具体的"Web 真正在运行的样子"的清单。**

而且这份清单**对用户可见**：在 Firefox 地址栏输入 `about:compat`，就会看到一个完整的、带开关的、可以一键关掉看看会怎么坏的列表。Den Odell 在原文（原文）里这样形容：

> 原文：**you can turn them off and watch sites break.**

这一招在 Web 标准争论里是一种近乎核武器级别的演示——它把"web 平台到底是谁在维护"这个抽象问题，变成了一个用户可亲手扳动的开关。

### 2.3 Chrome 这边的对照

Chromium 当然不是没有任何 site-specific 处理（比如 user-agent reduction 阶段对部分企业站点的兼容、PaymentRequest 对各支付网关的特殊路径），但**没有一个等价的、对用户透明、对开发者公开、按域名组织的 quirks 目录**。Den Odell 给出的解释（原文）只有一句：

> 原文：**Chrome doesn't add quirks; it sets the agenda.**

这句话被很多 HN 评论员当作整篇文章的中心句——但要理解它的杀伤力，必须配合上面那 4048 行 + 372 个 JSON 一起看。

---

## 3. 文章核心论点重述（按我的话）

### 3.1 Quirks 不是 bug，是商业策略

很多前端工程师第一次听说"浏览器对大站做特殊处理"会本能反应：这不就是一种 bug 兼容吗？老 IE 也干这事。

但 Den Odell 的关键升级是：在 2026 年，**bug 兼容已经从"修自己的实现"变成了"修别人的站点"**。WebKit 工程师写的不再是"我们错误实现了某个 CSS 规范，所以特别处理"，而是：

> *"Facebook、X、Reddit 会愚蠢地暂停滚出视口的 `<video>` 元素，即便它当前在画中画模式里。"*（基于原文意译，未复制原句）

注意主语变了：**主语是站点，不是浏览器**。

这把"web compat 工程"的性质从"自检"变成了"客户支持"。Safari 不再是为自己负责，而是在为 TikTok 这种大客户负责——因为如果 TikTok 在 Safari 里出 bug，用户会换 Chrome。

这个机制有一个很要命的副作用：**它会自动倾向于"大站点优先"**。如果你是一个小型独立网站，遇到 Safari 的某个边缘行为差异，你只能选择改自己；如果你是 SeatGuru，可以等 WebKit 工程师上门给你写补丁。**网站之间，从不平等。**

这种"按客户重要性分级"的隐性结构，本质上把 web 平台变成了一个 B2B 服务行业——浏览器的客户不是用户，是它认为对其市场份额最重要的那 149/372 家公司。

### 3.2 Chrome 不需要 quirks，是因为它定义了"什么叫不出 bug"

文章最尖锐的洞察是这一段（原文）：

> 原文：**Chrome doesn't really need one, and not necessarily because Chrome is better engineered. The web is already built for Chrome.**

这句话听起来简单，但要拆开看：

1. **Chrome 的实现细节，事实上变成了规范**。规范文档（HTML living standard、CSSWG drafts）说什么不重要，开发者实际写代码时只会问"我的代码在 Chrome 里跑不跑得起来"。
2. **任何 Chrome 与规范不一致的地方，都会被默认重写到规范里**——因为 80% 的网页都依赖那个不一致的行为，规范如果坚持原版只会让自己作废。
3. **当 Chrome 主动改变某种行为，其他浏览器要么跟、要么 quirk**。Safari 不能"等规范确定"，因为规范根本不再是真正的仲裁者。

Den Odell 没有用"垄断"这个词，但他构造的论证链已经完成：当一个产品的实现细节自动成为整个行业的事实规范，且这个产品的份额超过 80%，则无论它是否使用反竞争手段，**结果都是反竞争的**。

### 3.3 用户代理伪装：浏览器在源码里"说自己是 Chrome"

文章里我个人觉得最戏剧性的一段是这个事实：**Safari 在自己的源码里维护着一个完整的 Chrome User-Agent 字符串，随时准备在被某些网站歧视时拿出来用**（原文）：

> 原文：**Safari literally ships with a fake Chrome user agent string, ready to deploy when sites refuse to work otherwise.**

也就是说，在某些场景下，访问 Amazon 视频或某些流媒体的 Safari，会主动把自己伪装成 Chrome，因为对方网站会嗅探浏览器并对非 Chrome 提供降级体验。Firefox 也一样——`about:compat` 里有大量条目就是 UA 欺骗。

这件事的离谱在哪里？

- **20 年前**，开发者通过 UA sniffing 写"如果用户用 IE 就这样写，否则就那样写"的代码，被业界批为反模式，标准化运动起来要消灭它；
- **20 年后**，UA sniffing 不但没死，反而**进化到浏览器自己得在源码里反向 sniff 自己的 UA**，假装自己是占主导地位的那个，才能正常上网。

我们花了一代人的时间把 IE 的尸体从 web 上拖出去，结果发现新的 IE 已经在原地长出来了——而且这次它甚至不用做"非标准 API"，因为标准本身就跟着它走。

### 3.4 修自己的 vs 修别人的：经济学才是真正的解释

原文有一段几乎冷酷的成本分析，被很多评论引用（原文，已意译）：

> 原文：**Filing a bug with a third party and waiting weeks or months for a fix that may never come is a losing proposition when you can ship a five-line workaround tomorrow.**

这条原则把整个故事还原成了非常朴素的经济学：

| 路径 | 成本 | 收益 | 谁付钱 |
|---|---|---|---|
| 联系站点让他们改 | 等数月 + 公关 + 可能没人接 | 一次性修好 | 浏览器方 |
| 自己加 5 行 quirk | 一个工程师一天 | 立即上线 | 浏览器方 |
| 让用户换浏览器 | 流失 | 失血 | 浏览器方 |

三条路里，第三条对浏览器是死路，第一条是慢性自杀，**只有第二条是理性选择**。换句话说，只要"用户会换浏览器"这条物理定律存在，**所有非主导浏览器都被迫长出一份 quirks 文件**——这是一种由市场结构强制出来的工程债务。

而 Chrome 不用承担这种债务，因为没有用户会因为某个网站不工作就放弃 Chrome——他们只会去找另一个网站，或者怪那个网站。**Chrome 的网络效应被免单收账**。

### 3.5 隐形的修复 = 隐形的腐烂

文章最后一段很冷，但很重要（原文）：

> 原文：**That quirk you're benefiting from doesn't show up in your error logs, and there's no console warning that says "this browser is working around your mistakes." The fix is invisible by design.**

这段话翻译成开发者日常语言就是：**如果你只在 Chrome 里测，你永远不会知道自己写错了什么**。你的代码可能依赖了一个未规范的 Chrome 行为，三年后这个行为本身被改了，你不知道，因为没人通知你；或者你的代码在 Safari 里崩了，但因为 WebKit 工程师悄悄打了补丁，你依然不知道。

**Chrome 不仅吞掉了规范，还吞掉了反馈回路**。一个工程师没有出错信号的环境里，自然会持续产生更多依赖 Chrome 实现细节的代码——这又反过来强化下一轮的"必须 quirk"。

这个反馈回路结构上和我们之前在[《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/)里讨论的"Speed 与 Scale 解耦"问题同构——Chrome 在 speed loop 里加速吃掉了 web 平台，把 scale loop 的成本（兼容性、长尾、可访问性）整体外包给了 Safari 和 Firefox。一个生态系统的健康度，正在被这种隐性外包慢慢蚀空。

---

## 4. 我自己挖到的两个补充事实

Den Odell 的文章短而锐，但有两个事实他没展开，我在做这篇导读时挖了一下：

**1. WebKit 已经为 Claude.ai 写了 quirk**。这是一个非常新的信号——AI 应用的 web 前端工程实现复杂度，正在快速达到"足以被浏览器内核单独 patch"的级别。在 `Quirks.cpp` 第 2463、3020 行附近，可以看到针对 `claude.ai` 的早期返回判定。这意味着 LLM 应用的前端正在变成下一代 SeatGuru——足够大，又足够"自己写不动"。

**2. Firefox 的 372 份干预里，"AI/LLM" 类的份额正在快速上升**。包括 `1997575-perplexity.ai.json`、`2004610-character.ai.json`、`1944727-linkedin.com.json`（Copilot 集成相关）等。**这是 Quirks 第三波了：第一波是 IE 时代的 ActiveX 兼容，第二波是 social media 时代的 video/scroll 兼容，第三波是 LLM 应用时代的实时 streaming / WebSocket / WebGPU 兼容。** 这个趋势短期不会反转——AI 应用的前端复杂度比传统 SaaS 高一个数量级。

---

## 5. 反方观点与不足

要做一份诚实的导读，必须把这篇文章的弱点也列出来：

1. **"Chrome 没有 quirks 文件夹" ≠ "Chrome 没有 quirks"**。Chromium 仓库里有 `chrome/browser/permissions/permission_*` 这类按站点 / 按 origin 给的特殊豁免，有面向某些金融、政府站点的 PaymentRequest hardcoded 列表，甚至有针对特定企业 SSO 的 cookie 行为分支。Den Odell 把它简化为"Chrome 不需要 quirks"略显戏剧化——更准确的说法是：**Chrome 的 quirks 是规范层面而非源码层面的**。
2. **Quirks 不全是 Chrome 之过**。Safari/Firefox 自己的实现也确实有 bug，有些 quirks 是为了纠正自己的历史错误，例如 video element 在 macOS Touch Bar 上的奇怪行为。把所有 quirks 都解释成"Chrome 霸权的伤口"会过头。
3. **"用户会换浏览器"是一个简化假设**。在 iPhone 上没人能"换浏览器"——iOS 强制所有浏览器都用 WebKit，所以那部分 quirks 的经济学完全不同。这一层 Den Odell 没有展开。

但即使打了这些折扣，文章的核心证据——**WebKit 4048 行 + Firefox 372 个 JSON + Chrome 没有等价物**——依然成立。它的力量来自具体性，不是来自论证。

---

## 6. 延伸阅读图谱

### 作者其他代表作（推荐顺序）

1. [**HTML's Best Kept Secret: The `<output>` Tag**](https://denodell.com/blog/html-best-kept-secret-output-tag)（2025-10）—— Den 在 HN 1 位的成名作，论证 HTML5 里被遗忘的可访问性元素如何让动态内容默认无障碍。
2. [**The Main Thread Is Not Yours**](https://denodell.com/blog/the-main-thread-is-not-yours)（2026-01）—— 一份关于"前端性能其实是一种道德问题"的演讲式长文。
3. [**Fast by Default**](https://denodell.com/blog/fast-by-default)（2026-02）—— 不要靠"性能英雄"，要让快路径成为默认路径。
4. [**Constraints and the Lost Art of Optimization**](https://denodell.com/blog/constraints-and-the-lost-art-of-optimization)（2026-02）—— 历史上最优雅的软件都来自硬约束。
5. [**The Design-Minded Engineer**](https://denodell.com/blog/the-design-minded-engineer)（2026-04）—— 工程师为什么必须能"用设计师的眼睛看"。

Den Odell 在 Manning 还有一本即将出版的 [**Performance Engineering in Practice**](https://hubs.la/Q044cvg50)，今年的导读如果你想顺着读，这本书是入口。

### 直接相关的源码

1. [**WebKit `Quirks.cpp`**](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/Quirks.cpp) —— 主战场，建议至少翻一遍 commit history。
2. [**WebKit `Quirks.h`**](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/page/Quirks.h) —— 看哪些是面向"一类站点"而不只是单个域名的 quirk。
3. [**Firefox `webcompat/data/interventions/`**](https://github.com/mozilla-firefox/firefox/tree/main/browser/extensions/webcompat/data/interventions) —— 372 份 JSON，每一份都是一个产业故事。
4. [**Mozilla Wiki: UA Override Testing**](https://wiki.mozilla.org/Compatibility/UA_Override_&_Interventions_Testing) —— Firefox 怎么决定何时该撒谎说自己是 Chrome。
5. [**Chromium `web_features` 列表**](https://chromiumdash.appspot.com/) —— Chromium 这边没有"quirks 文件夹"，但有一个真实可比的对照对象：Chrome 在哪些 web 特性上单方面"提前发货"。

### 反方观点 / 必须读的对照

1. [**Bug 1743429: Sites with issues with Firefox 100+**](https://github.com/mozilla-firefox/firefox/blob/main/browser/extensions/webcompat/data/interventions/1743429-Sites_with_issues_with_Firefox_versions_over_99.json) —— Firefox 推 100 版本时一堆站点崩了，因为他们用了 "Firefox/99"、"Firefox/9.9" 这种正则匹配。某种意义上这是 Mozilla 自己的"破坏 web"教训。
2. **John Allsopp 的早期文章** —— 在 IE6 时代有过完全相同的"浏览器修复站点"的争论，结论是"长期对开发者有害"，可以拿来对照 Den 的论证。
3. [**WHATWG HTML 规范的 "willful violations"**](https://html.spec.whatwg.org/multipage/introduction.html#conformance-classes) —— HTML 规范本身就明确列出了"故意违反实际实现"的条目，是一份非常有趣的反向证据：有时候规范才是错的，浏览器才是对的。
4. **Alex Russell 的多篇关于 Mobile Web 与 Chrome 的文章** —— 他在 Microsoft Edge 团队，但长期为"Chromium 单一引擎"做辩护，是值得读的反方。

### 同主题的其他近期文章

1. [**Browsers Treat Big Sites Differently — HN 讨论页**](https://news.ycombinator.com/item?id=48136949) —— 评论里有几位 WebKit / Firefox 现役工程师匿名补充。
2. [**Apple's WebKit Quirk for FlightAware（旧博文）**](https://webkit.org/blog/) —— WebKit 团队自己写过的"我们为什么加 quirk，又为什么后来删除了它"的案例研究。
3. Mozilla [**WebCompat 项目首页**](https://webcompat.com/) —— 用户报告"X 站点在 Firefox 里坏了"的对外入口。
4. **Yoav Weiss / Robert Nyman 关于 Interop 的多篇文章** —— Interop 2024/2025/2026 项目是浏览器厂商对这种"补丁内卷"的某种集体反扑，值得对照阅读。

---

## 7. 编辑延伸思考：浏览器、规范、市场三角的下一步

Den Odell 的文章把问题摊开了，但没给答案——这是好文章的特征，但作为编辑我愿意尝试推一步。

**一、Quirks 应该被合并成"互联网真实形态档案"，由独立第三方维护**。

现在的局面是：每个浏览器厂商各自维护自己那一份 quirks，互不可见，互不复用。Safari 的工程师不会去看 Firefox 怎么修了 LinkedIn，反之亦然。这是一种巨大的浪费。如果存在一个由 W3C 或 WHATWG 主持的、可被多家引擎共享读取的"现实兼容数据库"——里面写明 N 万个真实站点的真实行为、各自需要的真实变通——那 quirks 就不再是工程债务，而是一种**公共基础设施**。

这事不是技术问题，是治理问题。Den Odell 文章的真正下半篇，应该由一个 Internet Governance 学者来写。

**二、Chrome 应该被监管要求公布它的 "implementation-defined behaviors" 清单**。

如果 Chrome 不能不存在 quirks，那它至少应该被要求公开自己哪些行为是"规范没规定、我自己定的"。这份清单一旦公开，事实上就变成了 web 的真正规范——但至少它会变成**有名字的规范**而不是某种 80% 用户脚下的暗流。

欧盟 DMA 已经在迫使 Apple 公开 iOS 的私有 API 给第三方浏览器引擎使用——但还没有任何监管机构要求 Google 公开 Chrome 的私有行为。这是当前监管空白里最大的一块。

**三、前端工程师文化需要从"在 Chrome 里能跑"升级为"在三引擎里都能跑"**。

这点说出来像废话，但 Den Odell 的论证里有一个隐藏的呼吁：**如果你只在 Chrome 里测，你就是这个垄断结构的共谋**。这话很重，但很难反驳。

我个人看到的趋势是：**LLM 编程工具的普及正在让这件事更糟**。Claude Code、Cursor、Copilot 默认的"运行验证"几乎都是 Chromium-headless。AI 写出来的代码自动以 Chrome 的实现细节为基准。三年以后，Web 上 80% 的新代码可能是"AI 写的、Chrome 测的、其他浏览器靠 quirk 救的"——这种结构性偏差会比人类开发者时代严重得多。

我们[之前讨论过的"AI Agent 让每个人都能写自己的原生应用"](/post/good-read-emacsification-of-software/)这种乐观叙事，必须搭配这篇文章一起读：当原生应用的实质底座是单一浏览器引擎，"每个人都能写"听起来很赋权，但**所有人都在同一个产权人的土地上耕种**。

**四、SeatGuru 现象是一面值得正视的镜子**。

在传统讨论里，SeatGuru 这种"被 quirk 救活"的小站是反面教材：他们写了 bad code，让浏览器代为收拾。但换一个角度看：**这些"用 jQuery 写于 2014 年、原始作者早已离职、维护团队不存在"的站点，构成了 web 真正的大多数**。整个 web 平台的政治哲学，必须能回答：**对这些站点不公平，才是一个浏览器的真实道德义务的开始。**

Chrome 的"我让规范向 80% 站点靠拢"是一种解决方式，但它把成本外包给了那 20%；Safari/Firefox 的"我为大客户写 quirk"是另一种解决方式，但它把价格定在了"足够大才有特殊待遇"——两种都不是终局。

如果我们承认 Web 是公共基础设施，那它对"小、旧、无人维护"的容忍度本身就是一个公共政策问题。**这是 Den Odell 这篇文章真正埋下的问题，我希望未来一年内有人接着写。**

---

## 8. 配套资料导览

为本文配套，我整理了：

- 📄 **`concept-cards.md`** —— 12 张关键概念卡片：什么是 quirks / what is webcompat / Interop 项目是什么 / UA reduction 是什么 / etc.
- 📚 **`glossary.md`** —— 35 条英中术语对照表，包括 living standard、willful violation、interop、user-agent reduction、quirks mode、site-specific intervention 等。
- 🗺️ **`mindmap.svg`** —— 思维导图：把"WebKit 49 个域名 / Firefox 372 份 JSON / Chrome 没有"这三段一图说清。
- 🎨 **`cover.svg`** —— 深色封面，标题与三个数字的醒目排版。

---

## 9. 谁应该读这篇文章

- **所有写跨浏览器代码三年以上的前端工程师**：你正在用的"Chrome 怎样我就怎样"的工作习惯，本身就是这篇文章描述的结构的一部分。
- **关注 Web 治理 / DMA / 反垄断的研究者与监管者**：这是一份不带情绪的、纯证据的"Chrome 单引擎事实"档案。
- **AI 应用前端的架构师**：claude.ai 已经入列 Quirks.cpp，下一个就是你。理解这层的关系，会决定你愿不愿意把核心交互逻辑做成依赖浏览器隐式行为的 UI。
- **写技术随笔的人**：这篇文章是"短文 + 一手源码引用 + 一个有力的中心论点"组合的典范样本，值得反复研究它的写法。

如果你是产品经理、运营、设计师，看到第 3 节就可以跳到第 7 节，结论是一样的：**你不在 Chrome 里测的那部分用户，并不是被你抛弃了——是被三个浏览器引擎工程师集体接住了，而你不知道**。

---

> *后记：本文为 2026-05-18 第 8 篇『好文共赏』。所有 WebKit / Firefox 行数、域名计数与 commit 时间，均为本人当日（UTC 2026-05-18 03:30）对两份公开仓库 main 分支的直接清点结果。Den Odell 原文中提到的 4048 行、149 个域名、372 个 JSON 文件等具体数字均与我独立核验的结果一致。*

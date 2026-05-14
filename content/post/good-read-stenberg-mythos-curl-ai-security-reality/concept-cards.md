# 概念卡片 · Mythos 与 curl 安全审计

> 用于团队晨会/读书会的 14 张速读卡。每张 ≤ 80 字。

---

### 卡 01 · Project Glasswing
Anthropic 为前沿模型设计的"受控部署框架"。核心思路：模型本体不削弱，但在 API/部署/授权层做精确能力门控。Mythos 是首个走 Glasswing 通道的模型。

### 卡 02 · "Too dangerous to release"
Anthropic 对 Mythos 的官方定性。既是安全主张，也是营销姿态。Stenberg 的工程评估认为：在 curl 这种成熟代码库上，没有看到"危险到不能放出来"的能力跃迁。

### 卡 03 · 5 → 1 折损率
Mythos 报告里"Confirmed vulnerabilities"5 条，curl 安全团队复核后只剩 1 个低危 CVE。3 个是误报、1 个是普通 bug。这是所有 AI 安全报告的典型折损量级。

### 卡 04 · AI "Confirmed" 的语义
AI 的 "confirmed" ≈ "我识别到符合常见漏洞 pattern 的特征"。CVE 流程的 "confirmed" 要求"可触发的攻击路径 + 违反明确安全语义"。两者不在一个坐标系。

### 卡 05 · curl 的尺度
176K LOC C 代码（不含空行）、660K 单词、平均每行被改写 4.14 次、1465 名贡献者、188 个历史 CVE、200 亿安装实例、110+ OS、28 CPU 架构。

### 卡 06 · curl 的防御 checklist
capped dynbufs / curlx_str_number explicit max / curlx_memdup0 overflow guard / CURL_PRINTF format-string enforcement / per-protocol response-size caps / pingpong 64KB line cap。

### 卡 07 · AI 找的是老品种漏洞
Stenberg 明确指出：AI 工具找到的是已知漏洞类别（CWE Top 25 / OWASP Top 10）的新实例，不是新类别。威胁建模框架不需要重写。

### 卡 08 · AI 代码审计的独门优势
注释 vs 实现一致性检查；跨平台/跨配置；内嵌第三方库 API 知识；内嵌协议规范知识；自然语言解释；自动补丁建议。这些是传统 AST 分析器做不到的。

### 卡 09 · "首次扫描债务"
没用过 AI 代码扫描的项目，首次扫描通常会一次性发现大量积压漏洞。这是一次性"安全债清算"——早做早安全，越拖攻击方越可能先发现。

### 卡 10 · "AI 工具组合"原则
不要押注单一模型。curl 同时使用 AISLE、Zeropath、OpenAI Codex Security、GitHub Copilot、Augment Code。组合的覆盖率远高于任何单一工具。

### 卡 11 · 评估资格的稀缺
能可靠评估 AI 代码工具的人，必须比工具更熟悉被评估对象。当工具能力逼近通用专家级，合格评估者会变得稀缺。这是 2026 年 AI 工具评测的根本难题。

### 卡 12 · 受控释放的反面
Glasswing 让访问链变长：合同→身份认证→API 路由→能力门控。Stenberg 自己最终也只能让"另一个有权限的人"代跑扫描。受控释放 = 使用摩擦。

### 卡 13 · 高质量安全报告的洪水
Stenberg 在另一篇文章里指出：AI 让安全研究者效率倍增，curl 项目正在被高质量报告淹没。"AI slop"问题已从"噪音淹没"演变为"信号也淹没"。

### 卡 14 · "in addition to" 原则
AI 代码分析工具不是替代人类审查，是叠加在人类审查之上。任何把 AI 报告直接进 CVE 流水线的流程都需要一道安全团队复核闸门。

---

> 来源：Daniel Stenberg, *Mythos finds a curl vulnerability*, 2026-05-11
> 整理：xiejiayun.github.io 好文共赏第 4 期

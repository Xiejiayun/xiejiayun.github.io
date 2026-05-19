# 关键概念卡片 · Vibecoded Photoshops

> 12 张可独立使用的讨论卡片，每张围绕原文中的一个核心命题或工具，方便在团队读书会、技术辩论、code review 场合直接引用。

---

### 卡 1 / 12 · 空集证伪（Empty Set Falsifier）

**命题**：如果"X 让任何人都能做 Y"这种强口号是真的，那么经过 t 时间应该至少有 N 个 Y 出现；如果 N=0，则口号被反例缺席否证。

**应用**：vibecoding 出现满两年，理论上能让 prompt 用户产出 Photoshop / Blender / 编译器，实证 N=0 → 强口号失效。

**注意**：这个工具只对**强口号**有效。弱口号"AI 让 Photoshop 不再被需要"它无能为力——因为弱口号的预测目标不是产生新 Photoshop，而是旧 Photoshop 失去需求。

---

### 卡 2 / 12 · Three Levels of Coding（三层编码模型）

| Level | 内容 | 例子 | AI 影响 |
|-------|------|------|---------|
| L1 Typing | 语法、模板、记忆型工作 | LeetCode、写 boilerplate | 边际成本压到 0 |
| L2 Verifying | 测试、harness、判断"几乎对"和"真正对" | 90 个测试拒掉 89 次输出 | 几乎不动 |
| L3 Deciding | 架构、不可逆判断、trade-off 决策 | 选 sync vs async、flat vs nested schema | 完全不动 |

**用法**：盘点你最近一周的实际工作时间，按 L1/L2/L3 切分。如果 L1 占比 > 60%，你的可替代成本在 AI 时代下跌最快。

---

### 卡 3 / 12 · 指控的四项最低条件

任何形如"这看起来是 X"（X = vibecoded / over-engineered / 不 idiomatic / 不 senior）的判断式语言，在被严肃讨论前必须先回答：

1. **Definition**：什么具体属性让你下了这个判断？
2. **Falsifier**：什么证据能让你撤回？
3. **检查成本**：你为这个判断花了多少分钟？
4. **校准记录**：你过去多少次被证伪？

**用法**：把这四问做成卡片，下次在 code review 上看到"this looks vibecoded"，把卡片亮出来。

---

### 卡 4 / 12 · 指控本身就是 vibecode（元批评）

**核心命题**：发出"vibecoded"指控的人，自己几乎没有 definition、没有 falsifier、没有花成本去检查、没有校准——这恰好是他们指控对方的所有罪状。**指控是真正的 vibecoded 内容。**

**话术反射**：
- "this looks vibecoded" → "你这个判断本身是 vibecoded 吗？"

这不是攻击对方，是要求对称的认知标准。

---

### 卡 5 / 12 · Level 1 危机：身份建立在被租用的层上

**社会学解释**：vibecoded 指控里的情感强度远超技术辩论合理范围，因为它不是技术辩论，是**身份保卫战**。当 L1 的市场价值崩塌，那些把 15 年职业生涯主要花在 L1 的人会发现"我证明自己属于这个行业的资本"在被清零。

**自查问题**：如果今天 AI 把 L1 的全部边际成本归零，**我在 L2 和 L3 上的存款是多少？** 如果答不出来，开始攒。

---

### 卡 6 / 12 · harness 即作品（demoscene 文化）

**命题**：判断一份工作是不是 vibecoded，**不要看代码本身，看代码周围的 harness**。真正的工程师投资在 L2，因为 L2 是 L1 量产时代里唯一不会贬值的资本。

**gizmo SoulPlayer 案例**：
- 4 套位元一致的参考实现（float / int / memory shadow / emitted asm）
- 90 个测试
- 整个 Python pipeline 比生成的 ~6KB 二进制大几个数量级

**结论**："Nobody bolts a four-way harness onto a vibecoded project."

---

### 卡 7 / 12 · 指控的不对称成本（Information Warfare）

**事实**：作出一个"this is vibecoded"指控的成本 ~10 秒；反驳它要把作者历年工程笔记翻出来一一证明，成本 ~10 小时。

**胜利条件**：指控不需要正确，**只需要让目标花掉足够多时间和士气，让下一个有创意的人选择不公开发表**。

**结论**：指控的真正目标不是被指控者，而是潜在的下一个分享者。看穿这一结构后，使用这类词语会更克制。

---

### 卡 8 / 12 · 守门工具的话语周期

技术圈 30 年里反复出现的指控话语周期：

| 年代 | 标签 |
|------|------|
| 1990s | "not a real programmer" |
| 2000s | "code monkey" |
| 2010s | "not a senior engineer" |
| 2020s | "vibecoded" |

**结构同构**：用一个语义模糊但情感强烈的词把外部群体污名化，从而保护内部群体的身份和报酬。**看穿了结构，你就有了免疫力。**

---

### 卡 9 / 12 · 宫本茂悖论（L3 不需要 L1）

**命题**：宫本茂大概率从未编译过一行代码，但 Donkey Kong / SMB / Zelda 中的 jump arc 调参、第一屏教学、电池存档决定全部是**L3 架构级判断**。

**反推**：如果你拒绝把宫本茂称为 "coder"，你其实在隐含地承认"coder = 仅在 L1 工作的人"——这正是 AI 时代最危险的自我定义。

**实践**：把"工程师"这个词从"打字者"扩展到"产生架构判断的人"。

---

### 卡 10 / 12 · gizmo 的反方（HN @stevex 的反驳）

**反方观点**：vibecoded Photoshop 永远不会出现，但人们不再需要 Photoshop——他们用 ChatGPT 直接做图。**vibecoded 应用就是 disposable 个人工具，本来就不会替代通用应用。**

**怎么读这个反驳**：它**承认**了 gizmo 的事实命题（Photoshop 没被替代），但提出**这个事实不重要**——软件形态本身在从"通用应用"转向"一次性 prompted 工具"。

**结论**：gizmo 完美反驳"AI 让任何人都能造 Photoshop"，但不能反驳"AI 让 Photoshop 不再被需要"。两个层次的命题需要分开讨论。

---

### 卡 11 / 12 · "Posture > Tool" 与 gizmo 框架的合流

把这篇文章和 [Addy Osmani 的"Don't Outsource Learning"](/post/good-read-addy-osmani-dont-outsource-learning/) 放在一起读：

| | Osmani 的"姿势 > 工具" | gizmo 的"L1/L2/L3" |
|---|---|---|
| 关注焦点 | 个人学习深度 | 工程能力分层 |
| 给的判据 | 你能跟同事讲清楚 AI 给你的代码吗？ | 你的 harness 在哪？你做了哪些 L3 决断？ |
| 风险描述 | 认知外包 → 主权丧失 | 身份建立在 L1 → 价值清零 |

**两者并不冲突**：Osmani 是"个人级"的诊断，gizmo 是"产业级"的诊断。一个对内，一个对外。

---

### 卡 12 / 12 · 给团队 lead / 工程经理的实操清单

如果你管一个团队，从这篇文章可以直接抽出 5 条行动：

1. **建立"指控四问"文化**：在 code review 模板里加一栏，要求任何形如"这看起来是 X"的判断给出 definition / falsifier / 检查时间。
2. **盘点 L1/L2/L3 工时分布**：让每个工程师自评一周内 L1 vs L2 vs L3 的时间占比，开放分享。
3. **奖励 harness 投资**：把"写测试 / 建 harness"从"开发成本"重新归类为"作品本身"。
4. **保护新分享者**：当团队内有人因为使用 AI 被攻击 "vibecoded"，公开站在他们一边，把举证责任转回到指控者。
5. **教 L3 词汇**：在 1:1 里多问"为什么选这个架构"而不是"代码哪里有问题"，让 L3 思考有训练场。

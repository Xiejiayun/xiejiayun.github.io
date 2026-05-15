# 概念卡片：Turso 关掉 Bug Bounty 的 12 张牌

## 1. AI Slop（AI 灌水）
**定义**：由大语言模型 (LLM) 自动生成的、表面上像那么回事但内容空洞或错误的内容产物。在 OSS 语境里特指机器自动产出的低质量 PR、issue、bug 报告。

**特征签名**：em-dash 修辞、绿色 checkmark、整齐的 markdown 表格、笃定的"我发现了 critical vulnerability"语气、对反驳的"wall-of-text"式拖延辩护。

**为什么 2026 年 5 月这个时间点上变成结构性问题**：当 LLM 推理价格跌到 \$0.001 / 提交，而维护者复审一份 PR 的人力成本约 \$50，激励比就从 1:1 变成 1:50000，攻击方期望值翻负为正。

---

## 2. Deterministic Simulation Testing (DST)
**定义**：一种把整个系统（包括时钟、调度、网络、磁盘）抽象成确定性事件序列，用伪随机种子驱动数十亿种状态组合的测试方法学。

**血缘**：FoundationDB (2014) → TigerBeetle (2023) → Antithesis (2024) → Turso (2024)。Turso 是这一脉里第一个用于"兼容现有协议"而非"全新协议"的案例。

**根本局限**：你只能在 "生成器（generator）能覆盖到的状态空间" 里找 bug。生成器没生成索引，索引 bug 就永远找不到；生成器没生成 ≥1GB 的库，pending page 之谜就永远不发生。

---

## 3. Bug Bounty（赏金计划）
**定义**：以现金或等价物激励外部研究者发现并报告软件缺陷的制度。最早由 Netscape 在 1995 年开创。

**经典假设**：报告者是理性的人类专家，每份提交的边际成本约等于半天的人类劳动（≈ \$200–\$2000），因此 \$1000 的赏金能筛出真心实意的高质量贡献。

**Turso 的反例**：当报告者变成 LLM 自动 agent，边际成本降到 \$0.001，假设破产。Glauber 用了一个非常直接的解决方案——拆掉激励本身。

---

## 4. Sybil Attack（女巫攻击）
**定义**：来自 2002 年微软研究员 John Douceur 的论文，指攻击者用多个虚假身份在一个系统中扮演多个独立参与者的攻击方式。

**在本文里的体现**：当 Turso 试图引入 vouching system（投票担保制）后，bot 立刻开始生成"质疑自己 PR 被关闭"的申诉 issue，每一条申诉都用一个不同的账号。任何"引入复审"的反 bot 机制都被同一拨 LLM 用同样的成本压垮。

---

## 5. The Singularity（奇点）
**Glauber 文章里的用法**：不是 Kurzweil 那个"通用人工智能超越人类"的奇点，而是一个更具体的产业事件——**LLM 生成 PR 的边际成本跌破某个阈值，导致 OSS 维护成本曲线发生不可逆的反转**的那个时间点。

**他的判断**：这个奇点不是渐进的，是 "overnight"——某一天醒来一切都变了。

---

## 6. SQLite TH3
**定义**：SQLite 的私有专有测试套件（Test Harness 3），号称 ~100% MC/DC（Modified Condition / Decision Coverage）覆盖。是 SQLite 这么稳定的关键。

**与 Turso 的关系**：TH3 不开源。Turso 要在没有 TH3 的情况下重建 SQLite 级别的可靠性，于是选择了 DST + 差分测试 + 形式化方法的组合作为替代路径。Bug bounty 是这条组合路径的最外圈防线。

---

## 7. 1GB Pending Byte 之谜
**事件**：Turso 在 2025 年 8 月发现，每当数据库越过 1GB 时下一次写入就被 SQLite 判定为损坏。调查一周后由工程师 Nikita 发现 SQLite 在 1GB 边界会插入一个特殊页，包含一个 vaguely 用于文件锁的 pending byte。

**意义**：这是文章里 Glauber 反复回到的一个例子，证明 DST 仿真器的"生成器盲区"是真实存在的——他们的 fault injection 太凶，库永远长不到 1GB，于是永远不会触发这种状态。

**为什么相关**：Bug bounty 的设计意图就是付钱让外部人帮忙找出这种"生成器盲区"，而 LLM 灌水的本质问题是：它没有"元认知"，因此根本不会去找盲区，它只会按训练分布吐出"看起来像 bug 报告"的文本。

---

## 8. Antithesis
**简介**：一家由前 FoundationDB 团队创立的初创公司，提供"在云端给你的系统跑确定性仿真"的服务。Turso 是早期客户之一。

**Antithesis 的卖点**：它替你解决了"实现一个 deterministic hypervisor"的工程难题，让你的应用只需把"逻辑层"对接进来，剩下的时钟 / 网络 / 磁盘 / 调度都由 Antithesis 模拟。

**与本文的连接**：Turso 用 Antithesis 是为了把"确定性"这件事做得比自家 in-house simulator 更深入。Bug bounty 则覆盖 Antithesis 同样发现不了的、来自外部研究者元思维的那一部分。

---

## 9. Pwn Request（GitHub Actions 的危险触发器）
**定义**：使用 `pull_request_target` 触发器的 GitHub Actions workflow 会在仓库的高信任上下文里执行外部 fork PR 的代码。这是 GitHub Security Lab 反复警告过的反模式。

**与本文的连接**：虽然 Glauber 没明说，但他文章里抱怨的 "bots 开 issue 申诉关闭" 本质是同一类问题——任何"在低信任输入上消耗高信任资源（维护者时间或 CI minutes）"的机制都会被同样的对手以同样的方式攻击。

---

## 10. Strip Mining / Resource Asymmetry
**比喻**：把开源项目当作一座露天矿，攻击者只需要支付推土机的油钱（LLM 推理成本）就能让矿主（维护者）付出搬运、清洗、回填的所有人力。

**关键不对称**：生成方与防御方的边际成本相差 4-5 个数量级。任何 \$0 以上的赏金都让"开采"的期望值变正。

---

## 11. "For now, we are choosing the latter."
**原文最末**：在"关闭系统或拆除激励"这两个选项之间，Turso 选择了后者。"For now"三个字是 Glauber 留给未来的一个 escape hatch——这个决定是战术性的，不是哲学性的。

**潜台词**：他不否认未来可能要走另一条路（关闭系统本身），但今天先用最小创伤的方式止血。这一句话被本文反复在不同小节里引用，是整篇文章的情绪锚点。

---

## 12. 真贡献者 vs. LLM 灌水：认知任务的分层
| 维度 | LLM 灌水 PR | Pavan Nambi 那种 contributor |
|---|---|---|
| 表面产物 | 一份英文 bug 报告 | 一份英文 bug 报告 |
| 中间过程 | 随机扰动 + 模板化文本生成 | 形式化模型 → model checker → DST 复现 |
| 内部模型 | 无（只有"看起来像 bug"的文本分布） | 完整的 Turso 形式语义模型 |
| 对生成器的元认知 | 0 | 高 |
| 边际成本 | ~\$0.001 | ~\$10000+ 的人月时间 |
| 单次产出价值期望 | 接近 0（且占用维护者时间） | 极高（往往跨项目，连带挖出 SQLite 的 bug） |

**核心洞见**：表面上 LLM 在做和真 contributor 一样的事，但中间的认知结构完全不同。LLM 缺的不是代码能力，是"对生成器分布盲区"的元认知。

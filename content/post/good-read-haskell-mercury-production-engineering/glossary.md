# 术语对照表 · Glossary

> 配套《【好文共赏】把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上》。覆盖类型系统、可靠性工程、durable execution、可观测性、组织工程五大维度的关键词。

## 类型系统与 Haskell 语言

| 英文 | 中文 | 说明 |
|---|---|---|
| Pure function | 纯函数 | 给定相同输入总产生相同输出，不可观察副作用 |
| Referential transparency | 引用透明 | 表达式可被其值替换而不改变程序意义 |
| `IO a` | IO 单子 | Haskell 中带副作用计算的类型标签 |
| `ST s a` | ST 单子 | 局部可变状态的受限单子，靠 `s` 类型参数防止泄漏 |
| `runST` | runST 函数 | `(forall s. ST s a) -> a`，把内部可变计算"封"成纯结果 |
| `forall s.` | 全称量化 | 在类型上扩展，rank-2 时表示 `s` 必须对所有可能的 type 成立 |
| `unsafePerformIO` | 不安全 IO 执行 | 强行从 `IO a` 取出 `a`，由调用者负责保证语义安全 |
| `unsafeCoerce` | 不安全强转 | 跨类型强行转换，编译器不检查 |
| Rank-2 type | 二阶类型 | 类型变量被嵌套在 `forall` 内的高阶类型 |
| GADT | 广义代数数据类型 | Generalized Algebraic Data Type，允许构造子精化类型 |
| Type family | 类型族 | 类型级的函数 |
| Phantom type | 幻影类型 | 不出现在值层、仅用于约束的类型参数 |
| Effect system | 效应系统 | 把副作用作为类型一等公民的系统（polysemy、effectful、fused-effects） |
| Monoid | 幺半群 | 有结合律的二元运算 + 单位元；`<>` 与 `mempty` |
| Semigroup | 半群 | 有结合律的二元运算，无单位元要求 |
| Endomorphism | 自同态 | 从类型到自身的函数 `A -> A`，在 composition + `id` 下构成 monoid |
| Records of functions | 函数字段记录 | 把模块的顶层函数封装为可被替换/包装的数据 |

## 可靠性工程

| 英文 | 中文 | 说明 |
|---|---|---|
| Safety-I | 安全 I | Hollnagel 框架：可靠性 = 故障的缺席 |
| Safety-II | 安全 II | Hollnagel 框架：可靠性 = 适应性容量的在场 |
| Adaptive capacity | 适应性容量 | 系统在面对扰动时维持功能的能力（Woods） |
| Resilience engineering | 韧性工程 | 把复杂系统能"持续工作"作为研究对象的工程子领域 |
| Production readiness review (PRR) | 上线就绪评审 | SRE 经典实践，发布前评估 blast radius / rollback / 幂等性 |
| Blast radius | 影响范围 | 失败时受波及的范围 |
| Idempotence | 幂等性 | 同一操作多次执行结果与一次相同 |
| Defense in depth | 深度防御 | 多层独立防御机制叠加 |
| Institutional dark matter | 制度暗物质 | 承重但不可见的隐性知识 |

## Durable Execution / 工作流

| 英文 | 中文 | 说明 |
|---|---|---|
| Durable execution | 持久执行 | 计算状态持久化，崩溃后可恢复到中断处 |
| Temporal | Temporal 工作流引擎 | 主流 durable execution 平台 |
| Workflow | 工作流 | 长时多步过程的代码描述 |
| Activity | 活动 | workflow 中可副作用的单步操作 |
| Event history | 事件历史 | workflow 执行的持久化日志 |
| Determinism | 确定性 | 同样输入序列必产生同样输出序列 |
| Replay | 重放 | 从 event history 重新执行 workflow 到当前状态 |
| Saga | Saga 模式 | 跨服务的补偿事务序列 |
| `hs-temporal-sdk` | Mercury 开源的 Haskell Temporal SDK | 基于官方 Rust Core SDK 通过 FFI 包装 |

## 可观测性

| 英文 | 中文 | 说明 |
|---|---|---|
| Observability | 可观测性 | 从外部输出推断系统内部状态的能力 |
| OpenTelemetry (OTel) | 开放遥测标准 | CNCF 维护的 traces/metrics/logs 统一规范 |
| `hs-opentelemetry` | Haskell OTel SDK | Mercury 开源，本文反复推荐 |
| Span | span / 跨度 | 一次操作的可观测单元，有起止时间和属性 |
| Trace | 调用链 | 多个 span 组成的端到端路径 |
| Middleware | 中间件 | 包装请求/响应链的可组合层 |
| Interceptor | 拦截器 | Temporal / gRPC 等语境下的中间件等价物 |
| Monkey patching | 猴子补丁 | 运行时改写库代码，强类型语言通常不支持 |
| Tower middleware | Tower 中间件 | Rust async 生态收敛的中间件模式 |

## 组织 / 招聘 / 文化

| 英文 | 中文 | 说明 |
|---|---|---|
| Pragmatism | 实用主义 | 以可交付价值为先的工程价值观 |
| Idealism | 理想主义 | 以"正确性 / 优雅性"为先的工程价值观 |
| Python Paradox | Python 悖论 | Paul Graham 提出，小众但优秀语言的招聘逆优势 |
| Hypergrowth | 超速成长 | 年 2x 或以上的组织增长率 |
| Onboarding | 入职培训 | 新员工进入团队的过程 |
| Stability team | 稳定性团队 | Mercury 内部专门负责可靠性基础设施的团队 |
| `Transact a` | Mercury 内部封装的事务类型 | 强制事件必须在事务内发布 |

## 金融 / Mercury 业务背景

| 英文 | 中文 | 说明 |
|---|---|---|
| Fintech | 金融科技 | Mercury 的所属类别 |
| OCC | 美国货币监理署 | Office of the Comptroller of the Currency，国家银行牌照监管 |
| National bank charter | 国家银行牌照 | Mercury 当前正在申请的资质 |
| SVB collapse | SVB 倒闭 | 2023 年 3 月硅谷银行倒闭事件，Mercury 在 5 天涌入 87000+ 客户和 20 亿美元存款 |
| Transaction volume | 交易量 | Mercury 2025 年处理 2480 亿美元 |
| Audit log | 审计日志 | 金融合规所要求的不可篡改操作记录 |

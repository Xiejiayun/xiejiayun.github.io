# 关键概念卡片

> 配合《【好文共赏】把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上》使用。每张卡片自成一个 mental model，可独立引用。

---

## 卡片 1 · Safety-I vs Safety-II

**Safety-I**：把可靠性等同于"故障的缺席"。方法是枚举失败、加测试、加守卫。

**Safety-II**（Hollnagel, 2014）：把可靠性等同于"适应性容量的在场"——系统能优雅降级、操作员能理解、架构让对的事容易做。

**关键转折**：Safety-I 训练你看见 *failure*；Safety-II 训练你看见 *normal work*——一线工程师每天临场修复了多少看不见的小变化。

> 在 200 万行 Haskell + 1500 人 fintech 这种系统里，Safety-II 不是哲学，是日常 SLA。

---

## 卡片 2 · 适应性容量（Adaptive Capacity）

**定义**（David Woods, 2015）：复杂系统在面对超出设计假设的扰动时，仍能维持必要功能的能力。

**反直觉**：适应性容量不是"冗余资源"，是"操作员的认知 + 系统的可调性 + 边界的清晰"的组合。

**Mercury 的实操译解**：
- 操作员能理解 ⇒ 可观测性必须设计进库
- 系统的可调性 ⇒ records of functions 而不是具体函数
- 边界清晰 ⇒ 错误是领域类型而不是 HTTP status code

---

## 卡片 3 · rank-2 类型与 `runST`

```haskell
runST :: (forall s. ST s a) -> a
```

`s` 这个 *存在类型* 被 `forall` 锁在括号内，**任何带 `s` 的引用都不可能"逃出"返回值**。这是 GHC 给"内部可变 + 外部纯"的工程方案。

**Mercury 推广**：任何运行时危险都可以圈在一个 scope 里，只要 scope 的"出口"类型窄到危险物体类型上"挂得住"。连接池、熔断器、retry 状态机本质上都是这个 pattern。

---

## 卡片 4 · 把"咒语"编码进类型

**反模式**：
```haskell
-- 请用 writeWithEvents，不要直接调下面这俩
writeWithEvents  :: Transaction -> [Event] -> IO ()
writeTransaction :: Transaction -> IO ()
publishEvents    :: [Event] -> IO ()
```
"请"是承重的——它在周五下午会塌。

**模式**：
```haskell
data Transact a       -- opaque
record :: Transaction -> Transact ()
emit   :: Event -> Transact ()
commit :: Transact a -> IO a   -- 唯一执行路径
```
把"事件必须在事务里发"变成**唯一的门**。咒语不再需要被记得，它是不可遗忘的。

---

## 卡片 5 · Records of Functions

Haskell 没有 monkey patching。你不能在运行时换掉一个具体顶层函数。

**对比**：
```haskell
-- 无 leverage：
sendRequest :: Request -> IO Response

-- 全 leverage：
data HttpClient = HttpClient
  { sendRequest :: Request -> IO Response
  , getManager  :: IO Manager
  }
```

有了 record，你可以：包装、注入 fault、mock、加 tracing、加租户特定行为，**全部运行时，不动库源码**。

**外推**：这个 pattern 对 Rust trait objects、Go interface{}、TypeScript dependency injection 实质上等价——**任何强类型语言"事后可观测性"的关键是"接口是否一等公民"**。

---

## 卡片 6 · Interceptor Monoid

WAI 的 `Middleware = Application -> Application` 是 endomorphism。endomorphism 在 composition + `id` 下构成 monoid。

一个 record of interceptor hooks 自动得到 fieldwise Semigroup：

```haskell
appTemporalInterceptors =
  mconcat
    [ otelInterceptor
    , sentryInterceptor
    , statementTimeoutInterceptor
    , teamNameInterceptor
    , ...  -- N 个独立 concern
    ]
```

**实用价值**：N 个横切关注点的组合从"工程问题"降级为"列表的连接"。每个 interceptor 独立维护，组合零协调税。

---

## 卡片 7 · Durable Execution 的本质

**问题**：金融流程跨多步、多服务、多失败模式。手卷"DB 状态机 + cron + retry table"等于一个差劲的 workflow 引擎。

**Temporal 的核心抽象**：
- workflow 是 event history 上的**纯函数**
- 确定性约束：replay 必须产生相同 command 序列
- side effect 隔离在 activity 里

**与 Haskell 的天然亲和**：纯函数 + 隔离副作用 = Haskell 在编译期做的事，Temporal 在运行期做相同的事。

> "Frankenstein's monster, in the flattering sense"——Temporal 是把 Erlang 原生能力强行螺栓到主流运行时上的义肢。

---

## 卡片 8 · 教堂 vs 帐篷光谱

**教堂派**（type-everything）：illegal states unrepresentable。重构数周。新人退课。
**帐篷派**（type-nothing）：`String` 和 `IO ()`。改得快但靠记得。

**中道启发式**：
1. **静默腐败 → 进类型**（feedback loop 太长，靠不住人）
2. **会大声失败 → 运行时检查 + 好错误消息**（CI 会抓到）
3. **抵抗把领域的全部内在矛盾建进类型**——业务永远不提供 crispness

---

## 卡片 9 · 领域类型 vs 传输类型

**反模式**：cron job 抛 `StatusCodeException 409`——HTTP 语义泄漏到非 HTTP 上下文。

**模式**：
```haskell
data PaymentError = InsufficientFunds | DuplicateRequest RequestId | PartnerTimeout Partner
toHttpError      :: PaymentError -> HttpResponse
toWorkerStrategy :: PaymentError -> WorkerAction
```
**transport 在边界上翻译，领域在内部保持原生语义**。

**应用普适性**：DDD 的现代再表达。语言无关。

---

## 卡片 10 · `unsafePerformIO` 的工程伦理

`unsafePerformIO` 在 `bytestring`、`text`、`vector` 内部到处都是。Mercury 的态度：

1. **承认它存在**，不假装语言"纯"
2. **文档化类型没检查的不变量**
3. **在 PR 评审里强制不适感**
4. **周期性回访 type-safe 替代方案的可行性**

> "Production Haskell is not the absence of compromise. It is the disciplined containment of compromise."

---

## 卡片 11 · institutional dark matter

**Patrick McKenzie 定理**（patio11）：在 2x 年增长公司里，永远有一半同事工作经验不足一年。

**后果**：任何"老员工记得"的知识就是 institutional dark matter——承重，但对周围多数人不可见。

**生存策略矩阵**：
| 知识载体 | 半衰期 | Mercury 的处理 |
|---|---|---|
| 口头传统 | 月 | 不可接受 |
| Wiki | 季 | 不够 |
| 入职文档 | 半年 | 必要但不充分 |
| 代码注释 | 同上 | 同上 |
| **类型签名** | 与代码同寿 | **首选载体** |
| **Temporal workflow** | 同上 | **流程类知识首选** |
| OpenTelemetry trace | 同上 | **运行时行为首选** |

---

## 卡片 12 · 理想主义者陷阱

**Haskell 招聘悖论**：Mercury CTO 公开说"backend Haskell engineer 是 Mercury 最容易招的角色"——因为兴趣即筛子。

**但**：Haskell 吸引理想主义者。这些人的副作用：

- 想用"新型代数关系类型级编码"重写数据库层 ⇒ 不在帮你 ship feature
- 拒绝合并"一次性脚本里用 String 而非 Text"的 PR ⇒ 不在帮你赶 deadline
- 把每次设计评审变成"按上周读的论文重写一切" ⇒ 拖慢团队

**解药**：主动培育 pragmatism 文化。**Haskell 给的是 power tool 不是宗教**。

> 这条命题可以逐字泛化到 Rust、Lean、Coq、formal methods 阵营——所有"小众但强大"的工具都同时是同类性向的人才磁石，且后者如果失控会反过来吃掉前者。

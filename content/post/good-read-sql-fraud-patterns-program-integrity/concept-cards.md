# 概念卡片 · SQL 反欺诈六模式

> 配套于《SQL 才是反欺诈的母语》一文。每张卡片定位为"一个名词 + 一段可背诵的解释 + 一个反例"。

---

## 卡片 1 · Velocity（速率规则）

**一句话定义**：在一个时间窗口内，对同一持卡人的交易次数计数，超过阈值即触发告警。

**SQL 骨架**：
```sql
HAVING count(*) > N
```

**关键参数**：窗口大小 + 计数阈值。同一阈值不同窗口，能抓不同犯罪结构。

**反例 / 假阳性**：售货机巡检员、批量充值的小商户。

---

## 卡片 2 · Sliding Window with QUALIFY

**一句话定义**：用 `RANGE BETWEEN INTERVAL '5 minutes' PRECEDING AND CURRENT ROW` 配合 `QUALIFY` 实现"滚动 5 分钟窗口的交易次数"，比 `GROUP BY` 更精确。

**支持方言**：Snowflake、BigQuery、Databricks、Teradata 原生支持 `QUALIFY`；Postgres 需要嵌套 CTE。

**适合**：实时速率检测、连续小额刷卡测试。

---

## 卡片 3 · Impossible Travel（不可能行程）

**一句话定义**：用 `LAG()` 取相邻两笔交易的时间和地点，计算等效时速，超过 600 mph 即标记。

**关键函数**：`haversine(prev_loc, location)`——大圆距离。

**阈值层次**：
- 600 mph：保险阈值，几乎零假阳性；
- 100 mph：进入"陆地超速"，开始抓本地克隆环；
- 40 mph：抓城内徒步级别——会扫出大量假阳性。

---

## 卡片 4 · Round-Amount Signal（整数金额信号）

**一句话定义**：极小整数金额（$1、$5、$10）几乎都是 carding（试卡）。

**生活类比**：真实消费有税、有 tip、有零头；$1.00 一杯咖啡在美国几乎不存在。

**注意**：欧元区因含税定价习惯不同，假阳性更高；福利交易里这条规则几乎没用。

---

## 卡片 5 · Just-Below-Threshold Signal（贴线规避信号）

**一句话定义**：$99.99 / $499.99 不是巧合，是有人知道 $100 是验 ID 线、$500 是 ATM 上限。

**犯罪学含义**：贴线行为暴露了"知情者"——这是无意识消费者不会做的事。

**变种**：可以用 `WHERE amount BETWEEN 99.50 AND 99.99` 这种"价格刚好低于审计线的窗口"扫出所有"被规避的政策线"。

---

## 卡片 6 · Self-Baselined Merchant Spike

**一句话定义**：用 168 小时（7 天 × 24 小时）的滚动均值作为该商户基线，spike_ratio > 3 即报警。

**SQL 骨架**：
```sql
ROWS BETWEEN 168 PRECEDING AND 1 PRECEDING
```

**为什么 168**：同时覆盖**日内季节性**（早高峰 vs 凌晨）和**周内季节性**（周二下午 vs 周六上午）。

**反模式**：用全行业均值作为基线——Costco 一分半干完的量会让所有小商户被淹没。

---

## 卡片 7 · Habit Threshold（习惯阈值）

**一句话定义**：在定义"该持卡人的正常时段"时，要求 `tx_count >= 2`——一次不算习惯，两次以上才算。

**为什么**：单次半夜买烟会污染整个"正常时段"，把异常时段永远变成正常。

**适用**：所有"基于历史推断习惯"的规则——时段、商户类别、地理范围。

---

## 卡片 8 · Composable Windows（窗口装弹床）

**一句话定义**：把窗口函数预计算成列（`time_since_last`、`merchant_change`、`running_24h_total`、`tx_of_day`），所有新欺诈假设坍缩为 WHERE 子句。

**工程价值**：把"实现新规则"从工程任务降级为分析任务。新假设从"加一周"变成"加三个 filter"。

**类比**：这是"穷人版 Feature Store"——一张物化表就够。

---

## 卡片 9 · Combined Scoring（组合评分）

**一句话定义**：每条规则单独都有假阳性；交易在 3-4 条规则上同时触发，几乎必为欺诈。

**实施方式**：每条规则输出 0 / 1 / 2 分；总分 ≥ 5 自动拦截，3-4 转人工，1-2 加权观察。

**关键守则**："Auto-blocking on a single rule is how you lose customers."

---

## 卡片 10 · Sentinel NULL（哨兵 NULL）

**一句话定义**：遗留系统用 `9999-12-31` / `0001-01-01` / `0` 表示"无值"，`IS NULL` 会静默漏掉。

**调试技巧**：先 `SELECT col, count(*) FROM t GROUP BY col ORDER BY count DESC LIMIT 20` 看可疑高频值。

**经验**：政府系统、保险系统、银行核心系统都有自己的哨兵约定。永远先问 DBA。

---

## 卡片 11 · PII Discipline（隐私纪律）

**一句话定义**：写反欺诈 SQL 之前，先确认你在哪个数据集上写——脱敏样本、生产副本、还是生产原表。

**最佳实践**：开发用脱敏，验证用样本，生产数据需要审批走访问令牌。

**反模式**：直接在 PII 表上 `SELECT *`——数据外泄责任工程师承担。

---

## 卡片 12 · Warehouse Cost Trap（仓库账单陷阱）

**一句话定义**：`LAG()` over 两年全量交易 = 一次性烧光本月 warehouse 预算。

**正确顺序**：先 `WHERE date_range`，再 `OVER` 窗口。

**通用规则**：任何窗口函数都要先用静态过滤把分区缩小到必要量级。

**SaaS 风险**：Snowflake / BigQuery / Databricks 按算力或字节计费，单次错误查询可能产生四位数美金账单。

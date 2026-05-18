# 术语表 · SQL 反欺诈 / 程序稽核

配套于《SQL 才是反欺诈的母语》一文。覆盖反欺诈业务、数据仓库 SQL、合规缩写等。

| 英文 | 中文 | 备注 |
| --- | --- | --- |
| Program Integrity | 项目稽核 / 项目廉洁 | 美国政府福利项目专门负责"防欺诈、防滥用"的内部团队 |
| Fraud Detection | 欺诈检测 | 也叫 fraud analytics、anti-fraud |
| Card Testing / Carding | 试卡 | 用小额交易验证盗刷卡号是否仍可用 |
| Carding Ring | 试卡团伙 | 通常在毫秒至秒级对 API 暴打 |
| Benefits Trafficking | 福利倒卖 | EBT / Medicaid 卡的"集中刷卡变现"团伙 |
| Skimmer | 刷卡器盗读设备 | 物理装在加油泵、ATM 上的硬件 |
| Velocity Rule | 速率规则 | 单位时间内交易次数超过阈值 |
| Sliding Window | 滑动窗口 | `RANGE BETWEEN ... PRECEDING AND CURRENT ROW` |
| Tumbling Window | 翻转窗口 | `GROUP BY date_trunc('hour', ts)`，无重叠 |
| Impossible Travel | 不可能行程 | 两笔交易在物理上无法由同一持卡人完成 |
| Haversine Distance | 大圆距离 | 球面两点最短距离公式，反欺诈里用来算空间速度 |
| Round-Amount Anomaly | 整数金额异常 | $1.00、$5.00 等极小整数几乎都是试卡 |
| Just-Below-Threshold | 贴线规避 | $99.99 / $499.99 等贴政策线下沿的金额 |
| Self-Baseline | 自我基线 | 让每个商户跟自己历史比，而不是跟全行业比 |
| Rolling Average | 滚动均值 | `AVG() OVER (ROWS BETWEEN N PRECEDING AND 1 PRECEDING)` |
| Spike Ratio | 尖峰比 | 当前值 / 历史均值，>3 视为异常 |
| Off-Hours Rule | 时段异常规则 | 持卡人在自身正常时段外的交易 |
| Habit Threshold | 习惯阈值 | 要求 `count >= 2` 才算"习惯" |
| Composable Windows | 可组合窗口列 | 预计算窗口函数列，让新规则坍缩为 WHERE |
| Feature Store | 特征商店 | ML 行业的"预计算特征基础设施"，本文是其极轻版本 |
| Combined Scoring | 组合评分 | 多条规则联合打分，避免单规则误杀 |
| False Positive | 假阳性 | 把正常交易误判为欺诈 |
| False Negative | 假阴性 | 把欺诈漏过 |
| Auto-Block | 自动拦截 | 规则触发后系统自动拒付，不经人工 |
| Customer Experience (CX) | 客户体验 | 反欺诈的另一面：拦错了客户就流失 |
| PII | Personally Identifiable Information，个人可识别信息 | 反欺诈数据的合规底线 |
| De-identified Data | 去标识化数据 | 移除直接标识符后的数据，开发环境优先用此 |
| Sampled Data | 抽样数据 | 用 10% / 1% 样本开发查询，避免烧仓库 |
| Sentinel Value | 哨兵值 | `9999-12-31` / `0001-01-01` 等代表"无值"的非 NULL |
| QUALIFY | QUALIFY 子句 | Snowflake / BigQuery / Databricks / Teradata 支持的窗口过滤 |
| OVER (PARTITION BY ...) | 窗口分区 | 窗口函数按列分组 |
| LAG() | 取前一行 | 窗口函数，反欺诈里用来比较相邻交易 |
| LEAD() | 取后一行 | 窗口函数，少用于反欺诈但常用于行为预测 |
| ROW_NUMBER() | 行号 | 用来标记"今日第几笔" |
| FIRST_VALUE() | 分区第一行 | 拿持卡人首笔交易特征 |
| Window Function | 窗口函数 | SQL:2003 引入，反欺诈的核心武器 |
| OLAP | Online Analytical Processing | 反欺诈大批量查询的运行环境 |
| OLTP | Online Transaction Processing | 真正记录交易的系统，反欺诈不直接在它上面跑 |
| Data Warehouse | 数据仓库 | Snowflake / BigQuery / Databricks / Redshift |
| ELT | Extract-Load-Transform | 把原始交易先 Load 进仓库，再用 SQL 转换 |
| Materialized View | 物化视图 | 反欺诈"装弹床"的最简实现方式 |
| EBT | Electronic Benefit Transfer | 美国福利电子转账卡 |
| Medicaid | 美国低收入医疗补助 | 政府福利稽核重点之一 |
| SNAP | Supplemental Nutrition Assistance Program | 食品券计划，也用 EBT 发放 |
| ML Fraud Detection | 机器学习反欺诈 | 通常基于 GBDT / 神经网络 / 异常检测 |
| GNN | Graph Neural Network | 团伙识别的热门 ML 方向 |
| Graph Database | 图数据库 | Neo4j、Memgraph、TigerGraph 等，反欺诈赛道竞品 |
| Audit Trail | 审计轨迹 | 反欺诈决策的可追溯证据链 |
| Regulator / Compliance | 监管 / 合规 | 反欺诈逻辑的最终读者之一 |

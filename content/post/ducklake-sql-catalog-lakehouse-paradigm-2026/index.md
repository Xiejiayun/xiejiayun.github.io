---
title: "DuckLake 1.0：当数据湖把元数据交还给 SQL，Iceberg/Delta 该紧张了"
description: "DuckLake 1.0 用一个反直觉的设计——把表元数据放回普通 SQL 数据库——挑战了 Iceberg 与 Delta 引以为傲的分层架构。这不只是另一个表格式，而是对 Lakehouse 概念边界的根本质疑。"
date: 2026-05-05
slug: "ducklake-sql-catalog-lakehouse-paradigm-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 数据湖
    - DuckDB
    - Lakehouse
    - 数据架构
draft: false
---

## 一、为什么 DuckLake 这次不一样

DuckDB 团队 2026 年 5 月发布的 DuckLake 1.0，被很多人轻描淡写地归类为"又一个开源表格式"。但仔细读完 spec 之后，我的判断恰恰相反：**这是过去五年 Lakehouse 范式中第一个敢于正面拆掉"元数据走文件协议"假设的设计**。如果它的简洁性能撑过生产规模考验，Iceberg 和 Delta Lake 在 2027 年将面对严肃的范式竞争。

为了说清楚 DuckLake 到底改了什么，需要先回顾一下 Lakehouse 的元数据演化路径。

## 二、Lakehouse 元数据的三代变迁

```
第一代 (2010–2017)：Hive Metastore + Parquet
  - 元数据放 RDBMS (Hive Metastore 用 MySQL/PostgreSQL)
  - 问题：与计算引擎强耦合、写一致性差、无 ACID

第二代 (2017–2024)：Iceberg / Delta / Hudi
  - 元数据 "落到对象存储里"，用 manifest + snapshot 文件实现 ACID
  - 优点：完全解耦计算与存储、跨引擎、版本化
  - 代价：每次 commit 要读写多个 JSON/Avro 文件，元数据放大严重

第三代 (2026–)：DuckLake = 数据文件在湖里 + 元数据在 SQL DB 里
  - "元数据回家"：所有 schema、snapshot、统计信息存进任意 ANSI SQL 数据库
  - 数据文件依然是 Parquet 在 S3/MinIO 等对象存储
  - 用一句 SQL 完成事务、版本、谱系
```

第二代设计有个被长期忽视的代价——**元数据本身变成了一个慢、贵、复杂的子系统**。Iceberg v2 表在频繁 upsert 场景下，可能产生数百万个小 manifest 文件，每次查询都要先做一轮 manifest pruning，云对象存储的 list/get 成本可能超过实际数据查询成本。Snowflake、Databricks 都不得不维护专有的元数据服务(Polaris、Unity Catalog)来加速这个过程，事实上承认了"纯文件元数据"在大规模场景下的短板。

DuckLake 的判断很直接：**对象存储不是为元数据设计的，何必硬塞**。元数据是结构化的、关系型的、强一致需求的——这正是 SQL 数据库 50 年来被打磨得最好的部分。

## 三、DuckLake 的架构骨架

```
┌──────────────────────────────────────────────────────────────────┐
│                         查询引擎层 (任意)                          │
│   DuckDB · Spark · Trino · Polars · Datafusion · Athena         │
└────────────────────────────────────────┬─────────────────────────┘
                                         │ DuckLake 客户端协议
        ┌────────────────────────────────┼────────────────────────────┐
        ▼                                ▼                            ▼
┌─────────────────┐         ┌────────────────────────┐    ┌─────────────────┐
│ 元数据数据库      │         │   对象存储 (S3/GCS)     │    │ 可选: 缓存层     │
│ Postgres/SQLite │         │  data/<table>/<file>   │    │ DuckDB 本地     │
│ MySQL/DuckDB    │  ◄───►  │  .parquet              │    │ Parquet 缓存    │
│                 │         │                        │    │                 │
│ ducklake_       │         │  纯数据文件             │    │                 │
│ ├─ schemas      │         │  无 manifest           │    │                 │
│ ├─ snapshots    │         │  无 _delta_log         │    │                 │
│ ├─ files        │         │  无 metadata.json      │    │                 │
│ └─ stats        │         │                        │    │                 │
└─────────────────┘         └────────────────────────┘    └─────────────────┘
```

整个架构的关键洞察是：**让对象存储只做它擅长的事(扔大块二进制)，让 SQL 数据库只做它擅长的事(管小而强一致的元数据)**。这不是新发明，反倒是回归了 1990 年代关系数据库教科书里的"目录与堆"分离模型。

举个具体的写入流程对比：

| 步骤 | Iceberg | DuckLake |
|---|---|---|
| 写入新数据 | 写 Parquet 文件 | 写 Parquet 文件 |
| 提交事务 | 写新 manifest + 写 snapshot.json + 写 version-hint.txt + 原子重命名 | 一句 `INSERT INTO ducklake_snapshots` 即完成 |
| 网络往返 | 平均 5–8 次 S3 调用 | 1 次 SQL commit |
| 单次 commit 延迟 | 200–800 ms | 10–40 ms |
| 并发冲突解决 | 基于乐观锁 + 重试 | 数据库原生事务隔离 |

这种简化带来的不只是性能，更是**操作复杂度的指数级下降**。Iceberg 的 metadata GC、orphan file cleanup、snapshot expiration 都需要专门的运维工具；DuckLake 把这些全变成了 SQL DELETE。

## 四、设计上的尖锐取舍

DuckLake 不是没有代价。它有几个非常激进的取舍，市场是否买单将决定它的命运：

**1. 元数据数据库成为新的运维负担**

第二代设计的卖点之一就是"无需运维元数据服务"——存到 S3 里，谁都能读。DuckLake 重新引入了一个需要 HA 部署的 Postgres/MySQL。对小规模场景这毫无负担(SQLite 足矣)，但对企业级跨区部署，意味着要为元数据库做主备、备份、地理复制。

**2. 跨引擎一致性需要协议层而非文件层**

Iceberg 之所以能做到 Spark/Trino/Snowflake/BigQuery 多引擎读写，核心在于元数据是公开的文件格式，谁都能解析。DuckLake 必须依赖每个引擎实现 DuckLake 协议——这是一个鸡生蛋的难题。目前已知 DuckDB、Polars、Datafusion 已支持，但 Spark/Trino 适配仍在早期 PR。

**3. 对象存储原生功能被放弃**

S3 的 conditional write、Versioning、Object Lock 这些为元数据冲突提供了底层支持。DuckLake 完全绕开它们，意味着如果 SQL 数据库出问题(比如分区脑裂)，恢复成本可能比 Iceberg 更高。

## 五、为什么我认为这条路线会赢小到中型场景

数据基础设施的历史一再证明：**最优雅的设计未必赢，但最匹配开发者认知的设计往往赢**。Iceberg 和 Delta 的复杂度对中小团队是过度设计——99% 的公司根本用不上跨数仓互操作，他们要的只是一个"能在 S3 上做事务、版本、time travel 的表"。

DuckLake 击中的人群画像非常精准：

- 数据规模在单数字 TB 到几百 TB
- 团队没有专职数据平台工程师
- 已经在用 DuckDB 做 ad-hoc 分析
- 不需要 Spark/Snowflake 这类重型引擎

这恰好是 Lakehouse 市场近 80% 的潜在用户。Snowflake/Databricks 用 Iceberg/Delta 攻顶，DuckLake 用极简攻底——这是教科书级的颠覆性创新位势。

我做一个偏激的预测：**到 2027 年底，新启动的 Lakehouse 项目里 DuckLake 会占到 25% 以上**，主要侵蚀的不是 Iceberg，而是更老的"PostgreSQL + S3 自研脚本"组合，以及 ClickHouse/StarRocks 在分析场景的市场。

## 六、对 Snowflake 与 Databricks 的潜在冲击

短期看不冲击，但中期值得警惕。原因有三：

**第一**，Snowflake 的 Polaris、Databricks 的 Unity Catalog 都在朝 "元数据集中化" 方向走，本质上承认了 Iceberg 纯文件元数据的不足。DuckLake 跟它们的方向一致，但它是开源的、不绑定任何引擎。

**第二**，DuckDB 在嵌入式分析的渗透速度惊人——dbt-duckdb、Polars+DuckDB 已经成为现代数据栈的默认配置。如果 DuckLake 成为这一生态的事实存储层，下一波创业公司会跳过 Snowflake 而原生构建在 DuckLake 上。

**第三**，云厂商可能反向受益：AWS Athena、GCP BigLake 完全可以快速适配 DuckLake，让用户用更便宜的方式跑分析查询。这会进一步削弱专有 Lakehouse 的议价能力。

## 七、还需要观察的几个变量

- **大规模生产案例**：当前 DuckLake 1.0 还缺乏 PB 级别的公开生产案例，元数据库的扩展上限有待验证。
- **多写入者并发**：高频 streaming 写入下，元数据库会不会成为瓶颈？理论上 Postgres 单实例能支撑数千 TPS，但配合 GC、统计更新可能压力倍增。
- **生态适配速度**：Spark/Trino/Flink 的 connector 何时 GA，将决定企业是否敢押注。
- **与 Iceberg REST Catalog 的互操作**：Iceberg REST Catalog 本质上也在做"元数据走 API"，DuckLake 与它如果能形成协议层互通，反而可能加速整体迁移。

## 八、写在最后：复杂度回潮的信号

过去十年数据基础设施的故事，是"把所有东西都丢进对象存储"的史诗。但 2026 年我们越来越多看到反向的信号：DuckDB 复活嵌入式数据库范式、SQLite 在边缘 AI 场景重新走红、ClickHouse 的本地表性能持续吸引用户、现在 DuckLake 把元数据从对象存储拉回 RDBMS。这不是技术退步，而是**经过一轮极致解耦之后，工程界开始重新评估"什么东西放哪里最合适"**。

DuckLake 不是 Iceberg 杀手，但它是一个清晰的提醒：**架构上看似简陋的方案，常常是真正可持续的方案**。当一项基础设施的元数据需要专门写一份白皮书才能解释清楚时，可能就到了重新思考的时候。

---

### 参考资料

1. InfoQ — *DuckLake 1.0: Data Lake Format with SQL Catalog Metadata*, 2026-05-02. <https://www.infoq.com/news/2026/05/ducklake-1-0/>
2. DuckDB Foundation — *DuckLake Specification 1.0*, 2026. <https://ducklake.select/spec/v1.0>
3. Apache Iceberg — *Table Spec v3*, 2025. <https://iceberg.apache.org/spec/>
4. Phil Eaton — *Who even uses jemalloc in 2026 anyway?*, 2026-04. <https://notes.eatonphil.com/2026-04-jemalloc.html>
5. Confluent — *Moves Schema IDs to Kafka Headers*, 2026-05-01. <https://www.infoq.com/news/2026/05/confluent-schema-headers/>

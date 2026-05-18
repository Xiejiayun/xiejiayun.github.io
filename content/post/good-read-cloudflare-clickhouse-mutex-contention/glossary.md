# 术语表 · Glossary

英中对照，按字母顺序。覆盖 OLAP 引擎、并发原语、ClickHouse 特有概念三大类。

| 英文 / English | 中文 / 中文释义 | 简短说明 |
|---|---|---|
| Active Parts List | 活动 parts 列表 | ClickHouse 内存中保存的当前可读 part 集合，被一把 mutex 保护 |
| Backpressure | 背压 | 下游处理不过来时反向减慢上游产生速率的机制 |
| Binary Search | 二分查找 | 在有序序列上 O(log N) 定位的经典算法，本次优化③核心 |
| Cached Shared Copy | 共享缓存副本 | 多个 reader 共用一份预先生成的快照，避免每次 deep-copy |
| ClickHouse | ClickHouse | 俄罗斯 Yandex 开源的列存 OLAP 数据库，现独立公司运营 |
| Copy-on-Write (COW) | 写时复制 | 多数 reader 直接共享数据，只在写发生时复制——RCU/MVCC 的近亲 |
| Cost-Based Optimizer | 基于代价的优化器 | 用统计信息估算执行计划代价的查询优化器 |
| Critical Section | 临界区 | 同一时刻最多一个或少量线程可进入的代码段 |
| Deferred Copy | 延迟复制 | 把复制操作从读路径推迟/搬到写路径的优化模式 |
| Devector | devector | C++ 容器，类似 deque 但内存布局更紧凑、复制成本更低 |
| Exclusive Lock | 独占锁 | 同一时刻只能有一个 holder 的锁——`std::unique_lock` |
| Flame Graph | 火焰图 | Brendan Gregg 发明的栈采样可视化，垂直轴是调用栈深度 |
| Granule | granule | ClickHouse 主键采样单元，默认 8192 行 |
| Index Granularity | 索引粒度 | 每隔多少行建立一个稀疏索引点 |
| Indirection | 间接层 | 通过一层抽象访问真实数据的设计 |
| Leaky Abstraction | 抽象泄漏 | 上层抽象因下层实现细节而崩塌的现象 |
| Lock Contention | 锁竞争 / 锁争用 | 多个线程争用同一把锁导致的排队等待 |
| MergeTreeData | MergeTreeData | ClickHouse 引擎里保存某张表所有 parts 元数据的类，本次 mutex 所在 |
| MarkRanges | MarkRanges | ClickHouse 表示要扫描的 granule 范围的容器 |
| Multi-tenancy | 多租户 | 同一份基础设施服务多个独立用户/团队的架构 |
| Mutex | 互斥锁 | 最基本的并发原语，同一时刻最多一个 holder |
| MVCC | 多版本并发控制 | 数据库经典并发控制方案，本质也是"读不阻塞写、写不阻塞读" |
| Namespace | 命名空间 / 租户标识 | Cloudflare Ready-Analytics 里用来区分不同租户的字段 |
| OLAP | 在线分析处理 | 列存、批扫描、聚合为主的数据库工作负载 |
| OLTP | 在线事务处理 | 行存、点查、低延迟、强一致性的数据库工作负载 |
| Optimistic Concurrency Control | 乐观并发控制 | 假设冲突罕见，提交时检测的并发控制策略 |
| Partition | 分区 | 表按某个表达式划分的逻辑组，对应一组 parts |
| Partition Pruning | 分区裁剪 | 根据查询条件在规划阶段排除不需要的分区/parts |
| Part | part | ClickHouse 中物理存储单元，一次写入或合并产生一个 |
| PB / PiB | PB / PiB | Petabyte (10^15) / Pebibyte (2^50)；本文 ClickHouse 表 ~2 PiB |
| Profile / Profiler | 性能剖析 / 剖析器 | 收集程序运行时分布信息的工具 |
| Pull Request (PR) | 拉取请求 | GitHub 上提交代码变更供 review/merge 的机制 |
| Query Planner | 查询规划器 | 把 SQL 翻译成可执行物理计划的引擎组件 |
| RCU | 读-复制-更新 | Linux 内核的无锁并发模式，思想同源于 cached shared copy |
| Real Time Sampling | 真实时间采样 | profiler 不论线程是否在 CPU 都采样，能捕获等待 |
| Ready-Analytics | Ready-Analytics | Cloudflare 内部"宽表+namespace"多租户数据平台 |
| Retention Policy | 保留策略 | 数据自动过期/清理的规则 |
| Shared Lock | 共享锁 | 多个 reader 可同时持有的锁——`std::shared_lock` |
| Sparse Index | 稀疏索引 | 不为每行建索引，而是每 N 行采样一个索引点 |
| Stack Trace | 栈轨迹 / 调用栈 | 程序某一时刻的函数调用链 |
| State Space | 状态空间 | 系统累积的全局状态总量，与瞬时工作负载不同 |
| TTL | 生存期 | Time-To-Live，数据自动过期时长 |
| Trace Log | 跟踪日志 | ClickHouse 内置的栈采样表 `system.trace_log` |
| Upstream | 上游 | 开源依赖的原始项目仓库；"上游 PR"即贡献回主仓库 |
| Vectorization | 向量化 | 一次操作多个数据点的 SIMD/批处理执行模式 |
| Wall-Clock Time | 墙钟时间 | 真实流逝的时间，与 CPU time 相对 |
| ZooKeeper | ZooKeeper | Apache 分布式协调服务，ClickHouse 用它存 replicated parts 元数据 |

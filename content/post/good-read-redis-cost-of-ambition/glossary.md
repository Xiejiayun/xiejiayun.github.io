# 术语表 — Redis and the Cost of Ambition

> 英中对照，按主题分组。术语后括号为首次出现时的简短定义。

## 一、Redis 核心架构

| 英文 | 中文 | 简释 |
|---|---|---|
| Remote Dictionary Server (Redis) | 远程字典服务器 | Redis 的本名缩写，强调它原本是"内存字典"的网络版 |
| Data structure server | 数据结构服务器 | Redis 早年自我定位，刻意避开"数据库"一词 |
| Single-threaded event loop | 单线程事件循环 | Redis 的核心架构选择，保证所有操作天然原子 |
| Non-blocking I/O | 非阻塞 I/O | 单线程模型能成立的前提 |
| Atomicity by design | 设计保证的原子性 | 因单线程而免费获得的特性 |
| Primary key | 主键 | 在 Redis 上下文里指 string key |
| TTL (Time to Live) | 生存时间 | 键的过期机制 |
| Ring buffer | 环形缓冲区 | 新 Array 类型的核心使用场景之一 |

## 二、Redis 数据结构

| 英文 | 中文 | 简释 |
|---|---|---|
| String | 字符串 | 最基础的 KV 类型 |
| List | 列表 | 双向链表实现，支持队列语义 |
| Hash | 哈希表 | 字段-值映射 |
| Set | 集合 | 无序去重 |
| Sorted Set (ZSet) | 有序集合 | 带 score 的集合，可用作排行榜/优先队列 |
| Stream | 流 | 5.0 引入，类 Kafka 语义 |
| HyperLogLog | 基数估计 | 概率性近似计数 |
| Bitmap | 位图 | 位级操作 |
| Geo | 地理位置 | 基于 Sorted Set 的封装 |
| BZPOPMIN | 阻塞式弹出最小元素 | 5.0 引入，Charles 认可的"真正有用"的扩展 |

## 三、协议层

| 英文 | 中文 | 简释 |
|---|---|---|
| RESP (REdis Serialization Protocol) | Redis 序列化协议 | Redis 的线协议 |
| RESP2 | RESP 第二版 | 请求-响应严格配对 |
| RESP3 | RESP 第三版 | 引入 Push 类型、Map 类型等，本文批评为"二次系统效应"标本 |
| Push type | 推送类型 | 服务器主动推送的消息 |
| Inline command | 内联命令 | 可用 telnet 直接打的命令格式 |
| Server-assisted client-side caching | 服务器辅助的客户端缓存 | Redis 6.0 引入，依赖 RESP3 |
| Tracking | 客户端缓存跟踪 | 服务器记录哪些客户端缓存了哪些 key |

## 四、扩展 / 模块

| 英文 | 中文 | 简释 |
|---|---|---|
| Redis Modules | Redis 模块系统 | 4.0 引入的动态扩展机制 |
| RedisJSON | JSON 模块 | 让 Redis 当文档数据库 |
| RediSearch | 搜索模块 | 让 Redis 当 Elasticsearch |
| RedisGraph | 图数据库模块 | 已废弃 |
| RedisTimeSeries | 时序数据库模块 | 让 Redis 当 InfluxDB |
| RedisBloom | 布隆过滤器模块 | 概率数据结构 |
| Vector Search | 向量搜索 | Redis 8.x 的 AI 故事核心 |

## 五、商业 / 实体 / License

| 英文 | 中文 | 简释 |
|---|---|---|
| antirez (Salvatore Sanfilippo) | Redis 创始人 | 意大利程序员，曾两次"退休"，2024 后回归 |
| Garantia Data | Redis Inc 的前身 | NoSQL 托管公司，后改名 Redis Labs / Redis Inc |
| Redis Labs / Redis Inc | Redis 商业实体 | 持有 Redis 商标 |
| BSD-3-Clause | BSD 三条款许可证 | Redis 2009-2024 的 license |
| AGPLv3 | GNU 仿射通用公共许可证 v3 | Redis Inc 2024 改用，号称"开源"但实际是 copyleft |
| SSPL | Server Side Public License | MongoDB 发明的反云服务 license |
| RSALv2 | Redis Source Available License v2 | Redis Inc 自定 license |
| Trademark capture | 商标抓取 | 公司逐步获取项目商标控制权 |
| Tri-licensing | 三授权 | 让用户在三种 license 中自选 |
| OSI approval | OSI 认证 | 开源社区对"是不是真开源"的官方认证 |

## 六、Fork / 生态

| 英文 | 中文 | 简释 |
|---|---|---|
| Valkey | Redis 的 BSD fork | 由 Linux Foundation 托管 |
| KeyDB | 早期的多线程 Redis fork | 已被 Snap 收购，发展放缓 |
| DragonflyDB | Redis 兼容的现代 KV | 多线程、共享内存架构 |
| Microsoft Garnet | 微软的 Redis 兼容服务器 | .NET 实现 |
| ElastiCache | AWS 的托管 Redis | 让 Redis Inc 想改 license 的直接动机 |
| MemoryStore | Google Cloud 的托管 Redis | 同上 |

## 七、相关概念 / 人物

| 英文 | 中文 | 简释 |
|---|---|---|
| Kyle Kingsbury (Aphyr) | Jepsen 创始人 | 分布式系统正确性测试领域权威 |
| Jepsen test | Jepsen 测试 | 模拟网络分区/崩溃验证一致性的工具集 |
| Linearizability | 可线性化 | 最严格的一致性级别 |
| Stale read | 过时读 | 读到旧版本数据的 bug 类型 |
| Aborted read | 中止读 | 读到未提交事务的数据 |
| Raft | Raft 共识协议 | Redis-Raft 想实现的协议 |
| Brooks's Second System Effect | 布鲁克斯第二系统效应 | 《人月神话》经典命题 |
| Astronaut mode | 宇航员模式 | antirez 自创词，无真实用例的设计 |
| Tastefully chosen | 有品味地挑选 | Charles 用来形容早期 Redis 数据结构 |
| Reductio ad absurdum | 归谬法 | Charles 用来描述"缓存的客户端还要缓存"的逻辑 |

## 八、Charles Leifer 个人项目 / 关联词

| 英文 | 中文 | 简释 |
|---|---|---|
| peewee | peewee ORM | Charles 的代表作，轻量 Python ORM |
| cysqlite | cysqlite 驱动 | Charles 2026 年 2 月发布的新 SQLite 驱动 |
| pysqlite3 | pysqlite3 | Charles 维护的另一个 SQLite Python 驱动 |
| Walrus | Walrus | Charles 写的 Redis Python 封装库 |

## 九、本文出现的文化引用

| 英文 | 中文 | 简释 |
|---|---|---|
| Tower of Babel | 巴别塔 | 文章首图 Bruegel 名画，喻"野心导致失败" |
| The Death of Caesar | 凯撒之死 | 文章中段插图，喻"野心是致命缺陷" |
| _The Mythical Man-Month_ | 《人月神话》 | Brooks 的软件工程经典 |
| _Paradise Lost_ | 《失乐园》 | 弥尔顿的史诗，Charles 多次引用 |
| _Cormac McCarthy_ | 科马克·麦卡锡 | Charles 在《Ghost in the Shell》中引用过 |

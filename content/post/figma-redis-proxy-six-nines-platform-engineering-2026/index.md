---
title: "Figma 自建 Redis 代理冲六个 9：平台工程的钟摆，正从'抽象'摆回'特化'"
description: "Figma 选择不用 Envoy 也不用 ElastiCache，而是用 Rust 自建 Redis 代理冲击六个 9 可用性。这不只是工程选择，而是平台工程范式从'通用抽象'摆回'业务特化'的信号。"
date: 2026-05-05
slug: "figma-redis-proxy-six-nines-platform-engineering-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 平台工程
    - Redis
    - 高可用
    - 中间件
    - 系统设计
draft: false
---

## 一、一个反直觉的工程决策

2026 年初，Figma 工程团队披露了一个看起来"逆潮流"的决定：放弃直接使用 AWS ElastiCache 内置的集群代理，也不沿用业界主流的 Envoy 通用 L7 代理方案，而是用 Rust 自研了一层专门给 Redis 用的代理，把整条缓存链路的可用性目标从五个 9 拉升到六个 9。

六个 9 是什么概念？一年只允许累计宕机 **31.5 秒**。对一个每天承载几千万协同编辑会话、并把 Redis 当作"在线状态、光标位置、协作锁"主存的产品，这个数字背后其实写着一句话：**任何一次客户端层面的重连风暴、任何一次跨 AZ failover 期间的连接抖动，都会击穿 SLO 预算**。

这件事之所以值得写一篇深度文章，不是因为 Figma 又造了一个轮子，而是因为它撞到了过去十年云原生中间件叙事里一根最敏感的神经：**通用抽象的尽头，是业务特化的回归**。

## 二、为什么通用方案不够：三个被反复低估的维度

把 Figma 的论证拆开看，本质是对通用云中间件在三个维度上的"局部不满"，而不是全盘否定。

**1. 连接管理：客户端连接池是错误的抽象层**

每个应用实例都维护自己的 Redis 连接池，是过去十几年的默认形态。但当应用容器扩到几千个、Redis 后端做主从切换时，会出现一个几乎无法消除的现象：所有客户端**同时**意识到旧主挂了，**同时**对新主发起重连，新主瞬间被 connection storm 打爆，failover 从理论上的 200ms 变成实际的 8~15 秒。这 8 秒就是六个 9 预算的 16 倍。

把连接池抽到代理层、并让代理在客户端和后端之间维持稳态长连接，是唯一能彻底消除这个 burst 的办法。Envoy 的 TCP proxy 模式可以做一部分，但它不懂 Redis 协议里 `MULTI/EXEC`、`SUBSCRIBE`、`CLUSTER` 这些有状态语义，无法在连接级别做安全的复用。

**2. 故障域隔离：通用代理把"半径"算错了**

ElastiCache 的内置代理在 AWS 的语境里是好东西，但它的故障域和 Redis 节点本身耦合——同一 AZ 的代理挂了，整片流量需要 DNS/ENI 切换。Figma 的做法是把代理作为**独立可扩展层**部署，代理实例数和 Redis 节点数解耦，单代理实例故障只影响该实例上的活跃连接，且通过协议感知重试在客户端无感重放。

**3. 协议感知重试：通用 L7 代理不敢做的事**

Envoy 在 HTTP 层可以做幂等重试，但 Redis 的命令幂等性需要协议层判断：`GET`、`HGET` 可以重放，`INCR`、`LPUSH` 不行，`EVAL` 取决于脚本内容。一个真正能为 Redis 提供透明 failover 的代理，必须内嵌这张语义表，并且能在 pipeline 中部分重试、部分回退。这件事 Envoy filter 写起来代价极高，自研一个窄而深的代理反而更便宜。

## 三、架构素描

下面这张图大致还原了 Figma 公开材料里的拓扑思路（具体实现细节不公开，这里是抽象示意）：

```
+------------------+        +------------------+        +------------------+
|  app pod (x N)   |  TCP   |  Redis Proxy     |  TCP   |  Redis Cluster   |
|  thin client     +------->+  (Rust, per-AZ)  +------->+  primary/replica |
|  no conn-pool    |        |  - conn coalesce |        |  shard 0..M      |
+------------------+        |  - retry policy  |        +------------------+
                            |  - shard router  |
                            |  - health probe  |
                            +--------+---------+
                                     |
                                     v
                            +------------------+
                            |  control plane   |
                            |  topology / SLO  |
                            +------------------+
```

几个关键点：

- **客户端是"瘦"的**：只保留一条到本地代理的连接，没有连接池、没有 cluster 拓扑感知、没有重试逻辑。客户端库代码量缩到不到 500 行。
- **代理按 AZ 部署**：每个 AZ 一组代理实例，跨 AZ 流量由代理之间转发或直接打到目标分片，可观测性从客户端剥离到代理 metrics。
- **控制面独立**：拓扑变更、SLO 阈值、限流策略都从控制面下发，代理本身是"愚而稳定"的数据面。

这个分层和 Envoy + xDS 的形态很像，但因为只服务一个协议、一个业务，整个数据面可以用 Rust 写到几千行代码、p99 延迟开销控制在 200μs 以内。

## 四、历史的钟摆：自研代理的第三次循环

把 Figma 这件事放回工业史里看，其实并不新鲜。这是过去 14 年里"自研 Redis/KV 代理"路径的第三次回归。

| 年份 | 项目 | 动机 | 退潮原因 |
|---|---|---|---|
| 2012 | Twitter **twemproxy** (nutcracker) | 为推文 fan-out 解决 memcached/Redis 分片+连接收敛 | 不支持高可用、不支持 cluster 协议 |
| 2014 | Netflix **Dynomite** | 给 Redis 套上多区域多副本协议 | 运维复杂、Redis Cluster 原生方案普及后被边缘化 |
| 2016 | Lyft **Envoy** | 通用 L7 代理统一服务网格 | 通用化太强，对协议级语义无能为力 |
| 2020 | AWS **ElastiCache cluster mode w/ proxy** | 托管化、降低客户端复杂度 | 故障域和后端耦合，failover 体验仍依赖客户端 |
| 2026 | Figma 自研 Rust 代理 | 六个 9、协议感知 failover | —— 故事正在发生 —— |

每一次循环都不是简单的复读，而是螺旋上升：

- twemproxy 解决了**连接收敛**，但停在静态拓扑；
- Dynomite 解决了**跨区域复制**，但没解决控制面动态性；
- Envoy 解决了**通用数据面 + 控制面分离**，但放弃了协议语义；
- 2026 年这一轮回归，要解决的是**协议感知 + 控制面动态性 + 极致可用性**三件事的同时成立。

钟摆从来没停过：业务规模触顶时摆向"自研特化"，规模红利消化完后摆向"通用抽象"，然后下一代业务又把它推回去。

## 五、平台工程的边界：抽象不是越多越好

国内外这两年关于"平台工程"（Platform Engineering）的讨论，几乎默认它等于"做一层封装、做一层 IDP（Internal Developer Platform）、做一层 self-service"。Figma 这件事提供了一个相反方向的样本：**真正成熟的平台工程，知道什么时候应该把通用抽象敲碎，重新特化回业务**。

可以列三条经验性原则：

1. **抽象的成本是延迟与盲区**。每多一层通用代理，就多一段不属于业务的延迟预算和一片不属于业务的可观测盲区。当 SLO 卷到六个 9，这些"小成本"会变成致命成本。
2. **协议语义不可外包**。任何"我们的代理 / 网关支持所有协议"的承诺，在极端可用性场景下都要打折。协议越复杂、有状态命令越多，外包越危险。Redis 是这样，Kafka 是这样，gRPC streaming 也是这样。
3. **平台团队的职责，是判断哪些通用件该用、哪些必须特化**。这个判断本身才是平台团队的核心价值，而不是"我们提供了多少通用件"。

Marc Brooker 在他 2024 年那篇被广泛引用的短文 *It's time to be right* 里说过一句很重的话：分布式系统工程师在过去十年学会了"快速迭代、容忍错误"，但真正难的是"在该 right 的地方坚持 right"。Redis 代理这种位于关键路径的中间件，就是必须 right 的地方——它一旦错，错的是整个产品的在线状态。

## 六、对照 Cloudflare：六个 9 的两条路

值得放在一起看的，是 Cloudflare 同期推进的 **Code Orange / Fail Small** 项目。两家公司都在追六个 9，但路径几乎正交。

| 维度 | Figma Redis Proxy | Cloudflare Fail Small |
|---|---|---|
| 切入点 | 协议感知的中间件 | 故障收敛半径（blast radius） |
| 主要手段 | 连接收敛 + 协议级重试 + 控制面 | 配置变更分级灰度、依赖图收敛、能力降级 |
| 优化对象 | 缓存数据面 | 整个边缘网络的变更安全 |
| 哲学 | 让每条命令都有最大成功概率 | 让每次故障都只影响最小区域 |
| 代价 | 多一层基础设施 + 自研维护成本 | 更慢的全球 rollout、更复杂的 feature flag 体系 |

把两者放在一起，能看到一个有趣的事实：**六个 9 在 2026 年已经不再是"单点更可靠"能解决的问题，而是要么把状态从客户端抽走（Figma 路径），要么把变更半径压到极小（Cloudflare 路径）**。

如果再粗暴一点概括：Figma 是在攻**稳态可用性**，Cloudflare 是在攻**变更可用性**。前者赌的是流量模式可预测，后者赌的是人为变更才是故障的真正大头（业内反复出现的统计：70%+ 的生产事故来自变更，而不是负载或硬件）。

## 七、对工程团队的启发：什么时候该自研一个代理？

不是每个团队都该模仿 Figma。把这件事抽象成一个判断框架，大概是这样：

- 你的关键路径中间件（Redis / Kafka / 数据库连接池）是否承担了**业务在线状态**，而不只是缓存或队列？
- 你的客户端实例数是否已经多到"重连风暴"成为现实威胁（经验阈值大约是 1000+ 长连接客户端）？
- 你能否独立招募并稳定维护一个 3~5 人的中间件小组，而不是把它寄生在 SRE 或后端团队的边角时间里？
- 你的 SLO 目标是否真的写到了五个 9 以上？如果只是四个 9，通用方案 + 良好的客户端实践完全够。

如果三条以上是 yes，自研代理就值得考虑；否则，老老实实用 Envoy / ElastiCache / 托管方案，把工程预算花在业务价值更高的地方。

平台工程不是炫技，也不是抄大厂方案。它的本质是**为业务做正确的"特化 vs 抽象"的资源分配**。Figma 这次自研代理不是要劝所有人都自研，恰恰相反——它告诉行业：通用抽象有边界，业务特化有回归窗口，**判断窗口在哪里、能不能进得去，才是这一代平台团队的真功夫**。

钟摆还会继续摆。下一次摆向"通用"，可能是 WASM filter 让协议感知逻辑可以在 Envoy 里以低成本写出来；再下一次摆向"特化"，可能是因为 AI 推理服务把另一类有状态中间件推到极限。每一次摆动都不是"对错"，而是"当前规模与当前抽象的匹配度"。

理解这一点，就比记住任何一篇架构文章都更接近平台工程的本质。

## 引用来源

- InfoQ：*Figma Builds In-House Redis Proxy for Higher Availability* — <https://www.infoq.com/news/>
- Cloudflare Blog：*Code Orange: Fail Small is complete* — <https://blog.cloudflare.com/>
- Twitter Engineering：*twemproxy — A fast, light-weight proxy for memcached and redis* — <https://github.com/twitter/twemproxy>
- Envoy Proxy 官方文档：*Architecture overview / L4 filters* — <https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/intro/intro>
- Netflix TechBlog：*Introducing Dynomite — Making Non-Distributed Databases, Distributed* — <https://netflixtechblog.com/>
- Marc Brooker：*It's time to be right* — <https://brooker.co.za/blog/>
- AWS 文档：*ElastiCache for Redis cluster mode and proxy behavior* — <https://docs.aws.amazon.com/AmazonElastiCache/>

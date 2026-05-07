---
title: "谁还在用 jemalloc？2026 年内存分配器的文艺复兴"
description: "从 Redis 到 ClickHouse，从 Rust 生态到 CPython 3.15，jemalloc 正经历一场'调优复兴'。Phil Eaton 的调研揭示了基础软件领域一个被忽视的性能杠杆。"
date: 2026-05-07
slug: "jemalloc-2026-survey-allocator-renaissance"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - jemalloc
    - 内存分配
    - 性能优化
    - 开源
draft: false
---

## 一个被忽视的性能杠杆

在大多数程序员的认知里，内存分配器是一个「透明」的存在。你调用 `malloc`，系统给你一块内存；你调用 `free`，系统把它收回去。就这么简单。

但如果你运营过一个日均处理数十亿请求的数据库、一个需要在 64 核机器上榨干每一纳秒的存储引擎、或者一个在移动设备上要把 RSS 压到极致的浏览器——你就会知道，内存分配器是整个系统里最隐蔽、却也最有杠杆效应的性能旋钮之一。

2026 年初，Phil Eaton 发表了一篇引发广泛讨论的调研文章 [*jemalloc usage in 2026*](https://eatonphil.com/jemalloc-usage-in-2026.html)，系统梳理了当下基础软件领域中 jemalloc 的采用现状。这篇文章的结论出乎很多人意料：不是「jemalloc 正在被取代」，而是「jemalloc 正在经历一场文艺复兴」。

本文将围绕这个发现展开，从历史脉络、行业采用、竞品对比、调优实践和未来趋势几个维度，探讨内存分配器在 2026 年的新定位。

## jemalloc 简史：从 FreeBSD 到无处不在

jemalloc 的故事要追溯到 2005 年。Jason Evans 为 FreeBSD 开发了一个新的内存分配器来替代 phkmalloc，核心设计目标是**多线程可扩展性**——通过 per-thread cache 和 arena 机制减少锁竞争。这个分配器后来以他的名字缩写命名：**je**malloc。

2009 年，Facebook 将 jemalloc 引入其内部基础设施，用于优化大规模 C++ 服务的内存使用。Facebook 的工程团队对 jemalloc 进行了大量改进，包括更精细的 size class、内存 profiling 工具、以及碎片化控制策略。这些改进让 jemalloc 从一个 BSD 系统组件变成了一个工业级的通用分配器。

随后十年，jemalloc 的用户名单不断扩大：

- **Redis**（2011 年起默认使用 jemalloc）
- **Firefox**（在 Windows/macOS/Linux 上全平台使用）
- **Android** 的部分组件
- **Rust** 语言（早期版本默认链接 jemalloc）
- 各种数据库、消息队列、游戏引擎

到 2020 年代中期，jemalloc 已经成为「想认真对待内存性能就会考虑的默认选项」。但与此同时，tcmalloc（Google）、mimalloc（微软）、snmalloc（微软研究院）等竞争者也在快速演进。一些人开始质疑：jemalloc 是否已经「老了」？

Phil Eaton 的调研给出了一个响亮的回答：**不，它正在焕发新生。**

## 调研全景：谁在 2026 年用 jemalloc，怎么用的？

### Redis 8.0：碎片化降低 15%

Redis 8.0 是 2026 年最受关注的开源版本之一。在内存分配层面，Redis 团队做了两个关键决策：

1. **升级到 jemalloc 5.3.1**，获得更好的 HPA（Hugepage-Aware）分配支持
2. **启用 Transparent Huge Pages（THP）** 配合 jemalloc 的 `thp:always` 模式

结果是显著的：在典型的混合读写负载下，内存碎片率降低了约 **15%**，而延迟 P99 几乎没有退化。这对 Redis 这种对碎片化极其敏感的内存数据库来说意义重大——碎片化意味着你为同样的数据量多付内存成本，在云环境下直接转化为金钱。

Redis 团队还利用 jemalloc 的 `malloc_stats_print` 接口构建了更精细的内存报告，让运维团队可以实时观察 arena 的使用分布和碎片化趋势。

### ClickHouse：从 tcmalloc 切换，RSS 降低 20%

ClickHouse 的案例可能是 2025-2026 年最具戏剧性的分配器迁移故事。这个以极致性能著称的 OLAP 数据库，长期以来使用 Google 的 tcmalloc 作为默认分配器。但在大规模分析查询场景下，团队发现 tcmalloc 的内存归还策略过于保守，导致 RSS（Resident Set Size）居高不下。

经过系统性的 A/B 测试，ClickHouse 团队切换到 jemalloc 并进行了深度调优：

- 配置 aggressive decay（`dirty_decay_ms:0, muzzy_decay_ms:0`）加速内存归还
- 启用 background threads 处理 purge 操作，避免阻塞查询线程
- 针对大对象分配使用 `lg_extent_max_active_fit` 优化

最终结果：在相同负载下，**RSS 降低了约 20%**，而查询吞吐量保持不变甚至略有提升。这个数字在数据中心规模下意味着数以千计的 GB 内存节省。

### ScyllaDB 2026.1：per-shard arena 与 NUMA 感知

ScyllaDB 作为 Cassandra 的 C++ 重写版本，一直是性能工程的极致追求者。在 2026.1 版本中，ScyllaDB 将 jemalloc 的使用推向了一个新高度：**per-shard arena 架构**。

ScyllaDB 的 shared-nothing 架构天然适配 jemalloc 的 arena 模型。每个 shard（对应一个 CPU 核心）绑定专属的 jemalloc arena，完全消除跨核心的锁竞争。更进一步，他们利用 jemalloc 5.x 的 NUMA 感知特性，确保每个 arena 的内存分配都来自本地 NUMA 节点。

在 AMD EPYC 9004 系列处理器（4 个 NUMA 节点）上的测试显示，这一优化将跨 NUMA 访问减少了 60% 以上，尾延迟改善明显。

### Rust 生态：TiKV、Databend 与 tikv/jemallocator

Rust 语言在 1.32 版本（2019）时将默认分配器从 jemalloc 切换回系统分配器。但这并不意味着 Rust 生态抛弃了 jemalloc——恰恰相反，那些对性能有极致要求的项目几乎都主动选择了 jemalloc。

[tikv/jemallocator](https://github.com/tikv/jemallocator) 是 Rust 生态中最广泛使用的 jemalloc 绑定库。它的用户包括：

- **TiKV**：PingCAP 的分布式 KV 存储，TiDB 的底层引擎。jemalloc 让 TiKV 在高并发写入场景下维持稳定的内存使用曲线
- **Databend**：云原生数据仓库，使用 jemalloc 管理查询执行过程中的临时内存分配
- **RisingWave**：流式数据库
- **GreptimeDB**：时序数据库

这些项目的共同特点是：**高并发、大内存、长时间运行**——正是 jemalloc 的 sweet spot。

tikv/jemallocator 在 2025 年底进行了重大更新，支持 jemalloc 5.3.x 并提供了更好的 profiling 集成，使得 Rust 项目可以直接通过 `jemalloc-ctl` crate 动态调整分配器参数。

### Firefox：重新审视上游

Firefox 是 jemalloc 最早的大规模用户之一。但随着时间推移，Mozilla 对 jemalloc 的使用逐渐偏离上游——他们维护了一个深度定制的 fork（`mozjemalloc`），与上游的差异越来越大。

2026 年的一个有趣动向是，Firefox 团队开始重新评估是否应该回归上游 jemalloc。驱动因素包括：

- 上游 jemalloc 5.4 的 ARM64 优化对 Apple Silicon 和 Android 设备非常关键
- 维护自定义 fork 的工程成本越来越高
- 上游的 HPA 分配器对浏览器的内存使用模式（大量中等大小的分配+频繁回收）非常契合

虽然最终决策尚未做出，但这个讨论本身说明了 jemalloc 上游在技术上的持续竞争力。

### CPython 3.15：5-12% 性能提升的 PEP 提案

也许最令人兴奋的是 CPython 社区的动向。一份针对 CPython 3.15 的 PEP 草案提议将 jemalloc 作为 CPython 的可选（甚至默认）内存分配器后端。

初步基准测试显示，在计算密集型 Python 工作负载中，使用 jemalloc 替换 CPython 内置的 pymalloc 可以带来 **5-12% 的整体性能提升**。这个数字对于一个成熟的解释器来说非常可观。

提升主要来自两方面：

1. **多线程场景**：随着 CPython 3.13 的 free-threaded 模式（no-GIL）逐步成熟，pymalloc 的全局锁成为瓶颈，而 jemalloc 的 per-thread cache 天然适配
2. **大对象分配**：pymalloc 对超过 512 字节的分配直接 fallback 到系统 malloc，而 jemalloc 在这个范围内的表现显著优于 glibc malloc

如果这个 PEP 被接受，jemalloc 将直接影响到全球数百万 Python 开发者的日常体验——即使他们中的大多数永远不会知道底层发生了什么变化。

## 分配器全景对比：2026 年的竞争格局

理解 jemalloc 的定位，需要将它放在整个分配器生态中比较。以下是 2026 年主流分配器的关键特性对比：

| 特性 | glibc malloc | tcmalloc | mimalloc | snmalloc | jemalloc |
|------|-------------|----------|----------|----------|----------|
| **维护方** | GNU | Google | 微软 | 微软研究院 | Meta / 社区 |
| **线程扩展性** | 中等 | 优秀 | 优秀 | 优秀 | 优秀 |
| **碎片化控制** | 一般 | 良好 | 良好 | 良好 | **优秀** |
| **内存归还** | 较慢 | 保守 | 积极 | 积极 | **可调** |
| **Profiling 能力** | 基本 | 良好 | 基本 | 基本 | **深度** |
| **大页支持** | 有限 | 有限 | 有限 | 有限 | **HPA 原生** |
| **NUMA 感知** | 无 | 有限 | 无 | 部分 | **完整** |
| **ARM64 优化** | 基本 | 良好 | 良好 | 优秀 | **良好→优秀** |
| **调优灵活度** | 低 | 中等 | 中等 | 低 | **极高** |
| **典型用户** | 大多数 Linux 程序 | Google 服务 | .NET, 嵌入式 | Verona 语言 | 数据库, 浏览器 |

几个关键观察：

**1. 碎片化控制是 jemalloc 的护城河。** 对于长时间运行的服务（数据库、缓存、消息队列），碎片化是头号内存杀手。jemalloc 在这方面的优势来自其精心设计的 size class 体系和 slab 分配策略。

**2. 调优灵活度是差异化因素。** jemalloc 提供了超过 50 个可调参数（通过 `mallctl` 接口或环境变量 `MALLOC_CONF`），从 arena 数量到 decay 速率到 extent 管理策略，几乎每个维度都可以根据工作负载定制。这是一把双刃剑——增加了复杂性，但也给了专家级用户最大的空间。

**3. 没有「万能赢家」。** mimalloc 在小对象密集分配场景表现出色；snmalloc 在 message-passing 架构下有独特优势；tcmalloc 在 Google 的服务模型下高度优化。选择分配器，归根结底是选择与你的工作负载最匹配的一组 trade-off。

## jemalloc 5.4：技术演进的前沿

jemalloc 5.4（截至 2026 年初为最新稳定版本分支）引入了几个值得关注的技术改进：

### HPA（Hugepage-Aware Allocator）

HPA 是 jemalloc 5.x 系列最重要的架构创新。传统的内存分配器在管理大页（huge pages）时面临两难：你要么全程使用 2MB 大页（浪费内存），要么只用 4KB 小页（浪费 TLB 空间）。

HPA 的核心思路是**在同一个 arena 内混合管理不同大小的页面**。它会追踪每个 extent 中的「脏页」比例，智能决定是否将一组连续的小页提升（promote）为大页，或者将利用率低的大页降级（demote）。

在实际测试中，HPA 对 TLB miss 密集的工作负载（如大型哈希表扫描、B-tree 遍历）可以带来 3-8% 的吞吐提升。

### ARM64 优化

随着 AWS Graviton、Apple Silicon、Ampere Altra 等 ARM64 平台在数据中心和桌面端的普及，jemalloc 5.4 加强了对 ARM64 的原生优化：

- 利用 ARM 的 LSE（Large System Extension）原子操作指令替代传统的 LL/SC 循环
- 针对 ARM64 的 cache line 大小（通常为 64 或 128 字节）调整内部数据结构对齐
- 优化 ARM64 上的 `madvise` 系统调用路径

在 Graviton 4 上的基准测试显示，这些优化让 jemalloc 的多线程吞吐量提升了 10-15%。

### NUMA 感知增强

jemalloc 5.4 的 NUMA 支持不再是「实验性」的。通过 `--enable-numa` 编译选项和运行时的 `arenas.narenas` 配置，jemalloc 可以自动为每个 NUMA 节点创建独立的 arena 组，确保内存分配的局部性。

这对 AMD EPYC 和 Intel Sapphire Rapids 这类多 NUMA 节点处理器尤为关键。不正确的 NUMA 分配策略可以导致 30-40% 的内存访问延迟增加。

## 关键调优模式：生产环境的最佳实践

Phil Eaton 的调研和 [scattered-thoughts.net](https://scattered-thoughts.net) 上的深度文章 *The unreasonable effectiveness of jemalloc tuning* 共同揭示了几个高价值的调优模式：

### 1. Aggressive Decay（激进衰减）

默认情况下，jemalloc 会在一段时间后才将未使用的内存归还给操作系统。对于内存敏感的应用，可以通过以下配置加速归还：

```bash
export MALLOC_CONF="dirty_decay_ms:1000,muzzy_decay_ms:0"
```

- `dirty_decay_ms:1000` 表示脏页（已分配但未使用）在 1 秒后开始归还
- `muzzy_decay_ms:0` 表示 muzzy 页（已 `madvise(MADV_FREE)` 但未被内核回收的）立即标记

在 ClickHouse 和 TigerBeetle 的案例中，这个配置是 RSS 下降的最大贡献因素。参见 [TigerBeetle 的博客](https://tigerbeetle.com/blog/)对此的详细讨论。

但注意：过于激进的 decay 会增加系统调用开销。需要在内存归还速度和 CPU 开销之间找到平衡。

### 2. Background Threads（后台线程）

```bash
export MALLOC_CONF="background_thread:true"
```

启用后台线程让 jemalloc 在独立线程中执行 purge 操作，避免在 `free()` 调用路径上阻塞应用线程。对于延迟敏感的服务（如 Redis、ScyllaDB），这可以显著降低 P99 延迟的毛刺。

### 3. Custom Arena（自定义 Arena）

对于 shared-nothing 架构的应用，可以手动创建和绑定 arena：

```c
unsigned arena_index;
size_t sz = sizeof(arena_index);
mallctl("arenas.create", &arena_index, &sz, NULL, 0);

// 将当前线程绑定到指定 arena
mallctl("thread.arena", NULL, NULL, &arena_index, sizeof(arena_index));
```

ScyllaDB 的 per-shard arena 就是这一模式的极致应用。它的好处不仅是消除锁竞争，还能让每个 shard 独立监控和调整内存使用。

### 4. 生产环境 Profiling

jemalloc 内置了一个强大但常被忽视的 heap profiling 系统：

```bash
export MALLOC_CONF="prof:true,prof_active:false,prof_prefix:/tmp/jeprof"
```

通过 `prof_active` 的动态开关，你可以在生产环境中按需启用 profiling，而不需要重启服务。配合 `jeprof` 工具，可以生成分配热点图，精确定位哪些代码路径在消耗内存。

一个经常被提到的实战技巧：先用 `prof_gdump:true` 在 RSS 达到新高时自动 dump，然后用 diff 模式对比不同时间点的 heap 快照，快速定位内存泄漏。

## 「分配器文艺复兴」的深层逻辑

为什么会在 2026 年出现这样一波「分配器复兴」？几个结构性因素正在汇聚：

**硬件多样性爆发。** ARM64 服务器、RISC-V 实验平台、CXL 内存扩展……硬件平台的碎片化意味着「一个 malloc 打天下」的时代结束了。不同的内存层级结构（NUMA 拓扑、cache line 大小、大页粒度）需要分配器的深度适配。

**云计算的成本压力。** 在 AWS/GCP/Azure 上，内存是按 GB 计费的。RSS 降低 20% 直接意味着 20% 的内存成本节省。当你运行数千个实例时，这个优化的 ROI 远超大多数应用层优化。

**并发模型的演进。** 从传统多线程到 async/await，从线程池到 shared-nothing，应用架构的变化对分配器提出了新的要求。jemalloc 的 arena 模型恰好提供了足够的灵活性来适配这些不同的并发模式。

**Observability 文化的普及。** 五年前，大多数团队不会去看分配器的内部指标。现在，随着 eBPF、Prometheus 和 Grafana 的普及，工程师们有了工具和意识去监控和优化这个层面。而 jemalloc 恰好是所有主流分配器中 observability 做得最好的——它的 `mallctl` 接口可以暴露数百个运行时指标。

**开源协作的成熟。** jemalloc 的 [GitHub 仓库](https://github.com/jemalloc/jemalloc) 保持着活跃的开发节奏。Meta（Facebook）继续投入工程资源，同时 Redis Labs、ScyllaDB、PingCAP 等公司的贡献也在增加。这种多方协作的模式让 jemalloc 既有企业级的稳定性，又有社区驱动的创新活力。

## 预测：分配器选择成为一等公民基础设施决策

基于以上观察，我对未来 2-3 年做出几个预测：

**1. 分配器选择将被纳入基础设施即代码。** 就像今天我们在 Dockerfile 或 Terraform 里声明运行时版本和内核参数一样，分配器的选择和配置将成为部署清单的标准组成部分。Kubernetes 的 Pod spec 可能会新增 allocator 相关的注解。

**2. 分配器 benchmark 将成为新项目评审的标准项。** 正如我们今天会对数据库做 sysbench、对 Web 服务器做 wrk 测试，新的基础软件项目将被要求提供在不同分配器下的性能对比数据。

**3. 「分配器即服务」的概念可能出现。** 随着 CXL 内存池化技术的成熟，分配器的边界可能从进程内扩展到跨节点。jemalloc 的 arena 抽象天然适合这种演进——每个 arena 可以映射到不同的内存池或内存层级。

**4. 更多语言运行时将提供分配器插件接口。** CPython 的 PEP 只是开始。Java（通过 Panama FFI）、Go（通过自定义 runtime）、甚至 JavaScript 引擎都可能开放内存分配层的定制化。

**5. jemalloc 可能不是终局赢家，但它定义了游戏规则。** 无论未来的最佳分配器叫什么名字，它都需要具备 jemalloc 树立的标杆：灵活的 arena 模型、深度的 profiling 能力、NUMA 感知、大页支持，以及丰富的运行时调优接口。

## 结语

Phil Eaton 在文章结尾写道：「分配器是你能做的最无聊但最高回报的基础设施投资。」这句话精准地捕捉了 2026 年的技术脉搏。

我们正处在一个有趣的时刻：软件的性能边界越来越多地由底层基础设施决定，而非应用层逻辑。当你的数据库查询优化器已经足够聪明、你的网络协议栈已经足够高效、你的序列化框架已经足够快的时候——下一个性能突破在哪里？

答案可能藏在最不起眼的地方：你的 `malloc` 实现。

在这个意义上，jemalloc 的文艺复兴不仅仅是一个分配器的故事。它是整个基础软件领域走向精细化运营的缩影——**当显而易见的优化都做完之后，真正的高手开始打磨那些看不见的齿轮。**

---

### 参考资料

- Phil Eaton, [*jemalloc usage in 2026*](https://eatonphil.com/jemalloc-usage-in-2026.html)
- scattered-thoughts.net, *The unreasonable effectiveness of jemalloc tuning*
- TigerBeetle Blog, [*Why we switched from tcmalloc to jemalloc*](https://tigerbeetle.com/blog/)
- [jemalloc GitHub 仓库](https://github.com/jemalloc/jemalloc)
- CPython PEP draft for jemalloc integration

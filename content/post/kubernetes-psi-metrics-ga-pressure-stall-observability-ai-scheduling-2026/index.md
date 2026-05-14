---
title: "Kubernetes 1.36 把 PSI 指标做成 GA：一个 Linux 内核老特性，正在重塑 AI 集群调度的'看世界'方式"
description: "PSI（Pressure Stall Information）从 2018 年起就在 Linux 内核里，但直到 2026 年 5 月才在 K8s 1.36 正式 GA。配合 1.36 同期的 PodGroup gang scheduling 和 DRA 演进，K8s 终于拥有了一套'感知卡死、感知 AI 拓扑'的现代调度感官。"
date: 2026-05-14
slug: "kubernetes-psi-metrics-ga-pressure-stall-observability-ai-scheduling-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Kubernetes
    - PSI
    - 可观测性
    - AI 集群
    - 调度
    - Linux 内核
draft: false
---

## 一句话总结

2026 年 5 月 12 日，Kubernetes 1.36 正式发布，把 **PSI（Pressure Stall Information）** 指标从 beta 提升到 **GA**——这是一项 2018 年就进入 Linux 内核、但在云原生世界蛰伏了 8 年的可观测性能力。

光是 PSI GA 本身是一件足够大的事，但更关键的是 1.36 把它和**两个 AI 时代的新调度能力**并列释出：

1. **PodGroup API + gang scheduling**（取代 1.35 的 Workload v1alpha1）；
2. **DRA（Dynamic Resource Allocation）的批量演进**——Prioritized list 进入 stable、Partitionable devices / Resource health status 进入 beta、Node allocatable resources（CPU/内存也进 DRA）进入 alpha。

如果说 K8s 的过去十年是"无状态微服务的胜利"，那么 **2026 年的 K8s 正在被 AI 训练 + 推理 workload 反过来重新定义**。这三个特性共同回答了一个新问题：**集群"看"自己的方式还够不够看得清 AI workload？**

本文要拆三件事：
1. **PSI 到底是什么、为什么传统 CPU 利用率不够用？**
2. **PodGroup + DRA 怎么把 AI workload "原生化"进 K8s？**
3. **这套新的调度感官，对生产实践意味着什么？**

---

## 一、PSI：当"CPU 50%"不再意味着"还有 50%"

传统的资源监控基于三个简单的数字：CPU 利用率、内存占用率、IO 等待。这套范式来自 1970 年代的 UNIX `top` / `vmstat`，在过去 50 年里基本没变过。

但这套范式有一个隐性的、几乎从没被诚实讨论过的缺陷：

> **利用率告诉你"资源被用了多少"，但不告诉你"任务因为资源不够等了多久"。**

举个例子：

- Node A：CPU 平均 50%、内存 60%、IO 30% —— 看起来一切正常；
- Node A 上跑着 80 个 Pod，每个 Pod 偶尔会因为 cgroup 配额竞争被卡住 200ms；
- 用户感受到的是：**接口延迟陡增、p99 飙升**，但 dashboard 显示"绿色"。

为什么会这样？因为利用率是**平均值**，而真正影响用户体验的是 **stall（卡死）time**——任务因为资源不可得而等待的累计时间。

Linux 内核团队 2018 年引入 PSI 时，已经准确地点了破：

```
some  avg10=2.34 avg60=0.78 avg300=0.55  total=12849823
full  avg10=0.41 avg60=0.05 avg300=0.02  total=2348711
```

每个 cgroup 都暴露这两行：
- **some**：至少有一个任务因为该资源（CPU / memory / IO）卡住的时间占比；
- **full**：所有任务都卡住的时间占比（更严重的状态）。

10 秒、60 秒、300 秒滑动平均给运维提供**时间维度的语义**——是瞬时抖动还是持续压力？

### 1.1 K8s 集成 PSI 用了 7 年

Linux 内核 4.20（2018 年底）加入 PSI 之后，K8s 社区对它的接入异常缓慢：

| 时间 | 状态 | 备注 |
|------|------|------|
| 2018 | Linux 内核 4.20 引入 PSI | Facebook 主导 |
| 2020 | 容器运行时（systemd、cgroup v2）开始暴露 | 仍是底层 API |
| 2022 | KEP-4205 提案被讨论 | 多次推后 |
| 2024 | K8s 1.31 引入 PSI 作为 alpha | KubeletPSI feature gate |
| 2026.05 | **K8s 1.36：PSI 进入 GA** | 默认开启，无需 feature gate |

**为什么这么慢？** 三个原因：

1. **kubelet 的资源探测代码非常敏感**——任何新轮询会被严格审计性能开销。SIG Node 用了一整年做大规模性能验证：在 80+ pod 密度下，开启 PSI 收集的 CPU 开销 ≤ **0.925%–3.125%**，最高瞬时 5.6%（很快恢复）。
2. **cgroup v1 不支持 PSI**——K8s 必须等大部分发行版默认 cgroup v2 才能稳定推广。这条线在 2024–2025 年才走完。
3. **K8s 团队对"误报"极度警惕**——之前的版本在内核不支持 PSI（`psi=0`）时仍会发布零值，造成误导。1.36 通过 cgroup 配置检测真实支持状态，才避免了这个坑。

PSI GA 意味着：**未来 12 个月，所有主流 K8s 集群默认会有这套新的观测能力**——只要节点是 Linux 4.20+、cgroup v2、内核 `psi=1`。

---

## 二、为什么 PSI 对 AI workload 是必须品而不是奢侈品

PSI 的真正价值，在 AI 训练 / 推理场景下被几倍放大。

```text
传统 Web 服务：           AI 推理服务：
- CPU 是主导瓶颈           - 内存带宽、HBM 容量、KV cache 是瓶颈
- 利用率 ≈ 实际负载        - 利用率经常显示高但实际在等内存
- 抖动通常 < 100ms         - GPU 等待 PCIe / NVLink 可达数百 ms
- 监控容易                 - 传统监控盲区极大
```

具体的三类盲区在 PSI 之前没有简洁的表达方法：

### 2.1 内存子系统的隐性饥饿

LLM 推理需要持续往 GPU 喂 KV cache + 模型权重。当 host 内存或 PCIe 带宽不够时，GPU 利用率显示 95%、但实际上每秒有几百 ms 在等待 host → device 拷贝完成。`nvidia-smi` 看到的"high utilization"是骗人的。

**PSI 的 memory.pressure** 直接暴露这种状态——`some` 值飙升 → 表明系统中至少有一个 cgroup 在等内存。

### 2.2 IO 子系统的不可预测停顿

ML 训练任务会周期性 checkpoint 到分布式文件系统（如 Lustre / Ceph）。一次 checkpoint 可能让整个节点 IO 卡顿 10 秒。在传统监控里你看到的是"IO util 100%"，但**你不知道这个 100% 是健康的批处理还是病态的等待**。

**PSI 的 io.pressure full** 立即区分：full 高 = 所有任务都卡在 IO 上，**这是真问题**；full 低 = 任务可以继续推进只是带宽用满了，**这是健康的**。

### 2.3 NUMA / 容器配额竞争

K8s 跑在大型 NUMA 节点上（如 256 核 Genoa-X、128 核 Sapphire Rapids），不同 cgroup 可能竞争同一个 NUMA 域的 LLC。看起来 CPU 利用率才 60%，但实际上一半 cgroup 在 last-level cache 争抢，被 stall。

**PSI 的 cpu.pressure** 是少数能跨 cgroup 给出"竞争压力"信号的指标。

### 2.4 配合 Workload-Aware Scheduling 形成闭环

K8s 1.36 的另一个核心特性是 **PodGroup scheduling cycle + gang scheduling**。其设计意图正是让一个 AI workload 的 N 个 worker pod **要么一起调度，要么一起失败重试**——避免传统 Pod-by-Pod 调度的死锁。

PSI 在这套机制里的作用是：**当某个 PodGroup 被调度到一组节点上后，调度器可以从 PSI 实时知道"这组节点真的 happy 吗"**。如果 PSI 显示其中一个节点在 memory pressure，调度器可以触发 workload-aware preemption，把整个 group 平移到健康节点——而不是等 OOM 才反应。

---

## 三、PodGroup + DRA：AI workload "进入头等舱"

K8s 1.36 的 PodGroup API 和 DRA 大幅升级，是 K8s 接纳 AI workload 的两条主线。

### 3.1 PodGroup：从 Pod 调度到 Workload 调度

1.35 引入 Workload API v1alpha1，但有个设计缺陷——把"模板"和"运行时状态"混在同一个对象里。一个 1000-pod 的训练任务，每个 pod 的状态变化都要写回 Workload 对象，IO 成为瓶颈。

1.36 把它拆成两个对象：

```yaml
# 1. Workload：静态模板（控制器持有）
apiVersion: scheduling.k8s.io/v1alpha2
kind: Workload
metadata:
  name: training-job-workload
spec:
  podGroupTemplates:
  - name: workers
    schedulingPolicy:
      gang:
        minCount: 4

---
# 2. PodGroup：运行时对象（一个 Workload 可以"印出"多个 PodGroup）
apiVersion: scheduling.k8s.io/v1alpha2
kind: PodGroup
metadata:
  name: training-job-workers-pg
spec:
  podGroupTemplateRef:
    workload:
      workloadName: training-job-workload
      podGroupTemplateName: workers
  schedulingPolicy:
    gang:
      minCount: 4
status:
  conditions:
  - type: PodGroupScheduled
    status: "True"

---
# 3. Pod：通过 schedulingGroup 引用 PodGroup
apiVersion: v1
kind: Pod
spec:
  schedulingGroup:
    podGroupName: training-job-workers-pg
```

这个拆分有三个重要后果：

1. **scheduler 路径简化**——以前要 watch Workload 解析模板，现在直接读 PodGroup；
2. **per-replica sharding**——每个 PodGroup 实例独立 status 更新，写入压力分散；
3. **铺路给未来的 topology-aware scheduling 和 workload-aware preemption**——这两个特性首次在 1.36 出现 alpha。

### 3.2 PodGroup scheduling cycle：原子调度

```text
传统 Pod-by-Pod 调度（容易死锁）：
  Pod A → Node 1 ✓
  Pod B → Node 2 ✓
  Pod C → Node 1 ✗（资源不够）
  → 整个 group 不完整，A 和 B 浪费资源等待

新的 PodGroup cycle（原子操作）：
  1. 取一个 group 成员 pop 队列
  2. 把 group 里所有未调度 pod 一起取出 + 排序
  3. 单次 cluster snapshot → 一致性评估
  4. 同时给所有 pod 找到节点 → 成功则批量 bind
  5. 失败 → 整个 group 退回队列等 backoff
```

这是经典 HPC 调度系统（Slurm、PBS）里的标准做法，K8s 终于学会了。

### 3.3 DRA：硬件资源管理的下一代

Dynamic Resource Allocation 是为 GPU / NPU / FPGA 这类"非简单 CPU/内存"资源设计的 API。1.36 的 DRA 演进涵盖：

| 特性 | 状态 | 价值 |
|------|------|------|
| **Prioritized list** | stable | "给我 H100，没有就 A100"——硬件异构性的正式支持 |
| **Extended resource** | beta | 老式 `nvidia.com/gpu` 标签可以平滑迁移到 DRA |
| **Partitionable devices** | beta | MIG（Multi-Instance GPU）成为原生概念 |
| **Device taints** | beta | 故障设备自动隔离，专属 GPU 给指定团队 |
| **Binding conditions** | beta | FPGA 等需要"准备时间"的设备调度 |
| **Resource health status** | beta | Pod status 里直接看到 GPU 是否健康 |
| **ResourceClaim for PodGroup** | alpha | 解决大规模 AI workload 共享 claim 的限制 |
| **Node allocatable (CPU/mem)** | alpha | **CPU 和内存也用 DRA API 管理** |
| **Resource pool status** | alpha | 集群管理员能查"我现在还有多少 GPU 可用" |

最后那个"Node allocatable" 特别值得关注——**DRA 不再是"专门给 GPU 的"**，而是要成为**所有资源的统一管理层**。这是 K8s 资源模型未来 3–5 年最大的架构变化。

---

## 四、对比表：1.34 → 1.36 K8s 的调度感官升级

| 维度 | K8s ≤ 1.34 | K8s 1.36 | 对 AI workload 的意义 |
|------|------------|----------|---------------------|
| 资源信号 | utilization | utilization + **PSI pressure** | 知道"卡多久"而不只是"用多少" |
| Pod 间调度 | 独立 Pod | **PodGroup 原子调度** | 训练任务可靠启动，不再死锁 |
| GPU 抽象 | 静态 device plugin | DRA + Prioritized list + Partition | 异构 GPU 集群可用 |
| 故障感知 | 节点级 NotReady | 设备级 health status | GPU 单卡故障可被精准识别 |
| 资源治理 | CPU/mem 一种、device 一种 | DRA 统一（alpha） | 未来一切都是 DRA |
| Workload API | 不存在 / 控制器自管 | Workload + PodGroup 双对象 | 调度器可以理解"批" |

---

## 五、生产环境的实际影响

### 5.1 监控栈需要更新

PSI 现在是 GA 指标，但**默认不会自动接入 Prometheus / Grafana**。你需要：

1. 确认 Linux 内核 `psi=1`、cgroup v2、kubelet 版本 ≥ 1.36；
2. 配置 Prometheus 抓取 `/metrics/cadvisor` 端点（PSI 指标暴露在这里）；
3. 在 Grafana 中新建 panel：
   ```promql
   container_pressure_cpu_stalled_seconds_total
   container_pressure_memory_full_seconds_total
   container_pressure_io_some_seconds_total
   ```
4. 告警阈值建议：**memory.full > 5% 持续 60s** → 严重告警；**cpu.some > 30% 持续 5min** → 容量告警。

### 5.2 调度策略要更新

如果你在跑 AI 训练 workload：

1. 把 Job controller 升级到使用 PodGroup API（1.36 的 Job → PodGroup 集成是第一阶段，但已可用）；
2. 在 GPU 节点上配 DRA driver（NVIDIA 和 AMD 都有官方版本）；
3. 用 Prioritized list 写硬件偏好——这比手动 nodeSelector 灵活得多；
4. **不要急着用 alpha 特性**（Node allocatable、Workload-aware preemption），它们 1.36 还不稳定。

### 5.3 容量规划范式改变

传统容量规划基于 CPU/mem utilization。引入 PSI 后：

- **真实容量上限往往是 PSI "some" 开始陡升的点**——不是 utilization 100% 的点；
- 这个点通常在 utilization **60%–75%** 之间（取决于工作负载混合）；
- 也就是说，**目前大部分集群"看起来还有 30% 余量"其实已经在 stall**。

这给运维团队提出一个反直觉的目标：**降低集群密度反而能提高有效吞吐**。

---

## 六、犀利判断与预测

**判断一：6 个月内主流可观测性产品全员接入 PSI。**
Datadog、Grafana Cloud、New Relic、阿里云 ARMS、腾讯云 Prometheus 都会在 Q3 之前推出 PSI dashboard 模板。Kubernetes-native 监控（kube-state-metrics、node-exporter）已经在做。

**判断二：调度器市场会出现"AI-aware K8s 发行版"。**
Run.ai（NVIDIA 收购）、Anyscale、Volcano、Yunikorn 等专门解决 AI workload 的项目会在 1.36 基础上做出更激进的扩展。其中 **Volcano 和 Kueue 大概率合并**——它们都在解决批处理调度。

**判断三：DRA 会推动 K8s 走向"Resource Mesh"架构。**
当 CPU、内存、GPU、FPGA、网络都通过同一套 DRA API 管理时，K8s 实际上变成了一个**资源 mesh**——每种资源由独立 driver 实现，调度器统一编排。这是接下来 3 年最大的架构变化，会让以前的 device plugin 路径完全退役。

**判断四：传统监控厂商面临"基础信号陷阱"。**
那些把 dashboard 卖给运维的厂商，如果不重做底层信号采集，会在 18 个月内被替代。**PSI + DRA 暴露的元数据不止是新指标，是新的世界观**——任何还在卖 CPU%、内存% 仪表盘的产品都在被边缘化。

**判断五：Linux 内核团队会被反向激励做更多 cgroup v2 投资。**
PSI、cgroup v2、BPF、io_uring 这些 K8s 时代的"上游优先级"在过去三年节奏明显加快。1.36 的 GA 进一步绑定了 K8s 和 Linux 内核的命运。**未来 5 年最关键的 Linux 创新会发生在"为容器集群优化"这条线上**。

---

## 七、读者可以带走的认知与行动

**如果你是 SRE / 运维**：
- 在 1.36 升级 plan 里把"PSI dashboard 上线"作为独立任务，预算 1–2 人周；
- 用 PSI 数据重新校准容量规划——很可能你目前的"30% buffer"是假的；
- 把 PSI 阈值告警接到 PagerDuty 之前先跑 4 周观察期，确定基线。

**如果你是 AI 平台工程师**：
- PodGroup + DRA 是未来 3 年的核心 API，现在开始迁移可以避免后面的痛苦；
- Resource health status 让 GPU 故障定位从小时级降到秒级——值得专门做 dashboard；
- 不要用 `nvidia.com/gpu` 标签写新代码——用 DRA。

**如果你是平台架构师**：
- 重新评估你的 K8s 发行版选择——AI workload 友好性正在快速变成核心评估维度；
- 投资 Volcano、Kueue、KubeStellar 等批处理调度补充——单 K8s 1.36 还不够。

**如果你是创业者 / 投资人**：
- "AI-native K8s observability"是值得关注的新赛道——传统监控厂商有结构性盲区；
- DRA driver 是一个新生态位——硬件创业公司必须早期就提供 DRA driver。

---

## 参考来源

1. Kubernetes Blog — *Kubernetes v1.36: PSI Metrics for Kubernetes Graduates to GA*：<https://kubernetes.io/blog/2026/05/12/kubernetes-v1-36-psi-metrics-ga/>
2. Kubernetes Blog — *Kubernetes v1.36: Advancing Workload-Aware Scheduling*：<https://kubernetes.io/blog/2026/05/13/kubernetes-v1-36-advancing-workload-aware-scheduling/>
3. Kubernetes Blog — *Kubernetes v1.36: More Drivers, New Features, and the Next Era of DRA*：<https://kubernetes.io/blog/2026/05/07/kubernetes-v1-36-dra-136-updates/>
4. Linux kernel PSI 原始文档：<https://www.kernel.org/doc/html/latest/accounting/psi.html>
5. Facebook PSI 早期博客（背景）：<https://facebookmicrosites.github.io/psi/>
6. Volcano + Kueue 项目：<https://volcano.sh> / <https://kueue.sigs.k8s.io>
7. SemiEngineering — *Why Vision LLMs Force A Rethink Of Edge AI Hardware*（同期话题）：<https://semiengineering.com/why-vision-llms-force-a-rethink-of-edge-ai-hardware/>
8. KEP-4205 PSI Metrics 提案（GitHub）：<https://github.com/kubernetes/enhancements/issues/4205>

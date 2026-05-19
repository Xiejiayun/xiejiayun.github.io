---
title: "【好文共赏】把 2000 秒砍成 50 秒：Modal 五年工程账本，从 LP 求解器到 CUDA Checkpoint 的『真·无服务器 GPU』栈"
description: "Charles Frye、Erik Bernhardsson 等四人把 Modal 五年攻克 serverless GPU 冷启动的全栈技术写成一份完整账本：从云端 buffer 的线性规划，到 ImageFS 的内容寻址 FUSE 文件系统，再到 gVisor checkpoint/restore 与 NVIDIA cuda-checkpoint，把 LLM 推理副本启动从『多个千秒』压到 50 秒，单平台已重启过约 5000 万个 replica。"
date: 2026-05-19
slug: "good-read-modal-serverless-gpu-cold-starts"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Serverless
    - GPU
    - 推理
    - CRIU
    - FUSE
    - CUDA
    - Modal
    - 系统工程
draft: false
---

## 📌 编辑推荐框

> **好文共赏 | Editor's Pick**
>
> 原文：[Cutting inference cold starts by 40x with LP, FUSE, C/R, and CUDA-checkpoint](https://modal.com/blog/truly-serverless-gpus) · 作者：Charles Frye / Jonathan Belotti / Erik Bernhardsson / Akshat Bubna（Modal） · 发布：2026-05-12 · 阅读时长：~20 分钟
>
> **多模评分**：Opus 9.2 / Sonnet 9.0 / Gemini 9.1 — 综合 **9.1 / 10**
>
> **一句话推荐**：这是 2026 年迄今**最完整的一份『serverless GPU 冷启动』全栈复盘**——把过去五年里那些只在 KubeCon talk 和 Twitter 线程里露过半张脸的工程细节，第一次合订成一本五十页的工程账本。

---

## 一、为什么这篇值得读

如果你只想读一句话总结：**Modal 把一台 B200 上 SGLang 服务一个十亿参数模型的副本启动时间，从『多个千秒』压到了 50 秒**——这是一个 40 倍的提速，过去三个月里他们在生产环境累计完成了大约 **5000 万次副本恢复**。

但这篇文章真正值得读的原因不是这个数字。值得读的原因是：

**第一，这是一份『端到端可验证』的系统工程作品**。绝大多数云厂商谈 serverless 时，会用『我们优化了启动路径』这种粒度的春秋笔法把关键细节藏起来。Modal 这次破了行业的潜规则，把四个核心环节——云端机器分配、容器镜像加载、CPU 进程恢复、GPU 上下文恢复——的延迟分布、瓶颈分析、tradeoff 全部摊开。它不仅告诉你『为什么慢』，还告诉你『为什么每一层快了之后才能解锁下一层』。

**第二，它把『分层基础设施』这个抽象口号变成了一种可触摸的工程信念**。文中有一句话很值得放在所有平台工程师工位上：

> 原文：The device checkpoint/restore builds on the host checkpoint/restore, which builds on the underlying filesystem. **Infrastructure compounds.**

这不是套话——你在读完文章后会真切看到，CUDA checkpoint/restore 之所以能从无变可用，是因为先有了 gVisor runsc 的 host-side C/R，而 gVisor 的 C/R 之所以能跑得快，是因为再下面有一个 lazy 加载的 ImageFS。每一层都是上一层的承重墙。这种『复利型』基础设施观，在 2026 年这个一切都在被 AI 改写的时间点上，是稀缺的、慢的、不流行的，但也是真正能形成壁垒的。

**第三，它用一个很反潮流的姿态写了一篇『反保密』的文章**。开头就直接说：

> 原文：we believe that secrecy is a bad moat. And if more people learn how to use GPUs efficiently, there will be more available in the market for us!

把『行业 GPU 利用率普遍只有 10–20%』当成蛋糕做大的市场机会，而不是自家护城河。这在 Anthropic 那种 frontier lab 价值观流行的 2026 年并不容易：那是一种『先把蛋糕做大、再去抢更大切片』的成熟主义。

**第四，它在合适的时候提出了一个被严重低估的指标**：**GPU Allocation Utilization**（GPU 分配利用率），而不是更性感的 Model FLOP/s Utilization (MFU)。这是一种我个人非常欣赏的视角转换——当所有人都在卷 MFU 的同时，真实世界里更多 GPU 时间其实是被『分配出去但没人在用』浪费掉的。我之前在[《AI Flame Graph：把推理性能问题从黑盒变可视》](/post/ai-flame-graphs-gpu-profiling-2026/)里讨论过 MFU 视角的局限，这篇文章正好补上了另一面。

---

## 二、问题框架：MFU 是给训练看的，Allocation Utilization 才是给推理算钱的

Modal 一开始就给『利用率』下了一个让我会心一笑的定义：

$$\text{Utilization} := \frac{\text{Output achieved}}{\text{Capacity paid for}}$$

它接着把这个比值在两个层级上展开。

第一个层级是大家熟悉的 **MFU**（Model FLOP/s Utilization），分子是模型理论需要的 FLOPs，分母是 GPU 提供的算术带宽。这是『hero run』训练的母题——xAI 训练 Grok 时候 MFU 大概只有 10% 一度成为 X 上的全网梗。

第二个层级才是 Modal 真正想谈的：**GPU Allocation Utilization**。

$$\text{GPU Allocation Utilization} := \frac{\text{GPU-seconds running application code}}{\text{GPU-seconds paid for}}$$

这个比值的分母不是『理论算力』，是『**你账单上写的 GPU 小时数**』。它衡量的不是『硬件被榨得多干净』，而是『你买的硬件有多少时间真的在跑你自己的代码』。

为什么这是推理时代真正的指标？Modal 引用了 AWS 工程师 Marc Brooker 的一句论断：

> 原文："the cost of a system scales with its (short-term) peak traffic, but for most applications the value the system generates scales with the (long-term) average traffic."

这句话翻译过来就是：**系统成本随短期峰值流量线性增长，但系统价值只随长期平均流量增长**。当推理工作负载的 peak-to-average ratio 越来越高（用户行为、社交媒体算法、产品 launch 都会瞬间打高峰），固定预留的容量永远是亏的。

文章里给出的现实数据足够吓人：根据《2024 State of AI Infrastructure at Scale》报告，**大部分组织在峰值期 GPU Allocation Utilization 都低于 70%，实测常见数字是 10–20%**。也就是说——你买的 10 张卡，可能有 8 张在大部分时间里只是在『准备好』而不是『在工作』。

这一段的妙处在于：它不只是把『冷启动慢』描述成一个工程难题，它把它**重新框架成一个会计学问题**——你的会计准则在多大程度上把『等待时间』算作『工作时间』。Modal 的 thesis 是：**如果冷启动够快，你就可以让 provisioned capacity 紧紧贴着真实 demand，把 allocation utilization 从 20% 拉到接近 100%**——这是上一段那个 5–10 倍的成本节约的真正来源。

（这层框架其实和[《把推理工程变成新的『编译时间』》](/post/inference-engineering-revolution-2026/)里那个『把每一次 inference 视为可重排的微批作业』观点相互印证——核心都是 **把推理从『一次性硬件预算』搬到『可调度的时间预算』**。）

---

## 三、四个核心配方：把 2000 秒砍到 50 秒的拆解

文章把启动一个新的推理 replica 拆成四个串行步骤，并把每一步的优化对应到一种工程武器：

| 步骤 | 朴素延迟 | 优化方案 | 砍掉的时间 |
|---|---|---|---|
| ① 申请实例并健康检查 | 几分钟～几十分钟 | **Cloud Buffer + LP 求解器** | 把『从无到有』移出热路径 |
| ② 加载容器镜像和文件系统 | 几分钟 | **ImageFS：libfuse + 内容寻址多级缓存** | 分钟 → 秒 |
| ③ 在 CPU 上做应用初始化 | 几十秒 | **gVisor runsc 的 checkpoint/restore (CRIU 思路)** | 10× 缩减 |
| ④ 在 GPU 上做设备初始化 | 几分钟～几十分钟 | **NVIDIA `cuda-checkpoint` + Driver-level 设备快照** | 4–10× 缩减 |

四层叠加之后，vLLM serving Qwen 3 0.6B 的均值冷启动从 **95.7 秒压到 13.8 秒**，SGLang 从 **83.7 秒压到 17.5 秒**——这两个数字是在十几万次冷启动样本上统计得出的，CDF 在每个分位点上都全面优于 baseline。

下面我把每一层单独拆开。

---

## 四、第一层：把 GPU buffer 当『硬件 SRAM』来调度

这一层乍看是最朴素的——**预留一些热备 GPU，新 replica 就调度到这些机器上，避免每次都向云厂商现要**。但 Modal 把它做出了两个有意思的细节。

**细节一：用线性规划同时调度 supply 和 demand。** Modal 自己实现了一个 LP 模型，喂给 Google 的开源求解器 **GLOP**。这个模型同时考虑：

- 每家云厂商在每个区域当前的『真实可用容量』（不是它宣传的 SKU 价格表，而是观测到的供给函数）；
- 各家的 spot/on-demand 报价；
- 各个用户任务对 GPU 型号、区域、内存的需求；
- buffer 本身的目标尺寸——既要够大以吸收突发，又要够小以不浪费。

这里 Modal 的隐藏前提非常重要：**不同云厂商的实际供给和 GUI 上点出来的价格表经常对不上**。当你跑到一定规模，你会发现某个 AZ 的 A100 在某个时段就是『要不来』。Modal 因此选择从『advertised price』退一步，做一种『observed supply feedback』。这是一种很务实的 ops 经验。

**细节二：放弃 100% 峰值利用率。** 文章里出现了一句几乎可以当作 SRE 圣经的话：

> 原文：A 100% utilized system has no margin for error, and so faults routinely become failures. **We can personally recommend adding more buffers to your life**—keep an extra toothbrush in your bathroom; keep a charger for your critical devices at home, the office, and on your person.

把『系统冗余』和『生活冗余』并置——这是工程师人格的一种『把哲学装进控制平面』的瞬间。具体到数字：buffer 让 Modal 的峰值 allocation utilization 永远低于 100%，但作为交换，他们把**热路径上的『分配等待』完全消灭了**。这是一种典型的 amortized engineering：把『顶峰摩擦力』变成『谷底维持成本』。

**细节三：GPU 健康检查比 SSD 还重要。** 这是文章里我读到时被『拍醒』的一处：

> 原文：health checks are critical for GPUs, which fail at a much higher rate than other hardware, including notoriously finicky components like spinning disks.

Modal 给出的方案是『启动时短时主动健康检查 + 持续监控 Xid 错误率，但更重的诊断（如 `dcgmi diag`）放到周度 cron』。在他们的图表里，**Xid critical 错误的频率长期维持在 0.05–0.2 次 / 卡 / 小时**——这意味着一片 1000 卡集群每小时大概会发生 50–200 次需要关注的硬件异常。如果你不在调度器层面把坏卡剔除，第二层、第三层、第四层做得再快都没用——你只是更快地把任务调度到一片正在 ECC 报错的 GPU 上。

（这一点也呼应了之前我们在[《GDDR Rowhammer：从消费级 GPU 拿下整台主机》](/post/gddr-rowhammer-gpu-host-takeover-2026/)那篇里讨论的——GPU 在数据中心环境下并不是想象中那种『硅级稳定』的纯计算单元，它的可靠性曲线接近于 HDD 而不是 CPU。）

---

## 五、第二层：ImageFS——把容器文件系统重写成一座 lazy 内容寻址塔

这是整篇文章里我个人最喜欢的一节，因为它在『工程优雅』和『性能 grind』之间找到了一个我很少在云厂商博客里看到的平衡点。

**问题陈述很经典**：标准容器镜像是分层 tarball，里面塞了几万个文件、几 GB 内容，包括完全没人用的全球时区数据。`docker run` 一启动就要把整层 root filesystem 拉下来——在普通云 Ethernet（几 GB/s）下要好几分钟。

**Modal 的解法是一个叫 ImageFS 的自研 FUSE 文件系统**，它把容器镜像拆成两件事：

### 5.1 metadata 先到，data 按需懒加载

容器启动只 block 在 metadata（几 MB 的 index）上——100ms 内可以全部拉下来。真正的文件数据放到后台，等程序 `open()` 的时候再取。

为什么这可行？因为大部分文件根本不会被访问。Modal 引用了 USENIX FAST '16 那篇经典的 **Slacker** 论文 Figure 5：典型容器在生命周期里实际读取的文件占整个镜像的比例**长尾极短**——绝大多数容器只读了不到 10% 的文件。

### 5.2 内容寻址多层缓存

ImageFS 不是按文件名缓存，而是按**内容哈希**缓存。这一点比 Docker 的 layer-wise cache 更优雅：因为不同镜像之间共享的 bytes 不一定在同一个 layer 里——比如两个不同的 Dockerfile 在不同步骤装了同一个版本的 PyTorch，那些 wheel 文件二进制相同，但 layer 哈希不同。Docker 的 cache 会让它们重复传输，**内容寻址不会**。

Modal 把缓存分成几层，每层对应云上的一类存储原语：

| 层级 | 延迟 | 吞吐 |
|---|---|---|
| Page Cache（RAM） | 0.001–0.1 µs | 10–40 GiB/s |
| 本地 SSD | 100 µs | 4 GiB/s |
| AZ Cache Server（同可用区） | 1 ms | 10 GiB/s |
| 区域 CDN | 100 ms | 3–10 GiB/s |
| Blob Storage | 200 ms | 3–10 GiB/s |

这张表看起来朴素，但它隐含了一个**很重要的设计哲学**：Modal 没有把所有内容塞到最快的层，而是接受了『**容量–速度–成本**』这个三难选择，让每个数据块自己找到合适的栖息地。每一层都在尺寸和延迟上跨了一个数量级。这种结构和 CPU 内部的 L1/L2/L3/RAM 是同构的——只不过 Modal 把这套金字塔搬到了数据中心维度。

**Modal 没做的事也值得注意**：他们在文章里坦白说『理论上还可以在 SSD 和 Blob 之间塞 RDMA 层或 AZ 内 P2P 共享』，**但因为工程复杂度太高，目前没做**。这是一种我喜欢的工程克制——基础设施工程师最难学的不是『还能怎么优化』，而是『**哪里该停下来**』。

### 5.3 grind 阶段的两个小钉子

文章最后用了一节专门讲『大架构定型之后那些榨百分点的小钉子』。我挑两个最有学习价值的：

**钉子 1：`read_ahead_kb` 调到 32MB**。Linux 内核的 FUSE 默认预读窗口只有 128 KB，对于容器镜像这种大文件流式读非常吃亏。Modal 把它调到 **32 × 1024 KB = 32 MB**，对大读非常友好。但他们也警告：**调到 GB 级别会导致 nasty 的 thrashing**，因为 page cache 被预读数据撑爆。这是个很典型的『参数过大并不一定线性变好』的反例。

**钉子 2：去掉 gzip 解压**。Docker layer 默认 gzip 压缩，但 DEFLATE 算法本质是单线程（LZ77 + Huffman），单核解压速度 ~100 MB/s，**远低于任何一层缓存的吞吐能力**。在这种情况下，gzip 不仅没省时间，反而成了 CPU 上的瓶颈。Modal 选择**直接不压缩传输**——这在他们的容量预算允许的前提下是个净胜手。文章顺便提到：如果你能完全控制镜像生成，可以试试 **zstd**（多线程、压缩比更高），但 Modal 因为要支持动态 agent workload 的快速镜像构建，连 zstd 的压缩耗时都不愿付。

这个细节其实非常深刻地揭示了一个事实：**在 100 GbE 普及的 2026 年，存储不再是网络的瓶颈；网络也不再是 CPU 的瓶颈；很多时候，CPU 的单线程能力反而成了整个数据通道的最窄处**。

---

## 六、第三层：在 gVisor 里 checkpoint/restore，把 `import torch` 直接『回放』

到了这一层，容器的根文件系统已经送达，下一个步骤是『让用户进程从二进制变成一个可服务请求的状态机』。对于一个典型的 Python 推理应用来说，仅仅 `import torch` 本身就可能触发几千行 Python 代码、几万次 syscall——加上别的库，从 `process_start` 到 `request_in_flight` 中间会消耗几十秒。

**Modal 的核心 insight 是把『进程』理解成一个可序列化的状态机**：

> 原文：The key insight here is that any running process is a heap, some threads, and a file descriptor table. ... If you can recreate that state ("create a checkpoint"), you can recreate the running process ("restore from checkpoint").

这是 Linux CRIU（Checkpoint/Restore In Userspace）几十年来的思路，但 Modal 没有直接用 CRIU。他们用的是 **gVisor 的 `runsc`**。

### 6.1 为什么是 gVisor 而不是 CRIU？

gVisor 是 Google 出的一个 user-space kernel——它在用户态实现了 Linux 内核接口的一个子集，给容器内的程序提供一个『沙箱化的内核』。在 Modal 的栈里，这件事顺便带来了三个好处：

1. **安全**：用户进程不直接和宿主内核打交道，最近爆出的 CVE-2026-31431（『CopyFail』漏洞）就被 gVisor 这层自动隔离掉了。
2. **可观测**：gVisor 是 Go 写的，每个 syscall 都要经过它的 task runtime，这让 Modal 可以在合作式抢占（cooperative preemption）的 `await` 点上**自然地暂停和续跑**。
3. **可 C/R**：这是关键——因为整个容器在 gVisor 里就是一台『被 Go 风格 async/await 切片好的状态机』，**序列化它比序列化裸 Linux 进程容易得多**。

`runsc checkpoint` 命令产出一个未压缩的 archive（注意——这里又一次拒绝 gzip，避免单线程瓶颈），核心是一个叫 `pages.img` 的文件，里面是裸 page 数据。这个文件**至少 100 MB，多则数 GB**。

整个 restore 性能的胜负，几乎全压在『**多快能把 `pages.img` 拉进 host page cache**』这一件事上——而这正好是上一层 ImageFS 已经解决的问题。两层在这里产生了优雅的对接：`pages.img` 也是一个『内容哈希定下来之后就 immutable 的大文件』，可以直接走 ImageFS 的多层 cache。

### 6.2 暴露给用户的 API：`@modal.enter(snap=True)`

Modal 没有让 C/R 完全透明（CRIU 推崇的是『用户程序完全不知道自己被快照』）。他们选择把**checkpoint 点**暴露给用户：

```python
@app.cls(enable_memory_snapshot=True)
class InferenceService:
    @modal.enter(snap=True)   # 在这个方法返回时打快照
    def startup(self):
        import torch
        self.model = load_model()

    @modal.enter(snap=False)  # 容器初始化时跑，但不快照
    def finalize(self):
        self.gpu_warm_up()

    @modal.method()
    def run(self, messages):
        return self.model(messages)
```

这种『半透明 C/R』比纯 CRIU 设计更现实：因为它**让用户可以显式区分『可重放的初始化』和『必须每次新跑的环节』**——例如，某些初始化会依赖当前时间、随机种子、宿主机 ID，这些必须放到 `snap=False` 里。这种『工程师自报家门』的模式，比工具自动推断要鲁棒得多。

### 6.3 一个让人哭笑不得的 caveat：`pclmulqdq`

文章里有一个我个人觉得**非常 educational** 的小段：

> 原文：the AWS g6.12xlarge instance type does not support the `pclmulqdq` Perform a Carry-Less Multiplication of Quadword instruction and so it cannot accept any snapshot created on a host which does

翻译：你在一台支持 `pclmulqdq` 指令的机器上做了快照，里面有些代码区可能 hard-code 了这条指令。如果你把这个 snapshot 在一台不支持 `pclmulqdq` 的 AWS g6.12xlarge 上 restore，它会**直接 illegal instruction fault**。

这告诉你两件事：

1. **transparent checkpoint/restore 在异构云上几乎不可能完美**——Modal 一个 inference service 的部署需要『**为不同 CPU feature 子集准备多个 snapshot**』。
2. **多云聚合带来的并不只是上层成本优化**，它在下层会增加大量这种『microarchitecture-aware engineering』。Modal 选择吃下这个复杂性，是因为他们的商业模型（从多家云厂商聚合容量）依赖这个能力。

（如果你对这种『CPU feature 异构带来的可移植性税』感兴趣，可以对照看看[《Apple Silicon 上的 swift 矩阵乘法 382x 提升》](/post/good-read-matt-gallagher-swift-llm-matmul/)那篇——本质上是同一种『硬件特性碎片化』在不同时空尺度上的呈现。）

---

## 七、第四层：CUDA Checkpoint——把 GPU 状态机也学会按下暂停键

这是整个故事里**最让人兴奋的一层**，也是最近两年才真正成熟的。

### 7.1 为什么 host-side C/R 不够？

前面第三层只能 checkpoint 进程在 CPU 这一侧的状态——堆、线程、文件描述符。但一个跑了 `model.cuda()` 的推理进程，**它的真实状态有一半在 GPU 上**：

- weights tensors（几十 GB）
- KV cache buffers
- 已经 capture 的 **CUDA Graphs**（一组带指针的内核启动序列）
- **Torch compiler** 编译出的内联内核
- nccl 通信组的拓扑状态

这些状态对 CRIU 和 gVisor 都是黑盒——它们能看到的只是『一个文件描述符指向 /dev/nvidia0』。

### 7.2 NVIDIA Driver 的优雅解法

NVIDIA 在最近几个驱动版本里加入了一个真正改变游戏规则的功能——**driver 内置的设备内存 checkpoint**。

Modal 的描述很精确：

> 原文：In short, the driver checkpoints device memory in host memory so that it can be checkpointed to disk by a host-side checkpointing system. Then, once the host-side system has restored the host memory, including the device checkpoint, the driver restores the device memory.

把这句话翻译成时序图：

1. **freeze**：CUDA driver 把整块 device memory（含 weights、KV cache、CUDA Graphs）**先暂存到 host memory 的一个 region**；
2. **host-side C/R** 看到那段 host memory 就和别的 page 一样，被序列化进 `pages.img`，再走 ImageFS 落盘；
3. **restore**：先恢复 host memory，driver 看到自己那段 region 还在，**再把内容打回 GPU**。

这个分层设计的优雅在于：**它让 GPU 状态机变成了 CPU 状态机的一个『扩展段』**。原本属于 device 的不可序列化资源（指针、handles、graph nodes），被 driver 在 freeze/thaw 这一对操作里**重新映射回了同构的 host buffer**。这是 NVIDIA 这两年驱动栈里少数让我会心一笑的工程作品。

### 7.3 数字会说话

Modal 的实测：

- **vLLM** 启动 Qwen 3 0.6B：**95.7 s → 13.8 s**（约 7×）
- **SGLang** 启动 Qwen 3 0.6B：**83.7 s → 17.5 s**（约 5×）
- Reducto 文档处理工作负载：**70 s → 12 s**（约 6×），让他们能在『kilo-GPU 级别』下做 truly serverless

CDF 图上**所有分位点**都全面优于 baseline——这一点对 SRE 比均值更重要，因为长尾才是 503 的来源。

### 7.4 不是没有 caveat

Modal 也老老实实列了两个限制：

1. **多 GPU 程序难以快照**：nccl 通信组不是为『暂停』设计的，一个 peer 静默几秒整个 collective 就会 deadlock。所以目前 GPU snapshot 主要适用于**单 GPU 模型**——也就是几 GB 到几十 GB 这个区间。
2. **大模型需要 weight offloading**：vLLM/SGLang 这种引擎在 init 时会预占 KV cache 内存。最好的做法是**先把 weights offload 回 host**，做完 snapshot 再 reload。empty KV cache 不在 snapshot 里——它从零重建比从快照恢复更快。

这两条 caveat 也告诉我们：**这一波 CUDA C/R 红利目前主要落在『中等模型 + 单卡推理』场景**——也就是文档抽取、ASR/TTS、小型 VLM。frontier 级别的多卡 LLM serving 还要等下一代 driver+collective 协同的快照能力。

---

## 八、复合利息：为什么这四层一定要按顺序解

文章里最让我觉得『有思想性』的一句话是这句：

> 原文：The device checkpoint/restore builds on the host checkpoint/restore, which builds on the underlying filesystem. **Infrastructure compounds.**

这一句话值得在所有平台工程团队的周会上挂三个月。它具体的含义是：

- 如果没有第二层 ImageFS 的内容寻址多层缓存，第三层 `pages.img`（多 GB）落盘读取就会成为瓶颈，C/R 就废了；
- 如果没有第三层 gVisor 的 host-side C/R，第四层 CUDA C/R **就没有可承载的『宿主载体』**——NVIDIA driver 把 device memory 倒进 host memory，但那段 host memory 必须由某个 C/R 引擎来负责持久化；
- 如果没有第一层 buffer，前三层做得再快也都是『从冷土壤开始的快』——你还要排队拿一张物理 GPU，多花十分钟。

这就是为什么 Modal 在文章开头说他们『**五年**』才把这件事讲完整。任何一层先做都没用——它必须等到下一层有承重墙才能往上摞。这种『**慢工厚积**』的特性，是当代基础设施工程最稀缺的品质，也是为什么我把这篇文章评到 9 分以上的根本原因。

（这点也和我之前写过的[《Cloudflare 一个 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/)那篇里 Cloudflare 工程师追十年时间债的体验高度同构——基础设施的复利不只是『快』的复利，也是『慢』的复利。）

---

## 九、延伸阅读图谱

### 9.1 作者群 & Modal 自己的衍生阅读

- **Erik Bernhardsson**（Modal CEO）— [《The Hyperdimensional Ad Hominem》](https://erikbern.com/2024/02/15/the-hyperdimensional-ad-hominem.html)：Erik 早期博客的代表作，讨论『为什么在工程里反对一个想法很容易但提出替代方案很难』。
- **Charles Frye** — Modal 上[《GPU Utilization Guide》](https://modal.com/blog/gpu-utilization-guide)：本文里那张 MFU vs Allocation Utilization 表格的深度版。
- **Jonathan Belotti** — [《Lazy container loading on Modal》](https://modal.com/blog/jono-containers-talk)：ImageFS 的早期 KubeCon 演讲文字稿。
- **Modal Engineering** — [《Memory snapshotting on Modal》](https://modal.com/blog/) 系列：本文第三层的细化版本，包含 `enable_memory_snapshot` 的 API 设计细节。
- **Modal × Reducto** 客户案例：本文末尾提到的 Reducto 把 cold start 从 70s 压到 12s 的实战。

### 9.2 学术 / 工业基础设施论文

- **Slacker (USENIX FAST '16)** — *Slacker: Fast Distribution with Lazy Docker Containers*：本文第二层 lazy loading 的理论基础，Figure 5 是引用源头。
- **To FUSE or Not to FUSE (USENIX FAST '17)** — 详细分析 FUSE 在 user-kernel context switch 上的代价，本文里 Modal 选 FUSE 的 tradeoff 直接来自这篇。
- **CRIU project** — checkpoint-restore.org：Linux 用户态 C/R 的原始项目，gVisor checkpoint 借鉴的核心算法。
- **gVisor open source repo** — Google 在 Go 里实现的 user-space kernel，本文第三层的底层依赖。
- **NVIDIA `cuda-checkpoint`** — [docs.nvidia.com/cuda-checkpoint](https://docs.nvidia.com/deploy/cuda-checkpoint/)：本文第四层依赖的 driver-level 工具，公开文档 2024 年才正式发布。

### 9.3 同时期相关文章（可作对照）

- **Marc Brooker** — [《Economics of serverless》](https://brooker.co.za/blog/2023/03/23/economics.html)：本文里 peak-vs-average traffic 那句金句的源头。
- **Hebbia** — *Modern GPU utilization is broken*：另一家公司从客户视角写的 GPU allocation 浪费问题。
- **AWS Lambda** SnapStart：AWS 自己的 Java/CPU snapshot 方案，本文第三层的『更窄垂直版』。
- **Firecracker microVM**：AWS 的轻量级 VM 项目，和 gVisor 走的是另一条隔离路线，可作架构对照。

### 9.4 反方观点 / 不同视角

- **William Angel — [Apple Silicon costs more than OpenRouter](https://www.williamangel.net/blog/2026/05/17/offline-llm-energy-use.html)**：从『一个开发者笔记本可以跑多少 token』反推『serverless cloud GPU 是否还有必要』。结论是 cloud 仍然便宜，但反向佐证了『Modal 必须把 cold start 砍成本，才能在和 OpenRouter / local 推理三方博弈中守住价格优势』。
- **Frederick Van Brabant — [《I don't think AI will make your processes go faster》](https://frederickvanbrabant.com/blog/2026-05-15-i-dont-think-ai-will-make-your-processes-go-faster/)**：从『瓶颈在哪里』的视角提醒：再快的 GPU 冷启动，也救不了一个上游需求不清的产品流程。
- **Mistral / Open-router on-demand serving**：把『冷启动慢』当成 router 路由问题、而不是底层平台问题——一种用 routing layer 抹平基础设施差异的思路。

---

## 十、编辑延伸思考：当 cold start 不再是问题，开发范式会变成什么

读完这篇之后，我一直在想一个相关问题：**当 GPU 冷启动从 2000s 砍到 50s，再砍到 5s 的时候，会解锁什么？**

### 10.1 「Dev replica = Prod replica」会重新变得可能

Modal 在文中半埋了一段重要的话：

> 原文：This buffer is especially useful for accommodating a wider variety of workloads on a single system. At Modal, we've leaned into supporting a variety of "development" workloads, not just production serving, because we can quickly create a new development environment.

翻译：**因为我能在 50 秒里给你一个新环境，所以『开发』和『生产』可以共用同一套基础设施**。

这是过去十年云原生世界一直在追求但始终没做到的东西——dev/prod parity。它一直没做到的根本原因不是抽象不够好，而是『慢』：每次为了一个开发分支拉一个新环境，要等几分钟，开发者就会自己用 Docker Compose 本地搞一套。Modal 在 GPU 这种最昂贵、最碎片化的硬件上把这件事做到了。这对我来说意味着——**在未来 12–24 个月里，agentic AI 的『开发态』可能会大规模迁移到这种『秒级 spawn』的 serverless 基础设施上**，因为 agent 自己就是一个不断需要新沙箱的开发者。

（这一点和[《当 AI Agent 让每个人都能写自己的原生应用》](/post/good-read-emacsification-of-software/)那篇的『软件 Emacs 化』观点结合得很自然——一旦 agent 能秒级拿到 GPU 沙箱，每个 agent 就拥有了一台『可弃用』的本地推理工作站。）

### 10.2 GPU 调度会越来越像 OS 调度

第三层和第四层的 C/R，本质上是在做一件事——**把 GPU process 当作可被中断、可被迁移的『进程』来对待**。这是过去几十年 OS scheduler 一直在 CPU 上做的事，现在它正在被搬到 GPU 上。

我倾向于认为，2026–2028 年这三年，会出现『**GPU OS**』这个范畴：它的核心能力不是更高的 MFU，而是『**可调度性**』——把 GPU process 的 quiesce、checkpoint、migrate 做成一等公民。这件事如果做成了，下一波 frontier lab 训练的 hero run 就会有一个新的护城河，叫做『**preemptive 高保真训练**』——可以在 spot capacity 上跑 1000B+ 模型的训练，凭借的就是这套快照层。

### 10.3 利用率的会计学正在被重写

这篇文章里那个『Allocation Utilization』指标，长远看可能会变得比 MFU 更重要。因为大部分企业最终会发现：他们买 GPU 的真正瓶颈不是『单卡跑得有多快』，而是『**一年下来这些卡有多少小时被付了钱但没跑代码**』。

如果 Modal 这套栈被验证之后被竞品复制（这是必然的——AWS Lambda 已经在做 Java SnapStart，Google Cloud Run 也在做类似事），整个 cloud GPU 市场的定价模型会发生一次微妙的变化：**从『每小时整卡』向『每秒应用代码运行时间』迁移**。这个迁移在 2014 年发生在 CPU 上（Lambda 引爆），现在轮到 GPU 了。

### 10.4 「Infrastructure compounds」是这十年最被低估的工程箴言

最后，我想把开篇那句『Infrastructure compounds』再放一次，并且把我自己的版本写出来：

> **基础设施的价值不在某一层的工程量，而在每一层是否成为下一层的承重墙。**

如果你的第二层是被第一层强行支撑起来的，那它会随第一层退场而退场；
如果你的第二层是从第一层自然延伸出来的，那它会让第三层成为可能；
如果第三层让第四层变成可行，整个金字塔就活了。

Modal 这五年做的不是『serverless GPU』这一个产品，是『**为后续十年的 GPU 工程铺承重墙**』。这才是这篇文章值得被反复阅读的原因。

---

## 十一、配套资料导览

这篇文章的目录下还附了三份资料供深度阅读：

- 📊 **`mindmap.svg`** — 四层冷启动栈的全景思维导图
- 🗂️ **`concept-cards.md`** — 12 张关键概念卡片（GPU Allocation Utilization、CRIU、FUSE、`cuda-checkpoint`、CUDA Graphs、gVisor runsc 等）
- 📖 **`glossary.md`** — 35 条英中对照术语表

---

## 十二、谁应该读这篇

- **构建 AI 推理平台的工程师**——这是过去五年这件事最完整的『参考实现说明书』
- **CTO / 平台 leader**——会让你重新思考自家『GPU 账单 vs GPU 跑代码时间』的会计学
- **基础设施研究者**——CRIU、FUSE、gVisor、cuda-checkpoint 四件套在生产环境的第一手集成报告
- **正在踩 vLLM/SGLang 冷启动坑的同学**——文末那张『Snapshot ON/OFF』对比图就是你下一次 PR 的 motivation
- **任何相信『复利型基础设施』这件事的人**——这是一份非常好的『慢工厚积』的现代样本

---

*🏷️ 标签：Serverless / GPU / Inference / CRIU / FUSE / CUDA / Modal / 系统工程 / Allocation Utilization / 冷启动*

*🧪 多模评分：Opus 9.2 / Sonnet 9.0 / Gemini 9.1 — 综合 **9.1 / 10***

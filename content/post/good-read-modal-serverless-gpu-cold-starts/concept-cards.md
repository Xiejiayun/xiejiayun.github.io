# 关键概念卡片 · Modal Serverless GPU 全栈

> 12 张可独立阅读的概念卡，配合主文使用。每张卡片只解释一个点，但保证读完就能 "拿走"。

---

## 🎴 #1 — GPU Allocation Utilization（GPU 分配利用率）

**一句话定义**：你买的 GPU 小时数里，**真正在跑你自己应用代码**的比例。

**公式**：

```
GPU Allocation Utilization = (GPU-seconds running app code) / (GPU-seconds paid for)
```

**为什么重要**：业界长期热议的 MFU（Model FLOP/s Utilization）衡量的是『硬件被榨得多干净』，但对推理负载来说，**绝大部分 GPU 时间根本不在跑代码，而是在等启动、等队列、等扩容**。Modal 引用《2024 State of AI Infrastructure》报告：**多数组织峰值期 allocation utilization 低于 70%，常见值 10–20%**。

**对比 MFU**：MFU 是给训练 hero run 看的；Allocation Utilization 是给推理付账的人看的。

---

## 🎴 #2 — Cold Start 的四段拆解

一个 LLM 推理 replica 从『申请』到『可服务请求』要经过 4 段：

| 段 | 工作内容 | 朴素延迟 |
|---|---|---|
| ① | 申请新机器 + 健康检查 | 几分钟～几十分钟 |
| ② | 加载容器镜像与文件系统 | 几分钟 |
| ③ | 在 host CPU 上跑应用初始化（import torch、模型加载） | 几十秒 |
| ④ | 在 GPU 上做 device 初始化（CUDA context、weights upload、CUDA graphs、torch.compile） | 几分钟～几十分钟 |

**关键直觉**：每段都对应一种工程武器，且**后段必须依赖前段的优化才能解锁**。

---

## 🎴 #3 — Cloud Buffer + Linear Programming

**做的事**：维护一小池『健康但空闲』的 GPU，新 replica 来了直接调度过去，再异步补充 buffer。

**LP 模型输入**：
- 各云厂商各区域的真实可用容量（observed supply，不是宣传价格表）
- spot / on-demand 报价
- 用户任务的 GPU 型号 / 区域 / 内存约束
- buffer 目标尺寸

**用的求解器**：Google 开源的 **GLOP**。

**反直觉点**：Modal 不追求 100% 峰值利用率。"100% utilized system has no margin for error"——他们把『buffer』类比成『多备一把牙刷，多备一根充电线』。

---

## 🎴 #4 — ImageFS：内容寻址的 FUSE 文件系统

**用 libfuse 自研，做两件事**：

1. **lazy loading**：只 block 在 metadata（几 MB index）上，文件数据按需读取
2. **内容寻址多层缓存**：按内容哈希而非文件名缓存，跨镜像共享 bytes 不重复传输

**为什么 metadata-only 启动可行**：Slacker 论文（FAST'16, Figure 5）证明——**典型容器只读取镜像里不到 10% 的文件**。

**多层缓存阶梯**：

| 层级 | 延迟 | 吞吐 |
|---|---|---|
| Page Cache (RAM) | µs 级 | 10-40 GiB/s |
| 本地 SSD | 100 µs | 4 GiB/s |
| AZ Cache Server | 1 ms | 10 GiB/s |
| 区域 CDN | 100 ms | 3-10 GiB/s |
| Blob Storage | 200 ms | 3-10 GiB/s |

---

## 🎴 #5 — FUSE 的两面性

**好处**：在 user space 写文件系统，比 kernel module 简单得多。

**代价**：每次 syscall **多一次 user-kernel context switch**，对延迟敏感的小读非常不利。

**Modal 的选择**：用在『throughput-dominated』场景（拉容器镜像）——大文件流式读，FUSE 的 overhead 被 hidden。

**调优钉子 1**：`read_ahead_kb` 从默认 128KB 调到 **32MB**，对大读非常友好。**但调到 GB 级会触发严重 thrashing**。

**调优钉子 2**：去掉 gzip 解压。DEFLATE 单线程 ~100 MB/s，远低于任何缓存层吞吐——**gzip 反而成了瓶颈**。Modal 直接不压缩传输镜像。

---

## 🎴 #6 — CRIU（Checkpoint / Restore In Userspace）

**核心 insight**：进程 = `(heap, threads, file descriptors)` 的快照。

**Linux 原生方案**：CRIU 项目（checkpoint-restore.org），是 Linux 容器迁移、混合云迁移、HPC 任务挂起的底层基础设施。

**透明 vs 半透明**：
- **Transparent C/R**：进程完全不知道自己被快照（CRIU 的方向）
- **半透明 C/R**：用户在 API 层显式标记 snapshot 点（Modal 的方向）

**Modal 为什么选半透明**：让用户区分『可重放的初始化』vs『每次必须新跑的环节』（如随机种子、当前时间、机器 ID 依赖）。

---

## 🎴 #7 — gVisor `runsc`：user-space kernel 的 C/R 优势

**gVisor 是什么**：Google 开源的 user-space kernel，用 Go 写，给容器内进程提供『沙箱化的 Linux 系统调用接口』。

**为什么 Modal 没用 CRIU 而用 gVisor**：

1. **安全**：用户进程不直接和 host kernel 交互，自动隔离掉 host kernel 的 CVE（如 CVE-2026-31431 "CopyFail"）
2. **可暂停**：gVisor 是 Go async/await，自带 cooperative preemption，**每个 await 点都是天然的 checkpoint 点**
3. **状态机化**：runsc 容器本质是一个 Go state machine，**序列化它比序列化裸 Linux 进程容易得多**

**`runsc checkpoint` 产出**：未压缩 archive，核心文件是 `pages.img`（裸 page 数据，100MB ~ GB 级别）。

---

## 🎴 #8 — Modal `@modal.enter` API 设计

```python
@app.cls(enable_memory_snapshot=True)
class InferenceService:
    @modal.enter(snap=True)
    def startup(self):
        # 这里跑完之后打 snapshot
        # 适合: import 重库、加载常驻模型权重
        ...

    @modal.enter(snap=False)
    def finalize(self):
        # 每次容器启动都跑、但不进 snapshot
        # 适合: 依赖当前时间/随机数/机器 ID 的操作
        ...

    @modal.method()
    def run(self, messages):
        # 真正的请求处理
        ...
```

**关键设计抉择**：把 snapshot 边界做成**装饰器粒度**，而不是『进程粒度自动推断』——让用户主动声明哪些初始化是『可复用的』。

---

## 🎴 #9 — `pclmulqdq` Caveat（CPU 指令异构性陷阱）

**问题**：你在 host A 上做 snapshot，host A 支持 `pclmulqdq` 指令（Carry-less Multiplication of Quadword）。你的库（如 zlib、AES-NI 路径）可能 hard-code 了这条指令。

**结果**：把 snapshot 在不支持 `pclmulqdq` 的 host B（例如 AWS g6.12xlarge）上 restore，会直接 **Illegal Instruction Fault**。

**Modal 的应对**：一个 inference service 部署需要**为不同 CPU feature 子集准备多个 snapshot**。

**普适教训**：**多云聚合的成本优化必然带来下层 microarchitecture-aware engineering 的复杂度税**。

---

## 🎴 #10 — CUDA Checkpoint / Restore（设备级快照）

**问题**：第三层（gVisor C/R）只能 checkpoint host 一侧的进程状态——堆、线程、fd。但一个跑了 `model.cuda()` 的程序，**真正昂贵的状态在 GPU 上**：

- weights tensors（GB ~ TB）
- KV cache buffers
- 已捕获的 CUDA Graphs（指针化的内核启动序列）
- Torch compiler 编译出的内联 kernel
- nccl 通信组拓扑

**NVIDIA Driver 的解法**（最近驱动版本才稳定）：

1. **freeze**：driver 把整块 device memory 拷贝到 host memory 的一个特定 region
2. **host-side C/R**：那段 host memory 被 gVisor / CRIU 当作普通 page 序列化进 `pages.img`，落盘走 ImageFS
3. **restore**：先恢复 host memory，driver 看到自己那段 region 还在，**把内容刷回 GPU**

**优雅之处**：GPU state 变成 CPU state 的『扩展段』；原本不可序列化的 device 资源（指针、handles、graph nodes），在 freeze/thaw 这对操作里被 **重新映射回了同构的 host buffer**。

---

## 🎴 #11 — vLLM / SGLang 实测数字

**在 Modal 上跑 Qwen 3 0.6B (bf16, ~1 GiB)**，超过 10,000 次冷启动的统计：

| Engine | Snapshot OFF (均值) | Snapshot ON (均值) | 加速比 |
|---|---|---|---|
| **vLLM** | 95,679 ms | 13,797 ms | **6.9×** |
| **SGLang** | 83,713 ms | 17,486 ms | **4.8×** |

**关键 caveat**：

1. **多 GPU 不行**：nccl 不支持 peer 静默，会 deadlock。GPU snapshot 当前只适用单卡。
2. **大模型需要 weight offloading**：snapshot 前先把 weights 倒回 host
3. **KV cache 不打快照**：从零重建比从快照恢复还快（empty cache）

---

## 🎴 #12 — "Infrastructure compounds"（基础设施复利）

**Modal 团队的工程箴言**：

> The device checkpoint/restore builds on the host checkpoint/restore, which builds on the underlying filesystem. **Infrastructure compounds.**

**具体含义**：

- 第四层（CUDA C/R）只有在第三层（gVisor host C/R）就位后才可行——device memory 必须由 host 来承接落盘
- 第三层只有在第二层（ImageFS）就位后才能跑得快——`pages.img` 多 GB，必须有内容寻址多级缓存
- 第二层只有在第一层（Cloud Buffer）就位后才能用上——否则你优化得再好也要先排队拿物理卡

**推论**：基础设施工程的价值不在『某一层的工程量』，而在『**每一层是否成为下一层的承重墙**』。

**为什么 Modal 用了 5 年**：因为每层都必须等下一层有承重墙才能往上摞——**这种 sequential dependency 不能用钱买快**。

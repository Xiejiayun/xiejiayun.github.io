# 术语表 · Modal Serverless GPU 全栈

> 35 条英中对照术语，按主题分组。

## 📘 总体框架

| 英文 | 中文 | 一句话注解 |
|---|---|---|
| Serverless GPU | 无服务器 GPU | GPU 容量按真实使用秒数计费，平台负责自动扩缩容 |
| Cold Start | 冷启动 | 从『副本不存在』到『可服务请求』的延迟 |
| Replica | 副本 | 一个对外提供推理服务的进程实例 |
| Inference Workload | 推理工作负载 | 与 training 相对，需求由外部用户行为驱动 |
| Auto-scaling | 自动扩缩容 | 根据 demand 动态增减副本数 |

## 📊 利用率与会计

| 英文 | 中文 | 注解 |
|---|---|---|
| MFU (Model FLOP/s Utilization) | 模型浮点利用率 | 理论 FLOPs / 硬件算术带宽 |
| Allocation Utilization | 分配利用率 | 真正跑代码秒 / 付费秒 |
| Peak-to-average ratio | 峰均比 | 流量短期峰值与长期均值的倍数 |
| Spot capacity | 抢占式容量 | 云厂商提供的低价但可被回收的 GPU |
| QoS (Quality of Service) | 服务质量 | 通常以 p99 延迟与可用性度量 |

## 💾 容器与文件系统

| 英文 | 中文 | 注解 |
|---|---|---|
| FUSE (Filesystem in Userspace) | 用户态文件系统 | Linux 把文件系统从内核搬到用户态的标准框架 |
| libfuse | libfuse 库 | FUSE 的标准 C 库 |
| Content-addressed Cache | 内容寻址缓存 | 按内容哈希索引，跨文件路径共享 bytes |
| Page Cache | 页缓存 | Linux 内核管理的内存级文件缓存 |
| `read_ahead_kb` | 预读字节数 | FUSE 内核预读窗口大小 |
| DEFLATE / gzip | DEFLATE 压缩 | 单线程压缩算法，~100 MB/s 单核上限 |
| zstd | zstd 压缩 | 多线程压缩算法，比 gzip 更高吞吐 |

## 🔄 Checkpoint / Restore

| 英文 | 中文 | 注解 |
|---|---|---|
| CRIU (Checkpoint/Restore In Userspace) | 用户态进程快照 | Linux 原生进程序列化方案 |
| gVisor | gVisor | Google 出品的 user-space kernel |
| runsc | runsc | gVisor 的 OCI 运行时 |
| Transparent C/R | 透明快照 | 进程完全不知道自己被快照 |
| pages.img | 页镜像文件 | runsc/CRIU 产出的核心快照文件，含进程裸 page |
| Cooperative Preemption | 协作式抢占 | async/await 风格的非抢占式并发模型 |
| Snapshot Boundary | 快照边界 | 用户显式声明的 checkpoint 切入点 |

## 🎮 GPU 与 CUDA

| 英文 | 中文 | 注解 |
|---|---|---|
| CUDA Context | CUDA 上下文 | GPU 上一个进程的运行环境 |
| CUDA Graph | CUDA 图 | 预先捕获的内核启动序列，含张量与内核指针 |
| Torch Compiler | Torch 编译器 | PyTorch 的 JIT 编译子系统 |
| KV Cache | 键值缓存 | LLM 推理中存储注意力中间结果的内存区域 |
| `cuda-checkpoint` | CUDA 快照工具 | NVIDIA 驱动 2024 年起正式发布的设备快照工具 |
| Weight Offloading | 权重外迁 | snapshot 前把 GPU 上的模型权重倒回 host memory |
| Xid Error | Xid 错误 | NVIDIA driver 报告的 GPU 硬件级异常代码 |
| `dcgmi diag` | DCGMI 诊断 | NVIDIA Data Center GPU Manager 的诊断命令 |
| nccl | NCCL | NVIDIA 集体通信库，多 GPU/多机间通信标准 |

## 🏗️ 推理引擎与系统

| 英文 | 中文 | 注解 |
|---|---|---|
| vLLM | vLLM | UC Berkeley 出品的高吞吐 LLM 推理服务器 |
| SGLang | SGLang | 高性能 LLM serving runtime，支持复杂 generation 控制流 |
| Inference Engine Setup | 推理引擎初始化 | 包含 CUDA Graphs 捕获、torch.compile、KV cache 预分配 |
| ImageFS | ImageFS | Modal 自研的 FUSE 容器镜像文件系统 |

## ⚙️ 调度与求解

| 英文 | 中文 | 注解 |
|---|---|---|
| Linear Programming (LP) | 线性规划 | 一类带线性约束和线性目标函数的最优化问题 |
| GLOP | GLOP | Google 开源的 LP 求解器 |
| Observed Supply | 观测供给 | 不是云厂商宣传的价目表，而是实际能拿到的容量曲线 |
| Health Check | 健康检查 | 副本启动时和运行中的硬件 / 软件状态检测 |

## 🔐 安全

| 英文 | 中文 | 注解 |
|---|---|---|
| CVE-2026-31431 ("CopyFail") | "CopyFail" 漏洞 | 2026 年新发布的 host kernel CVE，gVisor 因隔离不受影响 |
| nvproxy | nvproxy | gVisor 内与 NVIDIA kernel driver 通信的子组件 |
| `pclmulqdq` | 进位无关四字乘法指令 | x86 扩展指令，并非所有云实例都支持，是 snapshot 异构性陷阱的典型来源 |

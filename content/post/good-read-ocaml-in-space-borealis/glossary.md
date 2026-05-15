# 术语表 · O(x)Caml in Space · Borealis

> 英中对照，括号内为本文使用的"译法 + 简释"。

## 1. 项目 / 组织

- **Borealis** —— 极光（项目代号）；Parsimoni 在轨运行的纯 OCaml CCSDS 协议栈。
- **Parsimoni** —— 帕西莫尼（公司名）；Tarides 从其太空业务拆出的子公司。
- **Tarides** —— 塔里德斯（公司名）；OCaml/MirageOS 商业化母公司。
- **MirageOS** —— 米拉热 OS（库操作系统）；可把 OCaml 程序编译成无操作系统依赖的 unikernel。
- **DPhi Space** —— 共生载荷创业公司，提供 ClusterGate-2 模块。
- **ClusterGate-2** —— DPhi 的载荷模块；Arm Cortex-A53 ×4 / 4 GB RAM 的 Linux SoC。
- **OxCaml Labs** —— Anil Madhavapeddy 在剑桥大学带的 OCaml 实验室。
- **FP Launchpad** —— KC Sivaramakrishnan 在 IIT Madras 的实验室。
- **Jane Street** —— 量化交易公司，OCaml 大规模生产用户；OxCaml 的维护者。
- **Project Everest** —— Microsoft Research 主导的形式化验证密码学项目。
- **Nitrokey** —— 德国硬件安全模块厂商；NetHSM 长期跑 nqsb-TLS 栈。

## 2. 协议 / 标准

- **CCSDS** —— 空间数据系统咨询委员会（Consultative Committee for Space Data Systems）；星地通信协议族。
- **SDLP** —— Space Data Link Protocol；CCSDS 的链路层。
- **SDLS** —— Space Data Link Security；CCSDS 的链路层安全扩展。
- **COP-1** —— Command Operation Procedure-1；CCSDS 的可靠传输协议。
- **CFDP** —— CCSDS File Delivery Protocol；类似 FTP 的文件传输。
- **BPv7** —— Bundle Protocol version 7（RFC 9171）；延迟容忍网络的"消息单元"。
- **BPSec** —— Bundle Protocol Security（RFC 9172）；为 BPv7 提供端到端加密 + 认证。
- **OTAR** —— Over-The-Air Rekey；在轨更换加密/签名密钥。
- **NASA-STD-1006A** —— NASA 太空系统保护标准；2026 起把 PQ 命令认证升为强制要求。
- **EID** —— Endpoint Identifier；BPv7 中的"地址"。

## 3. 密码学

- **ML-DSA-65** —— Module-Lattice-based Digital Signature Algorithm（NIST FIPS 204）；后量子签名标准的中等参数集（≈ Dilithium 3）。
- **ML-KEM** —— Module-Lattice Key Encapsulation Mechanism（FIPS 203）；后量子密钥封装。
- **post-quantum cryptography (PQC)** —— 后量子密码学；能抵抗量子计算攻击的算法族。
- **Security Association (SA)** —— 安全关联；通信双方约定的加密参数集合（含 EK/AK/SPI）。
- **EK / AK** —— Encryption Key / Authentication Key；BPSec 中各自独立的密钥。
- **SPI** —— Security Parameter Index；标识 SA 的整数。
- **replay protection** —— 重放保护；用序列号阻止攻击者重放旧报文。
- **TCB (Trusted Computing Base)** —— 可信计算基；系统中所有必须可信的部件集合。
- **HSM** —— Hardware Security Module；硬件密钥保护设备。
- **fiat-crypto** —— Coq 生成的常数时间域算术库。
- **libcrux** —— Rust + 形式化验证的密码学原语库。

## 4. 编程语言 / 类型系统

- **OCaml** —— 一种 ML 家族的强类型函数式编程语言；可类比为"带 GC 的 Rust"。
- **OxCaml** —— Jane Street 维护的 OCaml 实验分支；mainline 兼容。
- **OCaml 5** —— 2022 年发布的 OCaml 主版本，引入 multicore runtime。
- **mode system** —— 模式系统；OxCaml 用类型系统正交维度跟踪 locality / uniqueness / linearity。
- **locality** —— 局部性；OxCaml 的核心 mode，区分 `local`/`global` 值，前者不允许逃出当前作用域。
- **`exclave_ stack_`** —— OxCaml 关键字组合；告诉编译器"在调用栈上分配这个 record，由调用者作用域消费"。
- **GADT (Generalized Algebraic Data Types)** —— 广义代数数据类型；允许构造器对返回类型参数施加约束，常用于建模状态机。
- **ADT (Algebraic Data Type)** —— 代数数据类型；OCaml 的 `type t = A | B of int | C of string` 形式。
- **uniqueness / linearity** —— 唯一性 / 线性；同一资源在某一时刻只允许一个所有者，防止数据竞争。
- **capabilities** —— 能力；显式表达"谁有权访问什么"。
- **GC (Garbage Collection)** —— 垃圾回收；minor GC = 年轻代回收，对延迟最敏感。
- **F\*** —— 微软的依赖类型证明型编程语言；可生成 C/JavaScript/OCaml。
- **EverParse** —— F\* 项目的二进制解析器生成器。
- **Coq / Rocq** —— 法国 INRIA 的证明助手，用于 fiat-crypto 等。

## 5. 系统 / 部署

- **unikernel** —— 单内核镜像；把应用代码和库 OS 编译进同一个可启动镜像。
- **library OS** —— 库操作系统；只链接应用需要的内核功能，运行时无系统调用边界。
- **hosted payload** —— 共生载荷；一颗卫星上多家租户共享总线、电源、姿态控制等。
- **delay-tolerant network (DTN)** —— 延迟容忍网络；适配长延迟、间歇连接的网络栈。
- **FROM scratch (Docker)** —— Docker 镜像基底"空"；只包含静态链接的二进制。
- **static binary** —— 静态链接二进制；不依赖运行时动态库。
- **Cortex-A53** —— Arm 中低功耗 64 位核心，常用于嵌入式 Linux。
- **APID** —— Application Process Identifier；CCSDS Space Packet 的应用进程标识，类似端口号。
- **Space Packet** —— CCSDS 的应用层报文格式。
- **frame** —— 帧；CCSDS 物理层 framing 单元。
- **wire format** —— 线协议格式；序列化后在网络上传输的字节布局。
- **schema-driven** —— 用 schema 描述、自动生成 codec。

## 6. 性能术语

- **p50 / p99 / p99.9** —— 50/99/99.9 分位延迟；越高越能反映尾部分布。
- **jitter** —— 抖动；延迟的方差，对实时系统比平均延迟更致命。
- **dispatch hot path** —— 调度热路径；每个报文必经的关键代码段。
- **stack allocation** —— 栈分配；函数返回时自动释放，不进 GC。
- **heap allocation** —— 堆分配；通过 GC 管理。
- **minor GC** —— 年轻代回收；OCaml 中频次最高、对延迟影响最直接的一类。

## 7. 工程模式

- **functional core, imperative shell** —— "功能式内核 + 命令式外壳"模式；纯函数算逻辑、副作用集中在边界。
- **reference implementation** —— 参考实现；其他实现做 byte-for-byte 比对的真相源。
- **interop pipeline** —— 互操作流水线；自动跑跨实现一致性测试。
- **schema-first** —— 协议先写 schema，再生成代码。
- **attestation** —— 证明；密码学证明"我正在跑的就是你期望的二进制"。
- **fleet management** —— 舰队管理；管成百上千颗卫星 / 实例的统一发布、监控。

## 8. 漏洞 / 案例

- **Dirty Pipe (2022)** —— Linux 内核 pipe write 越权 CVE-2022-0847。
- **nf_tables UAF (2024)** —— Linux netfilter use-after-free，被用于容器逃逸。
- **Dirty Frag (2026)** —— 通用 Linux LPE。
- **Fragnesia (2026)** —— Dirty Frag 同家族漏洞。
- **"Copy Fail" (2026-04)** —— Linux 内核提权，跨发行版一击命中（详见本博客 [《Copy Fail 与后量子 IPsec》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/)）。
- **CryptoLib heap overflow** —— NASA 参考实现历史 bug，TC frame 解析器整数下溢导致堆缓冲区溢出。

## 9. 行业 / 文化

- **NewSpace** —— 新太空；以 SpaceX、Rocket Lab 等为代表的商业航天浪潮。
- **ground pass** —— 过境窗口；卫星飞越某地面站可通信的时间段（一般几分钟）。
- **mission ops** —— 任务运维；卫星运营团队。
- **payload module** —— 载荷舱；卫星上租户负责的计算/通信单元。
- **flight software** —— 飞行软件；在轨运行的所有软件总称。
- **ground software** —— 地面软件；任务控制中心使用的指挥、监控、数据分析栈。

## 10. 文献缩写

- **ICFP** —— International Conference on Functional Programming。
- **ASPLOS** —— Architectural Support for Programming Languages and Operating Systems。
- **USENIX Security** —— USENIX 安全研讨会。
- **ESA** —— European Space Agency。
- **JPL** —— Jet Propulsion Laboratory（NASA 喷气推进实验室）。
- **F Prime (F´)** —— NASA JPL 的 C++ 飞控框架。

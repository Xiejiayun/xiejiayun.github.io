# XCA / Fabricked / BreakFAST 术语对照表

英中术语对照表（32 条），覆盖机密计算、TEE、SoC 互联、SEV-SNP 内部组件和 XCA 攻击专用术语。

| 英文 | 中文 | 一句话定义 |
|------|------|-----------|
| Confidential Computing | 机密计算 | 让数据"使用中"也对云厂商保密的硬件能力 |
| Confidential VM (CVM) | 机密虚拟机 | 在敌对 hypervisor 下仍保密的 VM |
| Trusted Execution Environment (TEE) | 可信执行环境 | 由 CPU 硬件强制隔离的运行环境 |
| Trusted Computing Base (TCB) | 可信计算基 | 必须信任才能保证安全的最小组件集合 |
| Root of Trust (RoT) | 信任根 | TCB 的最底层，通常是芯片内烧死的密钥/代码 |
| Threat Model | 威胁模型 | 系统对哪些攻击者负责防御的形式化描述 |
| Hypervisor | 虚拟机管理器 | 跑在裸机上、调度 VM 的低层软件 |
| BIOS / UEFI | 基础输入输出系统 / 统一可扩展固件接口 | 启动早期阶段执行的固件，在 SEV-SNP 模型下不可信 |
| AMD SEV | Secure Encrypted Virtualization | AMD 第一代 VM 内存加密 |
| AMD SEV-ES | SEV + Encrypted State | 第二代，加密 vCPU 寄存器 |
| AMD SEV-SNP | SEV + Secure Nested Paging | 第三代，加完整性保护，是当前主流 |
| PSP | Platform Security Processor | AMD CPU 内置的一颗 ARM 小处理器，SEV-SNP 信任根 |
| RMP | Reverse Map Table | 物理页所有权登记册，硬件强制查 |
| ImmutableEntry | 不可变条目 | RMP 中标记"系统页、不可被 hypervisor 改写"的条目 |
| Attestation | 远程证明 | 用 RoT 私钥签的"我在哪、跑什么"的报告 |
| VCEK | Versioned Chip Endorsement Key | AMD 每颗 CPU 唯一的、用于签 attestation 的私钥 |
| KDS | Key Distribution Service | AMD 运营的、用于验证 attestation 报告的服务 |
| SNP_INIT | SNP 初始化 | PSP 在 SEV-SNP 启动时执行的初始化命令 |
| Infinity Fabric | 无限互联 | AMD 自有的高速 SoC 内部互联总线 |
| Data Fabric (DF) | 数据平面 | Infinity Fabric 中负责数据搬运的部分 |
| Control Fabric (SMN) | 控制平面 / 系统管理网络 | Infinity Fabric 中负责寄存器配置的 4GB 空间 |
| Chiplet | 芯粒 | 单独制造、再封装拼接的 CPU 小块 |
| SoC | System-on-Chip | 把 CPU、内存控制器、IO 等做在同一颗芯片上的设计 |
| IOMMU | 输入输出内存管理单元 | 控制 DMA 设备能访问哪些物理内存 |
| DMA | Direct Memory Access | 设备绕过 CPU 直接访问内存 |
| FASTREGCNTL / FASTREG | 快速寄存器控制 / 数据寄存器 | 平台上一对暴露 1MB SMN 滑动窗口的隐藏寄存器 |
| Confused Deputy | 混淆代理（攻击） | 借有权限的代理替自己做没权限的事的攻击模式 |
| Interconnect Corruption Attack (XCA) | 互联总线腐化攻击 | 本文核心攻击类：通过改 fabric 路由让可信组件做错事 |
| Authenticated Interconnect | 认证互联 | 下一代设计方向：互联本身做端到端认证 |
| AES-XTS | XTS 模式 AES 加密 | SEV-SNP 用来加密 CVM 物理内存的对称密码 |
| CVE | Common Vulnerabilities and Exposures | 公共漏洞编号 |
| Side-Channel Attack | 侧信道攻击 | 通过共享资源（cache、power、time）泄漏数据的攻击 |

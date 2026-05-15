# 术语表（Glossary）：Tesla Wall Connector anti-downgrade bypass

英中对照术语表，涵盖 UDS / 汽车诊断 / 嵌入式安全的常见缩写与短语。

| 英文 / 缩写 | 中文 | 一句话解释 |
|---|---|---|
| **UDS (Unified Diagnostic Services)** | 统一诊断服务 | ISO 14229 定义的汽车 ECU 通用诊断协议 |
| **SWCAN (Single-Wire CAN)** | 单线 CAN 总线 | GMW3089 规范的低速 CAN，常用于诊断 |
| **PP (Proximity Pilot)** | 邻近导引 | EV 充电接口检测车辆接入、判断电缆电流容量的信号 |
| **CP (Control Pilot)** | 控制导引 | EV 充电主信号，承载 PWM 调制的功率协商 / 状态机 / 在 Tesla 场景里承载 SWCAN |
| **J1772** | SAE J1772 标准 | 北美 EV 充电接口规范 |
| **IEC 61851** | — | 国际 EV 传导式充电标准 |
| **OTA (Over-the-Air)** | 空中升级 | 远程下发固件 / 软件更新 |
| **A/B Slot** | 双分区 | flash 内同时存放两份固件，便于安全回滚 |
| **Partition Table** | 分区表 | flash 上记录各 slot 元数据（地址、大小、`gen_level` 等） |
| **gen_level (generation level)** | 代数 / 世代号 | 分区表里的整数，bootloader 用以挑选 active slot |
| **Bootloader** | 引导加载程序 | flash 固定地址的小程序，启动时挑 slot 并跳入 |
| **boot2** | — | Tesla Wall Connector bootloader 的内部名 |
| **Secure Boot** | 安全启动 | 启动链每一级都校验下一级签名 |
| **SBFH** | — | Wall Connector 固件镜像的魔术头 |
| **RSA Signature** | RSA 签名 | bootloader 用公钥校验固件来源 |
| **CRC32** | 循环冗余校验 | bootloader 用以验证镜像段完整性 |
| **PSM (Persistent Storage Manager)** | 持久存储管理器 | 设备内跨重启保持状态的子系统，存 ratchet |
| **NVRAM** | 非易失性 RAM | 类似 PSM 的概念 |
| **Anti-Rollback / Anti-Downgrade** | 防降级 | 阻止设备安装版本低于当前的固件 |
| **Security Ratchet** | 安全棘轮 | 单向递增的版本号，作为 anti-downgrade 的依据 |
| **VRSN / VRS2** | — | Wall Connector 固件 segment 表中的版本 / ratchet 描述符 |
| **Trust Anchor** | 信任锚 | 安全链的根，通常在最底层硬件 / bootloader |
| **Defense in Depth** | 纵深防御 | 在多层独立机制中重复校验关键属性 |
| **Race Condition** | 竞态 | 因执行顺序不可控导致的安全漏洞 |
| **State Machine Coupling** | 状态机耦合 | 多个状态机间共享变量 / 资源产生意外路径 |
| **LPE (Local Privilege Escalation)** | 本地提权 | 普通用户提升到 root / kernel 权限 |
| **RCE (Remote Code Execution)** | 远程代码执行 | 攻击者远程在设备上运行任意代码 |
| **ZDI (Zero Day Initiative)** | — | Trend Micro 旗下的漏洞收购计划，Pwn2Own 主办方 |
| **Pwn2Own Automotive** | — | ZDI 的汽车专场漏洞演示赛，2024 年首届，2025 年东京举办 |
| **MTE (Memory Tagging Extension)** | 内存标签扩展 | ARM 的硬件级内存安全机制 |
| **MIE (Memory Integrity Enforcement)** | 内存完整性强制 | Apple 基于 MTE 构建的端到端内存安全方案 |
| **Mythos Preview** | — | Anthropic 联合外部安全团队开发中的 AI 漏洞助手 |
| **IDA Pro** | — | 静态反汇编 / 反编译工具，硬件安全的常用工作台 |
| **JTAG** | 联合测试行动小组 | 嵌入式设备调试 / 编程标准接口 |

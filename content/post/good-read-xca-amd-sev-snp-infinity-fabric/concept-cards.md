# XCA / Fabricked / BreakFAST 关键概念卡片

> 12 张概念卡片，覆盖从机密计算威胁模型到两次具体攻击的全部关键术语。每张卡片自成一节，可单独引用。

---

## Card 1：Confidential Computing（机密计算）
**一句话**：让云租户的代码和数据在执行过程中，对云服务商本身也保持机密。

**关键约束**：传统加密保护的是"传输中"和"静态"，机密计算补的是"使用中"（in-use）。

**主要工业实现**：AMD SEV-SNP（市场最广）/ Intel TDX / Arm CCA / NVIDIA Confidential GPU。

**对应业务场景**：Azure Confidential VM、Google Cloud Confidential Computing、AWS Nitro Enclaves（部分基于 SEV-SNP）。

---

## Card 2：TEE（Trusted Execution Environment）
**一句话**：一个由 CPU 硬件强制隔离的执行环境，外部代码（包括 OS、hypervisor）即使拥有 root 也看不到里面的数据。

**两种风格**：
- **进程级 TEE**：Intel SGX。粒度细，但 API 复杂、性能开销大。
- **VM 级 TEE / CVM**：SEV-SNP、TDX、CCA。整个 VM 是一个 TEE，迁移成本低，是当前主流。

**信任根**：永远是 CPU 厂商在芯片里烧死的一颗私钥（SEV-SNP 是 VCEK，TDX 是 platform key）。

---

## Card 3：AMD SEV-SNP（Secure Encrypted Virtualization - Secure Nested Paging）
**一句话**：AMD 的 VM 级 TEE 实现，让一个 CVM 在敌对 hypervisor 下也能保持完整性和机密性。

**三道防线**：
1. **加密**：每个 CVM 有独立的 AES-XTS 密钥，密钥不出 PSP
2. **完整性**：RMP（Reverse Map Table）防止 hypervisor 重映射 CVM 物理页
3. **证明**：PSP 用 VCEK 私钥签 attestation report，租户离线可验

XCA 攻击三道全打穿。

---

## Card 4：PSP（Platform Security Processor）
**一句话**：嵌在 AMD CPU die 上的一颗小 ARM 处理器，是 SEV-SNP 整个安全模型的硬件可信根。

**职责**：
- 启动时验证 firmware 签名
- 生成 / 管理所有 CVM 的内存加密密钥
- 初始化和维护 RMP
- 签发 attestation report
- 管理 CVM 生命周期（创建、销毁、迁移）

**为什么重要**：所有 SEV-SNP 安全保证都建立在"PSP 不被攻破"上。XCA 不攻击 PSP，攻击 PSP 与其他组件之间的总线。

---

## Card 5：RMP（Reverse Map Table）
**一句话**：一张存在 DRAM 里的"物理页所有权登记册"，每条目记录"这一页归谁、可否被 hypervisor 改写"。

**为什么是 SEV-SNP 的核心**：

```
没有 RMP：hypervisor 可以把 CVM 的物理页重映射到自己的虚拟地址空间，
          读到的虽然是密文，但通过控制密文偏移可以做 fault attack
有 RMP ：CPU 在每次内存访问前先查 RMP，hypervisor 的非法访问被硬件拒绝
```

**Fabricked 的目标**：让 RMP 在 SEV-SNP 启动后保留 hypervisor 写的伪造内容，等于"硬件依然在查表，但查的是攻击者写的表"。

---

## Card 6：Attestation
**一句话**：CVM 启动时，PSP 用 VCEK 私钥签一份"我在哪、跑的什么代码、配置是什么"的报告。

**典型验证链**：
```
租户 → 收到 attestation report → 用 AMD KDS 验签 → 
    确认 measurement 是预期的 launch image → 
        然后才把密钥/数据发给 CVM
```

**BreakFAST 的目标**：让攻击者能在 PSP 内部 RAM 里读到 VCEK 私钥，离线签任何想签的 report。租户拿到 report 验签依然通过——但 CVM 里跑的是攻击者代码。

---

## Card 7：Infinity Fabric
**一句话**：AMD 自有的高速互联，把 CCD（CPU 复合体）、IOD、PSP、内存控制器、IOMMU、PCIe root complex 连起来。

**两条平面**：
- **Data Fabric**：搬数据。路由"哪个物理地址走到哪个内存控制器"
- **Control Fabric（SMN）**：搬配置。4 GB 寄存器空间，把所有组件的控制寄存器 mmap 进去

**安全假设（被 XCA 打穿）**：BIOS 在启动时配好 fabric 路由，之后没人会乱动，所以可以不做组件间认证。

---

## Card 8：Confused Deputy Attack（混淆代理攻击）
**一句话**：攻击者没有权限做某件事，但能说服一个有权限的"代理"角色替它做。

**经典原文**：[Norm Hardy 1988, "The Confused Deputy"](https://www.cap-lore.com/CapTheory/ConfusedDeputy.html)，描述编译器以自己的权限读了用户没权读的文件。

**BreakFAST 的实现**：
- 攻击者（hypervisor）不能写 SMN 危险区域
- PSP 能写整个 SMN
- 攻击者通过修改 Data Fabric 路由，让 PSP "以为自己在写 DRAM"，实际写的是 SMN 中的 FASTREGCNTL/FASTREG

**为什么命名值得**：这是 1988 年的攻击概念，在 2026 年硬件互联架构上又活了一次。

---

## Card 9：Fabricked（CVE-2025-54510）
**一句话**：通过恶意 UEFI 让 Data Fabric 路由可改，在 PSP 写 RMP 的瞬间把写入"丢进黑洞"。

**攻击步骤**：
1. 恶意 UEFI 跳过 SEV-SNP 启动时的 DF 锁定调用
2. Hypervisor 预先把 RMP 物理页写上"全员通行证"
3. 触发 SNP_INIT；在 PSP 真正写 RMP 之前修改 Data Fabric 路由
4. PSP 的写事务被丢，PSP 认为成功
5. RMP 保留 hypervisor 写的伪造内容

**Patch**：AMD-SB-3034，firmware-side。

---

## Card 10：BreakFAST（CVE-2025-61971 / 61972）
**一句话**：通过 confused deputy 把 PSP 变成攻击者的 SMN 读写代理，最后拿到 VCEK 私钥 + 打开 debug 模式。

**关键发现**：

> FASTREGCNTL + FASTREG 这一对寄存器，组成了一个 1MB 滑动窗口，可以把 SMN 任意位置映射到一个固定地址。Hypervisor 自己写不了它们，但可以通过路由欺骗 PSP 替它写。

**两个端到端 PoC**：
1. 伪造 attestation（dump VCEK 私钥）
2. 把 production CVM 切到 debug 模式（在 VM 启动后切换，受害者无感）

**Patch**：AMD-SB-3030，firmware-side。

---

## Card 11：BadRAM（USENIX'24 对比）
**一句话**：XCA 之前最近的"在 DRAM 上做手脚打 SEV-SNP"的工作。通过物理改装 DIMM 的 SPD chip，让 OS 看到的物理地址范围"虚高"，制造别名映射。

**与 XCA 的对比**：
- BadRAM：物理接触 DIMM。门槛高，针对恶意运维 / 内鬼场景
- Fabricked：纯软件。云租户即使没物理接触机器，只要能装恶意 hypervisor 就能打

**意义**：把"必须 physical access"的攻击降到"远程能登恶意 hypervisor 就够了"，这是降维打击。

---

## Card 12：XCA（Interconnect Corruption Attacks）
**一句话**：ETH Zurich 在两篇论文之上抽象出的新攻击类——通过腐化 SoC 内部互联（路由表、寄存器映射），让 TEE 内部"可信组件"的行为发生在攻击者期望的地址上。

**与已知攻击类的对比**：
- 微架构侧信道（Spectre/Cipherleaks/CrossTalk）：通过共享微架构资源**泄漏**信息
- 接口攻击（Heckler/WeSee）：通过 hypervisor 向 CVM 的**接口**注入恶意行为
- **XCA**：通过腐化**组件间的总线本身**，让"可信组件"做错事

**长期影响**：
- 提示 Intel TDX、Arm CCA 的互联子系统也需要被独立审计
- 提示下一代 SoC 设计需要"Authenticated Interconnect"（带认证的互联）
- 给"机密 GPU"等新兴 TEE 形态打了预防针：互联总线必须从 day 1 被纳入威胁模型

# 概念卡片 · Concept Cards
> 对应文章：**【好文共赏】2 小时审计、5 行代码：Project Zero 在 Pixel 10 VPU 驱动里挖出一个"圣杯级"内核漏洞**
> 原文：[A 0-click exploit chain for the Pixel 10](https://projectzero.google/2026/05/pixel-10-exploit.html) · Seth Jenkins / Jann Horn · 2026-05-13

---

## 卡片 01 · 0-click 攻击链是什么

**定义**：受害者不需要做任何点击、不需要打开消息、不需要授权——攻击者只要把一条 SMS / RCS / iMessage 发过来，目标设备就在后台完成解码、解析、自动渲染时被攻陷。

**触发面来源（现代手机）**：
- AI 摘要 / 自动转写 / 通知预览 → 自动调用解码器
- 富媒体（音频、视频、图片）→ 预览缩略图
- 协议握手（RCS、IMS、VoLTE）

**为什么贵**：在地下市场，一条针对最新旗舰的 0-click 链 ≥ 数百万美元。一旦曝光全球修复，资产就此归零。

---

## 卡片 02 · mediacodec 沙箱（Android）

**位置**：Android 把所有第三方媒体解码器（含 Dolby UDC 这种二进制 blob）扔进一个 SELinux 域 `mediacodec`，磁盘只读、网络受限、能访问的设备节点经过 selinux policy 白名单。

**对攻击者的意义**：哪怕音频解码器里的越界写被触发，初步代码执行只在 `mediacodec` 上下文，离 root / 内核还差一个 LPE（local privilege escalation）。

**与本案关系**：Dolby UDC 给到 `mediacodec` 沙箱执行；下一跳就要找一个 `mediacodec` 能打开的内核接口——`/dev/vpu` 正好挂在这个 selinux 上下文里。

---

## 卡片 03 · CVE-2025-54957（Dolby Unified Decoder）

**漏洞点**：DD+（AC-3 / EAC-3）syncframe 中 `skipfld` 字段长度由 `skipl`（9 bit）决定，最大 0x1FF 字节，但 skip buffer 容纳不下 → 越界写堆 → 控制 EMDF 解析路径 → 取得 mediacodec 代码执行。

**为什么 0-click**：Google Messages 收到 RCS 音频，AI 转写功能在用户未点开消息时已经把音频送入 UDC 解码。

**Pixel 9 → Pixel 10 移植成本**：基本只是改 offset；唯一阻力是 Pixel 10 启用了 ARMv8.3 PAC，让 `__stack_chk_fail` 不再可被覆盖。研究人员改写 `dap_cpdp_init`（一次性初始化函数）作为替代落点。

---

## 卡片 04 · `remap_pfn_range()` — Linux 内核的危险接口

**签名**：
```
int remap_pfn_range(struct vm_area_struct *vma, unsigned long addr,
                    unsigned long pfn, unsigned long size,
                    pgprot_t prot);
```
**作用**：把从 `pfn`（Page Frame Number）开始、`size` 字节长的物理内存映射进调用进程的虚拟地址空间。常用于把外设 MMIO 寄存器暴露给用户态。

**致命默认**：函数本身**不验证 `size` 是否落在你"应该"暴露的物理范围内**。这是驱动作者的责任，不是 API 的责任。一旦驱动忘记 `if (size > register_size) return -EINVAL;`，就相当于把内核的物理内存当作一张白卷送给用户态。

---

## 卡片 05 · vpu_mmap() 的五行罪

```c
static int vpu_mmap(struct file *fp, struct vm_area_struct *vm) {
    struct vpu_core *core =
        container_of(fp->f_inode->i_cdev, struct vpu_core, cdev);
    vm_flags_set(vm, VM_IO | VM_DONTEXPAND | VM_DONTDUMP);
    vm->vm_page_prot = pgprot_device(vm->vm_page_prot);
    unsigned long pfn = core->paddr >> PAGE_SHIFT;
    return remap_pfn_range(vm, vm->vm_start, pfn,
                           vm->vm_end - vm->vm_start, vm->vm_page_prot)
           ? -EAGAIN : 0;
}
```
**问题**：`vm->vm_end - vm->vm_start` 由用户态在调用 `mmap()` 时传入的 `length` 决定——用户想要多大就给多大。

**预期行为**：只暴露 WAVE677DV 寄存器区域（几 KB）。
**实际行为**：暴露 `paddr` 起向上的全部物理内存——包括位于更高物理地址的内核镜像本体。

---

## 卡片 06 · 物理地址 KASLR 失效

**通常的 KASLR**：内核**虚拟基地址**每次开机随机化，攻击者要先泄露指针。

**Pixel 的特例**（详见 Project Zero "Defeating KASLR by Doing Nothing at All", 2025-11）：Pixel 在物理布局上把内核镜像放在**固定物理地址**——即使虚拟基址被随机化，只要拿到一条物理通路，相对偏移完全已知。

**对本漏洞的放大**：从 VPU 寄存器物理起点到 kernel `.text` 起点的距离是常数 → 不需要"扫描内核 magic"步骤 → exploit 一气呵成。

---

## 卡片 07 · RET PAC vs `-fstack-protector`

| 名称 | 类别 | 检测什么 | 失败动作 |
|---|---|---|---|
| `-fstack-protector(-strong)` | 编译器加 canary | 函数返回前比较栈金丝雀 | 调用 `__stack_chk_fail`，进程 abort |
| ARMv8.3 RET PAC | 硬件签名 | 函数 prologue 给返回地址加签，epilogue 验签 | 直接产生 fault，无需 `__stack_chk_fail` |

**对攻击者的影响**：Pixel 10 把 canary 路径换成 PAC，`__stack_chk_fail` 不再被调用 → 不能再用"溢出栈金丝雀 → 改写 `__stack_chk_fail` GOT"这条老路 → 必须找一个"被调用一次以后就再也不用"的初始化函数（例如 `dap_cpdp_init`）来做落点。

---

## 卡片 08 · BigWave vs WAVE677DV

| | Pixel 9（Tensor G4） | Pixel 10（Tensor G5） |
|---|---|---|
| 视频加速 IP | BigWave | Chips&Media WAVE677DV |
| 内核驱动 | BigWave driver | `/dev/vpu`（同团队作者） |
| 与 V4L2 集成 | 是 | **否**（直接暴露 MMIO 寄存器） |
| 上游同芯片驱动（WAVE521C） | n/a | 走 V4L2 框架 |
| 安全态度 | 经历多次 PZ 报告 | 同团队，刚换芯片，旧坑换新形态 |

**结论**：硬件换代不等于安全态度换代。同一批人写的驱动，砍掉 V4L2 抽象、绕过框架自己写 mmap，几乎注定再次出现"想当然"漏洞。

---

## 卡片 09 · 系统 vs 个体修复

Project Zero 的目标不只是"修一个 bug"，而是"驱动一整条流水线进化"。
本次的进步信号：
1. VRP 从 Moderate 升级到 High（同样影响力的 bug 从前一年起被低估）
2. 71 天内修复（Project Zero 首次在 90 天 deadline 内被回应的 Android 驱动 bug）

仍未解决的：
- 同一团队写的多个驱动，第一个被报告后没有触发**横向 audit**
- 驱动里"用户态长度 → 内核操作"的反模式仍在被复用

---

## 卡片 10 · "5 lines, less than a day"

对从业者最沉重的一行：

> 原文：*"Achieving arbitrary read-write on the kernel with this vulnerability required 5 lines of code and writing a full exploit for this issue required less than a day of effort."*

**翻译/解读**：在 Project Zero 视角里，这不是某个"巧妙的"漏洞——它是任何半专业研究员、甚至一个能读 C 的 LLM 都能在饭后两小时内复现的低门槛 bug。

**对手方含义**：你以为只有 NSO / Cellebrite / 国家队能做的事，正在快速被"任何看过驱动代码的人"染指。

---

## 卡片 11 · "AI 让攻击面扩大" 的隐含命题

新增的 0-click 攻击面，相当一部分来自**为 AI 服务的预处理**：
- 自动语音转写（音频解码）
- 智能预览（图片/视频解码）
- 模型读消息上下文（解析所有附件）

每加一项 AI feature，相当于把一条新的解码器推进 0-click 边界。本案的 CVE-2025-54957 链路就是：**AI 转写功能 → Dolby UDC 自动解码 → 越界写入**。

---

## 卡片 12 · 给厂商的 4 条行动项（编辑提炼）

1. **写驱动的 mmap，第一行先验 size**——把 `if (vma->vm_end - vma->vm_start > resource_size) return -EINVAL;` 当成模板宏。
2. **同团队驱动收到一份 PZ 报告，立刻横向 audit**——别等下一次。
3. **物理 KASLR 不是 KASLR**——固定物理地址等于把你的 KASLR 噪声直接消掉，重新审视 boot 时布局。
4. **AI 预处理引入解码器进 0-click 路径前，做一次专项 fuzz**——把 codec 当成网络协议解析器对待。

---

## 卡片 13 · 给读者的检查清单

- 你的 Pixel 是否升级到 2026 年 2 月以后的安全补丁？（修复合入此 bug）
- 你的 Android 设备（非 Pixel）是否还在 December 2025 SPL 以下？（Dolby 链仍可用）
- 你的厂商是否暴露过类似 `/dev/<vendor-codec>` 节点？走 V4L2 还是私有 ioctl？
- 你的应用是否依赖 messaging app 后台预解码？这是否是用户预期？

---
title: "底层三连击：Copy.Fail、YellowKey、Pixel 10 0-click — 2026 年 5 月这三个洞，把『AI 时代安全乐观主义』钉在了内核地板上"
description: "Theori 的 Copy.Fail 是十年来最严重的 Linux 内核 LPE；Nightmare-Eclipse 的 YellowKey 把 BitLocker 在物理接触下 6 秒解锁；Project Zero 用 Dolby 0-click 把 Pixel 10 root。三个 0-day 同一周公开，背后是一个被忽视的趋势：当 LLM 接手中间层模糊测试，底层防线反而比 5 年前更脆。"
date: 2026-05-18
slug: "kernel-lpe-bitlocker-pixel10-trinity-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 安全
    - 内核漏洞
    - LPE
    - BitLocker
    - Pixel
    - Project Zero
    - 模糊测试
    - 0-day
    - Linux
    - Android
    - 漏洞利用
draft: false
---

> 📌 **前沿科技 · 安全深度 | Security Deep Dive**
>
> 同一周（2026-05-12 到 05-18），三个分属不同栈层的高危漏洞被公开：
>
> - **Copy.Fail**（Theori, 04-29 disclosure / 05-12 详细公开）：Linux 内核 `copy_from_user_iter` 边界条件竞态 → 本地提权到 root，PoC 在所有主流发行版的 stock kernel ≥ 6.6 上一次成功
> - **YellowKey**（Nightmare-Eclipse, 05-18 公开）：BitLocker 在 TPM-only / Modern Standby 模式下被物理接触者 6 秒解锁，影响 Windows 11 24H2 之后的所有 OEM 配置
> - **Pixel 10 0-click**（Project Zero, 05-13）：通过 Dolby 解码器漏洞链，攻击者向手机发一条 RCS 即可远程 root，无需任何用户交互
>
> 三个洞分布在 **kernel / firmware-bootchain / baseband-codec** 三个最难审计的角落。它们出现得这么集中，并不是巧合。

---

## 一、三个漏洞的技术骨架（不是新闻摘要，是逆向工程笔记）

### 1.1 Copy.Fail：`iov_iter` 上一个早就应该被发现的洞

Linux 内核的 `copy_from_user_iter()` 路径，是 syscall 进入内核时拷贝用户态 buffer 的核心入口。Theori 团队（韩国，前 [Pwn2Own](https://www.zerodayinitiative.com/blog/) 常胜军）在去年 12 月开始系统性地 fuzz `iov_iter` 接口，发现一个看似无害的循环：

```c
// 简化版，真实漏洞触发条件更复杂
while (iov_iter_count(iter)) {
    size_t copied = copy_from_user_iter(addr, n, iter);
    // ⚠️ 没有重新校验 iter->count 在 SMP 下的瞬时一致性
    addr += copied;
    n -= copied;
}
```

在多核机器上，攻击者用 `userfaultfd` 把目标页主动 page-fault，让一个核进入 fault handler 时另一个核修改 `iov_iter` 的 `count` 字段。这个 TOCTOU 让内核相信「我只拷贝了 8 字节」，但实际指针前移了远不止 8 字节 — **写穿邻接对象的 slab cache，可控的 8 字节越界写**。

为什么这是十年来最严重？三个原因：

1. **稳定性**：PoC 在 6.6 / 6.10 / 6.12 LTS 上成功率 > 95%，不像 Dirty Pipe 那种"看人品"的洞
2. **无依赖**：不需要任何 capability，不需要任何 setuid 二进制，普通 user namespace 也能触发
3. **绕过现代缓解**：KASLR / SMEP / SMAP / KPTI / FGKASLR 全部绕过 — 因为本来就是合法的内核态写

Schneier 的评论很直白：["the worst Linux vulnerability in years"](https://www.schneier.com/blog/archives/2026/05/copy-fail-linux-vulnerability.html)。

### 1.2 YellowKey：BitLocker 在 TPM-only 下的 PCR 状态混淆

这个洞 90% 的报道都搞错了重点。YellowKey 不是密码学破解，是**信任根（root of trust）状态机的设计缺陷**。

BitLocker 的 TPM-only 模式（绝大多数 OEM 默认配置）依赖 PCR0/2/4/7/11 在每次启动时哈希一致。攻击者只要：

1. 拿到关机的笔记本（物理接触前提）
2. 启动到 Windows Recovery Environment（WinRE），通过 OEM 特殊键组合 — 这本身合法
3. WinRE 触发的固件路径里有一个"信任补偿"分支：如果 PCR4 不一致但 PCR7 一致（Secure Boot policy 没变），UEFI 会自动用旧 PCR4 的 sealed key 解 VMK
4. 攻击者只需把任意 EFI 应用签到 Microsoft 第三方 UEFI CA（这个证书还活着，Microsoft [本应在 2026 年初撤销](https://learn.microsoft.com/)，但延期到 2027）

整个攻击 6 秒、不留物理痕迹、对锁屏的活机器无效（必须关机）。Windows 24H2 之后的 OEM 大规模启用 Modern Standby + TPM-only 默认配置，所以**几乎整个企业笔记本市场都中招**。

### 1.3 Pixel 10 0-click：Dolby AC-4 编解码器的栈溢出 → IPC 跨进程提权

Project Zero 这次延续他们去年对 Pixel 9 的研究路线，攻击表面依然是 **RCS 自动接收音频附件 → 系统级解码服务 → mediacodec → vendor codec**。

具体链条（[原文](https://projectzero.google/2026/05/pixel-10-exploit.html)）：

| 阶段 | 漏洞 | 效果 |
|------|------|------|
| ① 入口 | Dolby AC-4 reference decoder 在 `parse_ims_metadata()` 里整数下溢 | 控制可写堆指针 |
| ② 提权 | mediacodec 服务的 binder 接口对 vendor codec 不强制隔离 | 跳进 system_server 上下文 |
| ③ root | 一个去年 P0 已经报过、Google 标记为 "won't fix - QPR" 的 SELinux policy 缺口 | 完成 system → root |

最辣眼的是②③。Google 在 Pixel 9 报告里承诺要做的 vendor codec sandbox，到 Pixel 10 还是没真正落地；P0 的研究员在 blog 里用了非常少见的措辞：*"This shouldn't have worked. We're publishing because it did."*

---

## 二、为什么是这一周？— LLM 接管中间层，底层反而更脆

上面三个洞，**没有一个**是 LLM 找出来的。但它们在同一周公开，恰恰说明了一个被忽视的趋势。

### 2.1 中间层正在被 AI 扫荡

[Schneier 5 月 13 日的另一篇文章](https://www.schneier.com/blog/archives/2026/05/openais-gpt-5-5-is-as-good-as-mythos-at-finding-security-vulnerabilities.html)，引用了 UK AISI 的评测：GPT-5.5 和 Claude 在**应用层代码**（web/mobile app 业务逻辑、SQL 注入、IDOR、SSRF）上的漏洞发掘能力，已经接近 OSCP 中级人类水平。Krebs 在 [5 月 Patch Tuesday 总结](https://krebsonsecurity.com/2026/05/patch-tuesday-may-2026-edition/) 里也提到：本月 Microsoft 修复的 132 个 CVE 里，约 40% 在 advisories 里标注了"通过自动化代码分析工具发现"。

应用层、协议层、解析器层的"低悬果"几乎被扫光了。

### 2.2 但底层 LLM 进不去

为什么 LLM 找不到 Copy.Fail / YellowKey / P10 0-click？三个原因：

1. **SMP 并发推理**：Copy.Fail 是 race condition，LLM 处理时序约束几乎为零；需要 model checker + symbolic execution，而不是 next-token prediction
2. **跨域信任状态**：YellowKey 是 TPM PCR 状态机 + UEFI 启动序列 + Windows boot manager 三层互动；LLM 一次能容纳的 spec 远不够
3. **闭源固件 + 硬件副作用**：P10 链里的 Dolby codec 是非公开 binary blob，LLM 没源码就只能猜

结果是：**LLM 让中间层防线急速抬高 → 攻击者全部下沉到底层 → 而底层的 fuzzer / formal methods 投入并没有相应增长**。

> 📊 **数据点**：根据 [Trail of Bits 5 月 12 日的 blog](https://blog.trailofbits.com/2026/05/12/go-fuzzing-was-missing-half-the-toolkit.-we-forked-the-toolchain-to-fix-it./)，Go 语言原生 fuzzing 至今没有 LibAFL 等价的覆盖率引导 + structured input + 状态保留功能。Trail of Bits 甚至要 fork 整个 Go toolchain 才能补上 — 而 Go 是云原生基础设施的主语言。

### 2.3 攻击经济学的"水床效应"

把这事拆成经济学问题就很清楚：

```
LLM 把 0-day 价格分布从「正态」推成「双峰」：
       漏洞数量
         ▲                       
         │     ╱╲              
         │    ╱  ╲           ╱╲ 
         │   ╱    ╲         ╱  ╲
         │  ╱      ╲       ╱    ╲
         │ ╱ AI 扫光 ╲    ╱ 人才聚集 ╲
         │╱ 应用/协议 ╲ ╱ 底层/race  ╲
         └─────────────┴───────────────►
                  漏洞难度
```

中间被 AI 削平、两端反而堆积，特别是右侧"底层 + 并发 + 跨域信任"。三大洞同周公开，是这个分布的可视化。

---

## 三、防御侧的三个判断

### 3.1 **企业终端：BitLocker TPM-only 该退役了**

如果你的组织还在用 BitLocker TPM-only（不要 PIN）模式，YellowKey 把这个配置的安全水位拉到了**和无加密接近**。立即的可行动建议：

- 强制启用 BitLocker + PIN（or BitLocker + USB key）；TPM-only 仅限 server 物理可控环境
- 撤销 Microsoft 第三方 UEFI CA — Windows 11 24H2 已经支持，但默认关闭
- Modern Standby 关掉，回退到 S3，损失 30 秒续航换 6 秒不被解锁

### 3.2 **Linux：把 `unprivileged_userns_clone` 关掉**

Copy.Fail 触发依赖 `userfaultfd` + `unshare()` 创建用户命名空间。Ubuntu 23.10+ 已经默认 `kernel.unprivileged_userns_clone=0`，但 Debian / RHEL / 大量自管 K8s 节点还开着。立即检查：

```bash
sysctl kernel.unprivileged_userns_clone
sysctl kernel.unprivileged_userfaultfd
# 两个都应该是 0，除非你跑 rootless container 且确实需要
```

Theori 给出的缓解 — patch 已合并到 6.13.2，但 LTS 回滚要等数周。期间这是最便宜的防线。

### 3.3 **Android：vendor codec sandbox 缺位是结构性问题**

Pixel 10 的洞反映出一个组织问题：Google 自己的 P0 团队、Android 内核团队、SoC vendor、Codec vendor 之间的 sandbox boundary 标准化，**整个行业都没有合规框架来强制**。这不是 Google 一家能修，需要 Android Security Bulletin 把 "vendor blob isolation" 列入合规指标。短期建议（个人用户）：

- 把 RCS 的"自动接收媒体"关掉（设置 → Messages → Advanced → Auto-download）
- 不依赖 Pixel 做高敏感场景，特别是企业 BYOD

---

## 四、更大的图景：AI 时代的安全 = 重新分配人才

过去 5 年「安全人才」的主流叙事是：red team / pen-tester / bug bounty。这套岗位正在被 AI 大幅自动化。但同一时间，**内核 fuzzer 工程师、formal methods 研究员、firmware reverse engineer 的数量在全球只有几千人**。

这次的三个洞，分别由：

- **Theori**（韩国, ~40 人, 大半是前 KAIST/POSTECH 形式化方法博士）
- **Nightmare-Eclipse**（个人研究者, 公开线下身份未知）
- **Google Project Zero**（~25 人, 几乎全员前 OS / RE 资深工程师）

这些团队的总规模 < 100 人，但他们生产的 0-day 杀伤力远超过 BlackHat 上每年公布的几百份"红队报告"。**当 AI 把红队民主化、白盒审计自动化，安全防御真正的瓶颈，反而回到了 1990 年代的那批人**：会写汇编、读 datasheet、看 SMP race 的人。

CISO 们如果还在按 SOC / EDR / SIEM / SOAR 的旧模板加预算，2027 之后会被这种"底层突袭"打得很惨。

---

## 五、一句话总结

**三个洞、三种栈层、同一种叙事**：LLM 让"找漏洞"这件事的中间地带消失了，剩下的全是 hard problem。安全行业过去 20 年累积的方法论 — 自动化扫描、网络分段、零信任策略 — 在这场重新分布里都是"必要但严重不足"。

下一轮安全竞赛的胜负，不在 LLM 多大，在你团队里还有没有人会读 Intel SDM Volume 3 第 30 章。

---

## 📚 引用来源

1. **Schneier on Security** — *Copy.Fail Linux Vulnerability* (2026-05-12) · [https://www.schneier.com/blog/archives/2026/05/copy-fail-linux-vulnerability.html](https://www.schneier.com/blog/archives/2026/05/copy-fail-linux-vulnerability.html)
2. **Schneier on Security** — *Zero-Day Exploit Against Windows BitLocker* (2026-05-18) · [https://www.schneier.com/blog/archives/2026/05/zero-day-exploit-against-windows-bitlocker.html](https://www.schneier.com/blog/archives/2026/05/zero-day-exploit-against-windows-bitlocker.html)
3. **Google Project Zero** — *A 0-click exploit chain for the Pixel 10: When a Door Closes, a Window Opens* (2026-05-13) · [https://projectzero.google/2026/05/pixel-10-exploit.html](https://projectzero.google/2026/05/pixel-10-exploit.html)
4. **Krebs on Security** — *Patch Tuesday, May 2026 Edition* (2026-05-12) · [https://krebsonsecurity.com/2026/05/patch-tuesday-may-2026-edition/](https://krebsonsecurity.com/2026/05/patch-tuesday-may-2026-edition/)
5. **Schneier on Security** — *OpenAI's GPT-5.5 is as Good as Mythos at Finding Security Vulnerabilities* (2026-05-13) · [https://www.schneier.com/blog/archives/2026/05/openais-gpt-5-5-is-as-good-as-mythos-at-finding-security-vulnerabilities.html](https://www.schneier.com/blog/archives/2026/05/openais-gpt-5-5-is-as-good-as-mythos-at-finding-security-vulnerabilities.html)
6. **Trail of Bits Blog** — *Go fuzzing was missing half the toolkit. We forked the toolchain to fix it.* (2026-05-12) · [https://blog.trailofbits.com/2026/05/12/go-fuzzing-was-missing-half-the-toolkit.-we-forked-the-toolchain-to-fix-it./](https://blog.trailofbits.com/2026/05/12/go-fuzzing-was-missing-half-the-toolkit.-we-forked-the-toolchain-to-fix-it./)

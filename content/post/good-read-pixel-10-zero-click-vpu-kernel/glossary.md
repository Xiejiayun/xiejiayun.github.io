# 术语表 · Glossary
> 配套：**【好文共赏】2 小时审计、5 行代码：Project Zero 在 Pixel 10 VPU 驱动里挖出一个"圣杯级"内核漏洞**

| 英文 | 中文 | 含义 |
|---|---|---|
| 0-click exploit | 零点击攻击 | 不需要用户任何交互即可触发的远程攻击 |
| Project Zero (PZ) | Google Project Zero | Google 的精英漏洞研究团队，0-day 90 天披露政策的发明者 |
| Seth Jenkins | — | 本文作者，Project Zero 核心研究员，Android / Linux kernel 方向 |
| Jann Horn | — | Project Zero 灵魂研究员，Spectre/Meltdown 联合发现人，本案合作者 |
| Tensor G5 | — | Pixel 10 的 SoC 代号，集成 Chips&Media WAVE677DV 视频引擎 |
| VPU | Video Processing Unit | 视频处理单元，本案中指 `/dev/vpu` 内核字符设备 |
| WAVE677DV / WAVE521C | — | Chips&Media 的视频编解码 IP，前者新一代、本案对象；后者上游 Linux V4L2 驱动版本 |
| BigWave | — | Pixel 9 时代的视频加速驱动，Pixel 10 已下线 |
| Dolby UDC | Dolby Unified Decoder | Dolby 提供给 OEM 的 DD/DD+（AC-3/EAC-3）解码二进制 blob |
| AC-3 / EAC-3 | — | Dolby Digital / Dolby Digital Plus 音频格式 |
| EMDF | Extensible Metadata Delivery Format | Dolby 比特流中可扩展元数据格式 |
| syncframe | 同步帧 | DD+ 比特流的独立解码单元，含若干 audio block |
| skipl / skipfld | — | syncframe 内可选元数据字段长度与内容；本案越界源头 |
| CVE-2025-54957 | — | Dolby UDC 越界写漏洞，Project Zero 2026-01 披露 |
| CVE-2025-36934 | — | Pixel 9 BigWave 驱动 LPE 漏洞 |
| mediacodec | — | Android selinux 域，第三方编解码器隔离沙箱 |
| SELinux context | — | 强制访问控制策略上下文，决定一个进程能 open 哪些设备节点 |
| mmap() | — | POSIX 内存映射系统调用，把文件 / 设备映射进虚拟内存 |
| remap_pfn_range() | — | Linux 内核函数，把物理页帧号范围映射到 VMA |
| pfn (Page Frame Number) | 物理页帧号 | 物理地址右移 PAGE_SHIFT |
| VMA | Virtual Memory Area | 进程虚拟内存中的连续区域，包含 `vm_start`, `vm_end`, `vm_page_prot` |
| MMIO | Memory-Mapped I/O | 把外设寄存器映射到 CPU 物理地址空间 |
| pgprot_device() | — | 把页保护位调整为 device memory 属性（uncached, ordered） |
| KASLR | Kernel Address Space Layout Randomization | 内核地址空间随机化 |
| 物理 KASLR | Physical KASLR | 内核物理基地址随机化（Pixel 上未启用） |
| LPE | Local Privilege Escalation | 本地权限提升，从沙箱到 root/kernel |
| RET PAC | Return Pointer Authentication | ARMv8.3 给返回地址签名，替代/补充 `-fstack-protector` |
| `-fstack-protector` | 栈金丝雀 | GCC/Clang 选项，函数序言写入 cookie、返回前校验 |
| `__stack_chk_fail` | — | 栈金丝雀校验失败时调用的函数 |
| GOT / PLT | Global Offset Table / Procedure Linkage Table | 动态链接重定向表，常用攻击落点 |
| V4L2 | Video for Linux v2 | Linux 标准视频驱动框架，提供统一 ioctl / mmap 接口 |
| ioctl | — | 通用设备控制系统调用 |
| Android VRP | Vulnerability Rewards Program | Google 给 Android 漏洞研究者的赏金计划 |
| Patch Severity Rating | 严重程度评级 | Critical / High / Moderate / Low，决定修复优先级与赏金 |
| SPL | Security Patch Level | Android 设备的安全补丁日期标记 |
| 90-day disclosure policy | 90 天披露政策 | Project Zero 的默认时限：报告后 90 天，无论是否修复，公开披露 |
| MTE | Memory Tagging Extension | ARMv8.5 内存标签扩展，弱化 UAF/堆溢出 |
| iMessage / RCS | — | iOS / Android 的富通讯协议；现代 0-click 主战场 |
| Codec blob | 编解码黑盒 | 仅以二进制提供、源码闭源的解码库 |
| in-the-wild (ITW) | 实战中的 | 已被真实攻击者利用过的漏洞 |
| Defeating KASLR by Doing Nothing at All | — | Project Zero 2025-11 文章，揭示 Pixel 物理 KASLR 缺失 |


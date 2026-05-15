# 概念卡片：Tesla Wall Connector anti-downgrade bypass

> 12 张关键概念卡片，配合主文一起阅读。

---

## Card 01 · Pwn2Own Automotive

ZDI（Zero Day Initiative）主办的全球漏洞演示赛在 2024 年新设的"汽车专场"，2025 年 1 月首届在东京举行。目标包括：车载信息娱乐系统（IVI）、ECU 控制器、Tesla Wall Connector 等。**Synacktiv 在该赛上拿下了 Wall Connector**，这也是本文 Part 1 / Part 2 系列的来源。

> 关键意义：把"汽车攻击面"正式拉进职业漏洞研究的主战场。

---

## Card 02 · Tesla Wall Connector Gen 3

Tesla 出品的家用 / 半商用 EV 充电桩。AW-CU300 主控芯片，flash 内布置经典的 A/B 双 slot 固件、partition table、bootloader（`boot2`）。**最特别的能力**：可通过充电线（J1772 接口），由车辆作为"updater"对充电桩进行 OTA 固件升级。

---

## Card 03 · UDS（Unified Diagnostic Services / ISO 14229）

汽车 ECU 通用的诊断协议。本文涉及的关键 routine ID：

| Routine | 作用 |
|---|---|
| `0xFF00` | prepare_passive_slot：擦掉 passive slot |
| `0x201` | switch_to_new_firmware：校验镜像 + 翻转分区表 |
| `0x202` | reboot |

Tesla 私有扩展用了 Security Access Level 5（XOR-`0x35` 算法）作为认证。

---

## Card 04 · SWCAN（Single-Wire CAN）

GMW3089 规范下的单线 CAN 总线，常用于车辆低速诊断 / 唤醒。本文里：充电桩通过充电线的 **Control Pilot** 与车辆做 SWCAN 通信，**33.3 kbps** 速率，PWM 调制。这个低带宽决定了攻击需要约 30 分钟才能传完一个固件镜像。

---

## Card 05 · A/B Slot 双分区固件

OTA 工程的标准模板：

- `active` slot 正在运行。
- `passive` slot 是升级目标。
- 升级成功后，通过 partition table 的 **`gen_level`** 翻转 active / passive 角色。
- 失败时 active 不变，保证设备可启动。

本文的关键见解：**物理 slot 是否被擦** 与 **它是否被 bootloader 选中** 是两个独立动作。Berard 利用的就是这个解耦。

---

## Card 06 · `gen_level` & 分区表

`partition_table` 是 flash 上一个 4 KiB 的元数据区域，每个 slot 条目带一个 `gen_level` 整数。`part_write_layout()` 唯一的副作用是：

```c
v3->gen_level = v4->gen_level + 1;  // 让目标 slot 的 gen_level 比对方大
part_erase(...);
flash_write(...);  // 重写整个分区表
```

`boot2` 启动时挑 `gen_level` 最高的 slot 跳进去。**它不看 ratchet，不看 active/passive 状态，只看这个数。**

---

## Card 07 · `g_boot_flags` 与 passive 选择

`g_boot_flags` 在系统启动一次性写入，反映"我们从哪个物理 slot 启动"。整个 UDS 会话生命周期里 **它永远不变**。

```c
if ((g_boot_flags & 3) != 0)    // 从 slot 1 启动？
    f2 = f1;                    // 那 slot 0 是 passive
```

这意味着：**在一个会话内，物理 passive slot 是固定的。两次连续 `0xFF00` 会反复擦同一块物理 flash。**

---

## Card 08 · PSM（Persistent Storage Manager）

设备里的"小型 NVRAM" 子系统，专门存放需要跨重启保持的状态量。anti-downgrade 的 `current_ratchet` 就存在这里。每次成功升级到一个更高 ratchet 的镜像时，`current_ratchet` 被 PSM 写大。

PSM 自身没有任何回滚机制，但**本文的旁路完全不写 PSM**——`current_ratchet` 仍然停在 24.44.3 对应的值，与最终运行的是 0.8.58 形成了"幻影一致性"。

---

## Card 09 · Security Ratchet（VRS2）

固件镜像 segment 表里新增的描述符：

```
'NSRV' (VRSN) → major.minor
'2SRV' (VRS2) → ratchet byte
```

`verify_firmware_segments_platform()` 解析这个字段，与 PSM 比较：

```c
if (current_ratchet <= firmware_ratchet) return 0;  // accepted
else log("Security ratchet downgrade prevented");
```

这是一种 **anti-rollback** 模式，业界常见的反降级实现。要害是它运行在哪一层。

---

## Card 10 · Bootloader（`boot2`）信任锚

`boot2` 出厂烧在 flash 固定地址，**Tesla 的 OTA 从不下发新 bootloader**。它会做：

- 检查 `SBFH` 魔术头。
- 检查每个 segment 的 CRC32。
- 用 keystore 里的 RSA 公钥校验签名。

但它**不解析 VRSN / VRS2，不检查 ratchet，没有 secure boot**。在嵌入式安全里，这意味着 bootloader 不是"完整 trust anchor"，它把"哪个版本是合法的"这个判断委托给了上层更新器。

---

## Card 11 · 攻击编排（一句话版）

```
0xFF00 → 写新固件 → 0x201   # 让分区表升级 gen_level
0xFF00（同 slot 再擦）       # 内容没了 但 layout 还指向这里
写旧固件（合法签名 RSA ✓）
0x202                       # 直接重启 跳过 0x201
```

总时长 ~30 分钟（两份固件，SWCAN 33.3 kbps）。

---

## Card 12 · 修复策略（Defense in Depth）

补丁应同时具备三个属性：

| 属性 | 含义 | 24.44.3 的状态 |
|---|---|---|
| Completeness | 覆盖所有可达路径 | ❌ 漏掉 0xFF00 二次擦除路径 |
| Invariance | 任何上下文中防御都成立 | ❌ 只在 0x201 内生效 |
| Persistence | 跨重启/会话 | ✅（PSM 持久化） |

推荐修复：
1. **bootloader 也检查 ratchet**（最干净）。
2. **0xFF00 擦内容时一并失效 layout**（最小改动）。
3. **0x201 成功后强制重启 / 拒绝同会话二次更新**（协议层）。

Tesla 实际的修复内容未公开。

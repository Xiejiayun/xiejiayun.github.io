---
title: "Signal 加密被绕过的真相：iPhone 通知数据库才是侦查机关的金矿"
description: "FBI 从 iPhone 通知数据库提取已删除 Signal 消息的事件，揭穿了端到端加密一劳永逸的幻觉。本文拆解 iOS 通知栈的取证盲区、运营商与设备协同泄露面，以及隐私工程的真正护城河。"
date: 2026-05-01
slug: "iphone-notification-forensics-signal-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 隐私
    - 取证
    - iOS
    - Signal
    - 端到端加密
    - 移动安全
draft: false
---

## 当 E2EE 不再等于"安全"

2026 年初，Bruce Schneier 在博客上转载了一份联邦法庭文件：FBI 在一起调查中，从一台被解锁的 iPhone 上**提取出了用户已经"删除"的 Signal 消息**——而 Signal 服务端从未存储过这些消息，也没有任何后门。

很多读者第一反应是：是不是 Signal 被攻破了？答案令人沮丧地无聊：**不是。被攻破的不是密码学，是 iOS 的通知子系统。**

> 端到端加密保护的是消息从 A 到 B 的传输与服务端持久化，但它从来没有承诺过**消息抵达端点之后的命运**。当一条消息变成 Notification Center 里的横幅、Lock Screen 上的预览、CallKit/UNNotificationServiceExtension 的解密缓存时，它就重新回到了"明文+持久化"的世界。

这件事比"又一个隐私事件"严重得多。它暴露了一个被整个隐私工程社区集体回避的盲区：**端点上的"系统级辅助功能"，正在系统性地抵消密码学带来的所有进步。**

本文不打算复述新闻，而是拆三件事：iOS 通知数据库到底存了什么、为什么这是一个**结构性**而非偶然的泄漏，以及对真正在意隐私的产品和用户来说，有没有可行的对抗路径。

---

## 一、iOS 通知数据库的真实结构

iOS 上每条推送通知，都会经过这条链路：

```
APNs 推送 → UserNotifications 框架 → NotificationServiceExtension 解密
        → SpringBoard 显示 → DuetExpertCenter / CoreDuet 记录
        → biome / knowledgeC.db / DuetExpert 持久化
```

关键问题出在最后两步。从 iOS 15 开始，Apple 把"建议"、"专注模式"、"屏幕使用时间"等功能统一放在 Duet/Biome 框架下。这些框架会**默认记录所有通知元数据，并在大量场景下记录通知正文**，主要数据库包括：

| 数据库/路径 | 记录内容 | 默认保留 |
|-------------|----------|----------|
| `biome/streams/public/Notification/Publisher` | 通知发布事件，含 App、bundle id、时间戳 | 30 天起 |
| `biome/streams/restricted/Notification/Usage` | 用户对通知的交互（点击/清除/忽略） | 30 天起 |
| `Library/DuetExpert/People*.db` | 通话/消息联系人共现统计 | 永久 |
| `knowledgeC.db`（已弱化但仍存在） | App 使用、通知交互 | 数月 |
| `Library/SpringBoard/PushStore/*.pushstore` | 已展示通知的完整 plist，含 alert body | 直到清除 |

注意最后一项 `pushstore`：这是一个 binary plist，**默认不加密在用户分区**，即使用户从 UI 上滑掉了通知，文件不会立刻被覆盖。在 BFU（Before First Unlock）状态下文件受 Data Protection Class A 保护，但**一旦设备被解锁过一次（AFU），所有取证工具如 Cellebrite Premium、Magnet GrayKey 都能 dump 这块区域**。

Signal 消息为什么会出现在这里？因为 Signal 在 iOS 上使用了 `UNNotificationServiceExtension`：APNs 收到的密文 push 进入扩展，扩展用 keychain 里的密钥解密，然后把明文写回 `UNMutableNotificationContent`，交给系统显示。**这一刻，明文进入了 SpringBoard 的进程空间，并被 PushStore 持久化。**

Signal 此后无论怎么"删除"会话，删的都是它自己的 SQLite 数据库。**Apple 的 PushStore 是另一份镜像，不归 Signal 管。**

## 二、这是结构性问题，不是 bug

很多人以为 Apple 会"修一下"。不会。原因有三：

**1. 业务逻辑依赖。** Siri 建议、专注模式、Live Activities、CallKit 历史，整套"智能 OS"都建立在通知历史的可查询索引上。Apple Intelligence 上线后，这种依赖只会**指数级加深**——本地大模型需要历史上下文来做"重写"、"总结"、"建议回复"。

**2. 法律与监管激励反向。** 美国 CALEA、英国 IPA、欧盟 ProtectEU 草案都在朝同一个方向施压：要求平台保留**可由合法程序访问的端点元数据**。Apple 在 ADP（Advanced Data Protection）开启时已经放弃了 iCloud 上对通知历史的端到端加密承诺，本地端的 PushStore 就更没有动力封死。

**3. 模型隐喻错位。** E2EE 的威胁模型假设"端点是可信的"。但现代 iPhone 的端点同时跑着：用户 App、系统进程、Apple 智能服务、运营商 IMS 客户端、企业 MDM。**端点早已不是单一信任域。**

这意味着我们必须放弃一个流行的口号：**"用 Signal 就安全了"。**真正准确的说法是："用 Signal，意味着 Signal 的服务器和传输链路上的对手拿不到你的明文，**仅此而已**。"

## 三、取证侧的格局正在变化

过去十年取证工具的演进，可以被画成一个倒挂的剪刀差：

```
难度 ↑
        密码学攻击  ━━━━━━━━━━━━━━━━━ (基本不可行)
                  ╲
                    ╲
                      ╲
                        ━━━━━━━━━━ 端点辅助数据采集 (越来越容易)
难度 ↓
        2015 ─────────────────────────────────── 2026
```

从 2020 年起，Cellebrite、MSAB、Oxygen Forensics 的 release notes 里，新增解析器**几乎全部集中在 OS 辅助数据库**：knowledgeC、biome、CacheDelete、Spotlight `CoreSpotlight`、Apple Intelligence 的 `GenerativeFunctionsInstrumentation`。它们不再追求"破解 WhatsApp"——直接抓 OS 帮你保存的副本就够了。

GrayKey 在 2025 年底的版本已经能在 AFU 状态下，把 PushStore 与 biome stream 关联，**重建一条带时间戳的"对话流"，并标注哪些消息已被用户在 App 内删除**。也就是说，删除行为本身现在成了一个**取证信号**。

这件事对企业安全也有外溢影响。BYOD 场景下，公司 MDM 看不到这些数据库，但任何**物理获得设备**的对手都看得到。一台被海关扣押 30 分钟的高管手机，可能比任何 Phishing 都泄露得更彻底。

## 四、真正可行的对抗路径

我对很多"高级隐私建议"持怀疑态度——大多数会显著降低可用性，最后被用户自己关掉。下面这份清单是我认为**收益/代价比合理**的：

**对个人用户：**

1. **关掉锁屏预览。** 设置 → 通知 → 显示预览 → 锁定时不显示。这一步阻断了 PushStore 写入完整正文的最常见路径。Signal 的应用内设置里也有独立开关。
2. **对真正敏感的对话，使用 Signal 的"Disappearing Messages" + 对方也启用通知预览隐藏**。否则你的努力被对方设备一键作废。
3. **跨境出行前做一次"冷启动"**：完全关机 → 不输密码登机。BFU 状态下 PushStore 不可读。落地后再开机。
4. **不要相信"飞行模式 + 删除"**。删除只动 App 自己的库。

**对产品工程师：**

1. **重新审视 Notification Service Extension 的设计**。如果可以，让通知**只显示 "你有一条新消息"**，正文留在 App 内打开后再加载。Signal 已经支持这种模式但默认未启用，是个产品决策错误。
2. **在 entitlements 中显式声明 `com.apple.developer.usernotifications.filtering`** 但**主动不做内容预览**，这是当前 iOS 框架下能做到的最小化。
3. **教育用户**比"加更多加密"更重要。隐私 UX 的下一个十年是**威胁模型透明化**，而不是堆密码学。

**对监管与立法者**（虽然他们大概率不会读这里）：

E2EE 的合规辩论应该转向**端点取证治理**。今天的局面是：服务商被要求做 lawful access 而拒绝，但端点数据被默默采集且无任何司法监督门槛。这是个**逆向选择**——越是认真做加密的服务越被监管盯，而真正泄漏发生在监管视野之外。

## 四点五、Android 一侧并不更安全

很多 iPhone 用户会下意识觉得"Android 太碎片化、肯定更糟"，反过来 Android 用户也会觉得"我有 GrapheneOS、有更细的权限可以扛"。两边都过度乐观。

Android 的等价问题在 `NotificationManagerService` 与各厂商定制的"通知历史"功能（小米、华为、三星、谷歌 Pixel 都有）。Pixel 的 `NotificationHistory` 默认开启，存放路径在 `/data/system_ce/<userid>/notification_history`，**SQLite 明文**，未加密。任何拿到 root 或解锁 bootloader 的取证工具都可以一次性 dump。MIUI / HyperOS 的"通知历史"是云端同步的，问题更严重——你的消息预览跟着小米账号走，遇到帐号被司法调取或者撞库，全部一起泄漏。

GrapheneOS 在这件事上做得最干净——它彻底禁用了 Google Notification History，且用 Storage Scopes 限制取证 App 的访问。但即便是 GrapheneOS，**只要 Signal 显示了通知预览，通知本身就在 SystemUI 进程的内存里被处理过一次**，物理取证仍然有提取的可能性。

结论是：**没有任何一个移动 OS 在通知层是真正干净的**。这是平台业务逻辑与用户隐私之间的结构性张力，不是某家厂商的工程偷懒。

---

## 五、结语：加密不是终点，是起点

把"用 Signal"等同于"安全"的人，本质上和当年觉得"用 HTTPS 就够了"的人犯了同一个错——**只看了威胁模型最容易理解的那一面**。

E2EE 解决的是**链路与服务端**的对手。端点的对手——无论是物理取证、OS 厂商的辅助服务、还是设备上跑着的另一个 App——是另一个完全独立的威胁面。承认这一点，远比再发明一种新的加密协议有用。

这次 FBI 案件最大的价值，在于把这个长期被回避的真相**钉在了法庭文件上**。隐私工程社区如果还把"端到端"当成营销口号挂在首页，而不去解决端点的明文持久化，那么下一次曝光，只会更尴尬。

---

### 参考资料

- Bruce Schneier, *FBI Extracts Deleted Signal Messages from iPhone Notification Database*, Schneier on Security, 2026: <https://www.schneier.com/blog/>
- Apple, *UserNotifications Framework Reference & PushStore Data Protection*, Apple Developer Documentation: <https://developer.apple.com/documentation/usernotifications>
- Cellebrite, *Premium Release Notes – iOS Artifact Coverage 2025/2026*: <https://cellebrite.com/en/cellebrite-premium/>
- Sarah Edwards (mac4n6), *Knowledge is Power: Using the macOS/iOS knowledgeC.db & biome streams*: <https://www.mac4n6.com/blog>
- Signal Foundation, *Notification Service Extension and message preview behavior*: <https://support.signal.org/>

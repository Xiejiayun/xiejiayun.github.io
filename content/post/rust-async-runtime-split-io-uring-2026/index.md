---
title: "Rust 异步生态的分裂与重聚：io_uring、Tokio 单极、和一个迟到的标准"
description: "Rust async 是当代系统编程最成功也最分裂的实验。Tokio 事实上垄断、async-std 退场、glommio/monoio 用 io_uring 另起炉灶，而标准库的 Future 半成品躺了七年。本文剖析这场分裂背后的工程取舍与未来路径。"
date: 2026-05-04
slug: "rust-async-runtime-split-io-uring-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Rust
    - 异步运行时
    - io_uring
    - 开源
draft: false
---

## 一、一种"成功"的语言里最尴尬的部分

Rust 在 2026 年已经是 Linux kernel、Windows 内核组件、Android 系统服务、各大云厂数据面的核心语言之一。这门语言几乎没有失败的子领域——除了 **async**。

async/.await 语法 2019 年稳定，七年之后，标准库里仍然只有 `Future` trait 和 `Waker` 这点最小骨架，**没有官方运行时、没有官方 IO trait、没有官方任务派发**。事实上的标准是 Tokio，但它是一家公司控制的开源项目；其他运行时(async-std 已死、smol、glommio、monoio、embassy)各自占据小生态位，互相不兼容。这是 Rust 演进史上最严重的"半成品"。

## 二、为什么会变成这样：技术原罪

Rust 的 `Future` 设计是 **poll-based** 的：执行器主动调用 `poll`，未就绪时返回 Pending 并保存 waker。这个设计的好处是零成本、可在 no_std 嵌入式跑；坏处是：

- IO trait(`AsyncRead` / `AsyncWrite`) 和具体运行时强绑定。Tokio 的 `AsyncRead` 和 futures 库的不一样，至今没统一。
- 取消语义是"drop the future"，看似优雅，实际上对持有内核资源(尤其是 io_uring 的 in-flight SQE)的 future 是噩梦。
- Pin 的引入解决了自引用 future 的内存安全，代价是 API 复杂度爆炸，普通开发者三年都搞不清楚。

加上 Mozilla 退场、Rust 基金会治理重组，标准库异步演进直接停摆五年。这段空窗期就是 Tokio 完成事实垄断的窗口。

## 三、io_uring 重新洗牌：Linux 内核的礼物没人接得住

2019 年 Jens Axboe 在 Linux 5.1 引入 io_uring，它和 Rust async 是天作之合：

- 提交-完成两个无锁环形队列，天然 batch 化
- 真正的异步文件 IO(epoll 长期做不到)
- 可与 eBPF、network zero-copy、registered buffer 组合

| 维度 | epoll | io_uring |
|------|-------|----------|
| 文件 IO | 阻塞 | 异步 |
| 系统调用次数 | 高 | 单次 enter 提交多个 |
| 缓冲区注册 | 无 | 支持，0-copy |
| 取消 | 复杂 | 原生 IORING_OP_ASYNC_CANCEL |
| 模型 | readiness | completion |

但 io_uring 是 **completion-based**：你提交一个 SQE，内核完成后给你 CQE。Rust 的 poll-based future 与之根本不匹配。具体冲突点：

1. 如果用户 drop 了一个 in-flight read future，对应的 SQE 仍在内核里，它会写入用户提供的缓冲区——而那个缓冲区可能已经被 free。这是 use-after-free。
2. 解决方案要么是"owned buffer"(每次 IO 把 buffer 所有权移交内核，完成后归还)，要么是"buffer pool 注册"(由运行时管理生命周期)。两种方案都让 IO API 变得不像 std，迁移成本高。

Tokio 在 io_uring 上的态度长期暧昧：tokio-uring crate 存在但被刻意做成实验性，因为 Tokio 主仓库不愿意为 Linux 独有特性破坏跨平台 API。这就给 monoio(字节跳动)、glommio(原 ScyllaDB，现 Datadog)留下了空间——它们干脆放弃 epoll，专做 io_uring，性能在网络密集场景能比 Tokio 高 30-50%。

## 四、生态分裂的真实代价

```
   ┌──────────────────────────────────────────┐
   │            std::future::Future           │
   │      (只有 trait, 没有 runtime)          │
   └──────────────────┬───────────────────────┘
                      │
       ┌──────────────┼────────────────┬─────────────┐
       ▼              ▼                ▼             ▼
   Tokio (M:N)    smol (M:N)     monoio (1:1)   embassy
   epoll          epoll          io_uring        no_std
       │              │                │             │
   Hyper / Axum   Async-std 遗产   字节内部       嵌入式
   Tonic          (已弃)          少数开源        电池供电
```

每个运行时有自己的 IO trait、自己的 timer、自己的 channel。一个 crate 想"运行时无关"，要么放弃 IO 只做 CPU-bound，要么用 `async-trait` + 一堆 feature flag，编译时间爆炸。这是 Rust 异步生态最大的隐性成本：**库作者要么绑定 Tokio，要么牺牲性能与可用性**。

实际后果：90% 的网络库直接 hardcode tokio。任何"异构运行时"的努力(如 async-executor 的尝试)在生态层面都失败了。

## 五、2026 的转机：Async Working Group 的回归

2025 年下半年，Rust 项目重启了 Async Working Group，目标是 2026-2027 把以下东西塞进标准库：

- `AsyncIterator`(已 nightly)
- 标准化的 `AsyncRead` / `AsyncWrite`(还在 RFC)
- 异步 Drop(关键，对 io_uring 和 RAII 资源至关重要)
- Send-bound 推断改进，让 `async fn in trait` 不再痛苦

异步 Drop 是最难的，它涉及到"析构函数能不能 .await"。这个特性如果落地，io_uring 风格的资源管理才能真正在 stable Rust 里优雅写出来。但它需要语言层改动，乐观估计 2027 年才稳定。

## 六、几个判断

1. **Tokio 不会被替代**，但会逐渐让出"高性能 Linux 服务器"这一块给 monoio/glommio。Tokio 的护城河在跨平台和生态广度，而不是绝对性能。
2. **2027 年会有"官方推荐运行时"出现**，但形式上不是钦定，而是标准库提供足够多的 trait + 一个 minimal executor，让 Tokio 可以无缝扮演"参考实现"。
3. **io_uring 在用户态会输给 spdk/dpdk 吗？** 不会。云厂商内部的高性能存储/网络栈仍是 spdk/dpdk，但通用应用层 io_uring 会成为默认。
4. **WASM 组件模型会让 Rust async 再分裂一次**——WASI Preview 3 的 async 能力进来后，Web 生态又会有自己一套 runtime 假设。

## 七、结语

Rust async 是一个反例：极强的语言、极强的社区、极弱的标准化决心，结果是七年的工程债务。它告诉我们一件事：**语言设计不能只靠"零成本抽象"理想主义，IO 模型这种事最终需要语言项目方下场拍板**。Go 的 goroutine 早就赢了便利性，Rust 选择了正确的方向但走了最痛苦的路。希望 2027 是异步 Rust 终于能"开箱即用"的一年。

---

### 参考资料

- Rust Async Working Group, "Async Vision Doc & Roadmap 2026" — https://rust-lang.github.io/wg-async/
- Jens Axboe, "Efficient IO with io_uring" — https://kernel.dk/io_uring.pdf
- Glommio Project — https://github.com/DataDog/glommio
- Bytedance Monoio — https://github.com/bytedance/monoio
- Without.Boats, "A Four-Year Plan for Async Rust" — https://without.boats/blog/

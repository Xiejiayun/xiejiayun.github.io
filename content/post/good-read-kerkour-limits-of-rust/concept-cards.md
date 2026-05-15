# 概念卡片：Kerkour《The Limits of Rust》关键 12 张

> 阅读建议：每张卡片背面记录一个"我所在团队的现状"再回头看主文。

---

## Card 1 · async runtime fragmentation（异步运行时碎片化）

**含义**：Rust 的 async/await 语法是稳定的，但 executor（事件循环）不在标准库里。tokio、async-std、smol、glommio、monoio 等多家 runtime 各自实现 I/O 抽象，互相不兼容。
**关键事实**：
- tokio 占社区 95% 以上事实份额，但仍不是"官方"标准；
- 写一个跨 runtime 的库往往需要 sans-IO 设计模式，或者干脆 pin 死 tokio。
**验证点**：在你的 `Cargo.toml` 里搜 `tokio = "1.*"`，如果有多于一个版本，说明子依赖在拖你。

---

## Card 2 · event loop blocking（事件循环阻塞）

**含义**：在 async fn 中调用同步阻塞操作（`std::fs::read`, `std::sync::Mutex::lock` 持有时间长, CPU 密集循环），会卡住 tokio worker 线程，p99 延迟剧烈抖动。
**关键事实**：Kerkour 原话："I don't remember any project with more than a few thousands lines of code that DIDN'T had at least one occurence of blocking the event loop."
**验证点**：用 `tokio-console` 跑 1 小时，看有没有 task busy >50ms 的事件。

---

## Card 3 · Send + Sync × lifetime × generics 的化学反应

**含义**：async fn 返回的是匿名 Future 类型，跨 await 点存活的引用会被 borrow checker 检查 Send + Sync + lifetime 三重约束。
**痛点**：一个原本同步的函数改成 async，可能需要在所有调用方加 `'static` 或 `Arc`，引发雪崩重构。
**验证点**：尝试在你最大的 service 上把一个核心 sync trait 改成 async trait，看编译错误数量。

---

## Card 4 · edition churn（版本腐化）

**含义**：Rust 每 6 周一个 release（自 2015 起 70+ 版本），每 3 年一个 edition（2015/2018/2021/2024/...）。crate 作者跟进速度不一，导致依赖矩阵长期处于"几个版本同时存在"。
**关键事实**：Go 同期 12 个 release、Python 5 个、Node.js LTS 6 个。
**验证点**：一个放置 3 年的 Rust 项目重新 `cargo build`，统计需要修复的错误数。

---

## Card 5 · anemic std lib（贫血标准库）

**含义**：Rust 故意保持 stdlib 很小，把 datetime、crypto、HTTP、TLS、序列化全部丢给社区。设计哲学是避免 Python 2.7 的 stdlib 腐烂悲剧。
**代价**：审计预算被分散到 1000 个 crate 作者头上，复利失败。Go stdlib 在这点上恰好相反。
**验证点**：你的 `Cargo.lock` 里有几个不同的 crypto 实现？aws-lc-rs / ring / boring / rustcrypto 出现几次？

---

## Card 6 · FIPS validation gap

**含义**：FIPS 140-2/3 是美国联邦政府认证的密码模块标准。Rust 生态里**只有 aws-lc-rs 和 boring 有 FIPS-validated mode**。
**影响**：如果你的产品需要进美国政府/医疗/金融客户，你的 Rust 项目实际只能用其中一个 crypto 库；与 Cloudflare/AWS 自家用法严重错位。
**验证点**：你的项目能否在合规 review 时回答"我们用了哪个 FIPS-validated 模块"。

---

## Card 7 · cross-platform core（跨平台共享核）

**含义**：写一份核心 Rust 库，分别编译成 iOS Framework / Android AAR / WASM / Linux daemon / Windows DLL。
**典型案例**：WhatsApp E2E 加密层、Signal protocol、Proton drive 客户端、1Password 加密层。
**Rust 的独占优势**：唯一一个能同时满足"5 平台编译 + 内存安全 + 包管理 + 性能可控"的语言。
**适用判断**：如果你不在做 client-side SDK，这个优势对你无关。

---

## Card 8 · removing the runtime（RFC 0230）

**含义**：2014 年 Rust 团队接受 RFC 0230，**主动从标准库砍掉了 green thread / runtime**，理由是"语言不该绑定一种调度策略"。这是后来 async/await fragmentation 的历史起点。
**关键事实**：Go 走了相反路径——绑定 goroutine 进 runtime，换来了简单性，损失了可扩展性。
**意义**：理解这条历史决定，能让你不再问"Rust 为什么不抄 Go 的并发模型"。

---

## Card 9 · linear types × async

**含义**：Rust 的 ownership 是一种弱化的 linear type system，每个值只能被消费一次。
**与 async 的冲突**：async 让"值横跨多个 await 点"变得普遍，linear type 的"消费即销毁"语义需要复杂的 Pin/Future 抽象来保持。
**学术深读**：Aria Beingessner《The Pain of Real Linear Types in Rust》。
**验证点**：你能向团队解释 `Pin<Box<dyn Future<Output = T> + Send>>` 的每一层吗？

---

## Card 10 · crate supply chain attack surface

**含义**：cargo install 一个工具，可能拉取几百个间接依赖。每个 crate 作者都是潜在的供应链注入点。
**类比**：与 npm 同等量级，但 Rust 社区还没经历 TanStack / left-pad 这种级别的实战教训。
**Kerkour 自己专门写过**："Supply chain nightmare: How Rust will be attacked"。
**验证点**：`cargo audit` + `cargo vet` 是否在 CI 流水线里。

---

## Card 11 · Pingora / Firecracker 案例（不要简单复制）

**含义**：Cloudflare Pingora 替换 nginx、AWS Firecracker 替换 KVM userspace，都是 Rust 替换 C 的典范。
**陷阱**：这两家有 30+ Rust 专职工程师、专属审计预算、运维替换窗口。
**Kerkour 的判断**："这些是 30 万吨油轮，你的 30 人小船不该照同样的航线走。"
**验证点**：如果你团队没有 5 个 senior Rust dev，"复制 Pingora 路径"几乎肯定亏。

---

## Card 12 · AI-agent friendly language（隐藏维度）

**含义**：AI agent（Claude Code、Codex、GPT 5.5 等）生成代码的可靠度，与"语言 + stdlib"作为稳态平台的引力强相关。Go stdlib 不动，AI 写得稳；Rust 生态漂移，AI 选 crate 不稳。
**意义**：2026 年开始，"AI agent 的一次性通过率"会成为语言选型新维度。
**Kerkour 暗示**："If your team (of Humans or AI agents) already have extensive experience with Rust..."
**验证点**：让你团队的 AI assistant 实现同一个 HTTP+TLS+JSON 任务，分别用 Go 和 Rust，看哪边 first-pass 通过更接近线上代码风格。

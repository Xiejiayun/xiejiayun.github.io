# 英中术语表 · Kerkour《The Limits of Rust》

> 选型评审、安全审计、团队培训时建议先对齐这 30 条。

| 英文术语 | 中文译法 | 一句解释 |
|---------|---------|----------|
| async runtime | 异步运行时 | Rust 不在 stdlib 里提供，需要选 tokio / async-std / smol 等第三方库 |
| event loop | 事件循环 | 负责调度 Future 的核心组件，被同步阻塞会拖垮所有任务 |
| Future trait | Future 抽象 | Rust 异步编程的基础抽象，由编译器生成状态机 |
| async/await syntax | 异步语法糖 | 在 sync 函数语法上加 async 关键字，编译器展开为 state machine |
| executor | 执行器 | 真正驱动 Future 运行的组件，tokio runtime 就是一种 executor |
| reactor | 反应器 | 监听 I/O 事件的底层组件（epoll/kqueue/io_uring） |
| sans-IO pattern | 无 IO 模式 | 把协议状态机和 IO 分离，让库不绑定具体 runtime |
| Send trait | 可跨线程发送 | 类型可以安全地在线程间转移所有权 |
| Sync trait | 可跨线程共享 | 类型的引用可以被多线程同时读取 |
| ownership | 所有权 | Rust 的核心机制，确保内存安全且无 GC |
| borrow checker | 借用检查器 | 编译期验证所有权与生命周期规则 |
| lifetime annotation | 生命周期标注 | 显式告诉编译器引用存活的范围 |
| pin / Pin<T> | 固定 / 钉住 | 确保某个值在内存中地址不变，async self-referential 必需 |
| zero-cost abstraction | 零成本抽象 | 高层抽象编译出来不比手写 C 慢 |
| edition (2015/2018/2021/2024) | 版本年 | Rust 每 3 年发布一次的语言切片，允许同一 crate 内不同 edition 互操作 |
| toolchain | 工具链 | rustc + cargo + rustfmt + clippy 的整套版本 |
| crate | 包 / crate | Rust 的复用单位，对应 npm package / Go module |
| crates.io | Rust 官方包仓库 | 类似 npmjs.com，但治理较弱 |
| supply chain attack | 供应链攻击 | 通过劫持依赖 crate 注入恶意代码 |
| anemic standard library | 贫血标准库 | stdlib 故意保持小，把 datetime/crypto/HTTP 推给社区 |
| extended standard library | 扩展标准库 | Kerkour 提议的解决方案：vendor 一批关键 crate 进官方维护 |
| churn / project decay | 抖动 / 项目腐化 | 因为依赖频繁迭代，老项目维护成本不断上升 |
| FIPS-validated mode | FIPS 认证模式 | 美国联邦密码模块认证，金融/政府客户硬性要求 |
| ring (crate) | Rust 著名 crypto 库 | 基于 BoringSSL，社区分裂的代表 |
| aws-lc-rs | AWS 推的 crypto crate | 有 FIPS-validated mode |
| boring (crate) | Cloudflare fork 的 BoringSSL Rust binding | 有 FIPS-validated mode |
| RustCrypto | 纯 Rust 实现的 crypto crate 集合 | 学术正确，但没有 FIPS 认证 |
| cross-platform core | 跨平台共享内核 | 一份 Rust 编译到 iOS/Android/WASM/Linux，WhatsApp/Signal 典型用法 |
| ESP32-C / RISC-V | 嵌入式微控制器 | Espressif 提供官方 Rust HAL，是 Rust 嵌入式最佳起点 |
| HAL (Hardware Abstraction Layer) | 硬件抽象层 | 把寄存器细节屏蔽给上层，Rust 嵌入式生态成熟度的核心指标 |
| Firecracker | AWS microVM | Rust 写的 KVM userspace，秒级启动容器替代品 |
| Pingora | Cloudflare 自研 web proxy | Rust 替换 nginx，2024 开源 |
| Pingora-like trap | 复制陷阱 | 中型团队照搬 Cloudflare Rust 路径但缺人/缺审计预算的失败模式 |
| green thread | 绿色线程 | 由 runtime 而非 OS 管理的轻量线程；Rust RFC 0230 砍掉了 |
| linear types | 线性类型 | 每个值只能消费一次的类型系统；Rust ownership 是其弱化版 |
| sans-IO | 无 IO 协议状态机 | 与 runtime 解耦的库设计模式，QUIC/HTTP/3 库常用 |
| AI-agent friendly | AI 友好语言 | 由 stdlib 稳定性 + 生态低碎片化共同决定，AI 生成代码可预测性更高 |
| memory safety | 内存安全 | 无 use-after-free / data race / buffer overflow，Rust 编译期保证 |
| zero-copy | 零拷贝 | 数据在不同 buffer 间不实际复制，Rust 通过 borrow 实现 |

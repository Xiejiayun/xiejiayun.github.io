# 术语表 / Glossary：Turso 关掉 Bug Bounty

| 英文 | 中文 | 简释 |
|---|---|---|
| AI Slop | AI 灌水（俚语） | 由 LLM 自动生成的低质量、表面体面、内容空洞的内容产物 |
| Antithesis | Antithesis（公司名） | 一家提供"云端确定性仿真测试"服务的初创，前 FoundationDB 团队创办 |
| ARGV / Wall-of-text | 长篇辩护 | LLM 被反驳后常见的拖延式长文回应，内容空但格式工整 |
| B-Tree | B 树 | SQLite / Turso 在底层用来组织数据页的平衡多路搜索树 |
| Bug Bounty | 漏洞悬赏计划 | 以现金奖励研究者发现并报告软件缺陷的制度 |
| cgroups (memory) | 内存控制组 | Glauber 在 Linux 内核里写过的早期 memcg 实现 |
| Concurrent Writes | 并发写 | Turso 区别于 SQLite 的核心特性之一 |
| Data Corruption | 数据损坏 | 数据库出现违反内部不变式的状态，无法可靠读出 |
| Deterministic Simulation Testing (DST) | 确定性仿真测试 | 把时钟 / 网络 / 磁盘抽象为确定性事件，用伪随机种子穷举状态组合 |
| Differential Testing | 差分测试 | 用 oracle（参考实现）对比被测系统的输出来发现行为偏差 |
| Em-dash | 长破折号 (—) | LLM 生成文本的高频签名之一 |
| Fault Injection | 故障注入 | 在仿真里主动注入磁盘 / 网络 / 进程崩溃来逼出 bug |
| Forge | 代码托管平台 | GitHub / GitLab / sourcehut 等的统称 |
| Formal Methods | 形式化方法 | 用数学严格证明软件性质的工具集，如 TLA+、Alloy、Lean、P |
| Fuzzer | 模糊测试器 | 自动生成随机或半随机输入来探索程序状态空间的工具 |
| Generator (in DST) | 生成器 | DST 里负责构造测试输入的子系统，其分布决定了能找到哪些 bug |
| Hacktoberfest | Hacktoberfest | DigitalOcean 每年 10 月的 OSS 贡献活动，曾因水 PR 泛滥而被反复改革 |
| MC/DC Coverage | 修正判定覆盖率 | 一种航空级软件测试覆盖率指标，SQLite TH3 号称做到 100% |
| Model Checker | 模型检查器 | 通过系统性遍历状态空间来验证形式化模型性质的工具 |
| OOB (Out-of-bounds) Access | 越界访问 | 程序读写超出已分配内存范围，是 C/C++/unsafe Rust 的常见漏洞 |
| Open Contribution | 开放贡献 | Turso 用以描述自身治理模式的术语，强调任何人可提 PR |
| OSS Governance | 开源治理 | 关于谁能做决策、如何审核贡献、如何分配资源的规则集 |
| Pending Byte | 待定字节 | SQLite 在 1GB 边界插入的一个特殊字节，与文件锁相关 |
| Pwn Request | Pwn 请求（GitHub Actions 反模式） | 使用 `pull_request_target` 让 fork PR 在高信任上下文执行的漏洞 |
| Rewrite-in-Rust (RIIR) | 用 Rust 重写 | 最近几年大量基础设施软件用 Rust 重写的潮流，Turso 是其代表 |
| RLHF | 人类反馈强化学习 | LLM 主流对齐方法，但也会"教会模型写得像专家"而非"做得正确" |
| ScyllaDB | ScyllaDB | Glauber 联创的 C++ 重写版 Cassandra，与 Turso 在精神上同源 |
| Seastar | Seastar 框架 | ScyllaDB 用的 C++ thread-per-core 异步框架，由 Avi Kivity 主导 |
| Singularity | 奇点（本文特指） | LLM 生成 PR 边际成本跌破阈值导致 OSS 维护成本反转的那个时刻 |
| Slop Maker | 灌水制造者 | 本文用以称呼用 LLM 批量产 PR 投赏金计划的攻击者 |
| Sybil Attack | 女巫攻击 | 一个攻击者用多个伪造身份冒充多个独立参与者的攻击 |
| TH3 (Test Harness 3) | SQLite 的私有测试套件 | 闭源的航空级测试工具，是 SQLite 稳定性的核心 |
| TigerBeetle | TigerBeetle | 一家用 DST 做金融账本数据库的公司，与 Antithesis / Turso 同脉 |
| Turso | Turso | 用 Rust 重写 SQLite 的公司与开源项目，Glauber Costa 联创 |
| V4L2 | Video4Linux2 API | Linux 标准视频驱动接口（本文非主线，但出现在 Glauber 相关讨论中） |
| Vouching System | 担保 / 投票认证制 | Turso 一度尝试用来过滤 bot PR 的反作弊机制，未成功 |
| war room | 战情室 | 安全 / 运维事件爆发时的临时跨部门指挥中心 |
| Whack-a-mole | 打地鼠 | 攻击者每次都能用低成本新身份重启的对抗形态 |
| Window of opportunity | 机会窗 | 系统被攻击者发现可利用的状态间隔 |
| Working assumption | 工作假设 | 一项工程实践赖以成立的隐含前提（本文核心讨论对象之一） |

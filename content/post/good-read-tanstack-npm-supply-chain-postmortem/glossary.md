# 术语表：TanStack npm 供应链事件英中对照

> 配套于《【好文共赏】TanStack npm 投毒事件官方复盘》

## A

| 英文 | 中文 | 解释 |
|------|------|------|
| Attestation | 证明 / 出处声明 | npm provenance 系统中，对包发布来源做密码学签名的声明 |
| AWS IMDS (Instance Metadata Service) | AWS 实例元数据服务 | EC2 内可访问的元数据端点，常被恶意脚本用来探测凭证 |

## C

| 英文 | 中文 | 解释 |
|------|------|------|
| C2 (Command & Control) | 命令与控制 | 攻击者用于远程操控被感染机器的基础设施 |
| Cache Poisoning | 缓存投毒 | 让被信任的缓存内容被替换为攻击者控制的内容 |
| Cache Scope | 缓存作用域 | GitHub Actions 中按 branch/ref 划分的缓存隔离单位 |
| Checkout (refs/pull/.../merge) | 检出 PR 合并 ref | 检出 PR 在 base 上合并后的预览代码 |
| CI (Continuous Integration) | 持续集成 | 代码合并前自动运行测试与构建的流程 |
| Credential Harvesting | 凭证收割 | 在受害主机上扫描并外传 API key、token、SSH key 等敏感凭证 |
| CVE | 公共漏洞披露编号 | 用于唯一标识公开披露的安全漏洞 |

## D

| 英文 | 中文 | 解释 |
|------|------|------|
| Deprecation (npm) | 弃用标记 | 在 npm registry 给特定版本打上"不推荐使用"的元数据 |
| DevSecOps | 开发安全运营 | 把安全实践嵌入开发与运维流程 |

## F

| 英文 | 中文 | 解释 |
|------|------|------|
| Fork Network | Fork 网络 | GitHub 同一仓库的所有 fork 与原仓库组成的对象共享网络 |

## G

| 英文 | 中文 | 解释 |
|------|------|------|
| GHA (GitHub Actions) | GitHub 内置 CI 系统 | |
| GHSA | GitHub Security Advisory | GitHub 安全公告 |
| GITHUB_TOKEN | GHA 默认凭证 | workflow 运行期内由 GitHub 分发的短期 token |

## I

| 英文 | 中文 | 解释 |
|------|------|------|
| IOC (Indicator of Compromise) | 入侵指标 | 用于事后取证识别同类攻击的特征字符串/哈希/IP/域名 |
| `id-token: write` | OIDC 写权限 | GHA workflow 允许向 GitHub OIDC 端点 mint token 的权限位 |

## J

| 英文 | 中文 | 解释 |
|------|------|------|
| JWT (JSON Web Token) | OIDC token 的标准载体格式 | |

## L

| 英文 | 中文 | 解释 |
|------|------|------|
| Lifecycle Script | 生命周期脚本 | npm 包的 `preinstall` / `install` / `prepare` 等阶段自动执行的脚本 |
| Lockfile | 锁文件 | `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` 等冻结依赖版本与哈希的文件 |
| LSP (Language Server Protocol) | 语言服务器协议 | 与本文不直接相关，但 rust-analyzer 等 IDE 后端实现 |

## M

| 英文 | 中文 | 解释 |
|------|------|------|
| `maintainer:<user>` (npm search) | npm 注册表按维护者搜索 API | 蠕虫式扩散常用此接口枚举受害人其他包 |
| Memory Extraction | 内存提取 | 通过 `/proc/<pid>/mem` 或类似机制读取目标进程内存 |
| Mint (a token) | 颁发（一个 token） | 由 issuer 签发新 token 的动作 |

## N

| 英文 | 中文 | 解释 |
|------|------|------|
| npm Registry | npm 包注册表 | `registry.npmjs.org` |
| `.npmrc` | npm 配置文件 | 包含 npm token、registry URL 等敏感信息 |

## O

| 英文 | 中文 | 解释 |
|------|------|------|
| OIDC (OpenID Connect) | 身份联邦协议 | npm Trusted Publisher 用它把 GitHub workflow 身份信息传给 npm |
| `optionalDependencies` | 可选依赖 | npm 包字段，安装失败不报错；可指向 git ref，本次攻击载体之一 |
| Orphan Commit | 孤儿提交 | 没有任何分支指向的 commit，可通过哈希拉取 |

## P

| 英文 | 中文 | 解释 |
|------|------|------|
| Postmortem | 事后复盘 | 对事故全过程的根因分析与教训提炼文档 |
| Provenance (SLSA) | 软件出处 | 加密签名的"这个 artifact 是由哪个 workflow 在哪个 commit 上构建出来的"声明 |
| `pull_request` | PR 触发器 | GHA 触发器，跑在 PR 代码上下文，secret 不可用，需首次贡献者批准 |
| `pull_request_target` | PR-Target 触发器 | GHA 触发器，跑在 base 上下文，secret 可用，无需批准——Pwn Request 的根源 |
| Pwn Request | Pwn 请求 | GitHub Security Lab 命名的 `pull_request_target` + checkout fork 攻击模式 |

## R

| 英文 | 中文 | 解释 |
|------|------|------|
| `release.yml` | 发布 workflow | TanStack 配置的、合并到 main 时触发 npm 发布的 workflow |
| Runner.Worker | GHA 运行器主进程 | 实际执行 step 的子进程，OIDC token 在其内存中 |

## S

| 英文 | 中文 | 解释 |
|------|------|------|
| Session/Oxen | 端到端加密 messenger | 本次事件中被滥用为隐蔽数据外传通道 |
| Shai-Hulud | 沙虫 | 来自《沙丘》，社区给这类蠕虫式 npm 攻击的代号 |
| SLSA | 供应链等级框架 | Supply-chain Levels for Software Artifacts |
| Supply Chain Attack | 供应链攻击 | 通过攻击软件构建/分发链路实施的攻击 |

## T

| 英文 | 中文 | 解释 |
|------|------|------|
| Tarball | npm 包压缩文件 | npm registry 实际存储与分发的 `.tgz` 文件 |
| Trusted Publisher | 受信发布者 | npm 2024 推出的 OIDC keyless 发布机制 |
| Trust Boundary | 信任边界 | 系统内不同信任等级区域之间的分界，本次三段攻击都涉及跨边界 |

## U

| 英文 | 中文 | 解释 |
|------|------|------|
| Unpublish (npm) | 撤包 | npm 允许撤回包，但有"有 dependent 时不可撤"政策 |

## V

| 英文 | 中文 | 解释 |
|------|------|------|
| Vault | HashiCorp Vault 凭证管理器 | 本次攻击的凭证收割目标之一 |

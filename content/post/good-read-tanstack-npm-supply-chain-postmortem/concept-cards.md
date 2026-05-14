# 概念卡片：TanStack npm 供应链事件十二张关键概念卡

> 配套于《【好文共赏】TanStack npm 投毒事件官方复盘》

---

## 卡 1：`pull_request_target` 触发器

- **是什么**：GitHub Actions 的一个特殊触发器，与 `pull_request` 区别在于它跑在 **base 分支的上下文**里，可读 secrets、有 write `GITHUB_TOKEN`、且**不需要 first-time-contributor 批准**
- **设计意图**：让 fork PR 上的"加 label / 评论 / 通知 / 安全扫描"等 bot 操作能拿到 secrets 而又不暴露 fork 代码
- **致命使用模式**：`checkout(refs/pull/.../merge) → 跑 fork 代码`——构成 Pwn Request
- **判别 checklist**：workflow 触发器是 `pull_request_target` + 任何一步 checkout fork ref + 任何一步执行 fork 控制的脚本（包括 `npm install` 触发的 lifecycle scripts）

---

## 卡 2：Pwn Request 攻击模式

- **三要素**：`pull_request_target` 触发 + checkout fork code + execute fork code
- **历史案例**：Microsoft Azure、Spinnaker、Argo CD、TanStack
- **GitHub 官方警告时间**：2021 年
- **正确写法**：要在 PR 上跑 fork 代码 → 用 `pull_request` 触发器 + maintainer 手动批准；要给 fork PR 加 label/comment → 用 `pull_request_target` 但**绝不 checkout fork ref**

---

## 卡 3：GitHub Actions Cache Scope

- **scope 隔离规则**：cache 按 ref（branch/PR）分 scope，**但 fork PR 的 cache 写入 base 仓库的 main scope**
- **设计原因**：让 PR 能复用主线的依赖缓存以加速 CI
- **副作用**：fork 控制的代码可以往主线会读取的 cache key 写东西
- **2025-01 GitHub 修补**：禁止 post-job 写 cache（job 结束后不能再 save）
- **本次绕过手段**：把投毒动作搬进 build 期间，让 `actions/cache@v5` 在合法的 post 阶段保存已经被污染的 store

---

## 卡 4：Cache Key 预测攻击

- **场景**：当 `release.yml` 与 `bundle-size.yml` 使用相同的 cache key 模板（如 `${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}`）
- **攻击者动作**：用相同的 lockfile，在 PR 上跑出一个写入这个 key 的 cache entry
- **效果**：下一次 main 分支 `release.yml` 跑起来，restore 到的就是被污染的 cache
- **缓解方案**：发布相关的 workflow **完全禁用 cache**

---

## 卡 5：npm OIDC Trusted Publisher

- **是什么**：npm 在 2024 年推出的 keyless 发布机制——把"GitHub repo X 的 workflow Y 在 branch Z 跑时可发布 package P"作为一组绑定关系登记在 npm 一侧
- **工作流**：workflow 声明 `id-token: write` → Runner 向 GitHub OIDC 端点请求 token → token 包含 workflow 身份声明 → npm 验签后允许发布
- **安全收益**：无长期 secret、token 短期、与 workflow 身份绑定、产生 provenance
- **盲点**：`id-token: write` 是 **workflow 级别**权限——workflow 内任何步骤、任何执行能力都能 mint 这个 token

---

## 卡 6：OIDC Token 内存提取

- **技术路径**：
  1. 找到 Runner.Worker 进程 PID（通过 `/proc/*/cmdline`）
  2. 读 `/proc/<pid>/maps` 找到 heap 区域
  3. 读 `/proc/<pid>/mem` dump 内存
  4. 模式匹配提取 JWT 格式的 OIDC token
- **第一次公开案例**：2025-03 tj-actions/changed-files 事件
- **本次复用**：攻击者**保留原作署名注释**，没有原创

---

## 卡 7：Fork 反取证手法

- **手法**：fork 仓库后**改名**（如 `TanStack/router` → `zblgg/configuration`），让 GitHub 主页的 fork 搜索按"同名 fork"过滤时找不到它
- **网络仍然存在**：fork 关系数据库里依然记录，commit 对象通过 `github:owner/repo#sha` 依然可拉取
- **检测方法**：用 GitHub API 拉 `/repos/{owner}/{repo}/forks` 完整列表，不依赖 UI

---

## 卡 8：Lifecycle Script 投毒载体

- **怎么进入**：`optionalDependencies` 里指向 `github:tanstack/router#<sha>` 的 entry
- **触发时机**：`npm install` / `pnpm install` / `yarn install` → 解析 → 拉 git ref → 执行 `prepare` lifecycle script
- **payload 大小**：~2.3 MB 混淆 JS
- **行为**：harvest credentials（AWS IMDS、GCP metadata、K8s SA token、Vault、`~/.npmrc`、git creds、SSH keys）+ 通过 Session messenger 网络（端到端加密、无 C2 域名可封）外传 + 横向扩散到同 maintainer 的其他包

---

## 卡 9：Session/Oxen 作为隐蔽 C2

- **设计目的**：原本是面向人的端到端加密 messenger
- **被滥用方式**：作为文件上传通道
- **防御困难点**：
  - 无单一 C2 域名可封（用的是 `seed{1,2,3}.getsession.org` + `filev2.getsession.org`）
  - 端到端加密，IDS/IPS 无法看 payload
  - 用户合法用途存在，整域封禁有误伤
- **唯一可行的网络层 mitigation**：在企业网络对 Session 协议做完整封禁

---

## 卡 10：Self-Propagation（蠕虫式扩散）

- **机制**：恶意脚本通过 `https://registry.npmjs.org/-/v1/search?text=maintainer:<user>` 枚举 victim 维护的所有包
- **传播条件**：当前进程有 npm publish 权限（或能 mint OIDC token）
- **本次情况**：因为 OIDC binding 只授权 `TanStack/router` 这一个 repo 的 `release.yml`，自传播被限制在 `@tanstack/*` 命名空间内
- **更广义的威胁**：单 maintainer 用同一个 npm token 维护多个 scope 时，传播范围是 maintainer 的全部包

---

## 卡 11：`npm unpublish` 政策的副作用

- **规则**：npm 不允许 unpublish 已经有 dependent 的包
- **本意**：防止维护者撤包导致下游突然 build 失败（left-pad 教训）
- **事故时的副作用**：恶意版本**无法被维护者快速撤回**，只能依赖 npm security 后台介入拉 tarball
- **结果**：恶意版本在被拉之前的几小时内**依然可被 install**

---

## 卡 12：postmortem 的"三段诚实"模板

TanStack 这篇 postmortem 提供了一个值得模仿的事故复盘结构：

- **What went well**：外部研究者 20 分钟内发现、跨时区团队立刻协调、IOC 模式很快公开
- **What could have been better**：自己没有内部告警、`pull_request_target` 长期未 audit、第三方 action ref 浮动、`unpublish` 不可用、7 个 maintainer 等于 7 个凭证窃取目标、OIDC 没有 per-publish review
- **What we got lucky on**：攻击者 payload 破坏了测试（让 publish step skip 反而让攻击噪声变大）、攻击者复用公开 tradecraft（让 IOC 匹配更快）
- **Open Questions**：明确列出 9 个还没回答的调查问题

这种"What we got lucky on"和公开 open questions 的写法，在国内技术博客几乎绝迹——它是这篇 postmortem 工程价值的核心。

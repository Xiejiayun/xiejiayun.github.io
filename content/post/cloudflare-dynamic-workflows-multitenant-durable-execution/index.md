---
title: "Cloudflare Dynamic Workflows 全解析：300 行 TypeScript 如何让持久化执行'跟着租户走'"
description: "当多租户平台需要为数千万用户各自运行有状态工作流，传统容器方案的成本曲线崩溃了。Cloudflare 的方案是：把一切变成 Worker。"
date: 2026-05-08
slug: "cloudflare-dynamic-workflows-multitenant-durable-execution"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Cloudflare
    - 持久化执行
    - 多租户架构
    - Serverless
draft: false
---

## 引言：当「每个租户一个容器」的成本曲线崩溃

构建多租户 SaaS 平台时，最棘手的架构决策之一是工作流隔离。传统方案是每个租户分配独立的容器或进程——但当租户数量从数千增长到数百万时，这种方案的成本曲线从线性变成超线性：每个空闲容器仍然消耗内存、占用 IP 地址、需要健康检查。

2026 年 5 月 1 日，Cloudflare 发布了 `@cloudflare/dynamic-workflows`——一个约 300 行的 TypeScript 库，解决了一个精确的问题：**如何在单一平台上为数千万租户各自运行有状态、可恢复的工作流，且空闲租户的成本趋近于零**。

## 架构三层模型

Dynamic Workflows 的设计可以分解为三层：

```
┌──────────────────────────────────────┐
│       Workflows Engine (平台层)        │
│  持久化调度、失败重试、状态检查点        │
├──────────────────────────────────────┤
│       Worker Loader (路由层)           │
│  你的代码：读取 tenantId，加载对应代码   │
├──────────────────────────────────────┤
│       Dynamic Worker (租户层)          │
│  租户的代码：执行实际的 run(event, step) │
└──────────────────────────────────────┘
```

### 工作原理

1. 租户调用 `env.WORKFLOWS.create(params)` 创建工作流
2. 库自动注入 `__workerLoaderMetadata: &#123; tenantId &#125;` 到载荷中
3. Workflows Engine 持久化这个工作流，并在需要时调度执行
4. 调度时，Engine 调用 Worker Loader 的 `run(event, step)`
5. Worker Loader 从 metadata 中读取 tenantId，加载对应的 Dynamic Worker
6. Dynamic Worker 在隔离沙箱中执行实际逻辑

关键设计决策：**metadata 是路由提示，不是授权机制**。租户可以通过 `instance.status()` 读回自己的 metadata。

### 性能指标

| 指标 | Dynamic Workflows | 传统容器方案 |
|------|-------------------|------------|
| 租户启动时间 | 毫秒级 | 15-30 秒 |
| 空闲租户成本 | ≈ 0 | $5-20/月/容器 |
| 最大并发实例 | 50,000/账户 | 受限于集群规模 |
| 新实例创建速率 | 300/秒 | 受限于调度器 |
| 单租户内存占用 | 几 MB | 128-512 MB |
| 可支持租户数 | 数千万 | 数千 |

## 三个杀手级使用场景

### 1. Agent 平台

当 AI Agent 需要执行多步骤工作流时（搜索 → 分析 → 生成 → 审核 → 发布），每个步骤都可能失败并需要重试。Dynamic Workflows 为每个 Agent 会话提供持久化执行保证——即使 Worker 崩溃或超时，工作流从最后一个检查点恢复，而不是从头开始。

这正是为什么 Cloudflare 在其 Agents Week 中如此强调这个能力：Agent 的可靠性 = 工作流引擎的可靠性。

### 2. SDK/框架扩展系统

当你构建一个允许用户编写自定义逻辑的平台（如 Shopify Apps、Zapier Integration），用户的代码需要在安全沙箱中运行，并具备持久化执行能力。Dynamic Workflows 让平台方不需要管理任何容器——每个用户的代码被加载为 Dynamic Worker，生命周期由引擎管理。

### 3. CI/CD（Cloudflare 最看好的场景）

传统 CI/CD 的开销惊人：

```
传统 CI/CD 每次构建的「仪式」成本：
  VM 分配        15-30 秒
  镜像拉取        10 秒
  Git 克隆        10 秒
  环境初始化      5-10 秒
  ──────────────────────
  总仪式成本      40-60 秒（还没开始实际构建）
```

Dynamic Workflows 将这个成本压缩到秒级：没有 VM 分配、没有镜像拉取、没有预置资源。每个仓库的 pipeline 定义就是一个 `run(event, step)` 函数，作为 Dynamic Worker 按需加载。

## 底层构建块：不止于 Workflows

Dynamic Workflows 是 Cloudflare 「动态化」战略的一部分。三个底层原语共同构成了完整的多租户基础设施：

**Dynamic Workers**：运行时代码加载，隔离沙箱执行。启动时间毫秒级，内存占用 MB 级。

**Durable Object Facets**：每个租户独立的 SQLite 数据库。数据隔离在存储层保证，而不是在应用层过滤。

**Artifacts**：Git 原生的版本化文件系统。每个账户支持数千万个 artifact——用于存储租户的代码、配置、资产。

Cloudflare 的路线图显示，**所有 Workers 绑定都将拥有 Dynamic 对应物**——队列、缓存、数据库、对象存储、AI 绑定、MCP 服务器。这意味着一个完整的「每租户一切」基础设施栈，且成本曲线是亚线性的。

## 与竞品的定位差异

| 特性 | Cloudflare Dynamic Workflows | Temporal | AWS Step Functions |
|------|------------------------------|----------|--------------------|
| 多租户原生 | ✅ 核心设计 | ❌ 需自建 | ⚠️ 有限 |
| 代码隔离 | ✅ V8 Isolate | ❌ 需容器 | ✅ Lambda |
| 冷启动 | 毫秒级 | 秒级 | 秒级 |
| 空闲成本 | ≈ 0 | 集群固定成本 | 按状态转换计费 |
| 自托管 | ❌ | ✅ | ❌ |
| 调试体验 | 中等 | 优秀 | 中等 |

Temporal 在功能丰富度和调试体验上仍然领先，但其多租户方案需要自建命名空间隔离和工作队列路由。Dynamic Workflows 的优势是**原生多租户**——这不是附加功能，而是核心设计假设。

## 局限与风险

**Vendor Lock-in**：Dynamic Workflows 深度依赖 Cloudflare 的 V8 Isolate 运行时、Durable Objects、以及 Workers 生态。迁移成本极高。

**调试复杂度**：三层间接（Engine → Loader → Dynamic Worker）增加了调试的认知负担。当工作流在某个租户的代码中失败时，定位问题需要跨越多个抽象层。

**300 行代码的信任问题**：库本身只有约 300 行 TypeScript，这意味着核心逻辑高度依赖 Cloudflare 的平台层。如果平台层有 bug，你几乎无法绕过。

## 判断

Cloudflare 正在构建的不是一个工作流引擎，而是一个**多租户计算操作系统**。Dynamic Workflows 是其中的调度器，Durable Objects 是存储层，Workers 是进程模型，Artifacts 是文件系统。

对于正在构建多租户 SaaS 平台的团队，Dynamic Workflows 值得立即评估——尤其是租户数量预期在万级以上的场景。对于已经使用 Temporal 或 Step Functions 的团队，迁移的 ROI 取决于你是否真正受限于多租户的成本问题。

真正的信号是 Cloudflare 的路线图：当所有绑定都有 Dynamic 版本时，「每租户一切」将从架构选择变成默认选项。这对整个 SaaS 基础设施行业的定价模型将产生深远影响。

## 参考链接

- [Introducing Dynamic Workflows: durable execution that follows the tenant](https://blog.cloudflare.com/dynamic-workflows/) — Cloudflare Blog
- [Building the agentic cloud: everything we launched during Agents Week 2026](https://blog.cloudflare.com/agents-week-in-review/) — Cloudflare Blog
- [Skipper: Building Airbnb's embedded workflow engine](https://medium.com/airbnb-engineering/skipper-building-airbnbs-embedded-workflow-engine) — Airbnb Engineering
- [Temporal Documentation](https://docs.temporal.io/) — Temporal

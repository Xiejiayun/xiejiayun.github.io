---
title: "Spotify 用 Markdown 和 Bash 构建了 AI 广告接口——然后解释了为什么他们拒绝了 MCP"
description: "Spotify 开源的 Claude Code 广告 API 插件没有用 MCP 协议，而是选择了 Markdown 文件 + bash 脚本的极简方案。当 API 表面积达到 8600 行 OpenAPI spec 时，静态工具定义为何失败？"
date: 2026-05-07
slug: "spotify-claude-plugin-why-mcp-rejected"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Spotify
    - MCP
    - 开发者工具
    - API设计
    - 自然语言接口
draft: false
---

2026 年 5 月 1 日，Spotify 工程博客发布了一篇引发广泛讨论的文章：他们为 Spotify Ads API 构建了一个 Claude Code 插件，并将其开源。这个插件让广告主可以用自然语言管理广告投放——创建 campaign、调整预算、查看报告，全部通过对话完成。

但真正让开发者社区炸锅的不是插件本身，而是 Spotify 在技术选型中做出的一个决定：**他们明确拒绝了 MCP（Model Context Protocol）**，转而用 Markdown 文件和 Bash 脚本构建了整个系统。

这不是一个小团队的权宜之计。Spotify Ads API 拥有约 30 种资源类型、8600 行 OpenAPI 规范——这是一个真正的企业级 API。当这样规模的团队说「MCP 不适合我们」时，值得每一个 AI 工具开发者认真思考背后的原因。

## 背景：Claude Code 插件系统

在深入 Spotify 的方案之前，先快速了解 Claude Code 的插件体系。Claude Code 是 Anthropic 推出的面向开发者的 AI 编程助手，其插件系统由四个核心组件构成[^1]：

- **Skills（技能）**：通过 `/` 斜杠命令触发的结构化操作流程
- **Agents（代理）**：处理自然语言请求的智能体，负责理解意图并编排多步操作
- **Hooks（钩子）**：生命周期事件的回调机制，如认证令牌刷新
- **Settings（设置）**：插件级别的配置和环境变量管理

这套系统的核心设计哲学是**文件即配置**：所有的技能定义、代理行为描述都是 Markdown 文件，所有的执行动作都是标准的 shell 命令。没有自定义 SDK，没有专有协议，没有需要编译的代码。

## Spotify Ads 插件：架构全解析

### 组件一：Skills（技能层）

Skills 是用户的直接交互入口。每个 Skill 对应一个 Markdown 文件，定义了一个具体的操作流程。

```markdown
# /create-campaign

## 描述
创建一个新的 Spotify 广告 campaign。

## 步骤
1. 询问用户 campaign 名称和目标
2. 确认广告格式（audio/video/display）
3. 设置预算和投放时间段
4. 调用 POST /v1/campaigns 创建 campaign
5. 返回创建结果和 campaign ID
```

这种方式的优雅之处在于：**Markdown 本身就是 prompt engineering**。Claude 直接读取这些文件作为指令，不需要任何中间转换层。当你需要修改一个操作流程时，你编辑的是一个人类可读的文档，而不是 JSON schema 或 protobuf 定义。

Spotify 的插件包含了覆盖广告生命周期各阶段的 Skills：campaign 创建、ad set 管理、creative 上传、报表查询、预算调整等。每个 Skill 文件通常不超过 50 行 Markdown。

### 组件二：Agents（智能代理层）

如果说 Skills 是「菜单上的固定菜品」，那 Agents 就是「能根据你的描述自由发挥的厨师」。Agent 的定义同样是 Markdown 文件，但它描述的不是固定步骤，而是一个角色的能力和行为边界。

```markdown
# Spotify Ads Manager Agent

## 角色
你是 Spotify 广告平台的 API 专家。你可以帮助用户管理广告 campaign、
调整投放策略、分析广告效果。

## 可用 API
参考 OpenAPI 规范文件：specs/spotify-ads-api.yaml

## 执行原则
- 所有 API 调用使用 curl 命令
- 每次调用前向用户确认操作内容
- 涉及预算变更时必须二次确认
- 使用 $SPOTIFY_ADS_TOKEN 进行认证
```

当用户说「帮我把上周效果最差的三个 ad set 的预算降低 20%」时，Agent 会：

1. 解析意图：查询报表 → 排序 → 筛选 → 修改预算
2. 生成一系列 curl 命令调用 Spotify Ads API
3. 在每个关键步骤向用户确认
4. 执行并汇报结果

关键点：**Agent 不是通过预定义的工具函数来操作 API，而是直接生成 curl 命令**。这意味着它可以调用 OpenAPI 规范中的任何端点，包括那些没有在 Skills 中显式定义的端点。

### 组件三：Hooks（生命周期钩子）

Hooks 处理的是那些不该由 AI 决策的机械性任务。Spotify 插件中最关键的 Hook 是 OAuth token 刷新：

```bash
#!/bin/bash
# hooks/pre-request.sh
# 在每次 API 调用前检查并刷新 OAuth token

TOKEN_FILE="$HOME/.spotify-ads/token.json"
EXPIRY=$(jq -r '.expires_at' "$TOKEN_FILE")
NOW=$(date +%s)

if [ "$NOW" -ge "$EXPIRY" ]; then
    python3 helpers/refresh_token.py
fi

export SPOTIFY_ADS_TOKEN=$(jq -r '.access_token' "$TOKEN_FILE")
```

这里出现了 Spotify 方案中仅有的两个 Python 文件之一——`refresh_token.py`，负责 OAuth 2.0 token 刷新。另一个 Python helper 处理的是 multipart 文件上传（creative 素材上传），因为纯 bash 处理 multipart/form-data 确实不太优雅。

整个插件：**Markdown 文件 + Bash 脚本 + 2 个 Python helper**。没有了。

### 组件四：Settings（配置层）

Settings 管理环境变量和插件行为配置：

```json
{
  "spotify_ads_api_base": "https://api.spotify.com/ads/v1",
  "default_currency": "USD",
  "confirm_before_mutation": true,
  "max_budget_change_percent": 50
}
```

`confirm_before_mutation` 这个配置尤其值得注意——它确保所有写操作都需要用户确认，这是 AI 代理系统中至关重要的安全护栏。

## 为什么 Spotify 拒绝了 MCP？

现在进入本文的核心问题。MCP（Model Context Protocol）是 Anthropic 在 2024 年底推出的协议，旨在标准化 AI 模型与外部工具的交互方式。它已经得到了广泛采用，很多开发者默认认为「要做 AI 工具集成就该用 MCP」。

但 Spotify 工程团队在评估后明确选择了不用 MCP。根据他们的博客文章[^1]，原因可以归结为一个核心矛盾：

### MCP 的静态工具定义 vs. 大规模 API 的动态需求

MCP 的工作方式是：你为每个工具定义一个静态的 schema——名称、描述、参数类型、返回值类型。AI 模型在运行时从 MCP server 获取这些工具定义，然后选择合适的工具调用。

对于一个有 5-10 个端点的简单 API，这很完美。但 Spotify Ads API 有**约 30 种资源类型**和一份 **8600 行的 OpenAPI 规范**。

让我们算一下：如果为每个资源的 CRUD 操作定义 MCP 工具，你会得到 30 × 4 = 120 个工具定义。加上查询、批量操作、报表等特殊端点，实际数量可能超过 200 个。

这带来了三个严重问题：

**问题一：Context Window 膨胀**

每个 MCP 工具定义需要包含名称、描述、参数 schema。200 个工具的定义轻松消耗 15,000-20,000 tokens——这些 tokens 在每一次对话中都要被加载到上下文里，即使用户只是想查看一个 campaign 的状态。对于付费 API 调用而言，这是一笔不小的浪费。

**问题二：工具选择困难**

当模型面对 200 个工具时，选择正确工具的准确率会显著下降。相似名称的工具（`update_campaign` vs `update_campaign_budget` vs `update_campaign_status`）容易被混淆。这不是理论推测——多篇研究已经表明，工具数量超过一定阈值后，LLM 的工具选择准确率会明显降低[^2]。

**问题三：维护地狱**

8600 行 OpenAPI 规范会不断演进。每次 API 变更，你都需要同步更新 MCP 工具定义。而且 MCP 的静态 schema 无法表达 API 之间的依赖关系——比如「创建 ad set 前必须先创建 campaign 并获取 campaign_id」。这些业务逻辑只能硬编码在工具的描述文本中。

### Spotify 的替代方案为何更好？

Spotify 选择的路线是：**不要把 API 翻译成工具定义，让 AI 直接理解 API 规范本身。**

通过将 OpenAPI 规范文件作为 Agent 的参考文档，Claude 可以：
- 直接理解任何端点的用途和参数
- 动态组合多个 API 调用来完成复杂任务
- 根据上下文只加载相关的 API 信息，而不是全量加载所有工具定义
- 生成标准 curl 命令，用户可以直接审查和理解

**透明性**是另一个关键优势。当所有 API 调用都是可见的 curl 命令时，用户可以精确理解 AI 做了什么、发送了什么请求、得到了什么响应。相比之下，MCP 工具调用对最终用户是不透明的——你只看到「调用了 create_campaign 工具」，看不到实际的 HTTP 请求细节。

## 方案对比：MCP vs Claude Code Plugin vs 传统 SDK

| 维度 | MCP | Claude Code Plugin | 传统 SDK |
|------|-----|-------------------|---------|
| **工具定义方式** | 静态 JSON Schema | Markdown 文件 + OpenAPI 引用 | 编程语言函数签名 |
| **API 覆盖率** | 需要逐个定义工具 | 自动覆盖 OpenAPI 全部端点 | 需要逐个封装 |
| **扩展成本** | 每个新端点需添加工具 | 更新 OpenAPI spec 即可 | 每个新端点需写代码 |
| **Context 消耗** | 高（全量工具定义） | 低（按需加载相关文档） | 不适用 |
| **透明性** | 低（抽象工具调用） | 高（可见的 curl 命令） | 中（需查看 SDK 源码） |
| **调试体验** | 需要 MCP 调试工具 | 直接复制 curl 命令调试 | 断点调试 |
| **适合场景** | 小型 API（<20 端点） | 大型 API（>50 端点） | 程序化集成 |
| **多步编排** | 需要在描述中说明 | 自然语言描述即可 | 硬编码逻辑 |
| **安全审计** | 通过 MCP 日志 | 每条 curl 命令可审查 | 依赖 SDK 日志 |
| **部署依赖** | MCP Server 进程 | 仅文件系统 | 语言运行时 + 依赖包 |

这个对比表揭示了一个有趣的趋势：**在 AI-native 的世界里，中间抽象层的价值在下降**。传统 SDK 封装 HTTP 细节是为了方便程序员，MCP 封装工具调用是为了方便 AI 模型。但当 AI 模型足够强大，能直接理解 HTTP API 规范时，这些中间层反而变成了负担。

## 交互流程示例

让我们通过一个真实场景看看 Spotify 的插件如何工作：

**用户输入：**
> 帮我创建一个新的 audio campaign，名字叫「Summer Vibes 2026」，预算 5000 美元，投放时间 6 月 1 日到 8 月 31 日，目标受众是 18-34 岁的音乐爱好者。

**Agent 处理流程：**

```
[Step 1] 解析用户意图
├── 操作类型：创建 campaign
├── 广告格式：audio
├── 名称：Summer Vibes 2026
├── 预算：$5,000
├── 时间：2026-06-01 ~ 2026-08-31
└── 受众：18-34, music enthusiasts

[Step 2] 生成 API 调用序列
├── POST /v1/campaigns          (创建 campaign)
├── POST /v1/ad-sets            (创建 ad set + 受众定向)
└── GET  /v1/campaigns/{id}     (确认创建结果)

[Step 3] 向用户确认
"我将执行以下操作：
 1. 创建名为 'Summer Vibes 2026' 的 audio campaign
 2. 设置预算 $5,000, 投放期 2026-06-01 至 2026-08-31
 3. 定向 18-34 岁音乐爱好者群体
 确认执行？(y/n)"

[Step 4] 执行 curl 命令
$ curl -X POST https://api.spotify.com/ads/v1/campaigns \
  -H "Authorization: Bearer $SPOTIFY_ADS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Vibes 2026",
    "format": "audio",
    "budget": {"amount": 5000, "currency": "USD"},
    "schedule": {
      "start_date": "2026-06-01",
      "end_date": "2026-08-31"
    }
  }'

→ 200 OK: {"campaign_id": "camp_abc123", ...}

[Step 5] 创建 Ad Set
$ curl -X POST https://api.spotify.com/ads/v1/ad-sets \
  -H "Authorization: Bearer $SPOTIFY_ADS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "camp_abc123",
    "targeting": {
      "age_range": {"min": 18, "max": 34},
      "interests": ["music"]
    }
  }'

→ 200 OK: {"ad_set_id": "as_def456", ...}

[Step 6] 汇报结果
"✅ Campaign 创建成功！
 - Campaign ID: camp_abc123
 - Ad Set ID: as_def456
 - 预算: $5,000
 - 投放期: 2026-06-01 ~ 2026-08-31
 - 定向: 18-34 岁音乐爱好者"
```

注意整个流程中的几个关键细节：

1. **预请求 Hook 自动刷新了 token**——用户无感知
2. **每个 curl 命令完全透明**——用户可以直接复制到终端执行
3. **变更操作需要确认**——安全护栏生效
4. **多步 API 调用自动编排**——从单一自然语言指令生成了两个 API 调用，并正确传递了 campaign_id

## AI-Native API 设计的启示

Spotify 的这次实践指向了 API 设计领域一个深刻的范式转变。

### 启示一：API 文档即接口

传统观念中，API 文档是写给人看的，SDK 才是给程序用的。但在 AI-native 世界里，**API 文档本身就是最好的接口定义**。一份写得好的 OpenAPI 规范，包含了 AI 完成任务所需的全部信息：端点、参数、数据类型、业务约束、示例。

这意味着未来的 API 设计需要更加重视文档质量。不是因为开发者会仔细阅读文档（我们都知道他们不会），而是因为 AI 代理会逐字逐句地理解和执行文档中描述的每一个细节。

### 启示二：透明性胜过抽象

在 AI 驱动的工作流中，用户需要能够理解和验证 AI 的每一个动作。curl 命令是最透明的 HTTP 交互方式——没有隐藏的默认值，没有自动序列化的黑箱，没有 SDK 版本兼容性问题。

这与传统软件工程的直觉相反。我们花了几十年构建越来越厚的抽象层，现在 AI 却告诉我们：最好的接口可能是最薄的那个。

### 启示三：协议的适用边界

MCP 不是一个坏协议——它在适当的场景下非常优秀。对于那些有 5-15 个明确定义的操作的工具（文件管理、数据库查询、日历管理），MCP 提供了标准化和可移植性。但当 API 表面积扩大到几十甚至上百个端点时，静态工具定义的方法就不再经济。

这其实反映了软件工程中一个永恒的张力：**通用性与专用性的平衡**。MCP 追求的是通用的工具调用协议，但通用性有代价。当专用方案（如 Claude Code Plugin）能更好地解决具体问题时，工程团队应该有勇气走不同的路[^3]。

### 启示四：极简主义的回归

Markdown + Bash + curl——这是 2026 年一个世界级工程团队选择的技术栈。不是因为他们不了解更复杂的方案，恰恰相反，是因为他们深刻理解了问题的本质后，选择了最简单的工具。

在 AI 辅助开发的时代，代码的可维护性不只是对人类程序员的考量，也是对 AI 的考量。Markdown 文件比 TypeScript 类更容易被 AI 理解和修改；Bash 脚本比编译型代码更容易被 AI 调试和迭代。

## 开源与社区影响

Spotify 将这个插件完全开源，意味着任何拥有 Spotify Ads API 访问权限的广告主都可以直接使用。更重要的是，这个项目提供了一个**可复制的模式**：任何拥有 OpenAPI 规范的 API 都可以用类似的方式构建 Claude Code 插件。

整个项目的代码量令人印象深刻地少——几个 Markdown 文件、几个 Bash 脚本、两个 Python helper。这降低了分叉和定制的门槛，同时也证明了：在 AI 时代，构建强大的工具不一定需要庞大的代码库。

## 结语

Spotify 的这个案例给行业传递了一个清晰的信号：**在选择 AI 工具集成方案时，不要盲目追随协议热潮，而要从实际问题出发**。

MCP 依然有它的价值和使用场景。但当你的 API 足够复杂时，也许最好的「协议」就是一份写得好的 API 文档、几个 Markdown 文件和一些 Bash 脚本。

工程决策的核心永远是权衡取舍（trade-off）。Spotify 选择放弃 MCP 的生态兼容性，换取了更低的维护成本、更好的可扩展性和更高的透明度。这不是一个所有团队都应该复制的决定，但它是一个所有团队都应该理解的决定。

毕竟，有时候最先进的解决方案，恰恰是最简单的那个。

---

[^1]: Spotify Engineering Blog, "Building an AI-powered Ads API plugin with Claude Code", May 1, 2026. https://engineering.atspotify.com/2026/05/building-an-ai-powered-ads-api-plugin-with-claude-code/

[^2]: Patil, S. et al., "Gorilla: Large Language Model Connected with Massive APIs", arXiv:2305.15334, 2023. 该研究表明 LLM 在面对大量 API 选择时准确率下降的问题。

[^3]: Anthropic, "Model Context Protocol Specification", 2024. https://modelcontextprotocol.io/

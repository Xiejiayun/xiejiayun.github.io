# 英中术语对照表 · Glossary

> 配合《Cut Off》正文使用的 32 条术语对照。覆盖 AI 政策、安全发布、算力经济、地缘政治四大板块。

## A. 模型发布与访问机制

| 英文 | 中文 | 释义 |
|---|---|---|
| Frontier AI | 前沿 AI | 当前世代最强能力的 AI 模型，通常由 OpenAI/Anthropic/Google DeepMind 等少数实验室掌握 |
| Universal API | 通用 API | 任何注册用户都能在配额内调用模型的传统访问范式 |
| Selective Distribution | 选择性分发 | 仅向预先指定的合作伙伴列表（named partner list）开放访问 |
| Named Partner List | 点名伙伴名单 | 合同结构上明确列出的可访问方清单，传统上是政府合同的标准结构 |
| Capability Gating | 能力门控 | 在 API 层面对不同能力做差异化授权，例如允许检索但不允许执行代码 |
| KYC (Know Your Customer) | 客户身份核验 | 金融合规借来的概念，在 AI 上下文里指 API 用户身份与用途审查 |
| Pre-Deployment Authority | 预部署审视权 | 政府对模型发布前进行强制审查的权力 |
| Iterative Deployment | 迭代部署 | OpenAI 提倡的传统范式——先小范围发布，根据反馈逐步扩大，与 Selective Distribution 对应 |
| Tiered Allocation | 分级配给 | 不同用户拿到不同代际能力的访问结构 |
| API as a Commodity | API 即商品 | 把 token 当成无差别消费品的旧范式 |

## B. 安全与蒸馏

| 英文 | 中文 | 释义 |
|---|---|---|
| Mythos | Mythos | Anthropic 的网络安全模型代号，自我定性为 "too dangerous to release" |
| Glasswing | 玻璃翅膀 | Anthropic 的受控发布框架名称，专门用于分发 Mythos |
| Daybreak | 拂晓 | OpenAI 的对应受控发布框架，2026 年 5 月发布 |
| Misuse Risk | 误用风险 | 模型可能被用于网络攻击、生物武器等恶意目的的潜在风险 |
| Distillation | 蒸馏 | 通过 API 大规模查询把大模型的能力转移到小模型上的工程实践 |
| Fast Follower | 快速跟随者 | 模型能力落后前沿 6-9 个月的开源/半开源团队，DeepSeek 是典型 |
| Model Theft | 模型权重盗窃 | 直接窃取闭源模型的权重文件，区别于通过 API 蒸馏 |
| Defender-First Rollout | 防御方优先发布 | 把新模型先发给安全防御方修补漏洞，再开放给一般用户 |
| Capability Cliff | 能力悬崖 | 上一代和下一代之间的能力代差悬殊，限制访问的边界变得敏感 |

## C. 算力经济

| 英文 | 中文 | 释义 |
|---|---|---|
| Compute Crunch | 算力紧缺 | 前沿模型提供方持续面临的 GPU 集群不足状态 |
| Efficiency Curves | 效率曲线 | 单位 token 计算成本随时间下降的曲线，但仅救上一代能力 |
| Marginal Compute Demand | 边际算力需求 | 每多服务一个 token 所需的真实算力支出 |
| Token Economics | 代币经济学 | 把 AI 服务的成本/收益模型化为每 token 的经济分析 |
| Trainium2 | Trainium2 | AWS 的自研 AI 训练芯片二代，Anthropic 主要算力来源 |
| Rainier Megaproject | 雷尼尔超级项目 | AWS 为 Anthropic 部署的 2.2 GW 算力园区代号 |
| Datacenter Sovereignty | 数据中心主权 | 国家对本国境内 AI 数据中心运行规则的控制权 |

## D. 地缘政治

| 英文 | 中文 | 释义 |
|---|---|---|
| Middle Powers | 中等国家 | 经济与技术上不及超级大国但有相当影响力的国家，欧洲主要成员、日韩、印度、加拿大均属此类 |
| GAIN Act | GAIN 法案 | 美国国会提出的"美国买家优先购买美国芯片"立法尝试 |
| Bundle Diplomacy | 捆绑外交 | Trump 政府将贸易、情报、技术准入交叉绑定的外交风格 |
| EuroHPC | 欧洲高性能计算联合体 | 欧盟的算力公共投资框架 |
| AI Gigafactories | AI 千兆工厂 | 欧盟 2028 年规划的大型 AI 算力园区 |
| Sovereign AI | 主权 AI | 国家级别"自有前沿模型"政策口号，NVIDIA 主推的话术 |
| Compute-for-Access | 算力换访问 | Leicht 提出的对冲方案——以基础设施补贴换取前沿能力访问承诺 |

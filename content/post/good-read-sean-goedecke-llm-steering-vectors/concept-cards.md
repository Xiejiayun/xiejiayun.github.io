# 关键概念卡片 · LLM Steering

> 配套 Sean Goedecke 《DeepSeek-V4-Flash means LLM steering is interesting again》导读使用。

---

## 卡 1：什么是 Steering（操舵）

LLM steering 是指在**推理过程中直接修改模型的内部激活值**，从而引导输出走向某个概念，而不是通过 prompt 或 fine-tune。

最经典的案例是 2024 年 Anthropic 的 Golden Gate Claude——把 "Golden Gate Bridge" 这一特征的激活值人为放大几十倍，结果 Claude 在回答任何问题时都会强行扯到金门大桥，包括"我是谁"也会回答"我是金门大桥"。

它的位置正好夹在 prompt（外部输入）和 fine-tune（修改权重）之间，所以本质是"运行时的轻量微调"。

---

## 卡 2：朴素 Steering Vector 怎么算

给模型同一批 prompt 跑两次：

1. 原始 prompt，记录某一层 activation 矩阵 $A_0$
2. 在末尾追加目标行为指令（如 "respond tersely"），记录 $A_1$
3. **steering vector = $A_1 - A_0$**

把这个差分向量在推理时直接**加到那一层的激活**，理论上就能让模型按"respond tersely"的方向偏移——哪怕你 prompt 里没说这句话。

成本：不需要训练。代价：粒度粗、跨概念会污染、跨层不一定迁移。

---

## 卡 3：Sparse Autoencoder（SAE）

更精致的做法。Anthropic 的 *Towards Monosemanticity* 论文给出的方案：

> 训练一个**辅助小模型**（sparse autoencoder），输入是主模型某层的 activation，输出是稀疏激活的"特征向量"。

每个特征对应一个语义概念——"金门大桥""法语""撒谎""愤怒的猫"等。然后你可以单独放大某个特征。

代价：训练 SAE 本身耗算力；解释每个特征要靠人/LLM 打标；只有大厂玩得起。所以 Anthropic 在做，社区做的少。

---

## 卡 4：Polysemanticity 与 Superposition

理解 SAE 为什么必要，需要先理解 superposition（叠加态）：

模型**特征数量远多于神经元数量**，所以每个神经元会同时编码多个语义概念（这叫 polysemanticity，多义性）。

举例：同一个神经元可能在"数学题""车头""人脚"三个场景同时高激活。直接看神经元会一塌糊涂。SAE 就是为了**把叠加在一起的多个特征拆开**——把高维但密集的 activation 投射到更高维但稀疏的特征空间。

---

## 卡 5："Middle Class" Research Idea

Sean Goedecke 给 steering 下的精彩定位——它是个"中产阶级"的研究方向：

- **上不去**：大 lab 不缺这个，他们可以直接训练，steering 是凑合方案
- **下不来**：普通 API 用户拿不到 activation
- **中间被夹住**：只有有本地权重 + 模型够强 + 又没钱 fine-tune 的人会用

这个定位是为什么 steering 长期被讨论但很少落地。DS4 出现后，"本地权重 + 强模型"这一条第一次普惠化，所以 steering 突然变得有意义。

---

## 卡 6：DwarfStar 4（DS4）

antirez（Redis 之父）2026 年 5 月开源的 LLM 推理引擎，**只为 DeepSeek V4 Flash 这一个模型**裁剪。

关键之处：DS4 把 `dir-steering` 作为一等公民放进运行时，而不是事后插件。这意味着 steering 第一次成为本地推理引擎的内置 feature。

虽然初版功能简陋（基本就是 "verbosity" 玩具示例），但它把"普通工程师本地 + 强模型 + 可改 activation"这三个条件一次性凑齐。Sean 这篇文章就是基于这件事写的。

---

## 卡 7：Abliteration（去拒答）

steering 的一个**真实工业化用法**。

如果你想让一个对齐过的开源模型不再拒答，常规做法是 LoRA fine-tune"无审查"版本（uncensored model）。但 abliteration 是另一种路径：

1. 取一批被拒答的 prompt 和一批正常 prompt
2. 算两组激活的差，得到 "refusal direction"
3. 推理时**减去**这个方向

效果：模型几乎不拒答了，但其他能力损伤更小（相比 LoRA 微调）。

Sean 在文章 edit 处特别承认：HN 评论指出，这才是 steering 真正能做、prompt 做不到的事——他原本以为 uncensored 都靠 LoRA。

---

## 卡 8：Compression 假说

Sean 的第二个有趣想法：steering 能不能用来**节省 context window**？

假设你想让 GPT-5.5 熟悉你的代码库。常规做法是把代码塞进 context，几十万 token。

如果能找到一个 "knows my codebase" 的 steering vector，就可以把这些知识**从模型的工作记忆挤进它的隐式记忆**——activation 永远偏向"我知道这套代码"那个方向。

Sean 自己不看好，原因是这种复杂度的概念可能需要"几乎重新训练"才能压进 steering vector。但这是一个值得做的实验。

---

## 卡 9：智能不能 Steer 的理由

为什么不能简单做一个 "intelligence" steering vector 让 GPT-2 变聪明？

Sean 的回答是个归谬：如果你成功了，意味着你在所有层把 GPT-2 的激活换成了 GPT-5 的激活——但这其实是在直接运行 GPT-5。**智能在 steering，不在模型**。

类比：如果你给一个普通人脑里塞了一个爱因斯坦尺寸的"补丁"，做对每一步反应——那这个人已经不是他自己了，是爱因斯坦的拷贝。

所以"可 steer 的概念"有一个上限：越接近模型整体能力的概念，越接近"重新训练一个模型"。

---

## 卡 10：Prompt vs Steering vs Fine-tune

| 维度 | Prompt | Steering | Fine-tune |
|---|---|---|---|
| 操作粒度 | token 级 | 层级 activation | 权重 |
| 可逆性 | 完全可逆 | 完全可逆 | 不可逆（需另存版本） |
| 推理时开销 | 高（占 context） | 低（一次加法） | 零 |
| 需要权重访问 | 否 | 是 | 是 |
| 适合"不可表达"概念 | 差 | 好 | 最好 |
| 复杂概念压缩 | 用 context | 用 vector | 用全套权重 |
| 当前社区门槛 | 极低 | 中（DS4 之后） | 高 |

---

## 卡 11：Steering 的 "六个月窗口"

Sean 文末的预测：

> 如果 steering 真的有用，开源社区会在**未来六个月**找到杀手用法。

这句话的份量是：DS4 把门槛打开了，HuggingFace 上很可能很快出现"DeepSeek V4 Flash 的 200 个 boostable features"这样的资源包。如果到 2026 年 11 月还没有，那 Sean 自己也愿意承认 steering 终究只是研究玩具。

这是一个**带时间戳的预言**——值得追踪。

---

## 卡 12：与 Golden Gate Claude 的连续性

Golden Gate Claude（2024-05）→ Natural Language Autoencoders（2026-05）→ DS4 dir-steering（2026-05）→ Sean Goedecke 这篇导览（2026-05-16），形成一条清晰的演进：

1. **Demo 阶段**：放大一个特征看模型崩溃，证明 steering 可行
2. **解释阶段**：把 activation 用自然语言转译，可读化
3. **工具化阶段**：把 steering 放进本地推理引擎
4. **社区化阶段**：开始辩论 steering 的真实价值

这四步是 AI interpretability 从"白板研究"走向"工程实践"的标志性弧线。

---

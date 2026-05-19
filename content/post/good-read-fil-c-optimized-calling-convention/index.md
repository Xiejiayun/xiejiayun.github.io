---
title: "【好文共赏】Filip Pizlo 把内存安全 C 跑出 Yolo-C 的速度：一份 34K 字的 calling convention 工程手记"
description: "Fil-C 作者亲手拆解：通用 CC、寄存器 CC、直接调用三层优化，加上一个 64-bit 算术签名编码、几对 thunk 和一记 ELF/COMDAT 障眼法，让带 capability 检查的 C 调用几乎不再付额外代价。"
date: 2026-05-19
slug: "good-read-fil-c-optimized-calling-convention"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 内存安全
    - 编译器
    - LLVM
    - ELF
    - ABI
    - C/C++
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[The Fil-C Optimized Calling Convention](https://fil-c.org/calling_convention) ｜ 作者：**Filip Pizlo**（Fil-C 作者，前 Apple JSC 团队 Manager，前 Epic 语言工程 Senior Director，现 Roblox 可编程性总监）
> 发表：2026-05-15 前后（fil-c.org 内部 docs 更新） ｜ HN 讨论：[item?id=48162876](https://news.ycombinator.com/item?id=48162876)（109 pts / 20 评论，作者本人在场回帖）
> 阅读时长：原文约 34,000 字 / 含 4 段 x86 反汇编，建议 60–90 分钟
>
> 多模评分：Opus 9.2 / Sonnet 8.9 / Gemini 9.0（综合 **9.0 / 10**）
>
> **一句话推荐**：一篇罕见的"我亲手做了一个内存安全 C 编译器、现在我教你怎么让它的调用 ABI 几乎没有额外开销"的现场工程手记——把 InvisiCaps、LLVM IR、x86 反汇编和 ELF 链接器的 COMDAT 规则全部摆上桌。

---

## 1. 为什么这篇值得读

如果你最近一年留意过"内存安全 C"这个赛道，会发现它正在被多股力量同时挤压：

- **政府压力**：CISA、NSA、白宫多次发文要求新代码尽可能 memory-safe，老代码逐步搬迁，等于把 C/C++ 列上"减仓清单"；
- **硬件路线**：CHERI 在 Arm Morello 上证明了"硬件 capability + 128-bit 指针"路线可行，但代价是断 ABI、改硬件；
- **重写派**：Rust 通过 lifetime/borrow checker 在源语言层补这一块，代价是几乎所有项目都要从头来过；
- **守旧派**：sanitizer + bounds checker + control-flow integrity 拼一锅，但都只能挡一部分错误，且组合起来开销吓人。

Filip Pizlo 提出的 **Fil-C** 走的是第四条最难走的路：**保留 C/C++ 源语言、保留 64-bit 指针 ABI 表层、但运行时强制全部内存操作经过 capability 检查**。这一条本来在学术界叫 SoftBound（2009 ACM PLDI），从来没有被工程化推进——直到 Pizlo 用 InvisiCaps 重新发明了一遍指针模型，并把整套实现压到 4× clang 的开销区间。

但 4×（即"开销 300%"）仍是大数。Pizlo 接下来要做的就是逐层榨干这 4× 里能榨的每一点。这次的 calling convention 优化是其中最硬核、最具技术教科书价值的一击：

1. 它**完整**——从通用调用约定一直讲到 ELF COMDAT 怎么背锅，没有跳步；
2. 它**真实**——文中每段 x86 反汇编都是从真编出来的 .o 文件里 objdump 出来的；
3. 它**给出失败案例**——Pizlo 罕见地花了大段篇幅讲 weak-vs-weak 在 ELF loader 路径下会怎么死循环，以及他是怎么改 LLVM `ValueTracking.cpp` 救回来的；
4. 它**留白**——HN 上有人提议把 `my_thread` 放进保留寄存器，Pizlo 当场承认："这是显而易见、还没做的优化之一，你来贡献？"

对中文读者，这篇还有一个隐性意义：**让你看见一个真正的 JIT/编译器架构师在思考性能时的思考层级**——他不在 perf 工具里看火焰图，他直接读自己编出来的汇编，对照 ELF spec 推导哪条 `mov` 是真必要的、哪条是 weak 符号 race condition 的产物。这种"以编译器作者视角写编译器"的文字，全网一年也就一两篇。

> 📎 与我之前推荐过的 [《Black Hat Rust 作者 Kerkour 写给所有"想抄 Cloudflare 作业"的团队一封劝退信》](/post/good-read-kerkour-limits-of-rust/) 一起看，会得到一个非常有意思的对照：Rust 派的劝退理由是"边界论"，Fil-C 派的回答是"如果你不想换语言，我帮你给 C 做一身防弹衣"。

---

## 2. 设计目标：在 Yolo-C 速度下保住所有恶意行为的安全

Pizlo 在开篇就把目标摊牌了，**毫不掩饰它的反直觉**：

> 原文：*"Fil-C achieves memory safety even for programs that behave adversarially. That includes casting function pointers to the wrong signature and then calling them, exporting a function with one signature in one module and then importing it with a different signature in another, or even exporting a symbol as a function in one module and importing it as data in another (and vice-versa)."*

翻译成大白话：你**故意**把函数指针 cast 成错误签名、**故意**把同一个符号在一处导出成函数另一处导入成数据、**故意**给 `va_list` 用奇怪的方式逃逸——Fil-C 都不会让你越界。要么 panic，要么按 [GIMSO 语义文档](https://fil-c.org/gimso.html)给出一个 well-defined 的位级转换。

这一目标极其严苛。它意味着调用 ABI 不能简单"把参数推到寄存器就完事"——你必须**永远**能在被调用方一侧检测到"参数数量/类型对不上"并安全降级。

但 Pizlo 同时要求：**在"程序员行为良好"的常见情形下，调用代码应该几乎和 Yolo-C 一模一样**。

把这两条目标摆在一起，整个 calling convention 设计就变成一个倒推题——**先设想理想的 fast path 长什么样，然后回去补一层一层的兜底**：

- Fast path 应当只比 Yolo-C 多两件事：① 第一参数永远是 `my_thread`（线程对象）；② 返回值结构里多一个 `has_exception` bit；
- 慢路径必须能接住任意类型/数量错位的调用，且不能因此被 exploit。

接下来的整篇文章，就是三层优化的渐进剥皮：① **通用 CC**（baseline，慢但安全） → ② **寄存器 CC**（fast/generic 双入口 + 签名 hash + thunk） → ③ **直接调用优化**（用 LLVM IR 的符号命名规则跳过 getter）。

> 📎 这种"先严丢性能，再分层榨回来"的设计套路，与 [《把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上：Mercury 的十年》](/post/good-read-haskell-mercury-production-engineering/) 里 Haskell 团队做"先正确后性能"的方法论是同源的——只是 Pizlo 把它推到 LLVM/asm 这一层。

---

## 3. 第一层：通用调用约定（Generic CC）——baseline 究竟有多重

Fil-C 的通用调用约定是**所有优化的语义基线**。理解它，后面的优化才有"省了什么"的对比。

通用 CC 一次调用要做这些事（按时间顺序）：

1. **解析被调用方**。对间接调用，传入的 flight pointer 直接可用；对直接调用，必须调一个 *getter* 函数把符号名变成 flight pointer。所有这些都不能依赖 ELF linker 自动 resolve——因为 Fil-C 需要在符号解析时同时拿到 capability 信息。
2. **检查被调用方 capability**。capability 不能为 NULL，必须是 function capability，intval 必须匹配 capability 的 callable pointer。
3. **算 argument buffer 大小**。每个参数对齐到 8 字节，按类型对齐补 padding。`byref` 参数把指向的值整个复制进 buffer。
4. **分配两块 CC buffer**（线程局部）：一块装 payload，一块装 capabilities。
5. **复制参数进 CC buffer**。
6. **跳转到被调用方的 prologue**，把 callsite 地址保存到一个**用户代码完全无法触碰的私有 callstack**。
7. **prologue 给 byref 参数做 alloca**。
8. **从 CC buffer 拷参数到局部数据流**。
9. **如果被调用方做了 va_arg/zargs 等参数自省，把 CC buffer 整体拷进一个只读堆对象**——之后 CC buffer 可以释放。
10. 函数体执行。如果抛异常，回到 callsite 时附一个 flag。
11. **返回值走同一套流程**，size 算好，CC buffer 装好，回到 callsite 拷出。

如果你做过 ABI 设计，这套流程会让你立刻嗅出三个**结构性昂贵之处**：

- **参数永远经过线程局部 buffer，而不是寄存器**——这天然就是 register pressure 的反面；
- **每次调用都要 capability check**——即便 99% 的调用 capability 完全合法；
- **直接调用还要先调 getter 一次解析符号**——比间接调用更慢，这非常反直觉。

> 原文（关于这套设计的不效率）：*"This calling convention is inefficient in three major ways: arguments and return values are passed using thread-local CC buffers rather than in registers. The callee's capability must be checked. Direct calls require calling a getter to get a capability to the callee."*

但 Pizlo 没有去"修改"通用 CC，他选择**保留它作为永远的兜底**。这是关键设计抉择：**优化层只是"在常见情况下绕过通用 CC"，但语义边界永远是通用 CC 的语义边界**。这种"快路径必须严格 refine 慢路径"的设计是 Pizlo 在 JSC 上锤炼出来的肌肉记忆——速度可以分层，正确性不能分层。

---

## 4. 第二层：寄存器调用约定——靠一个 64-bit 算术 hash 换 100% 的 ABI 灵活性

如果说通用 CC 是"无脑慢路径"，寄存器 CC 就是 Pizlo 真正的工程亮点：**用一个 64-bit 算术编码把签名压成 perfect hash，再用两个 thunk 兜住所有签名不匹配的边界情况**。

### 4.1 函数对象现在多了三个字段

每个 Fil-C 函数对象本来就是一个 capability。Pizlo 给它加了三个不可被用户代码访问的字段：

- `fast_entrypoint`：用 native 寄存器 ABI 实现的入口点；
- `generic_entrypoint`：用通用 CC 实现的入口点（始终存在，作为兜底）；
- `signature`：64-bit 算术编码后的函数签名（0 表示该函数只有 generic 入口）。

### 4.2 callsite 看起来像什么

理想的寄存器调用 callsite（高度简化）是：

```c
filc_function *fobj = (filc_function*)fp.lower;
fast_fp = LIKELY(fobj->signature == 60125)
        ? fobj->fast_entrypoint
        : pizlonated1ET60125;       /* caller-side thunk */
rv = fast_fp(my_thread, fobj, arg1, arg2, arg3);
```

注意三件事：

1. **签名比对是一个寄存器值 cmp + jne**——比起 capability bounds 检查便宜得多；
2. **不匹配时不走慢路径**，而是落到一个**与签名同名的本地 thunk**，由 thunk 把寄存器参数序列化进 CC buffer 再调 generic_entrypoint；
3. **额外参数永远只多两个**——`my_thread` 和 `fobj`——其他和 native ABI 完全一致。

### 4.3 一对 thunk 是怎么生成的

Pizlo 在被调用方编译时**用 LLVM 的 `linkonce_odr` 链接（即 ELF weak + COMDAT）发射两个 thunk**：

- **Caller entrypoint thunk** `pizlonated1ET60125`：寄存器参数 → CC buffer → 调 generic_entrypoint → 检查 has_exception → 把返回值从 CC buffer 拉回寄存器；
- **Callee entrypoint thunk** `pizlonated2ET60125`：从 CC buffer 拉参数 → 调 fast_entrypoint → 把返回值塞回 CC buffer。

两个 thunk 的名字里**直接编码了 64-bit 签名**——这意味着同一个签名的 thunk 在整个程序里只会保留一份（ELF linker 会去重 weak 定义）。这是一个非常巧妙的"用名字承载语义"的设计：你完全不需要中央注册表。

Pizlo 把 caller-side thunk 的真实 x86 反汇编贴在了正文里。挑核心几行看：

```asm
1d4: mov    %rdx,0x80(%rdi)     ; arg1 -> CC payload
1db: mov    %rcx,0x88(%rdi)     ; arg2 intval -> CC payload
1e2: movsd  %xmm0,0x90(%rdi)    ; arg3 (double)
1f5: mov    %r8,0x188(%rdi)     ; arg2 lower -> CC aux
207: mov    $0x18,%edx          ; arg size = 24
20c: call   *0x8(%rsi)          ; call generic_entrypoint
20f: test   $0x1,%al            ; has_exception?
```

这套代码做的事情可以一句话总结：**把"寄存器世界"翻译进"buffer 世界"**。在签名匹配时，它根本不会被执行；只有那 1% 的签名错位调用才会落到这里。

### 4.4 算术编码：单个 64-bit 怎么塞 16 参数 × 11 类型 × 2 返回值

这是整篇文章最像"硬核数学"的部分。Pizlo 要解决的问题是：

> 给定 ≤16 个参数、≤2 个返回值、每个值有 11 种类型（整数 0..64-bit、float、double、long double、128/256/512-bit vector、pointer，以及 3 个保留类型），把整个签名压成单个 64-bit 整数。

**关键技巧 1：可变长度序列的 perfect hash**

Pizlo 用一种递增前缀求和的编码：

- 空序列 = 0；
- 单个类型 T：`1 + T`；
- 两个类型 T₁ T₂：`1 + 11 + T₁ + 11·T₂`；
- 三个类型 T₁ T₂ T₃：`1 + 11 + 121 + T₁ + 11·T₂ + 121·T₃`；
- 以此类推。

这套编码同时携带"长度"和"具体序列"，且**不会与不同长度的序列冲突**——因为前缀和把每一段长度的编码空间隔得整整齐齐。

**关键技巧 2：用 133 的进制把返回值和参数拼起来**

返回值最多 2 个类型，编码空间需要 `1 + 11 + 11² = 133`。把参数编码 `Arg` 提到 133 进制位：

```text
encoding = 1 + Ret + 133 * Arg     (Ret < 133, Arg < 50,544,702,849,929,377)
```

加上 0 保留给"通用签名"，整体编码可表达约 50,544,702,849,929,377 × 133 + 134 个不同签名——**仍然还剩 ~11.7 × 10¹⁸ 个空位**（接近 64-bit 空间的 2/3）。Pizlo 在文里特地强调这一点：

> 原文：*"This still leaves 11724298594668944475 values in the int64 (almost 2/3 of the encoding space). So in addition to having 3 reserved types, we also have 2/3 of the encoding space left for any kind of fancy next-generation signature encoding we would like to use."*

设计 ABI 的人都知道：**留 2/3 空间给未来的自己**比"刚好够用"难得多，因为前者要求你今天就预设"什么样的扩展是值得保留的"——Pizlo 选择把扩展空间留给"reserved type"和"fancy next-generation"，这种克制比设计本身更难。

### 4.5 性能账

Pizlo 在文末报：寄存器调用约定单独给 PizBench9019 贡献 **>1%** 的加速。这个数字看起来很小——但要意识到 Fil-C 整体瓶颈仍在 InvisiCaps 的 bounds check（贡献 4× 大头）上。**调用 ABI 在大型程序里的占比只在百分之个位数，能榨出 1% 就是 1/3 ~ 1/5 的占比转换为净加速**——非常可观。

> 📎 这种"每层只 +1% 的榨油机"思路，跟我之前推荐的 [《Modal 五年工程账本：从 LP 求解器到 CUDA Checkpoint 的真·无服务器 GPU 栈》](/post/good-read-modal-serverless-gpu-cold-starts/) 是同一种工程美学——单笔账都不大，但叠起来就是 40× 的差别。

---

## 5. 第三层：直接调用——把 getter 也省掉

寄存器 CC 解决了"如何高效传参"，但**直接调用还有一个昂贵步骤：每次都得 call getter 解析符号、check capability**。Pizlo 接下来要做的就是把这两步也省掉——同时保住语义。

### 5.1 命名约定换符号查表

核心 idea 简单粗暴：**在定义函数时，除了发射常规的 getter 符号，再额外发射一个签名携带在名字里的实现符号**：

```text
foo  --> pizlonated_foo            (常规 getter symbol)
       + pizlonatedFI60125_foo     (签名 60125 的实现入口)
```

在调用点，编译器直接把调用 lower 成：

```c
rv = pizlonatedFI60125_foo(my_thread, undef, arg1, arg2, arg3);
```

- 没有 getter；
- 没有 capability check；
- 没有 CC buffer；
- `undef` 是 LLVM 的 *poison value*——它告诉后端"这个参数寄存器不用设"，连一条 `mov` 都省了。

**如果同模块、强定义、签名一致**，整件事就成了：编译期生成 call 指令，链接器直接 patch 地址。这与 Yolo-C 的直接调用**几乎没有可观察差别**。

### 5.2 但 ELF 在等你犯三个错

这一步并不轻松。Pizlo 用了相当长的篇幅讲他踩到的三类陷阱：

**陷阱 1：弱定义在 loader 阶段会赢**

ELF 的链接器规则是"strong wins over weak"，但**这只在 link 阶段成立**。一旦动态库加载，loader 用的规则是"先到者赢"。如果某个跨动态库调用的弱定义比真实实现更早被加载，整个程序就会陷入"调用 → callsite thunk → getter → callsite thunk → ..."的死循环。

**Pizlo 的解法**：所有 callsite thunk 一律以 `hidden` visibility 发射。loader 完全看不见，linker 仍可见。代价是**跨动态库调用永远走 thunk 慢路径**——但 Pizlo 的工程假设是"库内调用远多于跨库调用"。

**陷阱 2：函数本身是弱定义**

这种情况下 strong 兜底拿不到——根本就没有 strong。Pizlo 的应对是引入双层符号：

- 函数实现永远以 `pizlonatedFIP60125_foo` 发射（多一个 P）；
- 只有当函数是**强定义**时，才额外发射 `pizlonatedFI60125_foo` 作为 strong alias 指向 P；
- 函数对象总是查找 `pizlonatedFIP` 而不是 `pizlonatedFI`，避免无限循环。

**陷阱 3：C++ inline 函数 + COMDAT**

C++ inline 函数在每个翻译单元都会复制一份机器码，靠 COMDAT group 让 linker 整组选定一份。Fil-C 的一个函数关联着一窝符号（getter + 实现 + 函数对象 + unwind 数据 + 几个签名别名），全部要塞进同一个 COMDAT group 才能"一起赢一起输"。

接下来更绕：**两个不同 TU 可能给同一个 C++ 函数生成不同 Fil-C 签名**（比如经过 `extern "C"` 处理后名字一样，但 Fil-C 视角下签名不同）。这时 COMDAT 会让某些 `pizlonatedFIP60125_foo` 在 linker 阶段被丢弃——而调用方还在 call 一个已经"不存在"的符号，结果是 *call NULL*。

Pizlo 的解法是改 LLVM 自己：

- 改 `ValueTracking.cpp` 与 `ConstantFold.cpp`，让 LLVM 接受"本地定义、非强、带 COMDAT 的符号可能是 NULL"；
- 在调用前插一条 NULL 检查；
- NULL 检查用一种**会强制 linker 实例化**的 relocation——如果 COMDAT 真的丢了它，链接阶段就报错。

> 原文：*"Amusingly, that relocation does cause linker errors in case COMDAT resolution drops the function we're calling. Hence, this unlikely safety issue is caught at link time rather than at run-time."*

把"潜在的运行时崩溃"转化为"必然的链接时错误"——这是工程上最优雅的危险品转移。

### 5.3 又一个 +1%

第三层优化的加速贡献又是 **>1%**。两层叠起来，Pizlo 把调用 ABI 的开销从"接近通用 CC 的几十倍"压回到"接近 Yolo-C 的 1-2 条额外指令"。

---

## 6. 反汇编中藏着的真理：weak callsite thunk 长什么样

为了让所有这些纸面机制落地，Pizlo 在文中贴了一段最长的反汇编——weak 兜底 callsite thunk `pizlonatedFI60125_foo` 完整版。我不在这里重抄，但有几行特别值得逐字理解：

```asm
11eb: call   1050 <pizlonated_foo@plt>   ; 调 getter
11fc: mov    -0x8(%rsi),%rcx             ; 读 capability header
1200: movabs $0x780000000000000,%rdx     ; capability type mask
1217: cmp    %rdi,%rdx
121a: jne    12ca                        ; -> filc_check_function_call_fail
1236: cmpq   $0xeadd,0x10(%rsi)          ; "EADD" magic - is fast call eligible?
123e: jne    1261                        ; -> generic fallback
1240: mov    (%rsi),%rax                 ; load fast_entrypoint
125f: jmp    *%rax                       ; tail-call
```

注意第 1236 行那个 magic number **0xEADD**——这就是 Pizlo 给"该函数对象有 fast entrypoint 可以接 60125 这种签名"的标记位。如果 ECDC（恰好像 *"E A.D.D."*）出现，说明可以走快路径；否则走慢路径。

这种**用 magic constant 把语义压进单条 cmp 指令**的做法，是 JIT 工程师的典型审美。一个 cmp + jne，整个分支预测都偏向"成功"，CPU 几乎不付代价。

---

## 7. 这篇文章和 Fil-C 的整体地位

Pizlo 在文末并没有 victory lap，他只用一段话总结：

> 原文：*"We started with direct calls having to call a getter, check the function's capability, store arguments to a buffer, have the callee check that they got enough arguments, have the caller check that they got enough return values, and load return values from a buffer. With all of these optimizations, the common case for a direct call does none of that: we just directly call the implementation, exchanging arguments and return values in registers."*

但放到整个 Fil-C 的工程坐标系里，这次优化的意义远不止"快了 2%"：

1. **它把 ABI 边界从"性能负担"变成"语义保险"**。Fil-C 现在可以骄傲地说：通用 CC 永远在，是所有快路径的语义衬底；任何快路径都只是"refine"而非"replace"。
2. **它把内存安全的 *adversarial* 用例从理论变成可工程化**。哪怕调用方故意用错签名，被调方也总能在 callee thunk 这一层兜住，且把开销限制在那条不被触发的代码路径里。
3. **它给后人留了 ~2/3 的 64-bit 签名空间**。这块空间未来可以装更精细的 effect tracking、call mode、async-ness 标记等扩展，**不需要破坏现有 ABI**。
4. **它示范了"软件 capability 系统"的可行性**。CHERI 派一直觉得 capability 必须靠硬件，Fil-C 用纯软件 + 一些 LLVM 改造证明：硬件不是必需，只是更便利的实现细节。

Daniel J. Bernstein 在他的 [Fil-C 笔记](https://cr.yp.to/2025/fil-c.html) 中表态："Fil-C 在加密微基准上一般是 clang 的 1×–4×"——这种话从 djb 嘴里说出来，含金量极高。djb 已经在做 [Filian](https://gitlab.cr.yp.to/djb/filian) 项目，把整个 Debian 13 用 Fil-C 重编一遍。Nix 社区也有 [Filnix](https://github.com/mbrock/filnix)。Fil-C 已经不是单人玩具，它正逐步上升为"内存安全 Linux userland"的候选基座。

而这次 calling convention 的优化，正是从"研究 demo"过渡到"生产可考虑"的关键性能拼图。

> 📎 内存安全的"生产可考虑"门槛同样困扰内核态。我此前写的 [《Cloudflare 一次 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/) 与 [《Linux Kernel CopyFail：从 IPSec 后量子改造到一份"信任图谱"》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/) 都指向同一个共识：在生产 C 代码这一层，**内存安全的边际成本必须降到工程团队可以承受**，否则它永远是论文里的事情。

---

## 8. 延伸阅读图谱

### Filip Pizlo 自己的相关材料

1. [**How Fil-C Works**](https://fil-c.org/how.html) — 整套设计的鸟瞰，含 InvisiCaps、FUGC、runtime 入口；
2. [**InvisiCaps: The Fil-C Capability Model**](https://fil-c.org/invisicaps.html) — 指针模型本身的演进史与与 SoftBound/CHERI 的对照；
3. [**Fil's Unbelievable Garbage Collector**](https://fil-c.org/fugc.html) — 让 use-after-free 必 panic 的并发 GC 设计；
4. [**Garbage In, Memory Safety Out (GIMSO)**](https://fil-c.org/gimso.html) — Fil-C 的安全语义规范；
5. [**Speculation in JavaScriptCore (2020)**](https://webkit.org/blog/10308/speculation-in-javascriptcore/) — Pizlo 在 JSC 时代的旗舰文章，可以与本文相互印证他对 thunk 与 IC 的偏好。

### 相关论文 / 学术工作

1. **SoftBound (PLDI 2009)** — Nagarakatte et al., 把指针 metadata 外置的源头之一；
2. **CETS (ISMM 2010)** — SoftBound 的 use-after-free 扩展；
3. **CHERI (S&P 2015 / Arm Morello)** — 硬件能力架构，与 Fil-C 形成"硬件路线 vs 软件路线"对照；
4. **Microsoft Pluton / EROFS / pKVM** — 同期把"capability"思想往不同方向推；
5. **HeapTherapy / DangSan** — 在普通 C 代码上做 use-after-free 检测；
6. [**A spectre of the JIT (2020)**](https://googleprojectzero.blogspot.com/2020/08/exploiting-spectre-bug-in-javascript-engines.html) — Project Zero 论 JIT capability 漏洞，给 InvisiCaps 的"指针 ≠ 单一 64-bit 值"提供了反面教材。

### 反方观点与社区讨论

1. [**Project Zero: Why Memory-Safety in Existing Code is Hard**](https://googleprojectzero.blogspot.com/) — 主流观点仍倾向"内存安全 C 极难做对，宁可换语言"；
2. [**HN 上对 Fil-C 性能的怀疑帖**](https://news.ycombinator.com/item?id=48162876) — 评论区有不少人质疑"4× clang 在生产仍嫌贵"；
3. **Rust evangelism 派**：认为给 C 加 capability 是"花大力气保住语义债"，应当从源头改写；
4. **CHERI 派**：认为软件 capability 永远比硬件 capability 慢，Fil-C 在 ABI 兼容性上的努力终究是过渡方案；
5. [**djb 的 Fil-C 笔记**](https://cr.yp.to/2025/fil-c.html) — 反方观点的反方：djb 显然认为 Fil-C 已经"足够便宜可以试用"。

### 站内交叉

- [《Black Hat Rust 作者 Kerkour 的 Rust 边界论》](/post/good-read-kerkour-limits-of-rust/) — 与本文形成"内存安全双路线"对照；
- [《把 200 万行 Haskell 跑在 2480 亿美元资金流上》](/post/good-read-haskell-mercury-production-engineering/) — 同样是"先正确后性能"的工程范式；
- [《antirez 一周写出 DS4：当 Redis 之父把 GPT 5.5 当结对程序员》](/post/good-read-antirez-ds4-local-inference/) — Salvatore 与 Pizlo 都是"个人项目逼近工业级"的代表；
- [《Modal 五年工程账本》](/post/good-read-modal-serverless-gpu-cold-starts/) — 每层 +1% 的工程美学相通；
- [《把 Swift 推到 1.1 Tflop/s：Matt Gallagher 的十种实现》](/post/good-read-matt-gallagher-swift-llm-matmul/) — 同样是"硬钻底层 ABI 与寄存器布局"的写法；
- [《Linux Kernel CopyFail 与信任图谱》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/) — 在内核态讨论同一类问题：内存安全的边际成本必须降下来；
- [《Trusting Trust：现代供应链版本》](/post/trusting-trust-modern-supply-chain-2026/) — 当 Fil-C 进入 Linux userland，Trusting Trust 这条线又会扩展出新的攻防面。

---

## 9. 编辑延伸思考：Fil-C 的方法论给我们留下什么

### 9.1 "性能优化不是技巧的堆叠，是分层的语义保护"

整篇文章最隐性的一条原则是：**所有快路径都在严格 refine 慢路径**。寄存器 CC 不替换通用 CC，它只是"在签名匹配时短路它"；直接调用不替换 getter，它只是"在符号强定义且签名匹配时短路它"。这种"快路径必须证明它没有偏离慢路径语义"的做法，是 JIT 工程师常年与 spec 编译器较劲后形成的肌肉记忆。

很多团队做性能优化时反着走——先写一个 fast path，然后再想"它会不会少检查了什么"。Pizlo 的方法是"先把所有检查写在通用 CC 里，再用语义等价证明快路径是合法的 refinement"。这是教科书级别的 ABI 设计纪律，值得任何做基础设施性能工程的团队抄。

### 9.2 "为未来留 2/3 空间"才是真正的 API 设计

64-bit 签名编码里 2/3 的空间是空的。这不是"用不完"，而是 Pizlo 主动保留——他在文中点名"可以用来做 fancy next-generation signature encoding"。

ABI 是给十年后的自己留信。Rust 在 1.0 时锁定了 trait coherence 的设计，导致后来想做 specialization 异常痛苦；C++ 在 ABI 上不断打补丁，每次 vendor change 都要先翻 ELF psABI。Pizlo 选择**用今天 1/3 的空间换十年后的扩展自由**，这种克制感非常值得在你下次设计协议、写 ABI、定 schema 时记住。

### 9.3 "找 LLVM/ELF 的最薄一层下刀"

Fil-C 没有去改 linker、没有去改 loader、没有去改 CPU。它只在**两个地方**改了 LLVM：`ValueTracking.cpp` 与 `ConstantFold.cpp`，让 LLVM 接受"locally defined COMDAT symbol may be NULL"。这是整个项目里**最小的侵入**——任何上游 LLVM 升级都很容易跟。

很多内存安全方案上来就要改 linker、改 kernel、改硬件。Pizlo 的工程纪律是：**先证明你只在一个最薄的层上做了改动**。这种"最小侵入"的纪律保证 Fil-C 永远跟得上 LLVM 主线。

### 9.4 "正式产品和 demo 的差距，就在 weak-vs-weak 这种东西上"

文中真正花篇幅最多的不是寄存器 CC，而是 ELF weak-vs-weak、COMDAT 解析、hidden visibility 这些**典型的工程债务**。学术界写 SoftBound 的时候不会写这些；研究生答辩的时候也不会有人问这些。但**一个项目能否从 demo 走到生产，就取决于作者愿不愿意把这些事情解决干净**。

Pizlo 用了整整三段讲三种陷阱，**几乎是用劝退的口吻写**——但他还是把它们一一解决了。当下次你看到一篇"研究 prototype 性能数据漂亮"的论文时，记得问一句："你处理过 weak-vs-weak 在 loader 路径下的死循环吗？"

### 9.5 "Pizlo 的留白：欢迎来贡献"

HN 评论里 Pizlo 自己回帖："`my_thread` 当然可以放保留寄存器或者 fs/gs 段。这是一个还没做的明显优化。如果你想感受一下亲手做加速的成就感，来贡献 Fil-C 吧。"

这条回复值得任何写技术博客的人记下来：**当你已经把一个项目推进到 4×-Yolo-C，并不意味着剩下的 3× 都是难题——其中一大半是"还没有人来做"**。开源项目的作者**主动暴露未优化点**，本身就是一种健康的协作邀请。它比"提交 PR 之前先发邮件确认 architecture"那种封闭姿态友好得多。

---

## 10. 配套资料导览

本期配套包含：

- 📊 **`mindmap.svg`** — Fil-C 调用约定三层优化 + InvisiCaps / FUGC / ELF 陷阱的思维导图；
- 🗂️ **`concept-cards.md`** — 15 张概念卡片：Yolo-C / InvisiCap / Flight Pointer / Function Capability / 算术签名 / Caller-Callee Thunk / Direct Call / pizlonatedFI vs FIP / Hidden Visibility / COMDAT / Generic CC Buffer / PizBench9019 / my_thread / GIMSO / 现状一览；
- 📖 **`glossary.md`** — 60+ 条英中术语对照，覆盖论文中所有需要查询的概念；
- 🎨 **`cover.svg`** — 深色风格封面，主题"Yolo-C 速度 / 内存安全 C"。

---

## 11. 谁应该读

- **编译器 / JIT 工程师**：本文是 LLVM-side ABI 设计的现代教科书；
- **系统语言设计者**（Rust / Zig / Carbon / Swift 团队）：Pizlo 给出"非完全弃用 C/C++ ABI 还能拿 4× 开销"的实证；
- **内存安全研究者**：SoftBound 派最完整的工程落地之一；
- **大厂安全 / 工具链团队**：如果你的代码库还是百万行 C/C++、又被合规要求 memory-safe，这篇文章值得团队 reading group 拆三周；
- **写过 ELF linker、loader、动态库工具的人**：weak-vs-weak、COMDAT、hidden visibility 这些题目你大概率踩过坑——Pizlo 在这里给了一个"在 LLVM 一侧整体解决"的范本；
- **任何在思考"该不该换语言"的技术 leader**：Fil-C 的存在意味着"不换语言、但拿到 ~Rust 级别的安全保证"成为一个真实的选项，至少值得作为基线考虑；
- **学生 / 自学者**：这是少有的、不端架子、不藏代码的工业级 ABI 文章。如果你刚学完一门编译原理课，把这篇配上 LLVM 反汇编输出，相当于补了一门"现代生产编译器"研究生课。

---

> 📌 **本期总结**：在 Fil-C 把 C/C++ 拉进"内存安全可工程化"赛道之后，Pizlo 选择把每一处性能开销逐层拆掉——这次拆的是调用 ABI。他用 64-bit 算术签名、一对 thunk、加上对 LLVM `ValueTracking.cpp` 的两处微改动，把直接调用的开销从"几十纳秒级"压回到"几条 mov + 一个 cmp"。这是 2026 年最值得一读的编译器工程文章之一，也是"内存安全 C 正在 ready for production"信号的具体一击。


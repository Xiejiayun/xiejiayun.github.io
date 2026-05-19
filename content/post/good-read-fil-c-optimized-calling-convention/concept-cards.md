# 概念卡片 · Fil-C Optimized Calling Convention

> 每张卡片聚焦一个关键术语或机制，方便你在系统课、JIT/编译器组讨论、内存安全设计评审中直接复用。

---

## 卡片 1 — Yolo-C

**定义**：Fil-C 作者用来代指**普通、不做内存安全检查**的 C/C++ 实现（包括 gcc、clang 默认编译出来的代码）。

**意图**：与 Fil-C 形成对照。Fil-C 在描述自己时永远是"几乎和 Yolo-C 一样快"。这种命名一开始有些挑衅，但它把"内存安全"和"性能"放在同一个度量空间。

**为什么重要**：当你看到 Pizlo 在文中说 *"Fil-C is almost as efficient as Yolo-C"*，他指的是寄存器调用 ABI、零额外签名检查的常见路径——而非完全消除所有 GC、bounds-check 开销。

---

## 卡片 2 — InvisiCaps

**全称**：Invisible Capabilities，Fil-C 的指针能力模型。

**核心结构**：每个用户层指针在 64-bit 系统上仍是 64-bit，但**伴生**有一个不可见的 `lower` 元数据指针，指向 capability object（含 bounds、type、free 状态等）。

**演进史**：PLUT (256-bit) → SideCaps (128-bit, 200× 慢) → MonoCaps (128-bit, 10× 慢) → InvisiCaps (64-bit, 4× 慢)。

**对比**：可视为 SoftBound 的可实践、线程安全变体；也可以看作 CHERI 的纯软件版本，但指针仍是 64-bit。

---

## 卡片 3 — Flight Pointer

**定义**：本地变量里的 Fil-C 指针在寄存器中以**两部分**形式存在：
- `intval`：用户可见的 64-bit 地址；
- `lower`：指向 capability object 的隐藏指针。

**为什么叫 flight**：因为它"在飞"——只有当指针从寄存器写回内存（landing）时，运行时才把两部分拼回完整的 InvisiCap 表示。

**ABI 含义**：传 InvisiCap 指针时，编译器实际传两个 64-bit 寄存器；这就是 Pizlo 在文中说"pointers are passed as tuples of lower and intval"的来源。

---

## 卡片 4 — Function Capability (filc_function)

**字段**：
- `fast_entrypoint`：寄存器调用 ABI 的入口；
- `generic_entrypoint`：CC buffer 调用的入口（始终存在）；
- `signature`：64-bit 算术签名（0 表示只有 generic）；
- `data_ptr`（闭包专用）：用户可控的 flight pointer。

**为什么重要**：所有 Fil-C 函数指针都已经携带一个 capability object——闭包功能（zcallee_closure_data）就是把它当作用户数据存储槽来实现 libffi 风格 closure，**不需要 JIT 权限**。

---

## 卡片 5 — Arithmetic Signature Encoding

**编码空间**：把 ≤16 个参数、≤2 个返回值、11 种类型（含 3 个保留类型）的函数签名映射进单个 64-bit 整数。

**关键技巧 1**：用"递增前缀和"表示可变长度序列。空序列 = 0；单元素 = 1+T；两元素 = 1+11+T₁+11·T₂；三元素 = 1+11+121+T₁+11·T₂+121·T₃……

**关键技巧 2**：总编码 = `1 + Ret + Arg * 133`，0 保留给"通用签名"。

**剩余空间**：64-bit 里还有约 2/3 的空间留给未来扩展。这种"留出未来"在 ABI 设计里非常少见、值得学习。

---

## 卡片 6 — Caller / Callee Entrypoint Thunk

**问题**：寄存器调用 ABI 只有签名匹配时才直接调用 fast_entrypoint。不匹配怎么办？

**方案**：在 LLVM IR 中以 `linkonce_odr`（即 ELF 弱定义 + COMDAT）发射一对 thunk：
- `pizlonated1ET<sig>`（caller-side）：把寄存器参数序列化到 CC buffer，调 generic_entrypoint。
- `pizlonated2ET<sig>`（callee-side）：从 CC buffer 反序列化到寄存器，调 fast_entrypoint。

**重点**：thunk 由签名命名，跨模块自动去重；ELF 弱定义+COMDAT 让链接器只保留一份。

---

## 卡片 7 — Direct Call Optimization

**消除目标**：直接调用还要做四件事 —— ① getter 解析符号；② capability 检查；③ CC buffer 序列化；④ 返回值大小检查。

**消除路径**：调用方按 `pizlonatedFI<sig>_foo` 命名直接发射 LLVM call；签名匹配的本地强定义直接接住，**整个调用退化为单条 call**。

**风险点**：不匹配时由本地 weak 定义的 known target callsite thunk 兜底；该 thunk 走完整慢路径并保证语义正确。

---

## 卡片 8 — pizlonatedFI vs pizlonatedFIP

**两层符号别名**：
- `pizlonatedFIP60125_foo`：函数**真实实现**永远以 P 后缀符号发射；
- `pizlonatedFI60125_foo`：只在 *强定义* 时作为 P 的 strong alias。

**为什么**：避免 weak 定义在 loader 路径下被 callsite thunk 抢走，进而造成"调用 → thunk → getter → thunk → ..."的无限循环。这是 Pizlo 论文里最容易看走眼的一个 ELF 细节。

---

## 卡片 9 — Hidden Visibility 技巧

**问题**：weak symbol 在 link 阶段会输给 strong，但在 load 阶段是"先到者赢"。这意味着跨动态库时弱兜底反而会赢真实实现。

**解法**：把 known target callsite thunk 全部用 `hidden` visibility 发射，让 loader 看不到它们。代价是跨动态库的调用永远走 thunk 慢路径——但这条假设是"库内调用远多于跨库调用"。

---

## 卡片 10 — COMDAT 与 C++ inline 函数

**痛点**：C++ inline 头文件函数在每个 TU 都产生一份机器码，靠 COMDAT 让链接器选一份赢家。Fil-C 又有 getter / 实现 / 函数对象 / Pizlonated 别名 / unwind data 等一整窝符号。

**解法**：把所有相关符号塞进同一个 COMDAT group，全员一起赢或一起输；同时改 LLVM 的 `ValueTracking.cpp` 与 `ConstantFold.cpp` 让"locally defined COMDAT symbol may be NULL"，再插入运行时 NULL 检查作为最后一道保险。

**结论**：跨 TU 内联函数的开销退化为"多一个 NULL 检查"，跨调用基本和库内静态函数同等开销。

---

## 卡片 11 — Generic CC Buffer

**作用**：通用调用约定下传参/传返回值的**线程局部双缓冲**——一份是 payload（值），一份是 aux（capability）。

**生命周期**：只活到被调用方取完参数。一般情况下，运行时复用同一段内存，无堆分配。

**逃逸场景**：当被调用方做 `va_arg`、`zargs` 等参数自省时，会把 CC buffer 拷贝进一个只读堆对象（变成稳定快照）。

---

## 卡片 12 — PizBench9019

**Pizlo 自家的基准套件**，文中两个数字皆来自它：
- 寄存器调用约定单独贡献 **>1%** 加速；
- 直接调用优化又贡献 **>1%** 加速。

**为何贡献率看似小**：因为 Fil-C 整体瓶颈仍在 InvisiCaps 的访问检查（4× 区间），而调用开销在大型程序里只占百分之个位数。即便如此，Pizlo 仍逐层抠到每 1%——这是高性能 JIT 工程师的典型做派。

---

## 卡片 13 — `my_thread` 参数

**模式**：Fil-C 的每个函数调用都额外传一个指向当前线程对象的指针（rdi/x0），作为**第一参数**。

**HN 讨论**：有人在评论区指出，这本可以预留一个 GPR 或用 fs/gs 等段寄存器实现，类似 TLS。Pizlo 当场承认 ——"这是显而易见的、还没做的优化之一，欢迎来贡献"。

**启示**：Fil-C 的工程性留白比已实现的多——它把内存安全 C 的可行性证明完了，还有大量"明显但还没做"的优化空间。

---

## 卡片 14 — GIMSO（Garbage In, Memory Safety Out）

**Fil-C 的安全语义文档名**。论文里说"calling convention 严格遵循 GIMSO 语义"，意思是：哪怕你以错误签名调用、哪怕你给函数指针读写不该读写的内存，Fil-C 也会要么 panic、要么给出**well-defined** 行为——绝不出现传统 C 那种"UB 一路传染"的崩塌。

**对照**：传统 C 用"UB 自由"换性能，Rust 用"借用检查 + lifetime"换安全，Fil-C 用"InvisiCaps + GC + 严格语义"在 C 源语言层补这一块。

---

## 卡片 15 — Fil-C 现在能跑什么

来自 djb（Daniel J. Bernstein）2025 年的笔记：
- 编译器自身 + glibc + 大量上层库可以一键 `build_all_fast_glibc.sh` 出来；
- djb 自己的 Filian 项目把整个 Debian 13 用 Fil-C 重编一遍；
- Filnix 把 Nix 包系统接到 Fil-C；
- Fil-C 整体性能开销在 **1×–4× clang** 区间（基于 ~9000 个加密微基准）。

**意义**：内存安全 C 已经从"研究 demo"过渡到"系统服务可以试着真切换"——这正是这次 calling convention 优化重要的工程背景。

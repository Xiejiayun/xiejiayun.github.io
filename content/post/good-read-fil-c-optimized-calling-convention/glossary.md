# 术语表 · Fil-C Optimized Calling Convention

英中对照，覆盖原文中可能让中文读者卡壳的所有专有概念。

| 英文术语 | 中文译法 | 说明 |
| --- | --- | --- |
| Fil-C | Fil-C | Filip Pizlo 主导的内存安全 C/C++ 编译器，输出经过 LLVM IR 转换后的 capability-checked 代码 |
| Yolo-C | "随便写"的 C | Pizlo 自创术语，指传统 clang/gcc 编译的 C/C++（无内存安全保护） |
| memory safety | 内存安全 | 静态或动态保证程序无法发生越界访问、use-after-free、double-free 等 |
| capability | 能力 / 权能 | 指针除"地址"外携带的元数据：边界、类型、是否仍可用 |
| capability model | 能力模型 | 决定 capability 在内存中如何存放、如何与指针绑定的设计 |
| InvisiCap | 隐形能力 | Fil-C 现版指针模型，64-bit 指针 + 隐藏 capability object |
| SoftBound | 软边界 | 学术界 2009 年的 C 内存安全方案，InvisiCap 的思想来源之一 |
| CHERI | CHERI | 剑桥/SRI 主导的硬件能力架构（128/256-bit 指针） |
| MonoCap / SideCap / PLUT | 单调能力 / 旁路能力 / Pointer-Lower-Upper-Type | Fil-C 历代被淘汰的指针模型 |
| flight pointer | 飞行指针 | 在寄存器中以 (intval, lower) 双元组形式存在的指针 |
| intval | 用户可见地址 | flight pointer 的高地址侧，等价于普通 C 指针值 |
| lower (pointer) | 元数据指针 | flight pointer 的低地址侧，指向 capability object |
| Generic Calling Convention | 通用调用约定 | 通过线程局部 CC buffer 传参的 Fil-C 慢路径 |
| Register Calling Convention | 寄存器调用约定 | 寄存器传参的 Fil-C 快路径，仅当签名匹配时生效 |
| CC buffer | 调用约定缓冲区 | 线程局部、双份（payload + aux）的临时参数缓冲 |
| signature | 函数签名 | 包含参数类型序列和返回类型序列的整体描述 |
| arithmetic encoding | 算术编码 | 把签名压成单个 64-bit 整数的 perfect-hash 编码 |
| fast_entrypoint | 快入口 | 函数对象里指向寄存器 ABI 实现的指针 |
| generic_entrypoint | 通用入口 | 函数对象里指向 generic CC 实现的指针，永远存在 |
| function object / function capability | 函数对象 / 函数能力 | Fil-C 用来代表函数的 capability，含 fast / generic / signature / closure data |
| closure | 闭包 | Fil-C 用 zcallee_closure_data 在函数对象里携带用户状态实现的非 JIT 闭包 |
| zcallee / zcallee_closure_data | zcallee / zcallee 闭包数据 | Fil-C 暴露给用户代码的闭包 API |
| libffi | libffi | 通用 ABI 调用库；Fil-C 通过 closure 字段无 JIT 实现 |
| thunk | 跳板 | 跨调用约定时做参数翻译的小函数 |
| caller entrypoint thunk | 调用方跳板 | 把寄存器参数序列化进 CC buffer，再调 generic_entrypoint |
| callee entrypoint thunk | 被调方跳板 | 把 CC buffer 参数反序列化到寄存器，再调 fast_entrypoint |
| getter | 获取器 | 把 ELF 符号名解析成 flight pointer 的运行时函数 |
| direct call | 直接调用 | 编译期能解析符号名的调用（区别于函数指针 indirect call） |
| indirect call | 间接调用 | 通过函数指针进行的调用 |
| known target callsite thunk | 已知目标调用站跳板 | weak 兜底版本的 callsite，签名不匹配或 weak 定义胜出时使用 |
| weak symbol | 弱符号 | ELF 中允许被同名 strong 符号覆盖、且可同名共存的符号 |
| strong alias | 强别名 | 给一个符号挂的额外强名字（如 `pizlonatedFI60125_foo`） |
| linkonce_odr | LLVM 弱链接 | LLVM IR 标记，对应 ELF 的 weak symbol in COMDAT |
| COMDAT | COMDAT 组 | ELF 区段机制，让一组同名符号被链接器整组选定或抛弃 |
| ODR (One Definition Rule) | 唯一定义规则 | C++ 语言层规定：一个实体在整个程序里只有一个定义 |
| pizlonatedFI / pizlonatedFIP | Fil 内部符号前缀 | FI = 直接调用入口；FIP = 真实实现（永远存在的 P 后缀版本） |
| ValueTracking.cpp / ConstantFold.cpp | LLVM 优化 pass | Pizlo 改这两个文件，让 LLVM 接受"locally defined COMDAT symbol may be NULL" |
| hidden visibility | 隐藏可见性 | ELF 符号属性，loader 看不见、但 linker 仍可见 |
| symbol resolution | 符号解析 | linker/loader 把符号名映射到具体地址的过程 |
| relocation | 重定位 | ELF 对象文件里记录"此地址需要后期填入" |
| GIMSO | Garbage In, Memory Safety Out | Fil-C 的语义规范文档；保证错误输入仍得到内存安全的输出 |
| FUGC | Fil's Unbelievable Garbage Collector | Fil-C 自研的并发 GC；free 时原子地 invalidate 所有 capability |
| use-after-free | 释放后使用 | C 经典内存错误；Fil-C 下保证 panic |
| GIMSO panic | GIMSO 触发的 panic | 用户代码做了 Fil-C 不允许的事，运行时立即停止 |
| safepoint | 安全点 | GC 暂停所有线程并扫描栈的程序点 |
| /opt/fil | /opt/fil | Fil-C 推荐的安装位置，包含一整套预编译的安全 userland |
| pizfix | 派斯前缀 | Pizlo 给 Fil-C 自己的"prefix"安装目录起的小名 |
| pizlix | Pizlix | 把整个 Linux userland 用 Fil-C 重编后的发行版 |
| Filian | Filian | djb 把 Debian 用 Fil-C 重编的项目（Filc + Debian） |
| Filnix | Filnix | 把 Nix 包接到 Fil-C 的项目（Mikael Brockman 主导） |
| ELF | ELF | Linux/Unix 主流可执行/目标文件格式 |
| `va_arg` / variadic | 可变参数 | C 中处理 `...` 函数参数的机制；Fil-C 强制走 generic CC |
| AOT (Ahead-Of-Time) | 预先编译 | Fil-C 是 AOT；与 JIT 相对 |
| JSC (JavaScriptCore) | JSC | Apple 的 JavaScript 引擎，Pizlo 曾任其负责人 |
| Roblox / Epic Games | Roblox / Epic | Pizlo 当前/上一份工作；Fil-C 多数代码挂 Epic 版权 |
| Zef language | Zef 语言 | Pizlo 顺手做的另一门语言，与 Fil-C 共用许多基础设施 |
| Yosh shell | Yosh | "AI bash fork"，Pizlo 个人项目 |

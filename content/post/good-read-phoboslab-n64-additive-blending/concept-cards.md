# 关键概念卡片

> 配套：《PSX 的爆炸为什么比 N64 漂亮》导读

---

## 卡片 1 / 饱和算术 (Saturating Arithmetic)

**核心**：当算术结果超出表示范围时，**钳位到边界值**而不是 wrap-around。

**对照**：
- `wrapping_add(250, 10)` = `4` （回绕，PC 上 C 整型默认）
- `saturating_add(250, 10)` = `255` （饱和，PSX GPU、N64 RSP、Rust `u8::saturating_add`）

**为什么重要**：在视觉/音频信号叠加场景里，饱和等价于"过曝/削顶"——可读的失真；wrap 等价于颜色反转或鼓声变安静——不可读的 bug。

---

## 卡片 2 / Color Combiner（颜色合成器）

**核心**：N64 RDP 内部一个可编程小单元，可以表达 `(P*A) + (Q*B)` 形式的任意线性混合。

**输入槽位**：
- `P / Q`: 任一 sprite RGB、framebuffer RGB、常量等
- `A / B`: alpha 通道、fog alpha、常量等

**对比 OpenGL**：类似 `glBlendFunc(GL_SRC_ALPHA, GL_DST_ALPHA)` 的可编程版本，但 N64 早于 OpenGL ES 多年。

**失败模式**：因为可编程性高，N64 没有内置 saturation——这正是这篇文章的核心 bug。

---

## 卡片 3 / RDPQ_BLENDER 宏

**核心**：libdragon SDK 暴露的混合配置宏，让 C 程序员能直接配置 Color Combiner。

```c
RDPQ_BLENDER(( IN_RGB, IN_ALPHA, MEMORY_RGB, ONE ))
// = sprite_rgb * sprite_alpha + framebuffer_rgb * 1
```

**用途**：典型的 additive blending、alpha blending、subtraction blending 都用这个宏写出来。

**陷阱**：宏只配置数学，**不附赠 clamp**——这是 phoboslab 全篇文章的起点。

---

## 卡片 4 / Fog Alpha Hack（雾化 alpha 重用）

**核心**：把本来给"远处雾化"的 fog 寄存器，挪用成"全局亮度缩放因子"。

```c
rdpq_set_fog_color(RGBA32(0, 0, 0, 256/8));  // 借用 alpha 通道做 1/8 缩放
rdpq_mode_blender(RDPQ_BLENDER((IN_RGB, FOG_ALPHA, MEMORY_RGB, ONE)));
```

**意义**：体现 demoscene 思维方式——**所有硬件寄存器都是潜在的多用途资源**，可编程性的真正用途是"把硬件免费乘法器借去做别的事"。

---

## 卡片 5 / RSP（Reality Signal Processor）

**核心**：N64 上的 128-bit 向量协处理器，原始用途是顶点变换 + 矩阵运算。

**关键特性**：
- 8 路并行（一条指令处理 8 个 16-bit 元素）
- MIPS scalar + vector 双 ISA
- 4 KB IMEM + 4 KB DMEM

**phoboslab 的用法**：写一段 RSP 微码做 32-bit → 16-bit 像素重打包，把 70 ms/帧 干到 3.1 ms/帧。

**笑话点**：N64 圈管 RSP 微码叫 "GPU microcode"，但它其实是 MIPS 汇编——文中那句 "MIPS plus assembly" 是对 GNU/Linux 命名梗的硬件版翻拍。

---

## 卡片 6 / Libdragon

**核心**：开源的 N64 SDK，替代任天堂闭源的 libultra。

**关键特性**：
- 现代 C API（不需要 Nintendo NDA）
- RDPQ 子系统暴露 RDP 命令队列
- 内置 RSP 微码加载器
- GCC 工具链 + 开源 emulator 支持

**意义**：libdragon 把"写一个 N64 卡带"从工作站特权降到了周末项目。

---

## 卡片 7 / RSPL（RSP Language）

**核心**：HailToDodongo 写的 C-like 微码语言，编译到 RSP 的 MIPS + vector ISA。

**为什么重要**：N64 微码原本必须用 MIPS 汇编手写；RSPL 让你能写出类似：

```rspl
state { vec16 pixels[8]; }
function pack_to_5551(vec16 in) -> vec16 {
    return ((in.r >> 3) << 11) | ((in.g >> 3) << 6) | ((in.b >> 3) << 1) | 1;
}
```

**生态位**：类似 NVIDIA PTX 之于 CUDA。

---

## 卡片 8 / 32-bit Framebuffer 路径

**核心**：N64 RDP 罕见地支持 32-bit (RGBA8888) 帧缓冲，但绝大多数游戏用 16-bit (RGBA5551)。

**代价**：32-bit 路径的 RDRAM 带宽消耗是 16-bit 的两倍——这也是 N64 时代它没被普及的原因。

**phoboslab 思路**：32-bit 不是为了最终显示，而是为了"提供 8 倍溢出预算"作为中间画布。最终输出仍然 16-bit。

---

## 卡片 9 / Saturation as Tone Mapping

**核心**：phoboslab 的三步管线在数学上等价于：

```
HDR_buffer = sum( sprite_color * 0.125 )    # 线性叠加 (32-bit)
LDR_buffer = clamp( HDR_buffer, 0, 31 )     # tone mapping → 16-bit
```

**结论**：这其实是一个 1990 年代不存在的概念——**N64 上的 pseudo-HDR 渲染管线**，藏在"修复 additive blending"的标题下。

**社区演化**：N64 homebrew *Tiny3D* 已在此基础上做出 Bloom、Post-processing 等现代效果。

---

## 卡片 10 / 可编程性 vs 默认正确性

**核心**（编辑总结）：**可编程性不能弥补默认错误**。

**对照表**：

| 系统 | 可编程性 | 默认正确性 | 实际胜负 |
|---|---|---|---|
| PSX 4 档混合 | 低 | 高（自带 clamp） | 90% 游戏用对 |
| N64 Color Combiner | 高 | 低（不 clamp） | 90% 游戏绕开 |
| C int 溢出 (UB) | 高 | 低 | bug 来源第一 |
| Rust `saturating_add` | 高 | 高（显式选择） | 安全 |
| Heroku | 低 | 高 | 默认对 |
| Kubernetes | 高 | 低 | 默认坑 |

**适用范围**：硬件、API、框架、SDK 设计的元原则。

---

## 卡片 11 / Dominic Szablewski 作品坐标

phoboslab.org 主理人，作品集形成一种独特的"low-level + retro + 小代码量"风格：

- **QOI**（2021）— 300 行 C，无损图像格式，比 PNG 快 20-50×
- **QOA**（2023）— 400 行 C，时域有损音频压缩
- **wipEout 重写**（2023）— 1995 年 PSX 经典的现代 C/WebGL 移植
- **high_impact**（2024）— Impact.js 引擎的 C 重写
- **N64 Rumble Pak**（2026-03）— 同一系列上篇，逆向不合规震动包
- **N64 Additive Blending**（2026-05）— 本文

**风格关键词**：单文件 C 库、规范定稿、retro 平台 + 现代工具。

---

## 卡片 12 / 2026 硬件考古浪潮

**观察**：最近 14 天 HN 头条出现的硬件考古长文：

1. Maurycy · AVR64DD32 跑完整 TCP/IP 栈
2. Leonard · Amiga PAULA + Atari YM 0% CPU 对唱
3. Scott Robinson · HCF 指令考古
4. Dmitry Grinberg · Fisher-Price Pixter 41,000 字完整保存
5. Ryan Miceli · 4 家 HDD/SSD 固件逆向
6. **phoboslab · N64 additive blending（本文）**

**为什么 2026 年集中爆发**（编辑分析）：
- AI 让通用代码变便宜，**领域知识反而升值**
- 现代开源工具链把"老硬件研究"门槛降到周末项目
- 90 年代玩家这代人开始有时间和钱做"童年遗憾修复"

**预测**：这个内容类目在未来 12-24 个月将持续稳定输出，比 AI 应用层博客寿命更长。

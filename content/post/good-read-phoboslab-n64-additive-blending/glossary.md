# 术语对照表（英中）

> 配套：《PSX 的爆炸为什么比 N64 漂亮》导读

---

## 硬件 / 平台

| English | 中文 | 说明 |
|---|---|---|
| Nintendo 64 (N64) | 任天堂 64 | 1996 年发售的 64-bit 家用机 |
| PlayStation (PSX) | 索尼初代 PS | 1994 年发售，与 N64 同代 |
| Reality Display Processor (RDP) | 现实显示处理器 | N64 的固定功能光栅化单元 |
| Reality Signal Processor (RSP) | 现实信号处理器 | N64 的 128-bit 向量协处理器，类似 SIMD DSP |
| RDRAM | Rambus DRAM | N64 的主存，单总线高延迟低带宽 |
| MIPS | MIPS 架构 | N64 主 CPU 和 RSP 用的 RISC 指令集 |
| Color Combiner | 颜色合成器 | RDP 内部的可编程混合单元 |
| Blender | 混合器 | Color Combiner 中负责最终 src + dst 的子模块 |

---

## 图形概念

| English | 中文 | 说明 |
|---|---|---|
| Framebuffer | 帧缓冲 | 显示输出的内存区域 |
| Additive Blending | 加色混合 | `output = src + dst`，适合爆炸/光效 |
| Alpha Blending | alpha 混合 | `output = src*α + dst*(1-α)`，半透明 |
| Saturating Addition | 饱和加法 | 溢出钳位到最大值 |
| Wrap-around | 回绕 | 溢出后从 0 重新开始 |
| Clamp | 钳位 | 把值压到指定范围 |
| Saturation Arithmetic | 饱和算术 | 所有运算自动 clamp 的算术系统 |
| Tone Mapping | 色调映射 | HDR → LDR 的非线性压缩 |
| HDR (High Dynamic Range) | 高动态范围 | 每通道超过 8-bit 的渲染中间表示 |
| LDR (Low Dynamic Range) | 低动态范围 | 标准 8-bit/通道显示输出 |
| Bloom | 泛光 | 高亮区域向周围扩散的后处理效果 |

---

## 像素格式

| English | 中文 | 说明 |
|---|---|---|
| RGBA 5551 | 16-bit 5-5-5-1 | 5 位红绿蓝 + 1 位透明，N64/PSX 主流 |
| RGBA 8888 | 32-bit 8-8-8-8 | 标准 8 位/通道 |
| Color Channel | 颜色通道 | R / G / B / A 中的一个 |
| Bit Depth | 位深度 | 每通道占用的二进制位数 |

---

## 工具链

| English | 中文 | 说明 |
|---|---|---|
| Libdragon | libdragon | 开源 N64 SDK |
| libultra | libultra | 任天堂闭源官方 SDK |
| RSPL | RSPL | HailToDodongo 写的 C-like RSP 微码语言 |
| Microcode | 微码 | 协处理器（RSP）上运行的低级程序 |
| N64Brew | N64Brew | N64 homebrew 开发者社区 |
| Homebrew | 自制软件 | 非官方平台软件 |
| RDPQ | RDPQ | libdragon 的 RDP 命令队列子系统 |
| Reverse Engineering | 逆向工程 | 不依赖原始设计文档恢复内部逻辑 |

---

## 软件 / 引擎

| English | 中文 | 说明 |
|---|---|---|
| Silent Bomber | 寂静轰炸者 | 1999 PSX 第三人称射击，文章中的爆炸示例 |
| Star Fox 64 | 星际火狐 64 | 1997 N64 飞行射击，对照示例 |
| wipEout | 反重力赛车 | 1995 Psygnosis PSX 经典，phoboslab 重写过 |
| Impact.js | Impact.js | phoboslab 的 HTML5 游戏引擎 |
| high_impact | high_impact | Impact.js 的 C 重写版 |
| QOI | QOI | phoboslab 的 300 行无损图像格式 |
| QOA | QOA | phoboslab 的 400 行有损音频格式 |

---

## 元概念

| English | 中文 | 说明 |
|---|---|---|
| Default Correctness | 默认正确性 | 系统在最常见输入下的开箱即用程度 |
| Programmability | 可编程性 | 系统暴露的可配置/可扩展程度 |
| Fixed-function Pipeline | 固定功能管线 | 不可编程但参数可调的硬件管线 |
| Programmable Pipeline | 可编程管线 | 可写自定义着色器/微码的管线 |
| Demoscene | demo 圈 | 用极限技术做艺术演示的亚文化 |
| Code Golf | 代码高尔夫 | 用最少字节实现一个目标 |
| Retro Computing | 复古计算 | 对老一代硬件平台的研究与重玩 |

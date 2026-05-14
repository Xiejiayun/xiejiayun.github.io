# 术语表 · Glossary

英中对照 + 简释，覆盖 Maxime Heckel 大气散射文章涉及的 38 个核心术语。分两层：**大气物理 / 光学** 和 **GPU 渲染 / WebGL**。

## 一、大气物理与光学

| 英文 | 中文 | 简要释义 |
|------|------|---------|
| Atmospheric Scattering | 大气散射 | 光在大气中被分子、气溶胶反复改变方向的过程。 |
| Rayleigh Scattering | 瑞利散射 | 波长远大于颗粒时占主导的散射，强度 ∝ 1/λ⁴。 |
| Mie Scattering | 米散射 | 波长与颗粒相近时占主导的散射，前向性强。 |
| Ozone Absorption | 臭氧吸收 | 高层 O₃ 对黄绿光（Chappuis 带）的选择性吸收。 |
| Optical Depth | 光学深度（τ） | 沿光线积分的密度×截面，决定透射率。 |
| Transmittance | 透射率 | 光通过介质后剩余比例，T = e^(-τ)。 |
| Beer-Lambert Law | 比尔-朗伯定律 | 描述光通过吸收介质强度衰减的物理定律。 |
| Phase Function | 相位函数 | 散射光在各方向上的概率密度。 |
| Henyey-Greenstein | 亨耶-格林斯坦函数 | 米散射常用的解析相位函数，参数 g 控制各向异性。 |
| Anisotropy (g) | 各向异性参数 | HG 函数里的 g ∈ [-1,1]，0 = 各向同性，1 = 纯前向。 |
| Scale Height | 标高 | 大气密度衰减到 1/e 时的高度（瑞利 ≈ 8 km，米 ≈ 1.2 km）。 |
| Aerosol | 气溶胶 | 悬浮于空气中的微小固液颗粒，是 Mie 散射的主体。 |
| Aerial Perspective | 空气透视 | 远处物体因大气累积而偏蓝、模糊的视觉效应。 |
| Karman Line | 卡门线 | 100 km 高度，约定的大气与太空分界。 |
| Multi-Scattering | 多重散射 | 光在大气中经历两次以上散射的修正项，本文作者未实现。 |
| Solar Eclipse / Sun Visibility | 日食 / 太阳可见性 | 月球角直径覆盖太阳时的遮挡效应。 |
| Corona | 日冕 | 太阳大气最外层，日全食时可见，需独立模型。 |
| Single Scattering | 单次散射 | 只考虑光被散射一次的简化模型，工业上多与多重散射近似配合使用。 |

## 二、GPU 渲染与 WebGL / Three.js

| 英文 | 中文 | 简要释义 |
|------|------|---------|
| Raymarching | 光线步进 | 沿光线分段采样的数值渲染方法，适合体积。 |
| Light Marching | 光行进 / 二次步进 | 在 raymarching 主循环内嵌套向光源采样的步骤。 |
| Fragment Shader | 片元着色器 / 像素着色器 | 在 GPU 上对每个屏幕像素并行运行的程序。 |
| Vertex Shader | 顶点着色器 | 在 GPU 上对每个顶点并行运行的程序。 |
| GLSL | OpenGL Shading Language | OpenGL/WebGL 使用的 C 风格着色器语言。 |
| WebGL | Web 图形库 | 浏览器里基于 OpenGL ES 的 3D 渲染 API。 |
| WebGPU | Web GPU API | 下一代浏览器图形 API，支持 compute shader。 |
| Three.js | / | 主流的 WebGL 封装库，本文使用。 |
| React Three Fiber | / | Three.js 的 React 声明式封装。 |
| Post-Processing Effect | 后处理效果 | 在场景渲染完成后对整张图进行的着色器处理。 |
| Depth Buffer | 深度缓冲 | 每像素存储最近物体距离的纹理。 |
| Logarithmic Depth Buffer | 对数深度缓冲 | 用对数变换让深度精度更均匀，解决大尺度 z-fighting。 |
| NDC（Normalized Device Coordinates） | 归一化设备坐标 | 渲染管线里 [-1,1] 的标准坐标空间。 |
| World Space Reconstruction | 世界空间重建 | 从 UV + 深度反推世界坐标的过程。 |
| Ray-Sphere Intersection | 射线-球体相交 | 在 shader 里判断光线与球体交点的解析公式。 |
| FBO（Frame Buffer Object） | 帧缓冲对象 | 将渲染结果输出到自定义纹理而非屏幕的 OpenGL 概念。 |
| LUT（Look-Up Table） | 查找表 | 预计算结果存进纹理，运行时查表代替计算。 |
| Compute Shader | 计算着色器 | 不挂在渲染流水线上的通用 GPU 程序，WebGPU 才支持。 |
| ACES Tone Mapping | ACES 色调映射 | 电影业标准的 HDR→LDR 颜色映射曲线。 |
| Gamma Correction | Gamma 校正 | 把线性空间颜色转换为显示器期望的 sRGB 的步骤。 |

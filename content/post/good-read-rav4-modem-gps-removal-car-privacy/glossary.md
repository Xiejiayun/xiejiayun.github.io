# 术语表 · Glossary

| 英文 / 缩写 | 中文 | 说明 |
| --- | --- | --- |
| DCM (Data Communication Module) | 车载数据通信模块 | 丰田/雷克萨斯体系中负责蜂窝/卫星上行的独立 ECU；本文核心被拆部件 |
| TCU (Telematics Control Unit) | 远程信息处理控制单元 | 行业通用叫法，与 DCM 概念基本等同 |
| ECU (Electronic Control Unit) | 电子控制单元 | 现代汽车里的"小电脑"，一辆车可能有 80-150 个 |
| OBD-II | 车载诊断接口（第二代） | 1996 年起美国强制装车的标准诊断口，可读取所有 ECU 数据 |
| CAN bus | 控制器局域网总线 | ECU 之间通信的物理层，1986 年由博世发明 |
| Automotive Ethernet | 车载以太网 | 高带宽车内通信（100 Mb/s ~ 10 Gb/s），用于摄像头、域控制器 |
| Head Unit | 车机主机 | 含中控屏、CarPlay、Android Auto、收音机等多功能集成体 |
| Infotainment | 信息娱乐系统 | 等同于"车机"，更偏市场术语 |
| OTA (Over-the-Air) Update | 空中升级 | 车厂通过蜂窝网络远程推送固件 |
| OEM | 原始设备制造商 | 此处指车厂本身 |
| MIE / MTE | 内存完整性强制 / 内存标记扩展 | 苹果 M5 等芯片的内存安全机制（本文对照延伸用） |
| SDV (Software-Defined Vehicle) | 软件定义汽车 | 把传统机械功能改造为可订阅的软件特性 |
| DR (Dead Reckoning) | 航位推算 | GPS 信号丢失时用速度/陀螺仪/方向盘角度估算位置 |
| GNSS | 全球导航卫星系统 | GPS / GLONASS / Galileo / BeiDou 的统称 |
| RTK | 实时动态测量 | 厘米级 GNSS 增强，部分高端车机/自动驾驶系统标配 |
| LTE / 5G NR | 4G/5G 蜂窝网络 | DCM 内置调制解调器的物理层 |
| eSIM | 嵌入式 SIM 卡 | DCM 通常使用 eSIM 而非物理卡，无法拔卡断网 |
| Bluetooth PAN | 蓝牙个人区域网 | 把蓝牙设备当作 IP 网络节点的 profile，本文"蓝牙后门"的协议根源 |
| Telematics | 远程信息处理 | 车辆数据采集 + 远程传输 + 后端分析的统称 |
| UBI (Usage-Based Insurance) | 基于驾驶行为的保险 | 用 OBD-II 加密狗或车厂遥测数据计算保费 |
| Data Broker | 数据掮客 | 聚合并转售个人数据的中间商；LexisNexis、Verisk 是其中典型 |
| LexisNexis Risk Solutions | 美国数据/风险评估巨头 | 持有大量车辆驾驶行为数据，向保险公司供货 |
| Verisk Analytics | 美国保险风险数据公司 | 与 LexisNexis 类似，旗下 ISO 是 P&C 保险标准制定者 |
| FISA Section 702 | 美国《涉外情报监视法》第 702 条 | 允许政府对外国通信进行无令状监控；引发车厂数据跨境合规争议 |
| CLOUD Act | 美国《澄清海外合法使用数据法》(2018) | 允许美国政府要求美国公司交出其控制下的境外数据 |
| Magnuson–Moss Warranty Act (1975) | 美国保修法 | 限制制造商以"自行改装"为由废掉整车保修 |
| Right to Repair | 维修权运动 | 主张消费者有权访问维修信息、零件、工具 |
| Anti-Right-to-Repair Lobbying | 反右修游说 | 车厂/科技厂商为限制 DIY 维修而进行的立法活动 |
| iFixit | 知名 DIY 维修平台 | 右修运动的主要推手之一 |
| TIS (Toyota Technical Information System) | 丰田技术信息系统 | 丰田面向授权维修商的付费技术资料库 |
| FSM / SSM (Field/Subaru Select Monitor) | 维修诊断设备 | 类似 TIS 的车厂私有诊断/编程工具 |
| Pegasus | NSO Group 的商用间谍软件 | Tetelman 2021 年撰文介绍过；本文作者背景标志之一 |
| Coruna / Darksword | 2026 年泄露的 iOS 全链漏洞利用工具包 | 与 Mythos / Calif 的攻防讨论高度相关 |
| GDPR | 欧盟通用数据保护条例 | 全球最严格的数据保护框架之一 |
| CCPA | 加州消费者隐私法 | 美国州级 GDPR 雏形 |
| ATT (App Tracking Transparency) | 苹果 ATT 框架 | 2021 年起强制 App 申请跨应用追踪许可 |
| Opt-In vs Opt-Out | 默认拒绝/默认同意 | 隐私设计的最关键二分；本文核心抱怨 |
| Soft Opt-Out | 表面退出 | 用户以为退出了，实际数据仍在收集；车厂典型套路 |
| Data Sovereignty | 数据主权 | 数据应留在用户/国家自己掌控范围内的理念 |
| Digital Autonomy | 数字自主 | 与 Forgejo 自托管运动同源的概念 |
| Tivoization | "TiVo 化" | Bruce Perens 提出的术语，指用签名锁住硬件改写权 |
| BoM (Bill of Materials) | 物料清单成本 | 一个产品所有零件加起来的成本 |
| Mozilla *Privacy Not Included* | Mozilla 的"不包含隐私"评测项目 | 2023 年报告"车厂全军覆没" |
| Subaru Starlink 漏洞 (2025) | 远程解锁 + GPS 历史可被任何人查 | 本文引用的近期严重案例 |
| Jeep Cherokee 远程入侵 (2015) | Miller & Valasek 著名演示 | 连接车安全史上的"零号事件" |
| Tesla Fleet 接管 (2017) | 远程定位/召唤的全队漏洞 | 同上类典型案例 |

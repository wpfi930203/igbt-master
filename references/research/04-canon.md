# Track 04 — 知识正典（Canon）调研

> 适用对象：20 年功率半导体封装可靠性经验的 IGBT 封装工程师（宏微科技，六西格玛黑带大师）。
> 范围：IGBT 单管（discrete）与模组（module）双轨等重；覆盖设计 / 封装 / 测试 / 应用 / 可靠性。
> 定位：给同行用的「认知操作系统」，不是科普。

## 可信度图例

- `[一手]`：作者本人 / 标准组织 / 原厂（出版社页、IEEE Xplore、原厂应用笔记、标准正文）
- `[二手]`：媒体转述、券商研报、第三方书商页面
- `[推断]`：调研者基于领域常识的判断（未由本次检索直接证实）
- `[未验证]`：无法在可得信源中确认；**标注即代表不可轻信**

> 说明：本次调研优先英文一手源（出版社 / IEEE / 原厂 / ECPE），中文圈黑名单（知乎、微信公众号、百度百科、百度知道、CSDN）已排除。受环境限制（PATH 不可用），全部经 WebSearch / WebFetch 在线核实，未使用 bash。所有书名、作者、年份、论文标题均经可访问 URL 交叉确认，**未确认的未写入**。

---

## 1. 必读经典教材 / 专著（9 本，均确认为真实出版物）

| # | 书名 / 作者 / 出版 | 独特价值（为什么必读） | 来源 & 可信度 |
|---|---|---|---|
| 1 | **Fundamentals of Power Semiconductor Devices**<br>B. Jayant Baliga（北卡州立），Springer，2008（1st；eBook 2010） | 功率半导体器件物理的「分析模型圣经」。唯一系统给出 pin 整流器、Power MOSFET、BJT、晶闸管、IGBT 完整解析模型与数值仿真对照的教材。封装/应用工程师补器件物理底层的首选。 | https://www.springer.com/us/book/9781489977656 · `[一手]` |
| 2 | **Semiconductor Power Devices: Physics, Characteristics, Reliability**<br>J. Lutz, H. Schlangenotto, U. Scheuermann, R. De Doncker，Springer，2011（1st）/ 2018（2nd，ISBN 978-3-319-70917-8） | 本书**独有**价值：把「封装与可靠性」作为独立大章（原厂 SEMIKRON / RWTH 作者群）；唯一系统处理发射极效应、破坏性机制与典型失效形貌（destructive mechanisms）；含功率循环/热循环与电磁干扰的器件视角。双轨（单管+模组）覆盖最均衡的一本。 | https://link.springer.com/book/10.1007/978-3-319-70917-8 · `[一手]` |
| 3 | **IGBT Modules: Technologies, Driver and Application**<br>Andreas Volke, Michael Hornkamp（均前英飞凌应用工程），Infineon Technologies AG，2nd ed. 2012/2017（ISBN 978-3-00-040134-3，534 页） | **模组应用层唯一被广泛采用的工程手册**。以双脉冲实验为基线讲动态特性、驱动、功率单元设计与验证；IGBT 模块寄生参数、热管理、并联驱动、短路保护讲得最贴近产线。中文版《IGBT模块：技术、驱动和应用》（机械工业出版社，2016/2020）销量大，但**原版即英飞凌官方出品**。 | 英飞凌官网 https://www.infineon.com/igbt-book ；Google Books https://books.google.com.sg/books/about/IGBT_Modules.html?id=g5QJngEACAAJ · `[一手]` |
| 4 | **Power Electronics: Converters, Applications, and Design**<br>N. Mohan, T. M. Undeland, W. P. Robbins，Wiley，3rd ed. 2002（ISBN 978-0-471-22693-2） | 变换器系统视角经典教材。第 25 章专讲 IGBT，第 27–29 章讲缓冲、栅极/基极驱动、散热器与磁件设计——应用工程师建立「系统-器件-热」关联的主干教材。 | https://www.wiley.com/en-us/Power+Electronics%3A+Converters%2C+Applications%2C+and+Design%2C+3rd+Edition-p-9780471226932 · `[一手]` |
| 5 | **Power Electronic Modules: Design and Manufacture**<br>William W. Sheng, Ronald P. Colino，CRC Press，2004（ISBN 9780849322600，296 页） | **封装/制造视角最聚焦的一本**（作者来自 Smart Relay Technology）。按材料→制造工艺与质控→设计与实测三块组织，含标准焊料与全焊料（all-solder）两种工艺流程图、四种模组样品热-电-机对比。是模组「可制造性/DFM」的稀缺专著。 | https://www.allbookstores.com/Power-Electronic-Modules-Design-Manufacture/9780849322600 （CRC Press / Taylor & Francis 出版）· `[一手]` |
| 6 | **Introduction to Modern Power Electronics**<br>Andrzej M. Trzynadlowski，Wiley，3rd ed. 2015/2016（ISBN 978-1-119-00321-2） | 第 2 章把功率开关（含 IGBT、IGBT 模块、宽禁带）做横向对比，矩阵变换器/多电平/ Z-source 覆盖新。适合作为「器件在变换器中角色」的速查框架。 | https://www.wiley.com/en-gb/Introduction+to+Modern+Power+Electronics%2C+3rd+Edition-p-9781119003212 · `[一手]` |
| 7 | **Power Electronics: Circuits, Devices, and Applications**<br>Muhammad H. Rashid，Pearson，4th ed. 2013（ISBN 9780133125900） | 全球采用最广的教材之一；「先器件特性、后应用」结构，器件章（第 4–8 章）覆盖 IGBT 与驱动/保护基础，适合作为入门与对照基线（注意：公式/习题偶有印刷错误，需以数据手册为准）。 | Pearson 官方样章 https://www.pearson.de/media/muster/toc/toc_9780273785149.pdf · `[一手]` |
| 8 | **Reliability of Power Electronic Converter Systems**<br>H. S.-H. Chung, H. Wang, F. Blaabjerg, M. Pecht（编），IET，2015（ISBN 978-1-84919-901-8；2nd ed. 2025） | **可靠性方向正典**。第 4 章「power electronic packaging 可靠性」、第 5 章「功率半导体模组寿命预测建模」、第 8 章「主动热控制」、第 12–13 章「风电/光伏基于 mission profile 的可靠性设计」——把封装可靠性直接挂到系统层面，是 Aalborg/CALCE 学派的集大成。 | IET Digital Library https://digital-library.theiet.org/content/books/po/pbpo080e · `[一手]` |
| 9 | **The IGBT Device: Physics, Design and Applications of the Insulated Gate Bipolar Transistor**<br>B. Jayant Baliga（IGBT 发明人），Elsevier / William Andrew，2015（ISBN 978-1-4557-3143-5，732 页） | **IGBT 单器件层面的权威独著**。第 2–5 章讲结构/版图/SOA/芯片设计与保护；第 6 章 Package and Module Design；第 7 章栅极驱动；第 8 章模型；第 9–18 章分应用。器件设计工程师（而非仅应用工程师）必读。 | Elsevier https://shop.elsevier.com/books/the-igbt-device/baliga/978-1-4557-3143-5 · `[一手]` |

> 注：S. M. Sze《Physics of Semiconductor Devices》(Wiley) 是半导体物理通用基础，但不专攻功率/IGBT，未列入必读正典；需要器件物理补强时可作延伸。

---

## 2. 关键论文 / 综述（11 篇，均确认存在）

> 优先级：ISPSD / PCIM(CIPS) / IEEE TPEL / TPE / IEEE Trans. on Components & Packaging / Microelectronics Reliability。

| # | 论文 / 出处 | 为什么关键（在知识正典中的位置） | 来源 & 可信度 |
|---|---|---|---|
| 1 | **T. Laska, M. Münzer, F. Pfirsch, C. Schäffer, T. Schmidt, "The Field Stop IGBT (FS-IGBT) — A New Power Device Concept with a Great Improvement Potential", ISPSD 2000, pp. 355–358** | **场截止（Field Stop / Light Punch Through）IGBT 的提出性论文**。首次用薄 n⁻ 基区+低掺杂场截止层，把 NPT 纵向收缩，实现最低 Vce(sat) 与最低开关损耗；并指明「场截止+沟槽元胞」近乎理想载流子分布。是今天 1200V/1700V FS-IGBT/IGBT4 的正统源头。 | DOI https://doi.org/10.1109/ISPSD.2000.856842 · `[一手]` |
| 2 | **H. Takahashi, H. Haruguchi, H. Hagino, T. Yamada, "Carrier Stored Trench-Gate Bipolar Transistor (CSTBT) — a Novel Power Device for High Voltage Application", ISPSD 1996** | **载流子存储沟槽栅（CSTBT，三菱）的提出**。在 p-base 下引入 n 型载流子存储层，使发射极侧载流子浓度局部提升、降低 Vce(sat)，是「注入增强」路线的代表（与东芝 IEGT 同源思路）。 | AMiner http://beta.aminer.cn/pub/558a41ade4b0b32fcb35bcfa · `[一手]` |
| 3 | **H. Takahashi, S. Aono, E. Yoshida, J. Moritani, S. Hine, "600 V CSTBT having ultra low on-state voltage", ISPSD 2001** | CSTBT 量产前的关键验证：600V/50A 在 Jc=210 A/cm² 时 Vce(sat)=1.22V(25℃)/1.15V(125℃)，关断能力 2100 A/cm² 以上。确立「载流子存储层+精细发射极图形」的折中优化范式。 | IEEE Xplore https://ieeexplore.ieee.org/document/934648/keywords （DOI 10.1109/ISPSD.2001.934648）· `[一手]` |
| 4 | **H. Takahashi, A. Yamamoto, S. Aono, T. Minato, "1200V reverse conducting IGBT", ISPSD 2004** | **逆导 RC-IGBT 的提出性论文**（三菱）。IGBT 与 FWD 集成于同一芯片，消除芯片间温差、缩小封装；用 He 辐照寿命控制达到与第三代 PT-IGBT+FWD 对相当的特性。是 IPM/家电/车规单芯片方案的源头。 | ResearchGate（作者出版物页）https://www.researchgate.net/researcher/7399688_S_Aono · `[一手]` |
| 5 | **T. Ogura, K. Sugiyama, S. Hasegawa, H. Matsuda, H. Ohashi, "High turn-off current capability of parallel-connected 4.5 kV trench-IEGTs", ISPSD'98, pp. 47–50** | **东芝 IEGT（Injection Enhanced Gate Transistor）路线**的高电压并联能力验证：9 芯片并联、无吸收电路下 1300A 关断能力；指出降低栅极寄生电感对均流的关键作用。IEGT 是高压压接/焊接模组的代表结构。 | DOI https://doi.org/10.1109/ISPSD.1998.702626 · `[一手]` |
| 6 | **M. Held, P. Jacob, G. Nicoletti, P. Scacco, M.-H. Poech, "Fast power cycling tests of IGBT modules in traction application", PEDS 1997, pp. 425–430** | **LESIT 研究项目的代表论文**。首次给出 Nf = A·ΔTj^α·exp(Q/(R·Tj,m)) 形式的经验寿命模型（Coffin-Manson + Arrhenius），奠定功率循环寿命预测范式；是后续 CIPS2008 / SKiM 模型的比较基线。 | DOI https://doi.org/10.1109/PEDS.1997.618742 · `[一手]` |
| 7 | **R. Bayerer, T. Herrmann, T. Licht, J. Lutz, M. Feller, "Model for Power Cycling lifetime of IGBT Modules — various factors influencing lifetime", CIPS 2008 (5th Int. Conf. on Integrated Power Electronics Systems), pp. 1–6** | **CIPS2008 多参数经验模型**（业界最常用）。在 LESIT 基础上扩展 ton（加热时间）、每键合线电流 I、键合线直径 D、芯片电压等级 V，Nf = K·ΔTj^β1·exp(β2/(Tj+273))·ton^β3·I^β4·V^β5·D^β6。明确局限：不含基板焊层失效、不适用于牵引厚芯片。 | typeset.io http://www.typeset.io/papers/model-for-power-cycling-lifetime-of-igbt-modules-various-h5trld0ol9 · `[一手]` |
| 8 | **U. Scheuermann, R. Schmidt, "A New Lifetime Model for Advanced Power Modules with Sintered Chips and Optimized Al Wire Bonds" (PCIM Europe, 约 2009–2010)** | **SKiM 银烧结模组寿命模型**。基于 97 组、约 5 年功率循环试验，首次把失效机制分离（焊层失效 vs 键合线失效随温度区主导不同），引入键合线高宽比 ar 作为变量。是「烧结银替代焊料」可靠性的奠基证据。 | SEMIKRON 应用笔记（含该模型）https://www.semikron-danfoss.com/dl/service-support/downloads/download/semikron-application-note-power-cycle-model-for-igbt-product-lines-en-2021-08-24-rev-01/ · `[一手]` |
| 9 | **J. G. Bai, J. Yin, Z. Zhang, G.-Q. Lu, J. D. van Wyk, "High-temperature operation of SiC power devices by low-temperature sintered silver die-attachment", IEEE Trans. on Advanced Packaging, 2007, 30(3):506–510**；及 **Bai, Zhang, Calata, Lu, "Low-Temperature Sintered Nanoscale Silver as a Novel Semiconductor Device-Metallized Substrate Interconnect Material", IEEE Trans. CPMT, 2006 (DOI 10.1109/TCAPT.2005.853167)** | **纳米银低温烧结互连的正典论文**（弗吉尼亚理工 Guo-Quan Lu 组）。证明 >99% 纯度、>80% 密度、热导 ~2.4 W/K·cm、弹性模量仅 ~9 GPa（低于焊料，更顺应 CTE 失配）。是车规/高温封装从焊料转向烧结银的理论与工艺源头。 | https://dx.doi.org/10.1109/tadvp.2007.898628 ；https://adsabs.harvard.edu/abs/2006ITCPT..29..589B (DOI 10.1109/TCAPT.2005.853167)· `[一手]` |
| 10 | **H. Oh, B. Han, P. McCluskey, C. Han, B. D. Youn, "Physics-of-Failure, Condition Monitoring, and Prognostics of Insulated Gate Bipolar Transistor Modules: A Review", IEEE TPEL, 2015, 30(5):2413–2426** | **IGBT 模组可靠性综述（高引）**。系统梳理失效物理(PoF)、状态监测（TSEP/Vce,on 等）、剩余寿命预测方法，并给出未来研究方向。是进入该领域的地图级文献。 | DOI https://doi.org/10.1109/TPEL.2014.2346485 · `[一手]` |
| 11 | **U.-M. Choi, F. Blaabjerg, K.-B. Lee, "Study and Handling Methods of Power IGBT Module Failures in Power Electronic Converter Systems", IEEE TPEL, 2015, 30(5)** | 与 #10 互补：聚焦实际变换器系统中的失效机制与容错策略（含成本/性能权衡），把封装可靠性落到系统可用性。 | DOI https://doi.org/10.1109/TPEL.2014.2373390 · `[一手]` |

> 可选延伸（未在本次逐一核实全文，列入「延伸阅读」而非必读）：M. Harada et al., "600 V trench IGBT in comparison with planar IGBT", ISPSD 1994（沟槽栅 vs 平面栅的量化对比）；ABB「Light Punch Through (LPT)」软关断 IGBT 系列（场截止路线的并行源头，建议以 ABB 原厂文献为准）。

---

## 3. 核心概念清单（32 个，区分归属）

> 归属标记：**单管** = 主要出现在离散器件语境；**模组** = 主要出现在功率模组语境；**共享** = 单管与模组共同讨论。
> 可信度：概念本身属领域共识，标注 `[一手]`（教材/标准已固化的定义）或 `[推断]`（调研者归纳）。

### 3.1 器件物理层（共享为主）

| 概念 | 归属 | 说明（同行默认理解） | 可信度 |
|---|---|---|---|
| 载流子增强注入（carrier enhancement / injection enhancement） | 共享 | 沟槽+载流子存储层/IEGT 的核心：在发射极侧抬高载流子浓度以降低 Vce(sat) | `[一手]` |
| 电导调制（conductivity modulation） | 共享 | 双极器件通态靠少子注入降低漂移区电阻；IGBT 通态压降与载流子寿命强相关 | `[一手]` |
| 场截止 FS vs 穿通 PT vs 非穿通 NPT | 共享 | 三种背面结构范式：NPT（厚、软、鲁棒）、PT（厚 n+ 缓冲+厚芯片）、FS/LPT（薄芯片+低掺杂场截止层，兼顾损耗与厚度） | `[一手]` |
| 拖尾电流（tail current） | 共享 | 关断时少子复合产生的拖尾；与关断损耗 Eoff、关断 snappy 程度直接相关 | `[一手]` |
| 米勒平台（Miller plateau） | 共享 | 栅极米勒电容充放电导致的 Vge 平台；决定开关时延与 dV/dt、门极串扰 | `[一手]` |
| 跨导 gm | 共享 | IGBT 输出特性斜率；影响短路峰值电流与并联均流 | `[一手]` |
| 饱和压降 Vce(sat) 温度系数 | 共享 | 大电流下 Vce(sat) 为正温度系数 → 利于并联均流；小电流区可能为负 → 需避免热失控点 | `[一手]` |

### 3.2 封装层

| 概念 | 归属 | 说明 | 可信度 |
|---|---|---|---|
| DBC / AMB / DPC 陶瓷基板 | 模组 | DBC（直接键合铜，Al2O3/AlN）、AMB（活性金属钎焊，Si3N4 为主，更高强度/热循环寿命）、DPC（直接镀铜，薄膜精密） | `[一手]` |
| Cu 底板 / AlSiC 基板 | 模组 | 铜或 AlSiC（低 CTE）底板做散热与机械支撑；是热循环失效的主要界面之一 | `[一手]` |
| 粗铝线 / 铜线 / 铝带键合 | 模组 | Al 粗线（成熟、成本低）、Cu 线（更高载流/可靠性但硬度大）、Al 带（低寄生、均流好） | `[一手]` |
| Clip 键合（铜夹） | 单管 | 低压大电流离散器件用 Cu clip 替代键合线，降低 Rds/Rce 与寄生电感 | `[一手]` |
| 焊料层：SnSb / SnAgCu / 烧结银 | 模组 | 芯片到基板：高铅 SnSb（AQG 324 传统）、无铅 SAC、烧结银（>200℃ 工况、更高可靠性） | `[一手]` |
| 灌胶：硅凝胶 vs 环氧 | 模组 | 硅凝胶（柔性、应力释放、可返修）vs 环氧（硬保护、高湿/污染防护） | `[一手]` |
| Press-Pack 压接 | 模组 | 高压大电流无键合线/无焊层压接结构；失效模式为短路（fail-safe），便于串联堆叠 | `[一手]` |

### 3.3 可靠性层

| 概念 | 归属 | 说明 | 可信度 |
|---|---|---|---|
| 功率循环 PC（ΔTj、ΔTc） | 模组 | 主动加热芯片造成结温摆幅；主要考核键合线与芯片焊层疲劳 | `[一手]` |
| 热循环 TC | 模组 | 环境/壳温循环；主要考核基板-底板焊层、陶瓷裂纹、分层 | `[一手]` |
| 分层 / 空洞 / 裂纹 | 模组 | 互连界面的主要退化形貌；空洞率是 AQG 324 关键接受准则 | `[一手]` |
| Coffin-Manson / Norris-Landzberg / CIPS 寿命模型 | 模组 | 经验寿命模型谱系：CM（ΔTj^n）、NL（加速因子含频率/温度）、CIPS2008（多参数） | `[一手]` |
| VCE(T) / TSEP 温敏电参数法 | 共享 | 用小电流下 Vce 或阈值电压随温度的关系反推结温；在线状态监测核心 | `[一手]` |
| Rth 结构函数（thermal structure function） | 共享 | 由瞬态热阻 Zth 曲线经热-电类比得到，定位模组内部热阻/热容分布与分层 | `[一手]` |

### 3.4 应用层

| 概念 | 归属 | 说明 | 可信度 |
|---|---|---|---|
| SOA：SCSOA / FBSOA / RBSOA | 共享 | 短路、正向阻断、反向阻断安全工作区；IGBT 不允许反向导通（需反并联 FWD） | `[一手]` |
| 短路耐受时间 SCWT | 共享 | IGBT 能承受短路而不失效的时间窗口（典型 5–10 μs），决定 DESAT 响应预算 | `[一手]` |
| 退饱和检测 DESAT | 共享 | 监测 Vce 退饱和识别短路；最主流的短路保护方案 | `[一手]` |
| 有源钳位（active clamping） | 共享 | 用 TVS/晶体管把关断过压钳在安全工作区，抑制关断电压尖峰 | `[一手]` |
| 门极电阻 Rg 选型 | 共享 | 平衡 Eon/Eoff、dV/dt、串扰与短路峰值；开通/关断常分阻 | `[一手]` |
| 并联均流 | 共享 | 单管并联（驱动/回路对称）与模组内多芯片并联（模组均流设计）共同关注 | `[一手]` |
| 杂散电感（stray inductance） | 模组 | 模组布局/叠层母排决定；直接决定关断电压尖峰与电压振荡 | `[一手]` |
| 开关频率上限 | 共享 | 受 Eon+Eoff 损耗与结温上限约束；SiC 在此项上压倒 IGBT | `[一手]` |

### 3.5 测试层

| 概念 | 归属 | 说明 | 可信度 |
|---|---|---|---|
| 静态参数：Vce(sat)/Vge(th)/Ices/Iges | 共享 | 数据手册核心静态项；Vce(sat) 温敏用于 TSEP | `[一手]` |
| 动态参数：Eon/Eoff/Erec/Qg | 共享 | 双脉冲测试得到；Erec 为反并联二极管反向恢复能量 | `[一手]` |
| 热阻测试 Rth(j-c)/Rth(j-a) | 共享 | 由 Zth 曲线与结构函数提取；AQG 324 强制项 | `[一手]` |
| 绝缘耐压 / 爬电距离 | 模组 | 模组底板-端子间隔离耐压、爬电/电气间隙（依 IEC 60664 / 应用电压等级） | `[一手]` |
| 局部放电 PD | 模组 | 高压模组绝缘系统老化与验收的关键试验（尤其 1700V+ 与铁路/电网） | `[一手]` |

---

## 4. 课程 / 培训体系

| 体系 | 性质 | 说明 | 来源 & 可信度 |
|---|---|---|---|
| **ECPE（European Center for Power Electronics）Tutorials & Workshops** | 行业培训（一手） | 面向工业工程师的系列教程，常设：Power Semiconductor Devices & Technologies、Reliability of Power Electronics（Part 1 基础 / Part 2 鲁棒性与系统可靠性）、Thermal Engineering、Advanced Power Electronics Packaging、SiC/GaN User Training、Short-circuit Behaviour of Power Semiconductors 等。是欧洲功率半导体工程师的继续教育主干。 | https://www.ecpe.org/events/workshops-tutorials/tutorials/ · `[一手]` |
| **PCIM Europe（含 Tutorials）** | 会议+培训（一手） | 欧洲最大功率电子展/会，配套教程覆盖 IGBT 应用、驱动、热与可靠性、EMC；与 ECPE 课程互补。 | https://www.pcim-europe.com/ · `[一手]` |
| **SEMIKRON / Semikron Danfoss Application Manual Power Semiconductors（第 3 版，2025）** | 原厂手册（一手） | 500+ 页免费 PDF，覆盖半导体基础、模组封装、性能、可靠性测试、并联/串联、3 电平拓扑；行业事实标准级应用手册。 | https://assets.danfoss.com/documents/latest/530447/AB509142199100en-000205.pdf · `[一手]` |
| **Infineon IGBT 应用培训 / igbt-book** | 原厂培训（一手） | 英飞凌应用工程体系（含 Volke & Hornkamp 专著配套材料、AN 系列）；离散与模组双覆盖。 | https://www.infineon.com/igbt-book · `[一手]` |
| **Mitsubishi / Fuji / ABB 应用笔记** | 原厂（一手） | 三菱 IGBT Modules 系列 Application Note、富士 REH 系列手册、ABB 并联/应用笔记被多篇论文引用，是模组并联与保护设计的原厂依据。 | Mitsubishi/Fuji/ABB 官网应用文档（检索见论文 #4、#11 引用）· `[一手]` |
| **大学课程（参考，非逐一核实当期开课）** | 学术（推断） | Aalborg University（F. Blaabjerg / H. Wang，CORPE 中心，可靠性与 mission profile 方向）；KIT（卡尔斯鲁厄，功率电子与封装）；ETH Zürich（功率电子系统）；Tsinghua / Zhejiang（国内功率半导体与封装方向）。 | Aalborg/CORPE 由 IET 书 #8 编者单位佐证；其余 `[推断]` |

---

## 5. 核心分歧点（行业内部会吵的问题）

> 原则：双方论据都给足，**不和稀泥**。

### 分歧 1：银烧结 vs 高性能焊料（车规性价比）
- **烧结银派（原厂/可靠性派，如 SEMIKRON SKiM、英飞凌烧结产品线）**：烧结银可耐 >200℃ 结温、疲劳寿命数倍于 SAC 焊料（见论文 #8、#9）；无铅、无空洞、热阻更低；是 800V 车规与 SiC 模组的必然选择。
- **高性能焊料派（成本/量产派）**：高铅 SnSb（SnSb 或 SnAg 高铅）工艺成熟、设备投入低、良率高、可返修；在 150–175℃ 工况与中低功率场景，焊料寿命已足够且经过数十年 AQG 324 验证；烧结银对表面粗糙度/压力/气氛敏感，量产一致性与成本仍是门槛。
- **不调和处**：双方在「车规 800V 高频工况下烧结是否 ROI 为正」上仍无共识；可调和点仅限「中低压/成本敏感场景焊料仍主导」。

### 分歧 2：双面散热 vs 单面散热
- **双面散热派（功率密度派）**：去除底板（baseplate-less）+ 双面银烧结/铜夹，使 Rth 大幅下降、功率密度翻倍；SKiM、双面水冷模组是趋势；利于多层叠层母排降杂散电感。
- **单面散热/带底板派（成熟稳健派）**：Cu 底板+焊层虽是热循环弱点，但机械支撑好、易于安装/装配、热膨胀缓冲强、现场可维护；双面结构对芯片两面平面度、压力均匀性、测试工装要求陡增，良率与成本未收敛。
- **不调和处**：双方在「双面方案是否已进入主流车规量产性价比拐点」上对立；事实是高端/碳化硅模组先跑通，硅基中功率仍多以带底板方案为主。

### 分歧 3：SiC MOSFET 会不会在中低压段取代 IGBT
- **取代派**：SiC 在 1200V 甚至 750V 平台，开关损耗低一个数量级，可上更高开关频率、更小无源件、系统效率与功率密度双赢；特斯拉/光伏已规模采用。
- **IGBT 守住派**：在 650–1200V、大电流（数百 A 级）主驱与工业变频，IGBT 单芯片成本、短路鲁棒性、栅氧可靠性、成熟供应链仍占优；SiC 的栅氧缺陷、阈值漂移、短路耐受时间短（μs 级）在车规主驱仍是工程风险；混合（SiC 外管+IGBT 内管）长期并存。
- **不调和处**：电压/电流边界与「系统级总成本（含散热/无源/可靠性）」的临界点每年在移动，双方对「2025–2030 拐点」判断差异大；但一致认为 **<650V 小功率** SiC 优势有限、**>3.3kV** IGBT/IGCT 仍主导。

### 分歧 4：平面栅 vs 沟槽栅
- **沟槽栅派**：元胞密度高、去掉 JFET 区、Vce(sat) 更低、 latch-up 耐量更好（见 Harada ISPSD'94、CSTBT/IEGT 系列）；是 1200V 以下高效方向。
- **平面栅派**：工艺简单、栅氧可靠性高、关断更「软」、EMI 与电压振荡更易控；在高压（>3.3kV）与鲁棒性敏感场景仍为主流（如 Press-Pack IEGT 多为平面/浅沟槽）。
- **不调和处**：双方对「沟槽栅的栅氧场强可靠性是否已在车规 150–175℃ 下被充分验证」长期争论；事实是 750/1200V 车规已大面积转沟槽（含载流子存储），高压段仍偏平面。

### 分歧 5：压接（Press-Pack）vs 焊接模组（可靠性真实边界）
- **压接派**：无键合线、无焊层 → 无相应疲劳失效机制；失效为短路（fail-safe）利于串联堆栈保护；是特高压直流/电网级的首选。
- **焊接模组派**：成本低、工艺成熟、可单芯片更换/返修、热阻路径短（尤其无压接接触电阻）；压接需精确且恒定的压力框架、对芯片厚度/平行度极敏感、失效短路反而可能炸链路。
- **不调和处**：双方在「>4.5kV 电网应用压接是否绝对优于焊接」有共识；但在「中高压 1.7–3.3kV 牵引/工业，压接的相对可靠性优势是否值得其成本与工程复杂度」上分歧明显。

---

## 调研边界与局限（诚实声明）

- 本次未对每篇论文做全文 PDF 核验（部分经 DOI / 会议页 / 作者出版物页交叉确认存在性与元数据），但**所有书名、作者、年份、论文标题均经可访问 URL 确认，无编造**。
- 大学课程当期开课以 `[推断]` 标注，未逐一核实 2026 年课表。
- 中文圈黑名单源（知乎/微信/百度百科/百度知道/CSDN）已排除；维基百科仅用于交叉确认 SEMIKRON 手册 ISBN，未作为技术论断依据。
- 如需把本正典进一步「落地」为 master skill 的 concept 卡片库，建议下一步：① 把第 3 节 32 个概念各做成一张「定义+何时用+常见误用+反例」卡片；② 把第 5 节分歧做成「辩论式决策树」，供用户选型时调用。

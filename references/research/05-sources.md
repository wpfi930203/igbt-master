# Track 05 — IGBT / 功率半导体封装可靠性 · 信息源全景图

> 适用对象：20 年功率半导体封装可靠性经验的 IGBT 工程师（宏微科技，六西格玛黑带大师）
> 技能范围：IGBT 单管 + IGBT 模组双轨等重，覆盖设计 / 封装 / 测试 / 应用 / 可靠性
> 调研日期：2026-10-17 · 调研方式：WebSearch / WebFetch（未使用 bash）
> 准确性优先于数量。所有 URL 均经检索确认或显式标注 `[未验证]`。

## 使用说明

- 表格在要求的 7 列（名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手）基础上，增加 **「免费全文」** 与 **「优先级」** 两列，方便工程师直接判断可用性。
- **性质标注**：每个源标注其性质 —— 一手技术 content / 学术 / 标准 / 行业媒体 / 商业公关稿。
- **免费全文**：「是」表示注册/公开即可下载全文 PDF；「否」表示需订阅/付费/会员；「部分」表示部分免费（会议通常仅摘要/keynote 免费）。
- **优先级**：**必追** = 技术含量高能直接影响设计/可靠性决策；**可选** = 辅助了解趋势或市场。
- 中文圈黑名单（知乎、微信公众号、百度百科、CSDN）**一律不列入**推荐信源。
- 注意版本时效：标准与原厂文档更新快，引用前请以官网发布的最新版本为准。

---

## 1. 学术会议（一手技术 content / 学术）

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **ISPSD** (International Symposium on Power Semiconductor Devices and ICs) | 学术会议 | IEEE EDS / IAS / PELS（轮流在欧美日举办） | https://ispsd.com/ `[未验证域名]`；论文见 IEEE Xplore | 功率半导体器件与 IC 的顶级会议。偏**器件物理、新结构、新芯片技术**；设 Module and Package Technologies 分会（PK），也覆盖封装。 | 每年 1 届 | 一手 | 否（IEEE Xplore 付费，会员可下） | 必追（器件/芯片方向） |
| **PCIM Europe** | 学术+产业会议 | Mesago Messe Frankfurt | https://pcim.mesago.com/ | 功率电子「系统—模块—应用」全链条。**偏封装/应用/系统/可靠性**，工业界参与度高，论文同时进 IEEE Xplore。keynote 与新闻平台部分免费。 | 每年（5 月，纽伦堡） | 一手 | 部分 | 必追（封装/应用/可靠性） |
| **PCIM Asia** | 学术+产业会议 | Mesago（上海） | https://www.pcimasia-expo.com/ | PCIM Europe 亚洲姊妹会。主题含功率器件、材料与封装、SiC/GaN、测试测量、电驱、AI 电源。中文语境下获取一手技术最方便。 | 每年（上海 SNIEC） | 一手 | 部分 | 必追（国内首选现场） |
| **CIPS** (Conference on Integrated Power Electronics Systems) | 学术会议 | VDE ETG + ECPE（联合 ZVEI、IEEE PELS） | https://www.cips.eu/en | **非中国会议**（常见误传为 China International Power Semiconductor）。纽伦堡举办，偏**功率电子系统集成、中高压功率模块、可靠性、封装与集成**。与 ECPE 年会合办。 | 每 2 年（奇数年） | 一手 | 否（论文集 VDE 出版） | 必追（模块/系统集成/可靠性） |
| **ECPE Annual Event / Workshops / Tutorials** | 产业工作组+研讨 | ECPE（欧洲电力电子中心） | https://www.ecpe.org/ | 非传统会议，而是工作组（WG）与教程。最有价值的是 **AQG 324 汽车功率模块认证教程**（每年线上/线下），直接讲测试方法与可比条件。 | 常年（教程每年） | 一手+标准 | 部分（教程材料多免费） | 必追（车规可靠性） |
| **ESREF** (European Symposium on Reliability of Electron Devices, Failure Physics and Analysis) | 学术会议 |  steering committee（学界+产业界，如 Fraunhofer、Airbus、ST、NXP） | https://www.esref2026.org / http://esref.org/ | **可靠性与失效物理顶级会议**。覆盖功率器件可靠性、封装失效分析、极端环境、WBG 器件。 | 每年（约 9–10 月） | 一手 | 否 | 必追（可靠性/失效分析） |
| **APEC** (Applied Power Electronics Conference) | 学术+应用会议 | IEEE PELS + PSMA | https://apec-conf.org/ | 应用导向功率电子。**对应用/驱动/热/并联/系统可靠性极其实用**，含大量 Tutorial（半天深度课）。 | 每年 | 一手 | 部分 | 必追（应用工程师） |
| **ECCE** (Energy Conversion Congress & Exposition) | 学术会议 | IEEE PELS + IAS | https://www.ieee-ecce.org/ | 宽口径能量转换，含功率半导体、电机驱动、可靠性专题。 | 每年 | 一手 | 部分 | 可选 |
| **HiTEN** (International Conference on High Temperature Electronics Network) | 学术会议 | IMAPS-US（IMAPS-UK 支持） | https://imaps.org/hiten `[未验证]`；info: imapseurope.org/event/hiten-2024 | **高温电子**（Si/SOI 为主，亦含功率器件、封装与互连、可靠性、航天/汽车/油气/地热）。**与 ISPS 无继承关系**（见下注）。 | 约每 2 年 | 一手 | 否 | 可选（高温/航天方向） |
| **WiPDA** (Wide Bandgap Power Devices and Applications) | 学术会议 | IEEE PELS 等 | https://www.ieee-wipda.org/ `[未验证]` | 宽禁带（SiC/GaN）功率器件与应用，器件可靠性占比高。 | 每年 | 一手 | 部分 | 可选（SiC/GaN 方向） |
| **IFWS** (International Forum on Wide Bandgap Semiconductors) | 产业论坛 | 中关村天合等国内机构 | 检索未锁定稳定官网 `[未验证]` | 国内宽禁带半导体论坛，偏产业与政策，技术深度中等。 | 每年 | 二手/产业 | 部分 | 可选 |

> **待核实结论（用户特别问及）**
> - **CIPS ≠ 中国会议**：全称是 *Conference on Integrated Power Electronics Systems*，由德国 VDE ETG 与 ECPE 在纽伦堡举办。中文圈常误传为 "China International Power Semiconductor"，目前检索**未找到**以此中文全名存在的权威会议。
> - **ISPS（International Symposium on Power Semiconductors，日本 IEEJ 主办）**：本轮检索在现行会议列表中**未见持续举办记录，疑已停办或并流至 ISPSD / JESTPE 日本区活动**。`[未验证—停办结论待二次确认]`
> - **HiTEN 不是 ISPS 的后继**：HiTEN 是 IMAPS 旗下**高温电子**会议（Si/SOI 高温应用、封装、可靠性），与功率半导体器件会议无继承关系。

---

## 2. 期刊（学术）

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **IEEE TPEL** (Transactions on Power Electronics) | 学术期刊 | IEEE PELS | https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=63 | 功率电子顶级期刊，含功率半导体器件/模块、驱动、可靠性、封装热管理。 | 月刊 | 一手 | 否（IEEE Xplore） | 必追 |
| **IEEE T-ED** (Transactions on Electron Devices) | 学术期刊 | IEEE EDS | https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=16 | 器件物理与工艺，IGBT/MOSFET/SiC 新结构、可靠性机理。 | 月刊 | 一手 | 否 | 必追（器件/机理） |
| **IEEE JESTPE** (Journal of Emerging and Selected Topics in Power Electronics) | 学术期刊 | IEEE PELS | https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=6509394 | 专题型，常设宽禁带功率、可靠性、汽车功率电子专辑。 | 双月刊 | 一手 | 否 | 必追 |
| **Microelectronics Reliability** (Elsevier) | 学术期刊 | Elsevier | https://www.sciencedirect.com/journal/microelectronics-reliability | 微电子可靠性、失效物理、功率器件寿命与加速试验。 | 月刊 | 一手 | 否（ScienceDirect） | 必追（可靠性） |
| **IEEE TCPMT** (Transactions on Components, Packaging and Manufacturing Technology) | 学术期刊 | IEEE CPMT | https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=6047879 | **封装、互连、材料、热、可靠性**专刊，对模组封装直接可用。 | 月刊 | 一手 | 否 | 必追（封装方向） |
| **《电工技术学报》** | 中文学术期刊 | 中国电工技术学会 (CES) | http://www.ces-transaction.com/ `[未验证]` | 国内功率电子/电机驱动/可靠性高质量中文论文。 | 半月刊 | 一手 | 部分（官网摘要，全文多需期刊库） | 必追（中文一手） |
| **《中国电机工程学报》** | 中文学术期刊 | 中国电机工程学会 | http://www.pcsee.org/ `[未验证]` | 电力电子化、牵引、新能源并网中的功率半导体应用与可靠性。 | 旬刊 | 一手 | 部分 | 可选 |
| **《半导体技术》** | 中文学术/技术期刊 | 中国电子科技集团第 13 所 | http://www.bdtj.cbpt.cnki.net/ `[未验证]` | 半导体器件、工艺、封装、可靠性中文技术文章。 | 月刊 | 一手 | 部分 | 可选 |

---

## 3. 标准组织与标准获取渠道（标准）

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **IEC TC 47**（Semiconductor devices）及其 SC | 标准组织 | IEC | https://www.iec.ch/ | 统筹半导体器件标准。功率器件关键：**IEC 60747-9（IGBT 分立器件）**、**IEC 60749 系列（离散器件环境/机械试验方法）**、IEC 61287-1（轨道交通变流器）、IEC 62109（光伏逆变器安全）。SC 47A=集成电路，SC 47D=封装/互连技术（细分 `[未验证]`）。 | 持续维护 | 标准 | 否（IEC 商店付费） | 必追（设计基准） |
| **JEDEC JC-70**（Wide Bandgap Power Electronic Conversion Semiconductors） | 标准委员会 | JEDEC | https://www.jedec.org/committees/JC-70 | **JC-70.1 = GaN 功率标准**；**JC-70.2 = SiC 功率标准**。已发布 JEP173/180/182/183/184/190/192/194/195/197/198/200/201/202/203/204 等（可靠性、datasheet 参数、测试表征）。**全部免费下载**。 | 持续（新 JEP 频出） | 标准 | 是 | 必追（SiC/GaN 可靠性） |
| **ECPE AQG 324**（Automotive Qualification Guideline for Power Modules） | 产业标准/指南 | ECPE（基于德国 LV 324，联合 ZVEI） | https://www.ecpe.org/research/working-groups/ | **汽车功率模块车规认证事实标准**。最新 **Release 04.1/2025**（2025-04，主文 Si 模块 + SiC 附录；后续扩展 GaN）。CC BY-ND，**官网公开发布可免费下载**。覆盖 QM/QC/QE/QL 四大类（含功率循环、HTRB/HTGB、H3TRB、机械、动态测试）。 | 约每 2 年大版本 | 标准 | 是 | 必追（车规模块可靠性） |
| **ZVEI**（德国电气电子行业协会） | 行业协会 | ZVEI | https://www.zvei.org/ | 与 ECPE 共同发起 LV 324 → AQG 324；代表德国汽车 OEM 立场。了解车规演进的语境源。 | 持续 | 标准/产业 | 部分 | 可选（背景） |
| **AEC**（Automotive Electronics Council）— **AEC-Q101** | 产业标准 | AEC（美系车厂联合） | https://www.aecouncil.com/ | **AEC-Q101 = 分立半导体（含 IGBT 单管）失效机理应力认证**。现行 **Rev-E（2023）`[未验证最新版号]`**。注意：AEC-Q101 管**分立器件**，AQG 324 管**模块**，二者互补不替代。 | 数年版 | 标准 | 是（aecouncil.com 免费） | 必追（单管车规） |
| **SAC/TC78**（全国半导体器件标准化技术委员会） | 标准组织 | 中国国家标准化管理委员会 | 归口查询：https://openstd.samr.gov.cn/（国家标准全文公开系统） | 负责制修订 GB/T 半导体器件标准（多等同/修改采用 IEC 60747/60749 系列）。 | 持续 | 标准 | 部分（公开系统可在线读部分正文） | 必追（国内合规） |
| **GB/T 查询** | 标准数据库 | SAMR（国家市场监督管理总局） | https://openstd.samr.gov.cn/ | 国标全文公开系统，可检索 GB/T 29332（IGBT 相关）、GB/T 半导体器件系列等。 | 持续 | 标准 | 部分（强制/推荐性部分公开） | 必追（国内合规） |

> 备注：功率半导体**模块级车规**实际由 AQG 324（欧）/ 企标（美系 Tier1 多用 AEC-Q101 + 内部模块规范）主导；IEC 偏器件级产品标准与测试方法，不直接提供「模块车规认证」。

---

## 4. 原厂技术文档库（最重要的实战信息源）

> 规律：**国际大厂均提供免费 PDF 应用笔记/手册**；国产厂以 datasheet + 装配/存储说明为主，深度 application manual 较少公开。

| 名称 | 类型 | 主办/出版方 | URL | 内容特征（强项） | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **Infineon（英飞凌）** | 原厂技术库 | Infineon | https://www.infineon.com/cms/en/product/power/igbt/ （中文：infineon.cn 同路径） | IGBT 模块（EconoDUAL/Easy/XHP/IHM/HVIGBT）应用笔记**极全**：热阻/瞬态热测量、功率循环与热循环计算、装配/焊接/压装、IPOSIM 在线仿真工具。 | 持续 | 一手 | 是（多数 AN 公开 PDF） | 必追 |
| **Mitsubishi Electric（三菱电机）** | 原厂技术库 | Mitsubishi | https://www.mitsubishielectric.com/semiconductors/powerdevices/design_support/note/index.html | **IGBT 模块应用手册经典**（NX/T 系列、HVIGBT 手册、DIPIPM）。结构/特性/栅驱/并联/串联/安装全覆盖。 | 持续 | 一手 | 是 | 必追 |
| **Fuji Electric（富士电机）** | 原厂技术库 | Fuji | https://www.fujielectric.com/products/semiconductor/model/power_modules/igbt/application/igbt.html | **IGBT Modules Application Manual（REH984，9.2MB，2026）** 章节完整，第 11 章专讲功率模块可靠性（功率循环曲线、可靠性试验条件）。 | 持续 | 一手 | 是 | 必追 |
| **Semikron Danfoss（赛米控丹佛斯）** | 原厂技术库 | Semikron Danfoss | https://www.semikron-danfoss.com/（产品页 → Documents 标签） | 应用指南体系化：AN 14-003 开关损耗、AN 14-004 热阻、AN 21-001 **功率循环模型**、AN 17-003 宇宙射线失效、AN 20-003 现场测试。 | 持续 | 一手 | 是 | 必追 |
| **Hitachi Energy / ABB（日立能源，原 ABB 半导体）** | 原厂技术库 | Hitachi Energy | https://www.hitachienergy.com/（StakPak: 站内搜索 StakPak） | **压接式 IGBT（StakPak/HiPak）与 HVDC** 专长；datasheet 为主，深度手册少，技术多经 PCIM 论文/白皮书释放。5SNA/5SNE 系列延续 ABB 命名。 | 持续 | 一手 | 是（datasheet） | 必追（压接/HVDC） |
| **onsemi（安森美，含 Fairchild IGBT 遗产）** | 原厂技术库 | onsemi | https://www.onsemi.com/ | **IGBT Applications Handbook（HBD871/D）**、TND6235-D 概览、AND90xx 应用笔记（栅驱、并联、热、感应加热）。中文 AN 也较全。 | 持续 | 一手 | 是 | 必追（单管/家电） |
| **STMicroelectronics（意法半导体）** | 原厂技术库 | ST | https://www.st.com/（产品页 → Application Notes） | IGBT 偏中低压；**SiC MOSFET 文档更强**（AN 驱动/烧结/米勒钳位）。IGBT 有 AN4544 datasheet 教程、AN4694 EMC。 | 持续 | 一手 | 是 | 可选（IGBT 弱于 SiC） |
| **Littelfuse / IXYS** | 原厂技术库 | Littelfuse（收购 IXYS） | https://www.littelfuse.com/ | **压接 IGBT（PP-IGBT）** 与离散 IGBT 专长；有 DC-breaker 应用笔记、功率半导体选型指南 2026。 | 持续 | 一手 | 是 | 必追（压接/直流断路器） |
| **Vishay** | 原厂技术库 | Vishay | https://www.vishay.com/（产品页 → Application Notes） | 功率 MOSFET/IGBT 模块（MTP 系列）、栅驱光耦、自举/退饱和二极管应用笔记。IGBT 深度一般。 | 持续 | 一手 | 是 | 可选 |
| **StarPower（斯达半导）** | 国产技术库 | 斯达半导体 | https://www.powersemi.com/EN/ ；欧洲站下载：https://www.starpowereurope.com/download | 产品 datasheet + **装配/存储说明 + 目录**齐全；欧洲站有各封装（L2/L3/C5/C6/P6/P7H 等）安装指南。未见类似 Fuji/Mitsubishi 的统包应用手册。 | 持续 | 一手 | 是（datasheet/装配） | 必追（国产主力） |
| **CRRC Times Electric（中车时代电气）** | 国产技术库 | 中车时代电气 | 官网：http://www.tec.crrczic.cc/ ；压接手册 PDF：https://ctsc.csrzic.com/portal/rootimages/uploadimg/1702330059953172/1702330059953172.pdf | 轨道交通/电网压接 IGBT 强。有**《中车压接系列 IGBT 模块 应用手册》**（含可靠性试验 LTS/HTS/TC/HTRB/PCsec/PCmin 等）。 | 持续 | 一手 | 是（手册 PDF 公开） | 必追（压接/牵引/电网） |
| **MacMic（宏微科技）** | 国产技术库 | 宏微科技（用户所在公司） | http://macmicst.com/ | 产品 datasheet 公开（IGBT 模块/单管 PDF，如 MMG 系列）。**未检索到统包 application manual**，深度资料以内部分享为主。 | 持续 | 一手 | 是（datasheet） | 必追（自有产品） |
| **Silan（士兰微）** | 国产技术库 | 士兰微电子 | https://www.silan.com.cn/（产品页 → 技术文档） | 车规/工业 IGBT 模块 datasheet 公开（如 SGM 系列 750V/1200V）。应用手册深度有限。 | 持续 | 一手 | 是（datasheet） | 可选 |
| **CR Micro（华润微）** | 国产技术库 | 华润微电子 | https://www.crmicro.com/ | 产品线全（IGBT 单管/模块/SiC）。官网偏产品导航，**公开 application note 少**，datasheet 多经分销商（世强/EEWorld）流出。 | 持续 | 一手 | 部分 | 可选 |
| **Yangjie（扬杰科技）** | 国产技术库 | 扬杰科技 | https://www.21yangjie.com/（产品页 → 规格书下载） | IGBT 单管/模块 datasheet 公开（如 DGQ/DGW 系列、easy 1B 六单元模块）。 | 持续 | 一手 | 是（datasheet） | 可选 |
| **新洁能（NCE Power）** | 国产技术库 | 无锡新洁能 | 未检索到独立公开技术文档库 `[未验证]` | 以 datasheet 经授权分销商（世强/LCSR/icspec）获取为主，未见系统应用笔记。 | — | 一手 | 部分 | 可选 `[未验证]` |
| **BYD Semiconductor（比亚迪半导体）** | 国产技术库 | 比亚迪半导体 | 未检索到独立公开技术文档库 `[未验证]` | 车规 IGBT/SiC 模块自用+外供，公开技术资料稀缺，多以新闻稿/产品发布为主（偏商业公关）。 | — | 二手/公关 | 部分 | 可选 `[未验证]` |

---

## 5. 行业媒体 / Newsletter / 播客（一手技术 content 与二手并存，需甄别）

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **Bodo's Power Systems** | 行业媒体（杂志+网） | Bodo's Power | https://www.bodospower.com/ | **高质量**、偏功率电子系统/模块/驱动/可靠性，常有原厂总工深度技术文。无营销号感。 | 月刊+常更 | 一手+二手 | 是 | 必追 |
| **Power Electronics News** | 行业媒体 | AspenCore（EEWeb 体系） | https://www.power-electronics.com/ | 新技术/产品/应用文章，含设计指南。广告占比中等，技术尚可。 | 常更 | 二手/一手 | 是 | 必追 |
| **Semiconductor Engineering** | 行业媒体 | Semiconductor Engineering | https://semiengineering.com/ | 半导体制造/器件/可靠性深度报道，功率半导体与 WBG 覆盖好。 | 常更 | 二手（采编） | 是 | 必追 |
| **EE Times（Power / Power Management 版块）** | 行业媒体 | AspenCore | https://www.eetimes.com/ | 产业+技术并重，功率半导体并购/技术动向快。 | 常更 | 二手 | 是 | 可选 |
| **Power Electronic Tips** | 行业媒体 | Endeavor Business Media | https://www.powerelectronictips.com/ | 设计导向短文、how-to、选型，偏应用工程师。 | 常更 | 二手 | 是 | 可选 |
| **PCIM News Platform / Podcast / Magazine** | 行业媒体 | Mesago | https://pcim.mesago.com/（Insights 区） | PCIM 衍生的新闻、播客、杂志，紧跟欧洲功率电子圈。 | 常更 | 二手 | 是 | 可选 |
| **B 站 / 小宇宙 技术 UP** | 视频/播客 | 个人创作者 | 站内检索（不列具体号，避免营销号） | **存在少数实质技术内容**（高校课题组、原厂应用工程师个人频道），但**质量参差、营销号多**。建议仅追踪可追溯身份（高校/原厂在职）的创作者，且以官方文档交叉验证。 | 不定 | 二手 | 是 | 可选（需甄别） |

> 媒体分级原则：Bodo's / Power Electronics News / Semiconductor Engineering 属「可追」；纯新闻稿、厂商通稿、营销号一律降权。中文营销号（含知乎/公众号/CSDN）不列入。

---

## 6. 数据 / 数据库

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **IEEE Xplore** | 文献数据库 | IEEE | https://ieeexplore.ieee.org/ | ISPSD/APEC/ECCE/PCIM(部分)/TPEL/T-ED/JESTPE/TCPMT 全文。 | 实时 | 一手（仓储） | 否（订阅/会员） | 必追 |
| **ScienceDirect** | 文献数据库 | Elsevier | https://www.sciencedirect.com/ | Microelectronics Reliability 等期刊全文。 | 实时 | 一手 | 否 | 必追（可靠性） |
| **Espacenet / 专利库** | 专利数据库 | EPO | https://worldwide.espacenet.com/ | 功率器件/封装/可靠性**专利检索**主入口（含全球同族）。 | 实时 | 一手（专利） | 是（专利文献免费） | 必追（竞品/自由度分析） |
| **Google Patents** | 专利数据库 | Google | https://patents.google.com/ | 专利检索体验好，含法律状态、引用树。 | 实时 | 一手 | 是 | 必追 |
| **IEC 标准库** | 标准数据库 | IEC | https://www.iec.ch/ | IEC 60747/60749/61287 等原文购买与预览。 | 实时 | 标准 | 否 | 必追 |
| **JEDEC 文档库** | 标准数据库 | JEDEC | https://www.jedec.org/ | 全部 JEP/JESD 免费下载（含 JC-70 系列）。 | 实时 | 标准 | 是 | 必追 |
| **Yole Group（原 Yole Développement）** | 产业研究报告 | Yole Group | https://www.yolegroup.com/ | 功率半导体/SiC/IGBT 市场、产能、技术路线、拆解。**付费**。 | 季度/年度 | 二手（分析） | 否（报告付费，摘要免费） | 可选（市场/技术路线） |
| **Omdia** | 产业研究报告 | Omdia（Informa） | https://omdia.tech.informa.com/ | 半导体市场数据与预测，含功率器件。付费。 | 持续 | 二手 | 否 | 可选 |
| **TechInsights** | 产业研究/逆向 | TechInsights | https://www.techinsights.com/ | 器件逆向、成本建模、工艺分析。付费且贵。 | 持续 | 二手 | 否 | 可选（竞品拆解） |

---

## 7. 社区 / 问答（务实评估）

| 名称 | 类型 | 主办/出版方 | URL | 内容特征 | 更新频率 | 一手/二手 | 免费全文 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| **Infineon Community** | 厂商技术论坛 | Infineon | https://community.infineon.com/ | 原厂应用工程师与用户互动，IGBT/驱动/热问题有较实回答。**是功率半导体圈最可用的开放问答**。 | 常更 | 一手+二手 | 是 | 可选（产品答疑） |
| **EDABoard（Power Electronics 版）** | 技术论坛 | EDABoard | https://www.edaboard.com/ | 电力电子/驱动讨论，偶有资深工程师，但 IGBT 封装可靠性深度帖少。 | 常更 | 二手 | 是 | 可选 |
| **ResearchGate / LinkedIn** | 学术/人脉 | 各自 | — | 直接追会议作者、ECPE/原厂专家动态，获取 preprint 与讲义。 | 常更 | 一手+二手 | 部分 | 可选 |

> **诚实结论：这行没有高质量「开放技术社区」像 StackOverflow 那样可用。**
> IGBT / 功率半导体封装可靠性的核心知识**高度集中在：(1) 会议论文（ISPSD / PCIM / CIPS / ESREF / APEC）；(2) 原厂应用笔记与手册（Infineon / Mitsubishi / Fuji / Semikron Danfoss 最强）；(3) 标准（AQG 324 / AEC-Q101 / JEDEC JC-70 / IEC 60747·60749）。**
> 公开论坛质量低、营销号多、且易传播未经验证的「焊层寿命经验公式」等。**不要依赖社区做设计决策**，社区仅用于产品级答疑与找人。中文知乎/公众号/CSDN 明确不列入推荐。

---

## 8. 给「必追」路线的最小清单（时间紧时）

1. **标准**：ECPE AQG 324 (04.1/2025) · AEC-Q101 · JEDEC JC-70.x JEP 系列 · IEC 60747-9 / 60749
2. **原厂手册**：Fuji REH984 · Mitsubishi HVIGBT/NX 手册 · Infineon 热/功率循环 AN · Semikron Danfoss AN 21-001 功率循环模型
3. **会议**：PCIM Europe/Asia · CIPS · ESREF · APEC · ISPSD（器件方向）
4. **期刊**：TPEL · TCPMT · Microelectronics Reliability · JESTPE
5. **数据库**：IEEE Xplore · Espacenet（专利）· ScienceDirect
6. **媒体**：Bodo's Power · Power Electronics News · Semiconductor Engineering

---

## 9. 待二次核实项（诚实标注）

- [ ] **ISPS 是否确已停办**（疑已停办/并流 ISPSD，需查 IEEJ 历史公告）
- [ ] **CIPS 中文误传**（已确认为德国 VDE/ECPE 会议，非中国会议）
- [ ] **AEC-Q101 最新版号**（本文写 Rev-E/2023，待官网核对）
- [ ] **IEC TC 47 的 SC 47D 具体分工**（封装/互连技术归属待核）
- [ ] **ISPSD 永久官网域名**（ispsd.com 未经直接访问确认）
- [ ] **新洁能 / BYD 半导体公开技术文档库**（未检索到，可能以分销商/内部为主）

# Track 01 — 人物 / 机构与思想源头（Figures）

> 调研日期：2026-10-17
> **重要约束**：IGBT 领域与"LLM agent infra"这类领域不同——它的个人 IP 很弱，**核心知识沉淀在机构（原厂 AN + 标准组织）而非个人**。本轨因此以「机构 + 可验证的代表作者」组织，而不是硬凑"行业大 V"。
> 可信度：`[一手]` = 其著作/论文已在 Track 04 经 URL 核实；`[推断]` = 领域共识但本次未逐一核实其个人主页或动态；`[未验证]` = 不可引用。

## 0. 判断：这个领域该不该做「人物蒸馏」

**不该。** 理由：

1. IGBT 的关键工程知识以**原厂应用手册 + 标准正文**为载体（Fuji REH984、Mitsubishi 应用手册、Semikron Application Manual、AQG 324），而不是某个人的博客或播客。
2. 这行**没有高影响力的个人 newsletter / podcast**（见 Track 05 §7 的诚实结论）。
3. 人物的"思维方式"在这里基本等价于**机构的方法论**：Infineon 的热设计方法论、Semikron 的功率循环模型方法论、三菱的芯片结构路线。

所以：本轨的可用方式不是"按某某的视角看问题"，而是**"按某机构的技术路线看问题"**。这比伪造个人 IP 更诚实、也更好用。

---

## 1. 思想源头：可验证的关键作者（10 人，全部来自 Track 04 已验证文献）

| 人物 | 归属机构 | 核心一句话 | 代表工作（已核实） | 在本技能中的调用场景 |
|---|---|---|---|---|
| **B. Jayant Baliga** | NC State University | 功率器件的分析模型可以做到与数值仿真对齐；IGBT 的提出者 | *Fundamentals of Power Semiconductor Devices* (Springer 2008)；*The IGBT Device* (Elsevier 2015) `[一手]` | 需要**器件物理层**判断时（VCE(sat) 与 Eoff 折中从哪来、SOA 边界为什么在这） |
| **Josef Lutz** | TU Chemnitz | 封装与可靠性是器件物理的一部分，不是附属品 | *Semiconductor Power Devices*（与 Schlangenotto / Scheuermann / De Doncker，Springer 2011/2018）`[一手]` | 需要把**失效形貌 ↔ 物理机制**连起来时（破坏性机制章节） |
| **Uwe Scheuermann** | Semikron Danfoss | 寿命模型必须按**失效机理分离**，不能一个公式套所有 | SKiM 寿命模型（烧结芯片 + 优化铝线）；Semikron AN 21-001 功率循环模型 `[一手]` | 做**寿命外推**、判断"该用哪个模型"时 |
| **Reinhold Bayerer** | 原 Infineon | 功率循环寿命是多参数函数（ΔTj、ton、I、V、D 全都在里面） | CIPS 2008 多参数模型 `[一手]` | 需要**多参数敏感性**分析、解释"为什么同样的 ΔTj 寿命差一倍"时 |
| **Michael Held** | 原 ABB | 牵引应用的快功率循环可以外推到场寿命 | LESIT 模型（PEDS 1997）`[一手]` | 建立**最基础**的 ΔTj + Arrhenius 寿命估计、作为比较基线 |
| **T. Laska**（及 Infineon 团队） | Infineon | 薄漂移区 + 场截止层 = 同时降 VCE(sat) 与 Eoff | FS-IGBT，ISPSD 2000 `[一手]` | 解释现代 1200V/1700V IGBT 的结构来历时 |
| **H. Takahashi**（及三菱团队） | Mitsubishi Electric | 在发射极侧抬载流子浓度，是降饱和压降的另一条路 | CSTBT（ISPSD 1996/2001）；RC-IGBT（ISPSD 2004）`[一手]` | 讨论**注入增强**路线、RC-IGBT 单片集成时 |
| **T. Ogura**（及东芝团队） | Toshiba | 高压大电流要靠多芯片并联 + 低栅极寄生电感 | IEGT 并联（ISPSD'98）`[一手]` | 讨论**4.5kV 级、压接/高压模组并联**时 |
| **Guo-Quan Lu**（及 Bai/Zhang/Calata） | Virginia Tech | 纳米银低温烧结可以同时给出高导热与低模量 | IEEE TCPMT 2006、IEEE Trans. Adv. Packag. 2007 `[一手]` | 讨论**烧结银替代焊料**的物理依据与代价时 |
| **Frede Blaabjerg / Huai Wang** | Aalborg University (CORPE) | 可靠性要挂在 **mission profile** 上算，不是挂在单个试验上 | *Reliability of Power Electronic Converter Systems*（IET 2015，2nd ed. 2025）`[一手]` | 讨论**系统级寿命设计、风电/光伏 mission profile** 时 |

### 补充（领域共识，本次未核实个人主页，标注 `[推断]`）
- **Michael Pecht**（CALCE, University of Maryland）— 失效物理（PoF）方法论的推动者，与 Blaabjerg 团队合著上述 IET 书。
- **Mauro Ciappa**（ETH Zurich）— IGBT 功率循环失效机理与寿命模型，长期发表。
- **Francesco Iannuzzo**（Aalborg）— 功率器件可靠性、短路与 HTRB 表征。
- **Andreas Volke / Michael Hornkamp**（原 Infineon 应用工程）— *IGBT Modules* 专著作者，模组应用层最实用的作者组合 `[一手，书已核实]`。

> 使用纪律：提到这些人时，只引用其**已被核实的工作**（上面列的）。不要替他们编造立场或"最近动态"。

---

## 2. 真正该"按谁的方法论看问题"：6 个机构的技术路线

这是本轨对技能最有用的部分——**机构的路线差异，就是这行的思维差异**。

| 机构 | 技术路线特征 | 他们的默认假设 | 什么时候该用他们的思路 |
|---|---|---|---|
| **Infineon** | FS 沟槽栅为主；模组产品线最宽（EconoDUAL/Easy/XHP/IHM/HVIGBT）；工具链成熟（IPOSIM 在线仿真、热/功率循环 AN 体系完整） | "先把热与损耗算准，再谈可靠性" | 做**损耗-热闭环设计**、选型、给客户做技术方案时 |
| **Mitsubishi Electric** | CSTBT 载流子存储路线；HVIGBT（高压）与 DIPIPM（智能功率模块）；应用手册写得最像教科书 | "器件结构决定应用边界" | 讲**注入增强原理**、高压模组、IPM 集成时 |
| **Fuji Electric** | 模组封装与可靠性试验数据最完整（REH984 手册第 11 章专讲功率模块可靠性） | "可靠性要用试验数据说话" | 搭**可靠性试验矩阵**、要参考原厂 PC 曲线时 |
| **Semikron Danfoss** | 烧结银 + SKiM 的先驱；功率循环寿命模型（AN 21-001）公开度最高；Application Manual 免费 500+ 页 | "寿命模型要按失效机理分开建" | 做**寿命外推、烧结 vs 焊料论证**时 |
| **Hitachi Energy / ABB** | 压接（StakPak/HiPak）+ HVDC；LPT 路线 | "高压大电流的关键是无焊层、fail-safe" | 讨论**压接 vs 焊接、HVDC/电网级**时 |
| **中车时代电气 / 斯达 / 宏微** | 国产替代 + 牵引/车规；压接手册公开（中车）；封装形态覆盖广 | "先过客户认证，再谈性能领先" | 讨论**国产供应链、牵引/车规认证落地**时 |

---

## 3. 值得追的"人"其实在会议的作者名单里

会议论文作者是这行真正的前沿生产者。追人的正确姿势：

| 做法 | 具体动作 |
|---|---|
| 追会议而非追人 | ISPSD（器件）、PCIM Europe（封装/应用）、CIPS（系统集成）、ESREF（失效物理）的作者名单，逐年看重复出现的名字 |
| 追机构实验室 | Aalborg CORPE（可靠性/mission profile）、TU Chemnitz（器件与可靠性）、ETH Zurich（失效机理）、Virginia Tech CPES（封装互连）、Fraunhofer IISB/ISIT（封装工艺） |
| 追原厂 AN 作者 | Semikron AN 21-001、Fuji REH984 的署名作者，往往比"网红工程师"靠谱得多 |

> 结论：**这个技能不提供"人物视角"，提供"机构路线视角" + "会议/实验室索引"。** 这是对领域真实结构的诚实反映，而不是能力缺失。

---

## 4. 诚实边界

- 本轨**未做**任何个人社交媒体动态追踪（这行的人基本不在社交平台讲技术）。
- "最近 12 个月动态"在本领域无意义——IGBT 的核心知识变动周期是 **5–10 年**（FS 结构 2000 年、RC-IGBT 2004 年、烧结银 2006–2007 年都还在被引用）。
- 标注 `[推断]` 的 4 位学者，其机构与研究方向为领域共识，但本次未核实其 2026 年具体在研项目。

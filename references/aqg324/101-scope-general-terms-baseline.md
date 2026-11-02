# 101 · AQG 324 范围·总则·术语·试验基线（第 1–5 章：Scope / Overview / Referenced standards / Terms / General part）

> **层归属**：标准层（references/aqg324/，书源五＝ECPE AQG 324 Rel03.1/2021 原文蒸馏）；门：**G**（可靠性与认证），跨 **B**（封装定义 chip-near/chip-remote）
> **页引用约定**：正文页零偏移——PDF 页 = 标准页「Page N of 71」；附录按「Annex X, PDF pNNN」引。

> **R·原文锚点**
- p5（§1 Scope）：「requirements, test conditions and tests for validating properties, including the lifetime of power electronics modules … for use in power electronics converter units (PCUs) of motor vehicles **up to 3.5 t gross vehicle weight**」；「concern the module design as well as the qualification of devices on module level (i.e. the assembly), **but not the qualification of semiconductor chips or manufacturing processes**」
- p8（§2）：「Lifetime testing … primarily differentiates between two failure mechanisms – fatigue of **chip-near** interconnections and fatigue of **chip-remote** interconnections」
- p16（§4.7）：「Tolerances refer to the **measured value** … If no other tolerances are stated in the individual tests, the tolerances from Table 4.6 must be used」

> **I·骨架**（本模块回答：AQG 324 管什么、不管什么、术语与容差基线）
1. **适用范围与边界**（p5–6）：≤3.5 t 机动车 PCU 内的功率模块与「基于分立器件的等效特殊设计」；**不含芯片级与制造工艺资格**、不替代整车 PCU 资格试验；正文面向 **Si** 基模块，SiC 特殊性在 Annex III.A，GaN 留待后续版本。某项试验不适用时，**供应商必须向客户书面说明不适用理由**（这是与「选做」的本质区别）。热界面（TIM 等）若不在模块结构内，由模块厂给出**推荐参考测试装置**并文档化；已按旧版资格通过的模块**不受新版要求追溯**（以 qualification plan 一致日期为界）。
2. **四族试验谱系**（p7）：**QM**（模块试验：栅极参数/额定与漏电流/正向压降/X-ray/SAM/SAT/IPI-VI/OMA）→ **QC-01~05**（表征：Lp / Rth / 短路能力 / 绝缘 / 机械数据）→ **QE-01~04**（环境：TST / 可接触性 CO / 振动 V / 机械冲击 MS）→ **QL-01~07**（寿命：PCsec / PCmin / HTS / LTS / HTRB / HTGB / H3TRB），末尾全 DUT 终测 + 转可靠性数据。环境与寿命试验的 DUT 数量**须供需双方按 Annex I.A 流程事先约定**。
3. **失效机理二分**（p8，图 2.1）：芯片近端互连（键合线/带键合/Cu clip/烧结 + 芯片底面焊接/烧结/扩散焊）vs 芯片远端互连（负载/辅助端子接触、基板系统焊、无基板模块的模块-冷却器界面）——都是**异 CTE 热机械应力疲劳**；无基板模块的冷却界面必须在**应用型装置**上考核。
4. **引用标准底盘**（p9，表全文）：IEC 60747-2/-8/-9:2007/-15（器件）、IEC 60749-5/-6/-23/-25/**-34:2010（功率循环）**、IEC 60068-2-6/-27/-64（振动冲击）、IEC 60664-1/-2-1/-4（绝缘配合）、JESD22-A104F/-A119、ISO/IEC 17025。**IEC 60749-34-1 是功率循环试验的方法母法**（与 Volke 层 05、封装层 83 并列）。
5. **关键定义**（p10–11）：topological switch（拓扑开关：并联等效单开关）；special designs based on discrete components（FR4 上的 B6 桥即属模块，含驱动则成 IPM）；**HV = DC >60 V / AC rms >30 V**；direct cooling（模块即冷却系统一部分，无 TIM）vs indirect cooling（用 TIM）。
6. **总则五条**（p18–20）：芯片先过**芯片技术资格**再上模块；触发**全面技术资格（重新跑 §6–9 全部试验）**的设计/芯片变更清单（基板/衬底/外壳材料几何、任一接触面、贴片材料、互连技术、换芯片）——工艺相关变更文档化并按 **Annex I.B Delta 矩阵**商定验证措施；特殊设计按 AEC-Q101/Q100/Q200 + **只做 QC-01/02/03**；物理分析四步（非破坏→协商→破坏→存档）；试验室按 **ISO/IEC 17025 或 IATF 16949** 组织，器具**可溯源至 PTB** 或等效国家计量院。

> **A1·案例**（标准自带的判定素材）
- 表 4.6 标准容差（p16）：频率 ±1%；**实测温度 ±2 ℃；间接确定温度 ±5 ℃**；湿度 ±5%；时间 **+5%/−0%**（只许超不许欠）；电压 ±2%；电流 ±2%。写试验方案时未注明容差即自动套用本表。
- 表 4.7 标准值（p17）：**TRT = 23 ℃ ±5 ℃**；RH = 25%–75%；未注明的试验温度 Ttest = TRT。
- 触发全面技术资格的最小变更集（p18）：换散热基板材料或几何、换衬底、换外壳、**任一器件接触面变更**、换贴片/系统焊材料、换互连技术（烧结↔焊接↔扩散焊、线键合↔带键合↔Cu clip↔烧结）、换芯片（同厂或异厂）——**全部命中**；仅工艺参数漂移则走 Delta 矩阵。

> **A2·本地复算**
- `Nf` 定义自查（p12 表 4.1）：Nf = 每个 DUT **首个 EOL 判据命中**时的循环数——与 Volke 层 16 的「Weibull 前提＝个体失效循环数」衔接：AQG 的可靠性数据转换（§2 末步）吃的就是这批 Nf 分布，不是「平均寿命」。
- HV 阈值复核（p11）：DC 60 V / AC 30 V(rms) 与乘用车高压安全惯例一致，无换算需求。
- 缩略语账（表 4.1–4.5）：p12–16 共 5 张表（general / electrical / thermal / humidity / test times）；Tvj 用「virtual」的原因有脚注——结温不可直测，经 VCE,sat / VF,SD / VF 反推（与厂商层 45 的测量链误差、封装层 78 的热阻式口径闭环）。

> **E·触发场景**
- 回答「AQG 324 到底考模块还是考芯片」→ 本模块 §1：只考模块级装配，芯片资格是**前置件**（§5.1）。
- 客户问「改了键合工艺要不要重跑全套」→ §5.2 变更清单 + Annex I.B Delta 矩阵（模块 107）。
- 写试验大纲要定容差/环境基准 → 表 4.6/4.7 直接引用，不自行发明。
- 问「TO-247 并联板算不算模块」→ §4.1.4 特殊设计定义：算，且只加做 QC-01/02/03。

> **S·步骤**（把一个模块送进 AQG 324 资格的最短路径）
1. 确认器件在 ≤3.5 t PCU 用途、模块（或特殊设计）定义成立（§1、§4.1.2/4.1.4）。
2. 核对芯片技术资格证据链（§5.1）与既有资格基线版本（§1 末注：不受后续版本追溯）。
3. 逐条过 §5.2 变更清单 → 判「全面技术资格」还是「Delta 资格」（引 Annex I.B，模块 107）。
4. 按 Annex I.A 流程（模块 107）排 QM→QC→QE→QL→终测序列，DUT 数量与客户书面约定。
5. 试验室资质（ISO/IEC 17025 / IATF 16949）与量具溯源（PTB）写入试验报告（§5.8）。
6. 物理分析按四步法预置（§5.7，方法例证在 Annex II.C）。

> **B·边界**
- 本模块是**标准条文转述**，不替代标准原文作判废依据；争议以 ECPE 发布文本为准。
- Rel03.1/2021 口径；ECPE 后续版本（含 GaN、新互连）不在此覆盖——引用时必须带版本号。
- 「特殊设计只做 QC-01/02/03」**不豁免**分立器件自身的 AEC-Q101 资格；两条腿都要。
- Table 4.6 容差只适用于「未另行注明」的情形；各试验条款自带容差时以条款为准。

> **与其它模块的接口**
- 试验本体：102（QM-01 全表）、103（QC-01~05）、104（QE-01~04）、105（PCsec/PCmin）、106（HTS/LTS/HTRB/HTGB/H3TRB）。
- 判定与流程：107（Annex I 流程图 + Delta 矩阵）、109（SiC 差异）。
- 寿命数据→设计：108（Annex II.D 寿命计算指引）接 igbt_life 三模型（厂商层 16、Lutz 层 96）。
- 机理语言：chip-near/chip-remote 与封装层 76（键合）、75（贴片）、82（基板）一一对应。

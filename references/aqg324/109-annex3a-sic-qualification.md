# 109 · Annex III.A SiC 功率模块资质认证附加要求（QL-01～08 SiC 特款 + 动态试验族）

> **层归属**：标准层（references/aqg324/）；门：**G**（可靠性与认证），跨 **H**（SiC 特有失效机理）、**D**（栅驱动耦合的动态应力）、**F**（VGS,th 测量方法学）
> **页引用约定**：正文页零偏移；Annex III.A 为 PDF p99–129（约 31 标准页）。
> **定位**：Si 主文条款的**增量层**——HTS/LTS、QC、QE 等节全部「Refer to base document」；本模块只记 SiC 特款与新增动态试验族（DRB/DGS/dyn H3TRB）。

> **R·原文锚点**
- p101（§1 Scope，定位声明）：「SiC device development is still ongoing … Therefore, **many tests are not finally defined with all test parameters** … Test parameters currently are **empirical values** and will be given just as an orientation. **They have to be agreed between customer and supplier.**」——SiC 篇是鲁棒性验证路线（指定试验类型与失效机理，不定死参数）。
- p104（§6.1.5 VGS,th 测量法）：「The characterization method of VGS,th has to follow the recommendations of **JEDEC JEP183**. Both methods described in JEDEC JEP183 are possible. **The chosen one has to be kept during the whole qualification.** VGS,th has to be measured with a tighter tolerance at **TRT = 25°C ±1°C** to get a valid signal and no overlay of temperature drift.」
- p106/p114（PC 测温红线）：「When testing SiC-MOSFETs, the virtual junction temperature **must not be determined in the channel** of the SiC-MOSFET but **using the body diode**, for reasons of device design.」；「During the off-state and measurement via body diode the MOSFET channel **must be fully closed** to enable a valid Tvj measurement!」（Table 9.1/9.4 脚注 d）
- p108/p116（Table 9.1/9.4 脚注 c，标定陷阱）：「Be aware of the **shift of the temperature coefficient from positive to negative by lowering VGS,on**.」
- p112/p119（Table 9.3/9.6 脚注 a，EOL 分离机制）：「Compared to IGBTs, a **stronger increase of RDS,on and VDS,on with temperature** is known for SiC-MOSFETs. It is **strongly recommended to implement an additional measurement parameter VDS,on,cold** to enable **separation** of the thermally superimposed VDS,on (**bond wire degradation**) and Rth (**chip solder fatigue**). … The separation can also be enabled by a VDS,on measurement via a **sense wire**.」
- p120–121（QL-05b 双跑要求）：「in the sense of robustness validation, an additional test run with VGS=VGS,min … should be carried out as technology test (**QL-05b**). Due to **higher field strength in the SiC gate oxide** by using VGS=VGS,min … the failure mode can be changed … Reason is the **overlay of HTRB blocking stress and the negative gate stress HTGS**.」；表 9.9 脚注 c：「**Technology qualification requires both tests with VGS = 0 V and with negative gate bias**, as long as there is no evidence which test is more severe.」
- p122（HTRB 判据与伪失败防护）：「An increase in the drain-source leakage current IDS,leak by a **factor of 5** … must be considered as a failure」；「an increase in leakage current by **100% must initially not be assessed as a failure** and b) the reference value … must be set to the **new stationary reference value**」（位移电流条款）；「Testing closer to 100% of the blocking voltage … will increase the risk of **cosmic ray failure (random event)** … Failures therefore will have no information about reliability.」
- p124（§9.7.1 滞后红线）：「VGS,th will show a **hysteresis due to switching but this is not an aging effect**. A **pre-conditioning** is needed to get a defined measurement signal. This procedure has to be **the same during all measurements**.」
- p125（Table 9.10，HTGB 分半）：「50% of the DUTs with positive gate voltage VGS = VGS,max; 50% of the DUTs with negative gate voltage VGS = VGS,min」；判据 IGS,leak ×5；「a current-limiting series resistor or an intelligent circuit breaker … could be implemented」。
- p126（§9.7.4 DGS 定位）：「**This test is not only relevant on chip-level, but even on module-level.** The module design has an impact on the real VGS at chip-level due to the layout (e.g. paralleling, ringing, low inductive design). Currently the DGS test is **only known from SiC power devices** due to the fast switching. … Detailed test conditions should be aligned in accordance to **JEDEC JEP184**.」；Table 9.10a：≥**10^11 cycles**、25°C、VDS=0V（脚注 a：仅当芯片级试验已排除 VDS 对 VGS,th 漂移影响才充分）、dVGS/dt **1 V/ns（无过冲）**、f≥50 kHz（duty>20%）。
- p127–128（QL-07 H3TRB SiC）：恒压负载强制（IEC 60749-5:2017 §5.2 e)1)「Testing with constant voltage load」must be conducted）；Table 9.11：85°C/85%RH/≥1000h、VDS=0.8·VDS,max、VGS=0V；判据 **IDS,leak ×10**（注意：与 HTRB/HTGB 的 ×5 不同档，闭环 106 模块登记）。
- p128–129（QL-07a dyn H3TRB）：「The test parameters are **not yet fixed**, the given parameters are typical target values.」Table 9.11a：1000h、85/85、VDS>0.5·VDS,max、**dVDS/dt>30 V/ns**、15–25 kHz；「If the DUT is in active mode (MOS), chapter QL-06a has to be taken into account. Thus, a **VGS,th-drift is no failure related to humidity**.」
- p129（QL-08 HTFB 状态）：「The implementation of an HTFB test … is presently **under discussion**. This test addresses for example the **bipolar degradation** and therefore, is strongly chip-related.」

> **I·骨架**（本模块回答：SiC 模块认证相对 Si 主文改了什么、加了什么、哪些参数还没定死）
1. **分层读取规则**：§5～§8 与 §9.4/9.5（HTS/LTS）全部回主文；实质增量集中在 **§6.1.5（VGS,th 测量）+ §9.2/9.3（PC 特款）+ §9.6～9.9（偏压类 + 动态试验族）**。
2. **PCsec/PCmin SiC 特款**（试验骨架与 105 模块同构，只记增量）：
   - 测温：**体二极管测温，禁走沟道**；关断与测温期沟道必须全关（必要时负栅压并记录）；内并联二极管无法测温时允许改器件。
   - 栅压：VGS,on 典型 **15 V**（降低时注意 VDS(T) 温度系数**正翻负**——标定曲线可能失效）；VGS,off 典型 **−5 V**。
   - EOL 分离机制：SiC 的 VDS,on 温度敏感性强于 IGBT → **加测 VDS,on,cold**（冷态正向压降）把「键线劣化（热态 VDS,on 涨）」与「芯片焊料疲劳（Rth 涨→冷态也涨）」分离；或用 sense wire。
   - 其余全同 Si 主文：ton/toff 固定、禁恒损耗控制、IL>0.85·IDN 仅一点、两 ΔTvj 点差 ≥40%、≥6 开关/≥3 DUT、+5%/+20% 判据、TIM settling、二极管负温系数并联不均、SAM、单一失效机制筛选。
3. **偏压类三档判据矩阵**（SiC 版）：
   | 试验 | 条件 | 判据 | SiC 特款 |
   |---|---|---|---|
   | QL-05 HTRB | ≥1000h、Tvj,max、VDS≥0.8·VDS,max | IDS,leak **×5** | **技术鉴定须 VGS=0V 与 VGS,min（负栅压）双跑（QL-05b）**；首小时位移电流 +100% 不判失败、稳定后更新基准；>80% 阻断电压引入宇宙射线随机失效无可靠性信息 |
   | QL-06 HTGB | ≥1000h、Tvj,max、VDS=0V、**50% 正压/50% 负压** | IGS,leak **×5** | VGS,th 滞后非老化，测量前 pre-conditioning 且全程同程序；栅回路限流电阻/智能断路器 |
   | QL-07 H3TRB | ≥1000h、85/85、VDS=0.8·VDS,max、VGS=0V | IDS,leak **×10** | **恒压负载强制**（IEC 60749-5 §5.2 e)1)）；Tvj<90°C 初期 |
4. **动态试验族（SiC 新增，均「不强制但要求/强烈推荐」）**：
   | 试验 | 状态 | 核心参数 | 失效模式 |
   |---|---|---|---|
   | QL-05a DRB 动态反向偏置 | 不强制，**强烈推荐**；芯片级（AEC Q101 之外）或模块级 | 25°C、≥1000h、VDS≥0.8·VDS,max（过冲 0.8–0.95 允许钳位）、**dVDS/dt=50 V/ns**、f≥25 kHz、被动法 VGS,min,recom / 主动法开关 | 高 dV/dt 快速充电内部结构老化 |
   | QL-06a DGS 动态栅应力 | 「is」（要做）；**芯片级+模块级** | 25°C、**≥10^11 次开关**、VDS=0V、**dVGS/dt=1 V/ns 无过冲**、f≥50 kHz duty>20%、VGS 全摆幅 | VGS,th 漂移（BTI，按 JEP184）；模块布局（并联/振铃/低感）影响芯片处真实 VGS |
   | QL-07a dyn H3TRB | 附加通用芯片鲁棒性试验；**参数未定死** | 85/85、1000h、VDS>0.5·VDS/max、**dVDS/dt>30 V/ns**、15–25 kHz | 湿度+动态叠加；主动模式下 VGS,th 漂移归 QL-06a（栅应力）不算湿度失效 |
   | QL-08 HTFB | **讨论中，尚无条款** | — | 双极退化（bipolar degradation，芯片级） |
5. **记录链**：HTRB 加记 **VBR,DS 前后**（Si 主文无此要求）；HTGB/H3TRB 记 VGS,th 前后（按 6.1.5 JEP183 方法）。

> **A1·案例**
- VGS,on 标定陷阱：某 SiC 模块 VDS(T) 标定在 VGS,on=18 V 下做（温度系数为正），试验时降到 15 V → 温度系数翻负，测温极性反转而不自知，ΔTvj 全错。JEP183 方法选择同理——两种测法混用等于两套不可比数据。
- HTRB 伪失败实例：上电首小时 IDS,leak 从 2 μA 冲到 6 μA（+200%）→ 按旧基准判失败；实际是位移电流建立过程，第 3 h 稳定到 5 μA → 更新基准后再评估后续漂移。**首小时曲线不能直接套 ×5 判据**。
- DRB/DGS 的模块级意义：同款 SiC 芯片，模块 A 低感叠层（振铃小）过 DGS，模块 B 传统布局（振铃叠加负尖峰）VGS,th 漂移超标 → 这就是 DGS 要在模块级做、且参数要按应用对齐的原因。
- 双极退化（QL-08 预警）：SiC 体二极管/雪崩注入双极载流子引发 VDS,on 漂移——当前 AQG 尚无条款，客户可按鲁棒性验证思路自行要求芯片级试验。

> **A2·本地复算**
- 判据 ×5/×10 档位守恒：HTRB/HTGB 均漏电流 ×5，H3TRB ×10（湿度路径允更大幅值因含整体结构+凝湿噪声）——与 106 模块「H3TRB ×10 vs HTRB/HTGB ×5」登记闭环 ✓。
- dVDS/dt 谱系：DRB 50 V/ns > dyn H3TRB >30 V/ns（典型目标）> DGS 侧 dVGS/dt 1 V/ns——栅极斜率比漏极斜率慢 ~50 倍，因为栅氧应力关心的是电荷注入而非 dV/dt 充电，两族试验物理量纲不同不可混 ✓。
- 10^11 次换算：f=50 kHz → 10^11/5e4 = 2×10^6 s ≈ **23 天**连续开关；1000 h（DRB/H3TRB）@25 kHz ≈ 9×10^10 次 <10^11——DGS 时长由次数定、DRB 由时长定，两表不可互相代算 ✓。
- VDS,on,cold 分离逻辑：键线劣化只增接触电阻（温升路径全涨）→ VDS,on,hot 涨而 VDS,on,cold 基本不动；焊料疲劳推高 Rth → 同一 IL 下结温整体抬高 → 冷态压降也涨。两判据交叉即得机制归属 ✓（呼应 105 的「单一失效机制筛选」）。

> **E·触发场景**
- SiC 模块认证方案评审 → 本模块是「Si 主文 + 增量」的读法地图；HTS/LTS/QC/QE 直接回 104/103。
- 搭 SiC PC 台架 → 体二极管测温 + 负栅压关断 + VGS,on 温度系数标定陷阱 + VDS,on,cold 通道。
- SiC 供应商报价只做单栅压 HTRB → 引 Table 9.9 脚注 c 要求双跑（QL-05b）。
- 讨论 DRB/DGS/dyn H3TRB 要不要做 → 第 4 点状态表 + 模块级 DGS 论据。
- VGS,th 数据前后矛盾 → 检查 JEP183 方法一致性与 pre-conditioning 程序。

> **S·步骤**（SiC 模块认证落地顺序）
1. 按主文排 QC/QE/HTS/LTS（无 SiC 特款）；VGS,th 测量按 JEP183 选定方法并锁定全程。
2. PCsec/PCmin：体二极管测温方案 + 沟道全关验证 + VDS(T) 标定（注意 VGS,on 系数方向）+ VDS,on,cold 通道。
3. HTRB：双栅压方案（0V + VGS,min 两批）+ 位移电流监控流程（首小时不判、更新基准）+ VBR,DS 前后测。
4. HTGB：50/50 分半正负栅压 + pre-conditioning 程序文档化 + 栅限流。
5. H3TRB：恒压负载（禁间歇）+ ×10 判据。
6. 与客户对齐动态试验：DRB（推荐，芯片级优先）、DGS（模块级，按 JEP184 与应用对齐）、dyn H3TRB（目标值）；HTFB 留待后续版本。
7. 报告按 107 模块（Annex I.C 模板）+ 本模块记录链归档。

> **B·边界**
- **SiC 篇参数是经验方向值**，须客户-供应商书面商定——不能像 Si 主文那样当死条款执行。
- DGS 的 VDS=0V 前提是芯片级已排除 VDS 对 VGS,th 漂移的影响，否则 VDS=0V 不充分。
- dyn H3TRB 参数「not yet fixed」；QL-08 HTFB 尚无条款——引用时注明 Rel03.1 状态。
- PC 双分支的其余约束（40% 拉差、0.85·IDN、TIM settling 等）沿用 105，本模块不重复；两处冲突时以 Si 主文正文为准（门表/附件不得覆盖主文）。
- 负栅压 HTRB 的失效模式已变（栅氧应力叠加），结果不能与 VGS=0V 档合并统计。

> **与其它模块的接口**
- 101–108（主文与附件：105 PC 骨架、106 偏压类主文版、107 Annex I 模板/矩阵、108 寿命模型消费端）。
- 102（Table 6.1 module test 的 VGS,th 测量 → §6.1.5 SiC 特款）。
- 机理：SiC 栅氧 TDDB/BTI（对应 igbt-master 既有 SiC 对照体系待补强项 P1）、双极退化、离子污染迁移（106 模块主文版同机理）。
- 标准：JEP183（VGS,th 测量）、JEP184（BTI/DGS 对齐）、IEC 60747-8/-2、IEC 60749-5/-23/-34、AEC Q101（DRB 芯片级挂靠）。

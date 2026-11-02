# 106 · QL 存储与偏压试验 QL-03~07（第 9.4–9.8 节：HTS / LTS / HTRB / HTGB / H3TRB）

> **层归属**：标准层（references/aqg324/）；门：**G**（可靠性与认证），跨 **A**（HTRB/HTGB 的芯片物理靶位）、**H**（漏电流判据→失效归因）
> **页引用约定**：正文页零偏移（PDF 页 = 标准页）。

> **R·原文锚点**
- p65（HTRB 失效判据）：「An increase in the collector-emitter leakage current … by a **factor of 5** based on the initial value above the noise level … or an increase above the value specified in the data sheet must be considered as a failure.」
- p70（H3TRB 失效判据）：「An increase … by a **factor of 10** based on the initial value above the noise level … must be considered as a failure.」（两处判据系数不同——最易抄错的点）
- p70（表 9.11 注 a/b/c）：80 V 档「for devices with **VCE,max > 100 V only**, otherwise use variant 2」；变体 2「**Tvj < 90 °C** during initial test phase」；80 V/80% 之争「must be **agreed upon with the customer**」。
- p64（HTRB 宇宙线注）：「Testing closer to 100% of the blocking voltage … will increase the risk of **cosmic ray failure (random event)** … Failures therefore will have no information about reliability or sensitivity to high temperature reverse bias because they are based on **different physics of failure**.」

> **I·骨架**（本模块回答：五个寿命/耐久试验各打什么、条件是什么、怎么判）
1. **QL-03 HTS 高温存储**（p62，母法 IEC 60749-6:2002）：**1000 h @ Ta = Tstg,max ≥125 ℃（typ.）**（datasheet 更高用更高）；中间测量（如有、须客户同意）一律 **TRT 拆装**；试验后 **SAM 记录互连层分层程度**（存储类试验也带 SAM 要求——热老化本身可致互连层退化）；判据：全功能 + datasheet 参数漂移分析范围与客户商定。
2. **QL-04 LTS 低温存储**（p63，母法 JESD22-A119:2015 条件 A）：**1000 h @ Ta = Tstg,min ≤−40 ℃（typ.）**；靶位＝橡胶/塑料/金属/衬底/半导体的**低温脆化、开裂、断裂**（长寿命低温暴露效应，含运输工况）；其余同 HTS 框架（TRT 拆装、SAM、Table 6.1 前后测）。
3. **QL-05 HTRB 高温反偏**（p64–66，母法 IEC 60747-9:2007 §7.1.4.1 / 60747-8 / 60747-2 / 60749-23）：
   - 靶位：**芯片钝化结构/钝化形貌与台面封装的时效弱点**——产线离子沾污在温度+电场下迁移→表面电荷→漏电流抬升、VGE,th 漂移；模块装配工艺与材料 CTE 影响钝化完整性；
   - 条件（Table 9.9）：**≥1000 h @ Tvj,max**（注：Tc = Tvj,max − ΔTP,loss，ΔTP,loss 为漏电流损耗自升温）；**VCE ≥ 0.8·VCE,max**（VDS/VR 同构）；VGE = 0 V（MOSFET 沟道关不保证时用 datasheet VGS,min）；外壳温度应落在最大允许存储温度 ±10 K，否则实测记录；
   - **失效判据：漏电流 ×5**（基于试前 TRT 冷测噪声底以上初值）或超 datasheet 限；**位移电流豁免**：加压最初数小时的漏电抬升是位移电流，回落到规定稳态后 a) 100% 以内的抬升不判失效 b) 后续评估基准**重置为新稳态值**；
   - 判定双通道：定时长（比较 a 稳态抬升 + b 冷态前后值，任一超限即 FAIL）或定阈值（跑到漏电上限为止）；
   - 数据集：ICE,leak/IDS,leak **连续记录**；VGE,th/VGS,th、VBR,CE/VBR,DS 前后各测一次；
   - **80% 的物理含义**：提到 100% 不提升可靠性，只会把**宇宙射线随机失效**（不同失效物理）混进统计——与 Lutz 层 98 的 FIT-海拔机制直接闭环。
4. **QL-06 HTGB 高温栅偏**（p67–68，母法同 HTRB；**不适用于二极管**）：
   - 三靶位：a) 栅氧完整性（**TDDB** 加速——栅源/栅漏成阻性通路或低击穿二极管）；b) 半导体/介质界面退化（VGE,th 漂移、Miller 电容变化）；c) 可动离子沾污；
   - 条件（Table 9.10）：**≥1000 h @ Tvj.max；VCE = 0 V；栅压分半：50% DUT 加 +VGE,max、50% 加 VGE,min**（正负栅偏各半——注意是正负两组器件，不是时序切换）；外壳温度要求同 HTRB；
   - **失效判据：IGE,leak/IGS,leak ×5**（同 HTRB 口径）；VGE,th 前后各测；
   - 装置：栅回路串**限流电阻或智能断路器**防储能瞬间泄放。
5. **QL-07 H3TRB 高湿高反偏**（p69–71，母法 IEC 60749-5:2017 + 修正）：
   - 靶位：**整个模块结构**（非密封模块：芯片与键合线埋在透湿硅胶里，湿气最终到达钝化层）——钝化弱点 + 离子迁移 + 外壳热机械应力交互 + 腐蚀气体物质与 AIT/芯片的交互；机械应力提高电化学腐蚀敏感性；
   - 母法修正：只用 **§5.2 e)1) 恒压**变体（标准允许的间歇加压不用）；DUT **全程阻断**；§5.2.1 省略；
   - 条件（Table 9.11）：**≥1000 h @ 85 ℃ / 85 %RH**；电压二选一（与客户商定）：**变体 1 = 80 V（仅 VCE,max>100 V 的器件）**；**变体 2 = 0.8·VCE,max**（初始阶段 Tvj<90 ℃——防漏电流自热局部压低 RH）；VGE = 0 V（MOSFET 同 HTRB 特款）；
   - **失效判据：漏电流 ×10**（不是 ×5——高湿环境噪声更大，阈值放宽）；VGE,th 前后各测；
   - 开试前置：H3TRB 前必须过模块试验（§6.1），**只放无缺陷 DUT 进箱**；
   - 标准自注研究空白：电压对 H3TRB 的影响（如**枝晶生长**激活）仍需研究——引用时不得把 80 V 说成「物理等效 0.8·VCE」。

> **A1·案例**
- 判据对照速查（本 skill 高频错点）：漏电判fail 系数三档——HTRB **×5**、HTGB **×5**、H3TRB **×10**；+5%/+20% 的 PC/TST 判据是另一族（正向压降/热阻，模块 104/105）。写报告别串族。
- 用户 HV-H3TRB 数据链（1000 H 23 pcs / 1500 H 6 pcs / 168 H 74 pcs PASS）对表：条件 85/85、恒压阻断、漏电连续监测、×10 判据——1500 H 超出 ≥1000 h 底线属加严，报告可注明「超 AQG 底线 50%」。
- 位移电流实例：HTRB 加压头 1–2 h 漏电冲高 2× 后回落 → **不判失效**，但要把评估基准改成回落后的稳态值；忽略此条会把每个好器件都误杀。
- 80 V 变体实例：650 V IGBT（VCE,max=650 V>100 V）可选 80 V 或 0.8×650=520 V——两者激活的失效机制谱不同（枝晶 vs 钝化离子迁移），必须与客户书面定档。

> **A2·本地复算**
- 温度链自检：HTRB 的 Tc=Tvj,max−ΔTP,loss 与 Volke 层 27「端子值≠芯片值」同构——Tc 要留出漏电自热余量，直接把 Tvj,max 当箱温是常见设置错误。
- 时间容差配套：≥1000 h 与表 4.6「+5%/−0%」组合 → 实际 ≥1000 h、无上限；中断恢复后的时长累计规则与客户商定。
- H3TRB 变体 2 自检：0.8·VCE,max 对 750 V 器件 = 600 V；Tvj<90 ℃ 约束在 85 ℃ 环境下意味着自热余量 ≤5 K——漏电流大的器件（高功率档）可能撑不住 0.8 档，这正是要「客户商定」的工程内涵。
- 通用数据条款：§9.1 与 §8.1 同文——QL 分支也允许 generic data，但差异证明责任在申请方；PC 与 TST 之外的存储/偏压类最容易走 generic 路径。

> **E·触发场景**
- 用户实际岗位（HV-H3TRB 验证）：本模块 §5 即试验设计依据（条件/判据/读出/前置筛选全套）。
- 评审供应商 HTRB/HTGB 报告 → 先查判据系数（×5）、位移电流豁免、VGE 正负分半。
- 问「H3TRB 为什么 80 V 和 0.8 档并存」→ 注 a/b/c + 研究空白注——电压档选择是客户协议项，不是物理定值。
- 问「HTS 为什么还要 SAM」→ 存储热老化同样推进互连层分层（§9.4.2 显式要求）。

> **S·步骤**（QL-03~07 分支落地顺序）
1. 逐试验确认母法 + AQG 增补（HTS:60749-6 / LTS:A119 / HTRB·HTGB:60747-9 等 / H3TRB:60749-5 恒压变体）。
2. 温度链设置：存储类设 Ta=Tstg 极值；偏压类设 Tvj,max 并反推 Tc。
3. 判据入监测系统：HTRB/HTGB ×5、H3TRB ×10；位移电流豁免逻辑进 HTRB 软件。
4. 读出：漏电流全程连续；VGE,th/VBR 前后各测；存储类试验后 SAM 分层。
5. H3TRB 开箱前过 §6.1 模块试验；电压档与客户书面定档。
6. 参数漂移分析范围与客户商定后出报告（Annex I.C 模板）。

> **B·边界**
- HTRB/HTGB 是**芯片近环境失效模式导向**试验——不考核远端外壳；H3TRB 才是整机结构级。
- HTGB 不适用于二极管；二极管只走 HTRB/H3TRB。
- 宇宙射线失效混入 HTRB 统计会被标准明确排除（不同失效物理）——与 Lutz 层 98 的 FIT 数据链互斥使用。
- ≥1000 h 是底线：加严时长（1500 H 等）合规但属商业/客户协议行为，不改变判据。

> **与其它模块的接口**
- 105（PC 判据族 +5%/+20%）、104（TST 判据）、102（Table 6.1 读出矩阵：0 h/1000 h）、107（流程图与 Delta 矩阵）、109（SiC 对 HTRB/HTGB/H3TRB 的加严差异）。
- 机理：离子迁移/钝化（Lutz 层 89 工艺侧、封装层 79 灌胶/爆米花）、宇宙射线（Lutz 层 98）。
- 用户 PFMEA：H3TRB 失效模式行可直接引本模块条件列。

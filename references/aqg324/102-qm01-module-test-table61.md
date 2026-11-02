# 102 · QM-01 模块试验与 Table 6.1 读出矩阵（第 6 章：Module test）

> **层归属**：标准层（references/aqg324/）；门：**G**（可靠性与认证），跨 **F**（测量：读出矩阵即测量计划）
> **页引用约定**：正文页零偏移（PDF 页 = 标准页）。

> **R·原文锚点**
- p21（§6.1.1）：「the individual test steps of the module tests must be carried out **before and after each of the individual test branches** as per the test flow chart plan in Annex I.A and Table 6.1 … and the deviations outside the specified tolerances must be shown」
- p21（datasheet 红线注）：「Typical parameter values **without range or limit information are not permitted** as suitable criteria in the framework of module tests. If the range or limit information is missing in the data sheet, the module manufacturer must supply these later on.」
- p22（§6.1.4 注）：「Data sheets usually state the implemented nominal **chip** current (e.g. 800 A). This generally does not correspond to the nominal **module** current as a function of the thermal resistance and the cooling connection (e.g. 550 A).」

> **I·骨架**（本模块回答：资格前后测什么、怎么读出、什么算合格判据）
1. **QM-01 的位置**（p21）：模块试验是每个试验分支（QC/QE/QL）**前+后**的公共读出层——目的三个：确认 DUT 无失效、确认满足全部要求、验证功能行为与精度。中间测量纪律：**先关机降温到目标温度再测，测完先开机再调温**（§6.1.1 末）——防止中间测量自热污染读数。
2. **最小读出集**（§6.1.2–6.1.8，p21–22）：
   - EOL 端测（100% 可追溯记录）；
   - **互连层质量**：SAM 推荐，记录空洞/分层/裂纹；
   - **ICN 定义二选一并文档化**：a) Rth,j-c 下 Tvj≤Tvj,max 的恒直流，或 b) 最大 Rth,j-c 下 typ. VCE,sat 对应的电流；
   - VGE,th / IGE,leak / ICE,leak / VCE,sat(VDS/VF)：**一律在 RT 与最高工作温度两点测**（由最高结温导出）；反并联续流二极管的漏电流 = IGBT 漏 + 二极管漏之和；
   - VCE,sat 用**脉冲法**测以压低自热——它是后续寿命试验的基准数据。
3. **击穿电压特例**（§6.1.9，p22）：VBR **不在模块级定义**；测前先确认器件扛得住（局部过热损坏风险与技术相关），若测则评到 **90% ICE,max** 处。
4. **破坏性/非破坏目检**（§6.1.10，p23）：OMA + IPI/VI 记录负载应力造成的损伤。
5. **Table 6.1 读出矩阵**（p24）＝把 10 列读出（EOL/SAM/五个相关性/短路/双脉冲/绝缘）映射到各试验的读出时点：
   - **TST（QE-01）读出点 0 / 500(opt.) / 1000 循环**——500 是可选中间读出；
   - **HTS/LTS/HTRB/HTGB/H3TRB 读出点 0 h / 1000 h**；
   - **PCsec/PCmin 读出点 0 / EOL**（寿命试验到寿终，不做固定中点）；
   - PC 期间 SAM 只在 **EOL 点**做（其余列 opt.）；
   - 双脉冲动态试验按 **IEC 60747-15:2012 §5.3.2**（表注 d）；
   - 相关性（correlation）= 各时点 TRT 实测值 vs **初始测量值**比对，**预期偏差的最大百分比须事先规定**（表注 a）；
   - 绝缘试验按量产终测规范（表注 b）；**资格阶段不推荐加中间测量**（留给开发阶段，表注 e）。
   - Master samples（母样）只在 0h 做一次读出。

> **A1·案例**
- ICN 落差实例（p22）：芯片标称 800 A ≠ 模块标称 550 A——差值来自 Rth 与冷却接口。写报告引用「模块电流」必须指明是哪个定义（a 或 b）与哪个 Rth 前提。
- 读出点设计实例：TST 试验方案若写「250 循环中测」→ 违反表注 e（资格阶段不加中间测量）；若漏写 500(opt.) → 与 Annex I.A 流程不符，客户可要求补读出。
- 6.1.5 的笔误式重复：VGE,th 与 IGE,leak 两节用了同一句「This threshold voltage must be compared…」——标准原文即如此，引用时不改写。

> **A2·本地复算**
- Table 6.1 行数账（p24）：数据行 11 行（QC-01..QC-04 合一行、QC-05、QE-01/03/04、QL-01..07、Master samples）× 10 列读出；行内逗号分隔数字即「该列在该时点读出」。TST 行 13 个读出格为全表最密——热冲击是互连层退化最快的分支，读出最全。
- 两点温度测量的容差配套：温度读数 ±2 ℃（表 4.6）→ VCE,sat 两点差值法的温度不确定度直接进寿命基准，与厂商层 45 探头延时、Lutz 层 99 测量链口径一致。
- 时间容差 +5%/−0%（表 4.6）套在 1000 h 存储上：实际 ≥1000 h、上限不设——写报告「1000 h 完成」须给出实测时长。

> **E·触发场景**
- 排资格计划/读客户试验矩阵 → 本模块就是「每次资格前后要测什么」的完整清单。
- datasheet 只有 typical 值被客户当判据 → 直接引 p21 红线注拒绝。
- 客户问「为什么漏电流要加二极管」→ §6.1.7 反并联求和条款。
- 问「击穿电压为什么不在模块级测」→ §6.1.9 局部过热损坏风险 + 90% ICE,max 折衷。

> **S·步骤**（搭一套 QM-01）
1. 按 Annex I.A 定各分支前后读出时点（Table 6.1 逐行抄进计划）。
2. 每列读出写明容差与判据（无范围/限值的 typical 值先向模块厂索要限值）。
3. 中间测量规程写死「关机→调温→测→开机→调温」次序。
4. 相关性判据：初始值 + 预期偏差最大百分比，双方签认后再开跑。
5. 击穿电压条款：先书面确认器件可测，否则引用 §6.1.9 免测并文档化。

> **B·边界**
- Table 6.1 是**表格转述**，行列对应以标准原件为准；本模块不复制全部格子。
- 读出矩阵不含 QE-02（Contactability）行——p24 表中无该行，属 QE-02 试验自身定义读出（模块 104）。
- 双脉冲在 Table 6.1 是读出列（动态试验），方法细节在 QC-01 引用的 IEC 60747-15 §5.3.2。

> **与其它模块的接口**
- 103（QC-01~05 各试验本体）、104（QE 各试验）、105/106（QL 各试验）。
- 107（Annex I.A 流程图 = Table 6.1 的图形版）。
- ICN 定义与厂商层 41（SOA）、Volke 层 30（标称电流）对照。

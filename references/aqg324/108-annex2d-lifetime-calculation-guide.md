# 108 · Annex II.D 功率模块寿命计算指南（任务剖面仿真全流程）

> **层归属**：标准层（references/aqg324/）；门：**E**（应用系统），跨 **C**（热模型/损耗）、**G**（PC 试验数据是模型输入）、**B**（失效机理对应）
> **页引用约定**：正文页零偏移；Annex II.D 为 PDF p84–98（作者 M. Thoben / T. Reiter，多特蒙德 FH + 英飞凌）。
> **定位**：这不是「再做一组试验」的规范，而是**方法论指南**——把 PC 试验验证过的寿命模型接到整车任务剖面上，算出整车寿命消耗。

> **R·原文锚点**
- p92（Rainflow 红线）：「The **Rainflow method**, a procedure from material mechanics, gives the best results for counting temperature swing which creates a comparable stress level [12].」；「The Rainflow Counting Algorithm according to **ASTM standard E 1049-85** [13] is directly implemented in MATLAB 2017b and later versions [14]. **ΔT, ton and Tvj will be directly extracted** from the implemented algorithm.」
- p92（ton 保守性）：「The extraction of ton will always result in a **conservative value** for the global maximum.」——算法把大温升段归到**长 ton 半周期**。
- p91（Rth 取值红线）：「To prevent **'overengineering'**, loss data and Rth values for Lifetime estimation should focus on **typical values before stress test**.」——datasheet Rth,max 常已含寿命退化余量，PC 试验条件本身已含 Rth 退化，两者叠加会双重打折。
- p94（ton<100 ms 可滤除）：「typical Al bond wires in power modules need **more than 100 ms** to heat up due to their thermal capacitance. Therefore temperature swings with ton times lower 100 ms usually can be **neglected and filtered** for drive inverter application.」
- p89（装配对寿命的放大）：「Comparing a Power module without baseplate to direct cooled Power Modules a temperature increase of **40 to 50 K** was calculated, which reduces the lifetime capability at same Power Cycle result numbers by **more than a factor of 10**.」
- p97（结论三连）：任务剖面应代表 typical 而非 worst case（模型本身已含概率，典型 5% 失效）；「Applying large safety margins in the range of 20% will reduce the power density and **double the lifetime**」；小参数变化→寿命大变化（见下）。

> **I·骨架**（本模块回答：从整车工况到寿命消耗的链条怎么搭、每步的坑在哪）
1. **七步链（Fig. 1）**：任务剖面（车速/电机转速/相电流/母线电压）→ 损耗计算 → 热仿真（温度剖面）→ Rainflow 提取（ΔTvj、ton、Tvj,max 直方图）→ 逐档寿命消耗（对照寿命曲线）→ 累加为**单一等效应力值** → 判定（100% 消耗 = 曲线存活概率下 5% 件到寿终）。
2. **损耗计算（式 2–5，1 阶线性化平均模型）**：
   - IGBT 导通 `P_IGBT_cond = I²·r·[(√2/π) + m·cosφ·(3π/8 − 4cosφ/…)] + I·VCE0·[(1/2) + m·cosφ·(2/π)]`（式 2，Srajber-Lukasch 1992 型；r、VCE0 随温度取值）；二极管式 3 同构（方向项为 −m·cosφ）。
   - IGBT 开关 `P_IGBT_SW = (fsw/π)·(Eon_nom+Eoff_nom)·(Î/Inom)·(VDC/Vnom)·(TJ/Tnom)^α`（式 4）——**1/π=0.3183 正弦系数**，与 igbt-master 既有纪律闭环（恒流才 1.0）。
   - 二极管开关 `P_Diode_SW = (fsw/π)·Erec_nom·(0.75·Î/Inom + 0.125π)·(VDC/Vnom)·(TJ/Tnom)^α`（式 5）——**0.75Î/Inom + 0.125π 偏置项**拟合 E_rec 低电流非线性，**量级上自动给出 E_rec 的底值行为**，与既有「E_rec 轻载线性缩放低估」登记互证。
   - **红线（p88）**：1 阶线性化模型「approximate precise the **high ΔT** but is **less precise for the low ΔT**. The approach should **not be re-used for efficiency simulations** where light load conditions are the most dominate ones.」——同一套损耗式，寿命仿真可用（高 ΔT 主导消耗），效率仿真不可用（轻载主导）。**公式随用途换精度档**。
   - 开关损耗必须在**最终逆变器设计**上特征化：Fig. 3 实例同模块同栅阻同栅压，仅换栅驱动电路 → Eon 可差 **100%**；无栅驱动/杂散电感信息不可能预测开关损耗。
3. **热模型（p88–91）**：装配分级——装配 1 无基板直冷（≤10 kW，Al₂O₃ DCB）、装配 2 铜基板（≤60 kW，前几秒热容降 Rth）、装配 3 Pin-Fin 基板（≤140 kW，最低稳态 Rth）。**交叉耦合**（Fig. 7）适用于 **>100 ms**；更短脉冲下一阶滤波**高估**耦合，只能当 worst case。温度剖面计算要用**典型 Rth（应力测试前）**——见锚点 R 第三条。
4. **Rainflow 计数（p92–93）**：ASTM E1049-85 算法，MATLAB ≥2017b 内置；从每个循环直接取 ΔT、ton、Tvj。ECPE 环形比对用人工温度剖面（Fig. 12）验证各厂实现，结果仅舍入级差异。**ton<100 ms 的循环滤除**（键线热容）；被动温度载荷（冷启动、冷却液从环境升温、气候温差）可并入完整剖面或单独仿真。
5. **寿命模型三式（p95）**：
   - LESIT（式 6）：`Nf = A·ΔTj^(−α)·exp(Ea/(kB·Tj,mean))`——Coffin-Manson + Arrhenius；**无 ton 项**，对焊料时效类退化不够。
   - Bayerer/CIPS2008（式 7）：`Nf = K·ΔTj^β1·exp(β2/(Tj+273))·ton^β3·I^β4·V^β5·D^β6`——含键径 D、电流、电压、ton；与厂商层 16、Lutz 层 96 同源。
   - 扩展（式 8，Scheuermann-Schmidt 2013 [21]）：`nf = A·ΔTj^α·(arr^β1·ΔTj+β0)·((C+ton)^γ/(C+1))·exp(Ea/(kB·Tjm))·fDiode`——针对**银烧结芯片贴装**的 Ag 扩散时效。
   - 曲线须代表确定存活概率（典型 **95%**）；IGBT 与 Diode 可以各有曲线；曲线上的星标点必须对应 PCsec/PCmin 实测节点（105 模块交付物）。
6. **参数敏感性（Fig. 18）**：典型 75 min 驾驶剖面上各参数 ±10% → **Rth −10% ≈ 寿命 +40%**；导通损耗/逆变器电流量级影响相近；Eon/Eoff/Erec/开关损耗影响次之。**20% 的安全裕度 ≈ 功率密度下降 + 寿命翻倍**——裕度不是免费的。

> **A1·案例**
- 双重保守陷阱：厂方 datasheet 给 Rth,max=0.5 K/W（已含 20% 退化余量）→ 工程师再取 20% 安全裕度做寿命仿真 → 实际等效三重保守，功率密度损失换来的寿命「虚胖」。正确做法：寿命仿真用典型 Rth，概率安全由模型 95% 存活率承担。
- ton 滤除实例：市内蠕行工况高频小 ΔT 循环（ton=20 ms）被误计入寿命消耗 → 模型在 ton^β3 项上严重高估消耗（键线根本没热透）；正确流程是 Rainflow 后先滤 ton<100 ms 档。
- 交叉耦合实例：相邻 IGBT-Diode 间距近，>100 ms 用耦合 R/C 网络可行；做 10 ms 级 boost 脉冲仿真时耦合矩阵高估 diode 温升——此时应降级为一阶滤波 worst case 或用 ANSYS 降阶模型。

> **A2·本地复算**
- 式 4 系数核对：fsw/π 与 igbt-master 既有登记「正弦 VSI 开关损耗 1/π=0.3183」一致 ✓（同章同系数，无 3.14 倍口径漂移）。
- 式 5 偏置项复算：Î/Inom=0.2（轻载）时电流因子 = 0.75×0.2 + 0.125π ≈ 0.15+0.3927 = 0.5427——**不为零**，印证 E_rec 有底（与「0.55 底」既有登记同量级）；纯线性模型会给出 0.75×0.2=0.15，低估 ~3.6 倍 ✓。
- 敏感性外推自检：Rth↓10% → ΔTvj↓ ~10%（IL 不变）→ 由 Bayerer β1≈4–5 外推 Nf 比值 ≈ (1/0.9)^4.5 ≈ 1.6，与文中「+40%」同量级（文献 β1 取值区间内）✓；ΔTvj↓20% → ≈ (1/0.8)^4.5 ≈ 3.4，与「裕度 20% → 寿命翻倍」量级一致 ✓。
- 40–50 K 的机制换算：无基板 → 直冷降温 40–50 K，按 Nf∝ΔTj^(−4.5) 外推远超 10×——文中「>factor of 10」用的是「same Power Cycle result numbers」约束下的实测口径，公式外推与实测口径不可混（登记为口径敏感点）。

> **E·触发场景**
- 客户要求「用任务剖面证明模块 15 年寿命」→ 本模块就是完整作业链。
- 评审整车厂 mission profile 仿真报告 → 逐条核对：Rth 用典型值？ton<100 ms 滤了没？Rainflow 是 ASTM E1049-85？损耗模型精度档对不对？
- 问「datasheet Rth,max 能不能直接拿来算寿命」→ 锚点 R 第三条 + A1 第一例。
- 选封装方案（无基板 vs Pin-Fin）→ 锚点 R 第五条的 10× 差距。

> **S·步骤**（任务剖面寿命仿真落地）
1. 取任务剖面（典型驾驶循环 + 车厂经验循环，不用排放循环 WLTC/CADC 充当寿命剖面——不反映真实驾驶）。
2. 损耗计算：导通用式 2/3（r、VCE0、VF0、rD 温度相关），开关用式 4/5；**开关损耗数据必须来自最终逆变器设计实测**（双脉冲/DPT 在目标栅驱动上做）。
3. 热仿真：R/C 网络（含交叉耦合，>100 ms）+ 冷却液流量相关参数（低速无流工况 Fig. 8）；**Rth 用典型值**。
4. Rainflow（ASTM E1049-85）提取 ΔTvj/ton/Tvj 直方图 → 滤除 ton<100 ms → 叠加被动温度载荷。
5. 逐档查寿命曲线（95% 存活率）→ 累加寿命消耗 → 单一等效应力值 → 判定 <100%。
6. 敏感性回查（Fig. 18 口径）：确认 Rth/损耗/电流取值偏差对寿命的杠杆，向系统侧提出参数公差要求。

> **B·边界**
- 本指南**不产生试验要求**，只消费 105 模块 PC 试验产出的模型节点；寿命模型形式须与模块厂对齐（曲线拟合方法不限式 6/7/8）。
- 1 阶线性化损耗模型**只用于寿命仿真**，禁用于效率仿真（轻载失真）。
- 交叉耦合网络法对 <100 ms 脉冲是 worst case 高估；降阶模型（ANSYS 等）才是短脉冲正解。
- 95% 存活率是 AQG 样本量（105 模块）能支撑的上限——「定义更高概率不合理且不会带来更好的寿命预测」。
- 模型按典型剖面标定；typical ≠ worst case 是设计哲学，混用会双重保守。

> **与其它模块的接口**
- 105（PCsec/PCmin——寿命曲线节点数据的唯一合规来源；ton 5–15 s 空档）。
- 109（Annex III.A SiC 的 PC 试验——曲线节点同样进本流程）。
- 107（Annex I.C 模板——交付的寿命模型格式在这里被消费）。
- 机理与既有层：Bayerer 模型（厂商层 16、Lutz 层 96）、烧结银时效（封装层）、Rainflow/疲劳计数（Lutz 层）、1/π 正弦系数与 E_rec 底值（既有红线登记——本模块给出标准级原文出处，**原「二手源交叉」升格为标准原文锚定**）。

# 105 · QL 功率循环 PCsec / PCmin（第 9.1–9.3 节：寿命试验核心）

> **层归属**：标准层（references/aqg324/）；门：**G**（可靠性与认证），跨 **C**（ΔTvj 控制）、**H**（EOL→失效机理归属）、**B**（chip-near/chip-remote 应力分配）
> **页引用约定**：正文页零偏移（PDF 页 = 标准页）。

> **R·原文锚点**
- p48（§9.2.1）：「By limiting the key parameter ton … to a value range of **ton < 5 s**, the tests exert targeted stress on the **chip-near** interconnections (die-attach and top-side contacting).」
- p55（§9.3.1）：「If the time range of the key parameter value ton is expanded to values from **ton > 15 s**, this test exerts a different stress … The stress can be applied to the **chip-remote** interconnection (system soldering) **as well as** to the chip-near interconnection technology. This test thus enables **pro rata simulation of … a cold start**.」
- p49（控制策略红线）：「All other control methods, e.g. controlling … via the monitoring of the heat sink temperature Ts or the base plate temperature Tc, or **controlling using constant power loss PL, are not permissible**.」；「A change in the temperature rise of the virtual junction temperature ΔTvj in connection with this during the test duration is therefore **accepted, reflecting the aging of the DUT**.」
- p49/p57（Tvj 测量红线）：「The calculation of the junction temperature Tvj using the thermal resistance and the power loss PL provided in the datasheet is **not permissible**.」

> **I·骨架**（本模块回答：PCsec/PCmin 怎么跑、怎么控、怎么判 EOL）
1. **定位与分工**：两者都是「验证模块厂寿命模型」的加载试验（结果即模型节点数据）；母法 **IEC 60749-34:2011**（其表 1 试验条件**明确不采用**——不适于验证寿命模型）。**PCsec（ton<5 s）打 chip-near**（贴片层+顶面互连）；**PCmin（ton>15 s）兼打 chip-remote（系统焊）**，比例化模拟冷启动。5–15 s 之间是两谱的空档（标准未定义，选点须与客户商定）。
2. **加载与控制的硬约束**（§9.2.2/9.3.2，两分支同构）：
   - **ton/toff 固定值控制**，试前定好；跑合（run-in）后**全部控制参数保持到寿终**；栅压开头定死不许中途调；ΔTvj 随老化的漂移**接受**（它就是老化信号）；
   - **只许用栅压微调** ΔTvj（饱和区内、开头一次设定）——不许用 Ts/Tc 反馈控制、不许恒损耗控制；
   - **IL > 0.85·ICN（IDN）只能用于一个采样点**；第二个采样点可用 <0.85·ICN 以拉开 ΔTvj 差距（表注 a/b）；
   - Vgate 典型 **15 V**（IGBT）；Qcool 恒定并记录；
   - **至少两个 ΔTvj 点，最大者比最小者高 ≥40%**（才能撑起 Nf=f(ΔTvj,Tvj,max,ton) 曲线的节点）；
   - 结构相似 DUT 的**全部拓扑开关**都要在各 ΔTvj 点覆盖（模块内每个半导体至少被测一次），被测开关间避免热交互；
   - 样本量：**≥6 个拓扑开关、来自 ≥3 个不同 DUT**，覆盖应用相关电流路径。
3. **Tvj 与监测纪律**：Tvj 用 **VCE(T) 法**（Annex II.B [2] §3）或经相关性验证的芯片测温；**禁用 datasheet Rth×PL 反算**；Tc/Ts 参考点取图 7.2/7.3；无基板模块须先记录 **TIM 沉降（settling）过程**再定起始值（ΔTvj,start、Nstart 进 Table 9.2/9.5 文档化清单）；试验中**不许拆下 DUT 测 Rth**——做不到在线测时经客户同意可用 ΔTvj 代替 Rth 判 EOL。
4. **EOL 判据**（Table 9.3 = 9.6，p54/61）：**正向压降 +5%**（IGBT VCE,sat / MOSFET VDS / 二极管 VF,VFSD，以标准值为基准）；**热阻 +20%**（Rth,j-c/j-s/j-f 任一，或可选 ΔTvj）；逐循环连续监测压降与 ΔTvj，记录粒度须支撑 EOL 精确定位；Rth 时长充分性用 datasheet Zth 曲线核验（表注 b）；在线测不了 Rth,j-c 时的间接式：`Rth,j-c = Rth,j-c(datasheet) + [Rth,j-s(实测) − Rth,j-s(实测,起始)]`。
5. **二极管与 MOSFET 特款**：二极管寿命模型必须确认——若厂方保证与开关管同等功率循环能力（同 chip-near 工艺 + 小单芯片），可降为**至少一个条件的确认试验**（全二极管）；MOSFET 用**体二极管发热**加热（不许走沟道测温），必要时加负栅压全关断沟道并记录；体二极管发热方案须厂方论证 + 客户批准，电流可取 <0.85·IDN 以防超芯片功率。
6. **结果评价（§9.2.3/9.3.3）**：各 DUT 的 Nf 标注到厂方寿命曲线，**建议标概率（如 5%）**；**只允许同一失效机制的 DUT 进入统计**——机制偏离者剔除并记录、换新 DUT 重测；**无法明确归因于 AIT 老化的半导体失效不允许出现**；试验后推荐 SAM 检查焊点/衬底/芯片/外壳裂纹。

> **A1·案例**
- 采样点设计实例：PCsec 想做 ΔTvj=60 K 与 100 K 两点 → 第一点 IL=0.9·ICN（>0.85），第二点只能降电流（如 0.7·ICN）拉大 ΔTvj——**两点都 >0.85·ICN 违反表注 a**。
- 5%/20% 判据落到机制：VCE,sat +5% ≈ 顶面键合/接触电阻抬升（chip-near）；Rth +20% ≈ 贴片层空洞/分层扩展（PCsec）或系统焊退化（PCmin）——两条判据各自抓一条失效链，**谁先到谁定义 Nf**。
- ΔTvj 漂移的读法：ton=const 策略下老化使 ΔTvj 缓升是**预期行为**（p49 注）；若把 ΔTvj 反馈控稳，等于把老化信号抹掉，寿命模型标定失真——这就是禁恒 ΔTvj 控制的根因。

> **A2·本地复算**
- 40% 拉差自检：ΔTvj 两点 60 K/100 K → 100/60 ≈ 1.67 ≥1.40 ✓；60 K/80 K = 1.33 ✗ 不合规。
- ton 谱系复算：PCsec ton<5 s、PCmin ton>15 s → 周期比 ≥3×；与 Bayerer 模型的 ton 指数（厂商层 16、Lutz 层 96）对照——**跨 ton 段的 Nf 换算必须回到模型项 (Nf·β^−1 = A·ΔTj^β1·Tj^β2·ton^β3)**，PCsec 数据不能直接外推 PCmin 工况。
- EOL 判据与既有登记闭环：+5%/+20% 双判据**原始出处落定**（此前 igbt-master 记为「二手源交叉」）——TST 的 Rth +20%（§8.2.3）与本表同源同值。
- 样本量语义：≥6 开关/≥3 DUT 是**每 ΔTvj 点**的量（读「scope of random samples for this test」），两点合计 ≥12 开关的解读须与客户确认——登记为口径敏感点。

> **E·触发场景**
- 搭功率循环台架 / 评审厂方 PC 方案 → 本模块即完整 checklist（控制策略/采样点/样本量/EOL）。
- 问「为什么不用恒 ΔTvj 控制」→ §R 第三条红线 + A1 第三例。
- 寿命模型交付评审 → Nf 节点必须来自本试验，概率 5% 标注，单一失效机制筛选。
- MOSFET 模块 PC 方案 → 体二极管加热 + 负栅压条款全套。

> **S·步骤**（PC 试验落地顺序）
1. 按 chip-near（PCsec）/ chip-remote（PCmin）选分支，确认母法 IEC 60749-34:2011 + 本节增补。
2. 试前预标定：VCE(T) 法标定、ΔTvj 两点（差 ≥40%）、IL 采样点（一点 >0.85·ICN）。
3. 跑合期定 ton/toff/栅压/Qcool → 固定到寿终；无基板模块先跑 TIM 沉降并记录 Nstart。
4. 逐循环监测 VCE,sat/VDS/VF 与 ΔTvj（+ 在线 Rth 或约定的 ΔTvj 代用）。
5. 首个 EOL 即停（建议继续加载），取 Nf → 标到寿命曲线（标概率）。
6. SAM 复查 + 失效机制归因筛选 → 换掉异机制 DUT 重测 → 按 Annex I.C 模板 C.2（PCmin 显式引用）出报告。

> **B·边界**
- 本试验**验证**厂方模型，不产出现象学模型——模型形式（Coffin-Manson/Bayerer 等）在厂商层 16 与 Lutz 层 96。
- IEC 60749-34:2011 表 1 的「标准试验条件」被显式弃用——别拿通用功率循环参数表套 AQG 方案。
- ΔTvj 代 Rth 判 EOL 必须**客户书面同意**；Rth 间接式只在「datasheet j-c + 实测 j-s 漂移」假设成立时用。
- ton 在 5–15 s 之间无定义档；跨档换算受 Bayerer ton 指数约束，无数据支撑不做外推。

> **与其它模块的接口**
- 106（存储/偏压类 QL-03~07）、104（TST 的 Rth+20% 同判据）、107（Annex I.B Delta 矩阵中 PC 项）、108（Annex II.D 寿命计算指引——本试验数据是它的输入）。
- 机理：键合脱层（封装层 76、Lutz 层 96 失效物理）、系统焊疲劳（封装层 75）。
- 测温：VCE(T) 法与厂商层 45、Lutz 层 99 的测量链口径闭环。

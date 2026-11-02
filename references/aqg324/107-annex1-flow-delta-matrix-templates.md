# 107 · Annex I 规范性补充：试验流程图 / Delta 变更矩阵 / 文档模板

> **层归属**：标准层（references/aqg324/）；门：**G**（可靠性与认证），跨 **B**（变更→互连层级映射）、**H**（失效机理归因进模板）
> **页引用约定**：正文页零偏移（PDF 页 = 标准页）；Annex I 为 p72–77。

> **R·原文锚点**
- p72（Annex I.A）：「The numbers in the test flow chart in following figures indicate **the number of topological switches** to be tested (compare section 4.1.2).」
- p72（QC 复用规则）：「The test flow chart QC attempts to **minimize the number of DUTs by using DUTs multiple times in case of non-destructive testing**. As an alternative, all tests can also be conducted with new modules.」
- p74（Annex I.B）：Table B.1「Delta qualification matrix」+ 脚注 a：「According to chapter 8.3 it is pursued to specify suitable and beneficial testing routines for 'contactability' in later releases. Therefore, this empty column is **inserted intendedly already now as a placeholder**.」
- p74（generic data 条款）：「The use of generic data per test is permissible (**except for characterization tests**) as long as the difference between the module to be qualified and the reference module is documented and it can be verified that the differences … do not cause any changes in the module's properties.」
- p75（Annex I.C）：「Documentation of the tests must be provided in written form as part of the **Production Part Approval Process (PPAP)** documents.」
- p75（可靠性图强制要求）：「The parameters **VCE/DS/F = f(N) and ΔTvj = f(N) must be shown graphically** for the individual DUTs for each test and each tested temperature rise ΔTvj,1 … ΔTvj,n. … The procedure for creating the reliability diagram must be documented (allocation of the probability of failure …, method for the regression to the **Weibull density**, basis for the lifetime model (e.g. **Arrhenius, Coffin-Manson, CIPS2008**)).」

> **I·骨架**（本模块回答：整套认证怎么排队、设计变更后最少重做哪些试验、报告里必须交什么表）
1. **Annex I.A 三张流程图（Figure A.1 QC / A.2 QE / A.3 QL）**：
   - 图中数字 = **受测拓扑开关数**（不是模块数！读图第一红线）。
   - **QL 流程（Figure A.3，p73）**：总规模 **30+12 个模块**（数量随每模块电流路径数浮动）→ 全部先做 Module test–PRE（Table 6.1）→
     - **功率循环支路：2×6 拓扑开关（每模块 3 个）**——QL-01 PCsec（3 个开关）与 QL-02 PCmin（3 个开关），产出 Test/EOL parameter + lifetime model；
     - **存储/偏压支路：30 个模块**——QL-03 HTS（6）、QL-04 LTS（6）、QL-05 HTRB（6）、QL-06 HTGB（2×3=6，正负栅压各半）、QL-07 H3TRB（6），每个试验后接 **Module test–POST（Table 6.1）→ DRIFT documentation**。
   - **QC 流程（Figure A.1）**：非破坏试验允许**同一 DUT 复用**以压缩样本量；替代方案是全部用新模块。
2. **Annex I.B Delta 矩阵（Table B.1）**——「改了什么 → 最少重测什么」的规范性映射（10 种变更 × 16 试验列）。**逐格值已经 fitz 表格提取核验**（读图不可靠：PDF 文本流里 x 与空格乱序，曾致行级误读）：
   | 变更类型 | 触发的试验 |
   |---|---|
   | ① 基板底板（base plate）材料/几何 | QC-02 Rth、QC-04 绝缘、QC-05 机械数据、QE-01 TST、QE-03 振动、QE-04 机械冲击、**QL-02 PCmin** |
   | ② 陶瓷基板（substrate）材料/几何 | QC-01 Lp、QC-02 Rth、QC-03 短路、QC-04 绝缘、QE-01 TST、**QL-02 PCmin、QL-07 H3TRB** |
   | ③ 封装体（gel/塑框/塑封料） | QC-01 Lp、QC-04、QC-05、QE-01 TST、QE-03、QE-04、**QL-03 HTS、QL-04 LTS、QL-06 HTGB、QL-07 H3TRB** |
   | ④ 端子（frame bond wire 等） | QC-01、QC-03、QC-04、QC-05、QE-01、QE-03、QE-04、QL-03、QL-04、QL-06、QL-07 |
   | ⑤ 芯片至少一个接触区变更 | QC-01～04、**QL-01、QL-02、QL-07** |
   | ⑥ 芯片贴装（die attach）**材料**变更 | QC-02～04、QE-03 振动、QE-04 冲击、QL-01、QL-02、QL-05、QL-06、QL-07 |
   | ⑦ 系统（system）焊料材料变更 | QC-02、QC-04、**QE-01 TST**、QE-03、QE-04、QL-01、QL-02、QL-05、QL-06、QL-07 |
   | ⑧ 新半导体器件/材料/无源件（含换厂） | QC-01～04、QE-01、QL-01、QL-02、QL-05、QL-06、QL-07 |
   | ⑨ 芯片贴装**工艺**变更（焊/烧结/扩散焊） | QC-02～04、QE-01 TST、QL-01、QL-02、QL-05、QL-06、QL-07 |
   | ⑩ 顶面连接**工艺**变更（线键合/铜带/clip/烧结） | QC-01～04、QE-03、QE-04、QL-01、QL-02、QL-05、QL-06、QL-07 |
   - **矩阵的结构规律**（自洽性校验通过）：QE-02 CO 列整列空白（占位，脚注 a）；所有寿命试验列从不因「端子/封装体」这类非互连变更而触发 PC；**die attach 材料变更不触发 TST，而 die attach 工艺变更触发 TST**——标准制定者把 TST 应力归到 chip-remote（系统焊/基板界面），chip-near 贴装层的探查交给 PCsec；系统焊料变更触发 TST 且不触发 QC-01/03。
   - **generic data 边界**：特征化试验（QC-01～05）**不得**用 generic data；其余试验可用，前提是变更差异已文档化且证明不改变模块特性。
3. **Annex I.C 文档模板（PPAP 附件）**：
   - **C.1 PCsec 模板**：ΔTvj、Tvj,max、Tvj,avg、Tcool、ton、toff、IL、Vgate + 可靠性数据表（DUT no. / Cycles until EOL / Failure pattern）+ 寿命模型声明（**IGBT / Diode / Solder 三条 Nf=f(ΔTvj, Tvj,max, ton)**）。
   - **C.2 PCmin 模板**：在 C.1 基础上**换掉 Tvj,avg → Tc/s,max 与 Tc/s,min（系统焊/外壳温度上下限）+ Rth [K/W]**——PCmin 的 Stress 对象是系统焊，报告必须直接给出系统焊温度幅值与热阻。
   - **C.3 TST 模板**：ΔT、Tstg,min/max、tcycle、**温变斜率 T/t slope(10/50) 与 slope(10/90)**、保温时间 tdwell + 结果表 + **Rth 漂移表（0/500/1000 循环三点）**。
   - 强制图形：每个 DUT、每个 ΔTvj 档的 **VCE/DS/F=f(N) 与 ΔTvj=f(N)** 曲线；SAM 图像若做了必须归档。
   - 模板把「试验记录」与「模型交付」锁在一张 PPAP 文件里：没有 EOL 数据 + 寿命模型声明 = 报告不合格。

> **A1·案例**
- 变更评估实例：把 Al 顶面焊线换成 Cu 线（变更⑩）→ 最少重做 QC-01～04 + QE-03/04 + QL-01/02/05/06/07，**不触发 TST/QE-01**（顶面互连不是 TST 主应力对象）；但换贴装工艺从回流焊改银烧结（变更⑨）→ 触发 TST。
- 读图陷阱实例：工程师把 Figure A.3 里的「3」读成 3 个模块 → 实际是 **3 个拓扑开关**（§4.1.2 口径），按每模块 3 个电流路径折算 QL-01 只需 1 个模块；30+12 的总规模里 12 个就是两条 PC 支路的 2×6 开关。
- PPAP 审查实例：供应商交 PCsec 报告只有汇总表没有逐 DUT 的 VCE=f(N) 曲线 → 直接违反 C.1 强制条款打回；报告没写 Weibull 回归方法和失效概率分配 → 可靠性图无效。

> **A2·本地复算**
- 流程图样本量守恒：QL 支路 2×6=12（PC）+ 6×5=30（存储/偏压，其中 HTGB 是 2×3）= 42 = 30+12 ✓。
- Delta 矩阵列守恒：10 行 × 逐行 x 数（7/7/10/11/7/10/10/10/9/11）全部 ≤16 列，QE-02 列 0 命中（占位脚注自洽）✓。
- 矩阵机理自洽：变更①（base plate）触发 QL-02 PCmin 而非 QL-01 PCsec——base plate 退化是 chip-remote（系统焊）路径，与 105 模块「PCmin 兼打 chip-remote」的定位闭环 ✓；变更⑤（芯片接触区）同时触发 QL-01+QL-02——接触区横跨 chip-near 与 chip-remote 两层 ✓。

> **E·触发场景**
- 客户问「这个设计变更要重新认证哪些项目」→ 直接查矩阵行 + generic data 条款。
- 排认证预算/样本量 → Figure A.3 的 30+12 与各试验开关数。
- 评审供应商 PC/TST 报告 → C.1/C.2/C.3 模板逐栏核对，缺 VCE=f(N) 曲线或 Rth 漂移表即打回。
- 谈「为什么我们改个灌封胶要做 HTS/LTS」→ 矩阵行③，湿气/温度类存储试验是封装体的主探查手段。

> **S·步骤**（变更→再认证流程）
1. 在 Table B.1 的 10 行中定位变更类型（一行放不下就取并集）。
2. 对照 generic data 条款判断能否引用既有数据（QC 一律重做）。
3. 按 Figure A.1–A.3 排 DUT 数量与试验顺序（QC 复用非破坏 DUT；QL 全部 PRE→试验→POST→DRIFT）。
4. 按对应模板（C.1/C.2/C.3）出 PPAP 文档：参数表 + EOL 表 + 逐 DUT 曲线 + 模型声明 + SAM 归档。
5. 有疑问的格子回原 PDF Table B.1 高清图核对（本模块矩阵经 fitz 提取核验，但引用时仍以原图为准）。

> **B·边界**
- 矩阵是**最少集**（minimum）：客户可加严，厂方不可减项；QE-02 CO 列是占位，Rel03.1 尚无可执行的可接触性试验规范。
- 「拓扑开关数 ≠ 模块数」换算依赖每模块电流路径数，Figure A.3 的 30+12 注明「depending on number of current paths per module」。
- 106/105 模块里的试验条件（温度/时长/判据）不因 Annex I 而改变——本模块只管「做几个、什么顺序、交什么文档」。
- generic data 的「不改变模块特性」证明责任在申请方，客户有权要求重测。

> **与其它模块的接口**
- 101（§4.1.2 拓扑开关定义——流程图数字的口径源）、102（Table 6.1 module test——PRE/POST 的内容）、104（TST 判据与 C.3 模板闭环）、105（PCsec/PCmin 条件与 C.1/C.2 模板闭环）、106（QL-03～07 顺序即流程图右支）。
- 108（Annex II.D——C.1/C.2 交付的寿命模型如何被任务剖面仿真消费）、109（Annex III.A SiC 的流程增量）。

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""igbt_book_ledger.py -- 书源数据的"台账 / 计算器"五项（零第三方依赖）

与 igbt_book_budget.py 的分工：
  igbt_book_budget.py  算**式子里给了的**（DESAT 预算、短路能量、端子电压、并联降额、死区）
  igbt_book_ledger.py  算**带区间的 / 要记账的 / 要防陷阱的**（Miner 累积、AQG 试验台账、
                       R_th 链、CTE 失配、单位陷阱换算、书未给红线自检）

设计原则（重要）
  1. 每个子命令输出都带 [来源] / [假设] / [书未给] 标记，不许出现"无来源的确定数"。
  2. 涉及书内不一致值（CTE、λ）的子命令，**强制要求 --source 声明用哪一套**，
     不给默认值 —— 这是本技能最重要的纪律（见 references/material-database.md §0.2）。
  3. 书没有的数据一律 `n/a`，不给"典型值"。

子命令
  miner       Miner 线性累积（式 14.12）：多段周次 → 等效周次 → 小时 → 年
  aqg         AQG 324 试验台账骨架（样本量 / 状态 / 判据留空，只算与统计）
  rth         热阻链加总与反解（区分"自上而下"与"自下而上"两种口径）
  cte         CTE 失配矩阵与失配比（强制声明取值来源）
  unit        书内单位陷阱换算（Ω·mm²/m ↔ μΩ·cm、ppm/K 与 ΔL/L 等）
  redline     书未给红线自检：检查一份报告文本里是否把"书未给"当成了"书内数据"

示例
  python igbt_book_ledger.py miner --n 1.13e6 --n 4.11e6 --n 37.72e6 --n 0.36e6 --t-cyc 300
  python igbt_book_ledger.py miner --n 1.13e6 --n 4.11e6 --dT 24 --dT 18 --label "子周期1" --label "子周期2"
  python igbt_book_ledger.py cte --a 5 --b 17 --source table42 --name-a AlN --name-b Cu
  python igbt_book_ledger.py cte --a AlN --b Cu --source table42
  python igbt_book_ledger.py rth --rjc 0.055 --rbase 0.013 --rtim 0.003 --rhs 0.038 --ploss 1068 --tc 85
  python igbt_book_ledger.py unit --ohm-mm2-m 0.0264
  python igbt_book_ledger.py redline --file my_report.md
  python igbt_book_ledger.py aqg --list
  python igbt_book_ledger.py aqg --type module_si --n-sample 30

返回码：0 = 通过 / 无告警；1 = 有 FAIL 或红线命中；2 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 材料 CTE 三口径表（references/material-database.md §0.2）
# 每个值: (值, 等级, 出处)
# ---------------------------------------------------------------------------
CTE_SETS = {
    "p50": {          # A 套：书 p50 正文叙述，未标温度
        "Si":   (4.0, "L3", "书 p50"),
        "AlN":  (4.1, "L3", "书 p50"),
        "Al2O3": (7.1, "L3", "书 p50"),
    },
    "table42": {      # B 套：表 4.2，明标 20 ℃（**做定量计算的唯一合法口径**）
        "Si":    (3.0,  "L3", "书 p127 表 4.2（20 ℃）"),
        "AlN":   (5.0,  "L3", "书 p127 表 4.2（20 ℃）"),
        "AlSiC": (8.0,  "L3", "书 p127 表 4.2（区间 7–10，取中值 8）"),
        "Al2O3": (8.0,  "L3", "书 p127 表 4.2（20 ℃）"),
        "Cu":    (17.0, "L3", "书 p127 表 4.2（20 ℃）"),
        "Al":    (25.0, "L3", "书 p127 表 4.2 未列；取表 14.6 的 25，图 14.7 读 ~23"),
        "SnAg35": (57.0, "L3", "书 p127 表 4.2（20 ℃）"),
        "Fe":    (12.2, "L3", "书 p127 表 4.2"),
        "Au":    (14.2, "L3", "书 p127 表 4.2"),
        "Ag":    (23.0, "L3", "书 p127 表 4.2"),
    },
    "fig147": {       # C 套：图 14.7 柱状图读数，±0.5
        "Si":    (2.6, "L3", "书 p374 图 14.7（读数，±0.5）"),
        "AlN":   (4.0, "L3", "书 p374 图 14.7（读数，±0.5）"),
        "Al2O3": (7.0, "L3", "书 p374 图 14.7（读数，±0.5）"),
        "AlSiC": (8.0, "L3", "书 p374 图 14.7（读数，±0.5）"),
        "Cu":    (17.0, "L3", "书 p374 图 14.7（读数，±0.5）"),
        "Al":    (23.0, "L3", "书 p374 图 14.7（读数，±0.5）"),
    },
}

# 各口径下同一材料的取值范围（用于"跨口径不能混用"的告警）
CTE_RANGES = {
    "Si":    [2.6, 3.0, 4.0],
    "AlN":   [4.0, 4.1, 5.0],
    "Al2O3": [7.0, 7.1, 8.0],
    "AlSiC": [7.0, 8.0, 10.0],
    "Cu":    [16.5, 17.0],
    "Al":    [23.0, 25.0],
}

# 书未给清单（34-formula-index.md §12 / material-database.md §9）
REDLINE_PATTERNS = [
    (r"(Arrhenius|阿伦尼乌斯).{0,12}(γ|gamma)\s*[=＝]\s*[\d.]", "Arrhenius γ 书未给"),
    (r"(Coffin.?Manson|科芬).{0,20}(指数|c)\s*[=＝]\s*[\d.]", "Coffin-Manson 指数 c 书未给"),
    (r"(\bc\s*[=＝]\s*[2-5]\b).{0,20}(Coffin|寿命)", "把 c=2~5 当值代入"),
    (r"(Peck).{0,12}n\s*[=＝]\s*[\d.]", "Peck 指数 n 书未给"),
    (r"(Bayerer).{0,20}(β|beta)[0-9１-４]?\s*[=＝]\s*[\d.]", "Bayerer β1~β4 书未给"),
    (r"E_?as\s*[=＝]\s*[\d.]", "E_as 书未给"),
    (r"(熔断器|fuse).{0,20}I²?t\s*[=＝]\s*[\d.]", "熔断器 I²t 书未给"),
    # v2.7.0 收窄：原来 `HDF.{0,12}=数字` 会把「HDF_DMIN = 6 × (...)」判成"给了个 HDF 系数"，
    # 实际那是式 13.23 的第二项系数，不是 HDF 结果值。现在只抓"直接给 HDF 结果"：
    # 等号前的标识符必须以 HDF 结尾（如 `HDF = 0.21` 或 `HDF_SPWM = 0.21`），且等号后**不是** 6（那是 a2 系数）。
    (r"HDF[_A-Za-z]*\s*[=＝]\s*(?!6(?![\d.]))[\d.]+\s*(?!\s*[×*·])", "HDF 结果值书未给（四式代入发散，只能读图 13.20）"),
    (r"R_?th\s*\(?j-?c\)?\s*[=＝]\s*0\.[0-9]+\s*K/W.{0,12}(典型|通用|一般)", "R_th(j-c) 典型值书未给"),
    (r"驱动功率.{0,12}[=＝].{0,4}(P_?G|P_?GE).{0,4}η", "驱动功率显式式书错（式 6.12c η 应作分母，v2.7.0 确认）"),
    (r"探头.{0,6}(延时|补偿).{0,10}[=＝]\s*[\d.]", "探头延时补偿书未给"),
    # 归因类：把"书未给"的参数当成了"书内数据"来源（这一段是历史事故的固化）
    # 中文语序两种都常见：「据《IGBT 模块》p383 的 Coffin-Manson 指数」（出处在前）
    #                   「c=3 取自《IGBT 模块》p383」（系数在前）
    # 所以这里必须**双向**匹配，只写单向会漏掉更常见的前者（v2.2.0 修）
    (r"(据《?IGBT\s*模块》?|本书\s*p?\d*|书\s*p\d+)[^\n]{0,40}(Coffin|Bayerer|γ|β\d|E_?as|HDF|指数\s*c)",
     "把『书未给』的系数挂到了书本出处上（出处在前，**最严重的一类**）"),
    (r"(Coffin|Bayerer|γ|β\d|E_?as|HDF)[^\n]{0,30}(《IGBT\s*模块》|本书\s*p?\d*|书\s*p\d+)",
     "把『书未给』的系数挂到了书本出处上（系数在前，**最严重的一类**）"),
    # 式子误用类（v2.5.0 新增）：书给了式子但式子本身错 —— 比"书未给"更危险
    # 式 13.9（p347）分子缺 I_peak、量纲不成立，照抄小 1000 倍；正确用 C = L*I^2/dU^2
    # 判别要点：错式里 I_peak 是**一次方且紧跟除号**（I_peak/U²）；正确式里 I_peak 后面是
    # 平方记号（² 或 ^2），不紧跟 "/"。所以 `I_?peak\s*/` 就能区分两者，不需要看有没有 ²。
    # 比较运算符要同时容纳 = ≈ ≃（书 p347 印的是 ≈，v2.6.0 修：原来只认 =，漏检）。
    (r"(C_?S(nubber|n)?|缓冲电容|吸收电容)[^\n]{0,60}?[=＝≈≃][^\n]{0,25}?L[^\n]{0,20}?I_?peak\s*/",
     "用了量纲不成立的式 13.9（I_peak 取一次方，实为二次方，结果小 I_peak 倍）→ 改 C = L·I²/ΔU²"),
    # 上面抓「把错式子写出来」，这条抓「只引式号不写式子」的情形（同样危险，因为无从复核）。
    # 前置否定 lookbehind 是为了不误伤本技能自己写的「不要用式 13.9」这类**警告句**——
    # 警告句和误用句的差别只在两三个字，不排除的话工具会把自己的忠告判成违规。
    (r"(?<!不)(?<!不要)(?<!不能)(?<!不用)(?<!不应)(?<!切勿)(?<!禁止)(?<!勿)(?<!别)(按|依|用|采用|据)\s*式\s*13\.9",
     "把缓冲电容取值挂在式 13.9 上（式号引用同样不可用）→ 改 C = L·I²/ΔU²"),
    # v2.7.0 新增：式 6.12c 驱动功率 η 方向错（书 p176 明文定义 η 为效率，书却印成乘）
    # 抓法：同一行里既有「驱动/DC-DC 功率」又有「×η / *eta / ·η」这种**乘**的形态。
    # 除以 η 是正确写法（(P_GE+P_CG)/η），所以要排除紧跟除号的 η。
    (r"(P_?DC-?DC|驱动.{0,6}功率|驱动电源.{0,4}功率)[^\n]{0,60}?[×*·]\\?\s*(η|eta)",
     "用了式 6.12c 的 η 乘号（书 p176 印作乘，但 η 是效率，必须除）→ 改 (P_GE+P_CG)/η，比值差 η²"),
    # 式 13.23 / 13.24（HDF 的 DPWM 两式）：任何 m 下都偏图 3–10 倍，m≥0.7 变负
    (r"HDF[^\n]{0,20}(DMIN|DMAX)[^\n]{0,40}?[=＝][^\n]{0,30}?6\s*[×*·]",
     "用了 HDF 式 13.23/13.24（代入发散，偏图 13.20 读数 3~10 倍，m≥0.7 变负）→ 改读图 13.20"),
]

# 书内已知不一致（00-index.md §6）——命中时提醒必须标注口径
INCONSISTENCIES = [
    ("式 1-3", r"N_?D\s*[=＝]\s*10\^?1[45]", "例 1-3 的 N_D 与 x_SCR 不自洽（单边结应 14.95 μm，反推 N_D≈10¹⁴）"),
    ("p173", r"278\s*Ω|278\s*ohm", "图 6.27 应 417 Ω，书印 278 Ω"),
    ("p365", r"350\s*FIT", "正文 350 FIT，代入式用 250 FIT"),
    ("表 14.4", r"t_?ch?g?\s*(≤|<=)\s*3\s*s", "TST 的 t_stg ≥1 h 与 ≤3 s 并存（疑后者为转移时间）"),
    ("H3TRB", r"±\s*100\s*nA", "p373 H3TRB ±100 nA vs p372 HTRB ±100 μA，差千倍"),
    ("式 3.19", r"软因数", "式 3.19 软因数符号存疑"),
    # v2.7.0：η 已确认方向错；正则收窄到「6.12c」或「驱动功率…η」，
    # 原来单个 η 字符会命中任何讲效率的句子，噪声极大。
    ("式 6.12c", r"6\.12c|(驱动|DC-?DC)[^\n]{0,20}η", "式 6.12c η 应作分母（v2.7.0 确认，非存疑）"),
    ("式 13.21", r"13\.2[1-4]", "式 13.21–13.24 HDF：13.21/13.22 差 4/π 口径，13.23/13.24 发散（v2.7.0 结案，非排版问题）"),
    ("p61", r"10\^6\s*V/m|10⁶\s*V/m", "书 p61 印 10⁶ V/m，应为 10⁸ V/m（10 nm × 10⁸ ≈ 1 V）"),
    ("p370", r"21494", "21494 与表 14.2 合计 9097 口径不同"),
    # v2.7.0 反向测试补：原来「式 6.12c η 方向」只查"提没提"，不查"乘还是除"。
    # 于是一份**照抄错式**的笔记（× η）反而顺利通过 —— 假阴性。
    # 现在查真实形态：括号内的 (P_GE…+…) 直接乘 η 即判违规。
    ("式 6.12c·乘号",
     r"(?<![/÷])\(\s*P_?GE[^)\n]{0,30}\+[^)\n]{0,30}\)\s*[×*·]\s*η"
     r"|(?<![/÷])η\s*[×*·]\s*\(\s*P_?GE",
     "把它乘了 η —— η 是效率，必须作分母（÷η）；乘除差 η²（η=0.85 时约 1.38 倍）"),
    # v2.7.0 反向测试补：正弦 VSI 的开关损耗必须带 1/π，漏了就是 3.14 倍。
    # 只抓「同一行里出现 E_sw/P_sw 与 f_sw，却没有任何 1/π 或 0.318」的写法。
    ("1/π 折算",
     r"(?:E_?(?:sw|on|off|ts)|P_?sw)[^\n]{0,24}?[×*·]\s*f_?sw",
     "开关损耗式里没出现 1/π 或 0.318：正弦 VSI 单管用 0.3183，恒流/斩波才用 1.0（差 3.14 倍）"),
    # v2.7.0：式 3.27（p105）与式 5.1（p143）是同一判据的两次印刷。
    # 分别引成两个结论，会让人以为是两条独立的校核、互相印证——实际是同一条。
    ("3.27≡5.1",
     r"式\s*3\.27[^\n]{0,200}?式\s*5\.1|式\s*5\.1[^\n]{0,200}?式\s*3\.27",
     "式 3.27 与式 5.1 是同一判据（p105 / p143），统一写「式 5.1 ≡ 3.27」，别当两个结论引"),
]

# Baliga 层专项（v2.11.0）—— 只在 Baliga 层生效，不施加到书源一
# 为什么必须单列：Baliga 与《IGBT 模块》是两本独立的书，式号与符号体系完全独立，
# 已发现 3 处**同名不同物**（式 3.27 / 式 3.16·3.28 / 符号 n），
# 以及两条只在跨源时才会犯的错：把 Baliga 的概念挂到《IGBT 模块》出处上（伪造出处）、
# 把本层按单脉冲能量给的 E_OFF 乘上《IGBT 模块》层的 1/π（差 3.14 倍）。
# 施加到书源一上会全量误报 —— 那边本来就在用 1/π，也本来就有「式 3.27」。
BAL_LINE_RULES = [
    # (说明, 触发正则, 例外正则 —— 命中例外则该行豁免)
    # 注意：**裸式号规则不在这里**。为什么：在 Baliga 模块内部，裸写「式 3.27」就是
    # 本书自己的编号，完全无歧义（52/54 就是这么写的，一开始被这条规则全量误报）。
    # 歧义只出现在**同时讲两层的文档**里（报告、SKILL.md、34-formula-index），
    # 而且判据是「式号前面有没有层名」，不是「这一行有没有关键词」——见下面的代码段。
    ("Baliga 专属概念（BFOM / SiC / R_on,sp / 宽禁带）挂到《IGBT 模块》出处上 = 伪造出处",
     r"(?:据《?\s*IGBT\s*模块》?[\s\S]{0,60}(?:BFOM|4H-SiC|R_?on,?\s*sp|宽禁带))|(?:(?:BFOM|4H-SiC|宽禁带)[\s\S]{0,40}据《?\s*IGBT\s*模块》?)",
     r"应为|勘误|伪造|不许|禁止|不得|不要|并列"),
    ("本层 E_OFF 是单脉冲能量，不乘 1/π（混算差 3.14 倍）",
     r"(?:1/π|0\.318)[^\n]{0,40}(?:E_?(?:sw|off|on)|P_?sw|P_?OFF)|(?:E_?(?:sw|off|on)|P_?sw|P_?OFF)[^\n]{0,40}(?:1/π|0\.318)",
     r"不乘|不含|不涉及|不用|不得|口径|区别|并列|无关|另一层|另一个"),
]

# 跨层「裸式号」的歧义判据（v2.11.0）
# 已确认 3 处同名不同物：式 3.27（Baliga 积累电荷 vs 《IGBT 模块》RBSOA）、
# 式 3.16 / 3.28（《IGBT 模块》正弦 VSI 的 1/π 系数，Baliga 本层无此号）、符号 n
# （雪崩倍增指数 ≈6 vs Peck 指数）。规则形态：**式号前 18 个字符内必须出现层名**。
BAL_BARE_EQ = re.compile(r"式\s*3\.(?:27|16|28)(?![\d.])")
BAL_LAYER_NAME = re.compile(r"Baliga|IGBT\s*模块》|volke", re.IGNORECASE)
BAL_EQ_RECORD = re.compile(
    # 豁免情形（都是「已经能判断属于哪一层」的写法，不算歧义）：
    # ① 显式说不是同一式 / 禁止裸写；
    # ② 同一行出现「式 5.1」—— 3.27 ≡ 5.1 的配对只在《IGBT 模块》层成立，读者可据此定向；
    # ③ 行内点名了具体模块文件（`` `38-loss-closed-form.md` ``）—— 模块文件自带层归属；
    # ④ 讲检查器自身的历史文本（Changelog / 自测说明），不是引用行为。
    r"不是同一式|毫无关系|禁止|不许|不要|并列|口径|歧义|跨层|裸写|"
    r"式\s*5\.1|检查器|自测|redline|"
    r"`\d{2}-[a-z0-9\-]+\.md`")


def _hr(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def _tag(kind: str, text: str) -> str:
    return f"[{kind}] {text}"


# ------------------------------------------------------------------- miner
def cmd_miner(a: argparse.Namespace) -> int:
    """式 14.12（书 p383）：n_cyc = (Σ 1/n_i)^(-1)"""
    _hr("Miner 线性累积（式 14.12，书 p383）")
    ns = a.n
    if not ns or len(ns) < 2:
        print("[ERR] --n 至少要给 2 段")
        return 2
    if any(x <= 0 for x in ns):
        print("[ERR] 所有 --n 必须 > 0")
        return 2

    inv = [1.0 / x for x in ns]
    s = sum(inv)
    n_cyc = 1.0 / s

    labels = a.label or [f"段{i+1}" for i in range(len(ns))]
    if len(labels) < len(ns):
        labels += [f"段{i+1}" for i in range(len(labels), len(ns))]

    print(f"{'段':<10}{'n_i':>14}{'1/n_i':>14}{'损伤占比':>12}")
    print("-" * 64)
    for i, (lab, n, iv) in enumerate(zip(labels, ns, inv)):
        share = iv / s * 100
        star = "  <== 主损伤源" if share == max(inv) / s * 100 else ""
        print(f"{lab:<10}{n:>14.4g}{iv:>14.4e}{share:>11.1f}%{star}")
    print("-" * 64)
    print(f"{'合计':<10}{'':>14}{s:>14.4e}{100.0:>11.1f}%")
    print()
    print(_tag("算", f"n_cyc = (Σ1/n_i)^-1 = {n_cyc:.4g} 次 = {n_cyc/1e3:.1f} × 10^3 次"))
    print(_tag("来源", "式 14.12，书 p383"))

    # 主损伤源提示
    worst = labels[inv.index(max(inv))]
    print(_tag("结论", f"损伤占比最大的是「{worst}」（{max(inv)/s*100:.1f} %），"
                        f"寿命优化的靶心在这一段，不在摆幅最大的那一段"))

    if a.dT and len(a.dT) == len(ns):
        print("\n按摆幅重排（看是不是大摆幅在主导）：")
        order = sorted(range(len(ns)), key=lambda i: -a.dT[i])
        for i in order:
            print(f"  ΔT={a.dT[i]:>6.1f} K  n_i={ns[i]:>12.4g}  损伤占比 {inv[i]/s*100:>5.1f}%  ")

    if a.t_cyc:
        t_s = n_cyc * a.t_cyc
        print()
        print(_tag("算", f"t_total = n_cyc × t_cyc = {n_cyc:.4g} × {a.t_cyc:g} s = {t_s:.4g} s"))
        print(_tag("算", f"         = {t_s/3600:.0f} h = {t_s/3600/8760:.2f} 年（按 8760 h/年）"))
        if a.target_years:
            gap = a.target_years / (t_s / 3600 / 8760)
            print(_tag("算", f"目标 {a.target_years:g} 年 → 缺口 {gap:.2f} 倍（周次需同倍数提升）"))
            if gap > 1.5:
                print(_tag("结论", f"缺口 {gap:.2f} 倍，不能靠单一工艺改进凑（书内唯一给了倍数的手段是烧结银 1.82×）"))
    print()
    print(_tag("边界", "n_i 必须来自与被考工况同条件（同 Tc,min、同 t_cyc、同加热方式）的曲线；"))
    print(_tag("边界", "书未给 TC/PC 曲线的解析式（34-formula-index §12），n_i 只能查图/查表或向厂商索取"))
    return 0


# --------------------------------------------------------------------- aqg
AQG_TYPES = {
    "module_si": ("硅基 IGBT 模组（车规）", "AQG 324 04.1/2025", [
        ("TC", "热循环", "RQ", 5, True),
        ("TC", "热循环", "PQ", 5, False),
        ("PCsec", "功率循环", "RQ", 5, True),
        ("PCsec", "功率循环", "PQ", 5, False),
        ("H3TRB", "高温高湿反偏", "RQ", 1, True),
        ("HTRB", "高温反偏", "RQ", 1, True),
        ("HTGB", "高温栅偏", "RQ", 1, True),
        ("TST", "温度冲击", "RQ", 1, True),
        ("Vib", "振动", "RQ", 1, True),
        ("PTC", "被动温度循环", "PQ", 5, False),
    ]),
    "module_sic": ("SiC 模组（车规）", "AQG 324 + SiC 附录", [
        ("TC", "热循环", "RQ", 5, True),
        ("PCsec", "功率循环", "RQ", 5, True),
        ("DGS", "栅极开关稳定性（SiC 专用）", "RQ", 1, True),
        ("DRB", "动态反偏（SiC 专用）", "RQ", 1, True),
        ("dyn.H3TRB", "动态高温高湿反偏", "RQ", 1, True),
        ("H3TRB", "高温高湿反偏", "RQ", 1, True),
        ("HTRB", "高温反偏", "RQ", 1, True),
        ("HTGB", "高温栅偏", "RQ", 1, True),
    ]),
    "module_ind": ("工业/牵引模组", "IEC 60749-34-1:2025 + 客户规范", [
        ("TC", "热循环", "RQ", 3, True),
        ("PCsec", "功率循环", "RQ", 3, True),
        ("HTRB", "高温反偏", "RQ", 1, True),
        ("H3TRB", "高温高湿反偏", "RQ", 1, True),
        ("TST", "温度冲击", "RQ", 1, True),
    ]),
    "discrete_auto": ("车规 IGBT 单管", "AEC-Q101 Rev E", [
        ("TC", "温度循环", "RQ", 3, True),
        ("PC", "功率温度循环", "RQ", 3, True),
        ("H3TRB", "高温高湿反偏", "RQ", 1, True),
        ("HTRB", "高温反偏", "RQ", 1, True),
        ("HTGB", "高温栅偏", "RQ", 1, True),
        ("IOL", "间歇工作寿命", "RQ", 1, True),
    ]),
    "discrete_ind": ("工业 IGBT 单管", "IEC 60747-9:2019", [
        ("TC", "温度循环", "RQ", 3, True),
        ("HTRB", "高温反偏", "RQ", 1, True),
        ("H3TRB", "高温高湿反偏", "RQ", 1, True),
    ]),
}


def cmd_aqg(a: argparse.Namespace) -> int:
    """AQG 324 试验台账骨架 —— 只算统计，条件留空"""
    _hr("AQG 324 / AEC-Q101 试验台账骨架（条件留空，不代填）")
    if a.list:
        print(f"{'type':<16}{'说明':<28}标准")
        print("-" * 64)
        for k, (desc, std, _) in AQG_TYPES.items():
            print(f"{k:<16}{desc:<28}{std}")
        print()
        print(_tag("纪律", "本表只列试验**项**与分组，不列条件/样本量/判据"))
        print(_tag("纪律", "条件必须回标准正文或客户规范填写 —— 这是本技能的一贯立场"))
        return 0

    t = a.type or "module_si"
    if t not in AQG_TYPES:
        print(f"[ERR] 未知 type: {t}")
        return 2
    desc, std, rows = AQG_TYPES[t]
    print(_tag("产品", f"{desc}"))
    print(_tag("标准", f"{std}"))
    print(_tag("样本量", f"用户给定 {a.n_sample}（本脚本不提供默认值；AQG 324 的 RQ 常为 3~5，PQ 常为 5）")
          if a.n_sample else _tag("样本量", "未给定 —— 台账无法统计，请加 --n-sample"))
    print()
    hdr = f"{'#':<3}{'试验':<12}{'说明':<30}{'组':<4}{'样本':>6}"
    print(hdr)
    print("-" * 64)
    for i, (code, title, grp, nmin, req) in enumerate(rows, 1):
        n = a.n_sample if a.n_sample else nmin
        flag = "" if req else "  (PQ)"
        print(f"{i:<3}{code:<12}{title:<30}{grp:<4}{n:>6}{flag}")
    print("-" * 64)
    print(_tag("提醒", "RQ = 认证必需的试验组；PQ = 产品鉴定/周期性质量验证组"))
    print(_tag("提醒", "SiC 必须加 DGS / DRB / dyn.H3TRB —— 硅基的科目表不能直接套 SiC"))
    print(_tag("边界", "本台账**不含**具体条件（温度/电压/循环数/判据）。"))

    if a.format == "csv":
        out = Path(a.o or "aqg_ledger.csv")
        lines = ["no,test,title,group,samples,condition,criteria,owner,status,evidence"]
        for i, (code, title, grp, nmin, req) in enumerate(rows, 1):
            n = a.n_sample if a.n_sample else nmin
            lines.append(f"{i},{code},{title},{grp},{n},,,未开始,")
        # UTF-8 BOM：Excel 直接双击可读中文
        out.write_text("\ufeff" + "\n".join(lines) + "\n", encoding="utf-8")
        print(_tag("输出", f"已写 {out}（UTF-8 BOM，Excel 可直接打开；condition/criteria 留空待填）"))
        if not a.n_sample:
            print(_tag("警告", "未给 --n-sample，CSV 里的 samples 列填的是**最小样本量提示值**，"
                               "不是标准规定；正式台账必须回标准正文确认"))
    return 0


# --------------------------------------------------------------------- rth
def cmd_rth(a: argparse.Namespace) -> int:
    """热阻链：区分"自上而下"(从 Tc 加) 与"自下而上"(从 Tcoolant 加) 两种口径"""
    _hr("热阻链加总与反解（两种口径，别混）")

    segs = []
    if a.rjc is not None:
        segs.append(("R_jc（芯片→基板，datasheet）", a.rjc))
    if a.rbase is not None:
        segs.append(("R_base（基板本体）", a.rbase))
    if a.rtim is not None:
        segs.append(("R_tim（界面）", a.rtim))
    if a.rhs is not None:
        segs.append(("R_hs（散热器→冷却液）", a.rhs))
    for extra in (a.seg or []):
        if "=" in extra:
            k, v = extra.split("=", 1)
            segs.append((k.strip(), float(v)))
    if not segs:
        print("[ERR] 至少给一个 --rjc / --rbase / --rtim / --rhs / --seg")
        return 2

    total = sum(r for _, r in segs)
    print(f"{'段':<34}{'Rth K/W':>12}{'占比':>10}{'温降 K':>12}")
    print("-" * 64)
    for name, r in segs:
        dt = a.ploss * r
        print(f"{name:<34}{r:>12.4f}{r/total*100:>9.1f}%{dt:>12.1f}")
    print("-" * 64)
    print(f"{'合计':<34}{total:>12.4f}{100.0:>9.1f}%{a.ploss*total:>12.1f}")

    print()
    print(_tag("口径甲（自上而下，合法）", f"T_j = T_c + P × R_jc = {a.tc:g} + {a.ploss:g} × {a.rjc:g} "
          f"= {a.tc + a.ploss*a.rjc:.1f} ℃" if a.rjc else "T_j = T_c + P × R_jc（未给 --rjc）"))
    print(_tag("口径乙（自下而上，只在给全链时合法）",
               f"T_j = T_coolant + P × ΣR = {a.tcoolant:g} + {a.ploss:g} × {total:.4f} "
               f"= {a.tcoolant + a.ploss*total:.1f} ℃" if a.tcoolant is not None else
               "（未给 --tcoolant，跳过）"))
    print()

    if a.rjc and a.tc:
        tj = a.tc + a.ploss * a.rjc
        margin = a.tmax - tj
        print(_tag("判决", f"T_j = {tj:.1f} ℃ vs T_jmax = {a.tmax:g} ℃ → 裕量 {margin:+.1f} K "
                           f"[{'PASS' if margin >= 0 else 'FAIL'}]"))
        p_allow = (a.tmax - a.tc) / a.rjc
        print(_tag("反解", f"P_allow = (T_jmax − T_c)/R_jc = {p_allow:.0f} W；"
                           f"当前 {a.ploss:g} W，占 {a.ploss/p_allow*100:.0f} %"))

    worst = max(segs, key=lambda x: x[1])
    print(_tag("瓶颈", f"{worst[0]} 占 {worst[1]/total*100:.1f} % —— 改进必须先动这一段"))
    if a.rtim is not None and a.rjc is not None and a.rtim < 0.1 * a.rjc:
        gain = a.ploss * a.rtim * 0.5
        print(_tag("提示", f"R_tim 只有 R_jc 的 {a.rtim/a.rjc*100:.1f} %：即使 TIM 热阻减半，"
                           f"也只买回 {gain:.1f} K —— **换 TIM 救不了这个设计**"))

    print()
    print(_tag("纪律", "两口径**不能混**：用 T_c 算出 T_j 后，不能再拿 T_j 去和 T_coolant + ΣR 的结果对比"))
    print(_tag("纪律", "R_th(j-c) 按书 p143 只是参考值；R_th,ch 随 TIM 规格/厚度/压力变"))
    print(_tag("书未给", "R_th(j-c) 的行业典型值（34-formula-index §12）：必须查具体 datasheet"))
    return 0 if (not a.rjc or not a.tc or a.tmax - (a.tc + a.ploss*a.rjc) >= 0) else 1


# --------------------------------------------------------------------- cte
def cmd_cte(a: argparse.Namespace) -> int:
    """CTE 失配 —— 强制声明口径"""
    _hr("CTE 失配矩阵（强制声明取值口径）")

    def resolve(x: str):
        # 允许直接给数
        try:
            return float(x), "L4", "用户输入（非书内数据，须标 L4）"
        except ValueError:
            pass
        name = x.strip()
        for setname, table in CTE_SETS.items():
            if setname != a.source:
                continue
            for k, (v, lv, src) in table.items():
                if k.lower() == name.lower() or name.lower() in k.lower():
                    return v, lv, src
        return None, None, None

    va, la, sa = resolve(a.a)
    vb, lb, sb = resolve(a.b)
    if va is None or vb is None:
        miss = a.a if va is None else a.b
        print(f"[ERR] 材料「{miss}」不在口径 {a.source} 中。可选："
              f"{', '.join(CTE_SETS[a.source].keys())}，或直接给数值")
        return 2

    print(_tag("口径", f"--source {a.source}"))
    print(_tag("A", f"{a.name_a or a.a} = {va:g} ppm/K  [{la}] {sa}"))
    print(_tag("B", f"{a.name_b or a.b} = {vb:g} ppm/K  [{lb}] {sb}"))
    da = abs(va - vb)
    print()
    print(_tag("算", f"Δα = |{va:g} − {vb:g}| = {da:g} ppm/K"))
    if va > 0:
        print(_tag("算", f"相对比 = Δα / α_A = {da/va*100:.0f} %（以 {a.name_a or a.a} 为基准）"))

    # 跨口径告警
    print()
    for nm, vals in CTE_RANGES.items():
        if nm.lower() in (a.a.lower(), a.b.lower(), (a.name_a or "").lower(), (a.name_b or "").lower()):
            print(_tag("警告", f"「{nm}」在书内有 {len(vals)} 个口径：{vals} "
                               f"（差 {(max(vals)-min(vals))/min(vals)*100:.0f} %）"))
    print(_tag("纪律", "定量计算只能用 table42（唯一明标 20 ℃ 的口径）；"
                       "跨 ΔT > 100 K 时三套都不可直接用，须取 α_m(T1→T2)"))

    if a.compare_to:
        vc, lc, sc = resolve(a.compare_to)
        if vc is not None:
            d2 = abs(vb - vc)
            print()
            print(_tag("对比", f"{a.name_b or a.b}({vb:g}) ↔ {a.compare_to}({vc:g}) → Δα = {d2:g} ppm/K"))
            if d2 > 0:
                print(_tag("对比", f"失配降低 {da/d2:.2f} 倍（{da:g} → {d2:g}）"))
                print(_tag("寿命", f"按 C-M n ∝ Δα^-c，c=2~5 → 寿命提升 "
                                   f"{(da/d2)**2:.0f} ~ {(da/d2)**5:.0f} 倍（**c 书未给，仅灵敏度区间**）"))
    print()
    print(_tag("书未给", "Coffin-Manson 指数 c / Bayerer β1~β4：厂商标定，禁止跨型号套用"))
    return 0


# -------------------------------------------------------------------- unit
def cmd_unit(a: argparse.Namespace) -> int:
    """书内单位陷阱换算（34-formula-index.md §13）"""
    _hr("单位陷阱换算（书内 §13 八条）")
    n = 0
    if a.ohm_mm2_m is not None:
        v = a.ohm_mm2_m
        print(_tag("算", f"{v:g} Ω·mm²/m = {v*100:.4g} μΩ·cm"))
        print(_tag("陷阱", "书 p55 脚注用 Ω·mm²/m（Al 0.0264 / Cu 0.0178），"
                           "表 14.6 用 μΩ·cm（1.7 / 2.7）—— 两套单位差 100 倍，混用会把电阻放大/缩小 100 倍"))
        n += 1
    if a.ppm_per_k is not None:
        v = a.ppm_per_k
        print(_tag("算", f"α = {v:g} ppm/K = {v*1e-6:g} 1/K = {v*1e-6*100:g} %/K"))
        print(_tag("陷阱", "ppm/K 与 10⁻⁶/K 同值；写成 ×10⁻⁶×10⁻⁶ 会把 CTE 算小 10⁶ 倍"))
        if a.dT is not None:
            print(_tag("算", f"ΔT = {a.dT:g} K 时 ΔL/L = {v*1e-6*a.dT*100:.4f} %"))
        n += 1
    if a.lambda_w_mk is not None:
        v = a.lambda_w_mk
        print(_tag("算", f"λ = {v:g} W/(m·K) = {v/100:g} W/(cm·K) = {v*100:g} mW/(cm·K)"))
        print(_tag("陷阱", "W/(m·K) 与 W/(mm·K) 差 1000 倍；datasheet 里有厂商用 W/(m·K)，仿真软件偶尔用 mW/(mm·K)"))
        n += 1
    if a.mohm is not None:
        v = a.mohm
        print(_tag("算", f"{v:g} mΩ = {v*1e-3:g} Ω"))
        print(_tag("陷阱", "V_CE0/r_CE 拟合时 r 常以 mΩ 给出，脚本 --rce 要的是 Ohm（3.2 mΩ → 0.0032）"))
        n += 1
    if a.us is not None:
        v = a.us
        print(_tag("算", f"{v:g} μs = {v*1e-6:g} s = {v*1e3:g} ns"))
        print(_tag("陷阱", "书内时间量级跨 6 个数量级（ns 级开关、μs 级保护、h 级试验）；"
                           "脚本参数全部是 SI 秒，μs 必须 ×1e-6"))
        n += 1
    if n == 0:
        print("至少给一个参数，例如 --ohm-mm2-m 0.0264 / --ppm-per-k 17 / --lambda-w-mk 380 / --mohm 3.2 / --us 4.4")
        print()
        print("书内 §13 的八条陷阱全表见 references/volke-hornkamp/34-formula-index.md")
        return 0
    return 0


# ----------------------------------------------------------------- redline
def cmd_redline(a: argparse.Namespace) -> int:
    """书未给红线自检：扫报告文本，看有没有把"书未给"当"书内数据\""""
    _hr("书未给红线自检（扫文本）")
    if not a.file:
        print("[ERR] 需要 --file 指定要检查的文本/markdown 文件")
        return 2
    p = Path(a.file)
    if not p.exists():
        print(f"[ERR] 文件不存在: {p}")
        return 2
    text = p.read_text(encoding="utf-8", errors="ignore")

    # ── 厂商层识别（v2.8.0）──
    # 为什么要分来源：「式 7.5 必须抄全两项」这条规则的**约束对象是书源层的转写**——
    # 它防的是"把书里的式子抄漏一项"。厂商层（references/infineon/）里的死区讨论
    # 用的是英飞凌自己的口径（只取关断延迟与开通延迟之差 + 冗余），本来就**不该**
    # 出现驱动传输延迟差项；若对它施加书源规则，会逼作者在每次提到 t_DT 时
    # 都补一句"这不是式 7.5"，文字被噪声污染。→ 该规则对厂商层降级。
    # 但**与来源无关的物理错误**（死区用了 t_r 而非 t_f）仍然照常检查。
    # 识别方式二选一：路径含 references/infineon/，或正文声明「层归属：厂商层」。
    is_vendor = ("/infineon/" in p.as_posix().replace("\\", "/")
                 or "层归属：厂商层" in text
                 or "层归属: 厂商层" in text)

    # ── 豁免判据（v2.7.0 上移）──
    # 这两个判据被「书未给」和「书内不一致」两段共用，必须定义在**两段之前**。
    # 曾经它们被写在不一致段落里，而书未给段落先用了 _is_record ——
    # 26/30/39 三个模块每次跑到这里就 UnboundLocalError，rc=1 被当成『检出违规』，
    # 实际是**从来没检查过**。这是本项目最隐蔽的一类缺陷：崩溃看起来像检查结果。
    _ERRATA_MARK = re.compile(
        r"应为|勘误|订正|errata|书印|原印|印成|印错|错印|排印|印刷|"
        r"存疑|可疑|不一致|自相矛盾|口径不同|口径差异|未说明|未给|不用|不得|不要|禁止|勿|"
        # 「校核」在正文里多是"我做了一遍校核"，属**使用**；只有"交叉/互相校核"、
        # "校核发现"才算**记录**。单独收进来会把正常引用判成勘误（22/29 就是这么被吞的）。
        r"交叉校核|互相校核|相互校核|校核发现|复核|回原书|"
        r"量纲不成立|不成立|发散|救不回|物理不可能|不要用|改用|"
        r"差千倍|差百倍|差\d+\s*倍|并存|疑为|疑排版|按.{0,4}算|取自|以.{0,6}为准|"
        r"确认|结案|非存疑|v2\.\d\.\d|正文|代入式|原文|不一致|口径|"
        r"21494|9097|350\s*FIT|250\s*FIT|±\s*100\s*nA|L_?C|t_stg|t_chg|"
        r"假设|假定|—\s*假设|——\s*假设|设为|设于",
        re.IGNORECASE)

    def _is_own_finding(cur: str, tag: str) -> bool:
        """这一行是不是『本检查表登记的那个问题』本身。

        为什么需要这一条：INCONSISTENCIES 里每条勘误的**描述文字**都必然包含触发它的
        关键词（例：p173 那条描述自己就写着 417/278），于是任何一份把该勘误转述出来的
        笔记，都会在『不一致』检查里被判违规。这不是笔记的错，是检查表自我命中的设计缺陷。
        判据：这一行同时出现了 (a) 该 tag 的纠正侧数值/符号，或 (b) 明确的问题词，
        就认为它在**报告**这个问题，不再计违规。
        """
        # (a) 每条勘误的『正解侧』特征串：出现它说明作者已经知道正确值
        _RIGHT_SIDE = {
            "p173": r"417",
            "p365": r"250\s*FIT",
            "H3TRB": r"100\s*μA|100\s*uA",
            "p61": r"10\^?8\s*V/m|10⁸\s*V/m|10\s*MV/cm",
            "表 14.4": r"t_?st?g|存储",
            "式 1-3": r"14\.95|10\^?14|10¹⁴",
            "p370": r"9097",
        }.get(tag)
        if _RIGHT_SIDE and re.search(_RIGHT_SIDE, cur):
            return True
        # (b) 明确的问题陈述词（不含"应为/勘误"这种只在格式上出现的词，避免过度放水）
        if re.search(r"怎么算|对不上|算不|差\s*\d+\s*倍|矛盾|打架|打架|为什么.*不对|"
                     r"存疑|可疑|待核|待确认|挂起|开放问题", cur):
            return True
        return False

    def _is_record(cur: str) -> bool:
        """这一行是在『记录/引用』这本书的错，还是在『使用』它。
        v2.7.0 三条判据（次序即优先级）：
          1. 命中勘误标记词 → 记录型
          2. 是 Markdown 表格行（以 | 开头）→ 对照表/登记表，记录型
          3. 行内有加粗的『不成立 / 错 / 发散』→ 强调这是错的，记录型
        """
        s = cur.strip()
        # 剥掉 Markdown 引用块前缀「> 」。不剥的话，模块里凡是用 > 引用原文的表格，
        # 都会被判成"非表格行"，绕开下面的表格豁免 —— 22 模块 L90/L97 就是这么漏的。
        while s.startswith(">"):
            s = s[1:].lstrip()
        if s.startswith("|"):
            return True
        if _ERRATA_MARK.search(cur):
            return True
        if re.search(r"\*\*[^*]{0,14}(不成立|错|发散|不可用|不能用)[^*]{0,8}\*\*", cur):
            return True
        # 4. 表格**续行**：以 | 开头但单元格数明显少于表头（本例 4 格 vs 6 格），
        #    内容常是「✅ 同上 / 见上 / 待核」。它属于上一行的判定延续，本身不承载新断言。
        if s.startswith("|") and s.count("|") <= 5:
            return True
        # 5. 中性陈述"书把这几式给在哪一页"：只报出处不报数值结论，不是在使用它。
        #    例：「书同时给了 HDF 的解析式（式 13.21–13.24，p359）与图 13.20 的曲线族」
        if re.search(r"(书|原文)(同时)?(给|列|印)了", s):
            # 先把「式 13.21–13.24」「图 13.20」「p359」这类**编号**整段剔除，
            # 否则 "图 13.20 的曲线族" 里那个 13.20 会被当成"给出小数结果"。
            _t = re.sub(r"(式|图|表|页|章节|p)\s*[0-9一二三四五六七八九十][0-9.\-–—]*", "", s)
            if not re.search(r"[=＝]\s*-?\d|\d+\.\d+\s*/|❌|✅|不成立|发散|应为", _t):
                return True
        return False

    # 登记表自检问题（v2.6.0）：34-formula-index 与 material-database 本身就是**红线清单**，
    # 必然逐条出现"书未给 / 式 13.9 错式"的原样文本。若无条件判违规，这两个文件永远不通过，
    # 检查结果就退化成噪声，人会开始忽略它 —— 那比没有检查更糟。
    #
    # v2.11.1 补入 scripts/README.md：这份文件是**工具说明书**，为了让读者看懂判据，
    # 它必须原样列出"✅ 命中"的反例（如 `按 Coffin-Manson，c=3 取自《IGBT 模块》p383`）。
    # 这些不是误用，是**示例**；与登记表同性质，一并按登记内容处理。
    REGISTRY_FILES = {"34-formula-index.md", "material-database.md", "00-index.md",
                      "SKILL.md", "README.md"}
    is_registry = p.name in REGISTRY_FILES

    hits = 0
    errors = []          # 规则自身错误（正则编译失败等），与 hits 严格分开
    print(_tag("扫描", str(p)))
    if is_registry:
        print(_tag("模式", "红线登记表本身（命中为「登记」而非「违规」）" + ("；已加 --strict" if a.strict else "；要按违规判请加 --strict")))
    print()
    print("── 书未给（§12 红线）──")
    found_any = False
    _muted_rule = 0
    for pat, msg in REDLINE_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            line = text[:m.start()].count("\n") + 1
            ls = text.rfind("\n", 0, m.start()) + 1
            le = text.find("\n", m.end())
            cur = text[ls: (le if le != -1 else len(text))]
            # 记录型豁免（v2.7.0）：同一行里写明"书印 / 量纲不成立 / 不要用 / 改为 …"的，
            # 是在**登记这条错**，不是**在用这条错**。判为记录，不计 hits。
            if _is_record(cur):
                _muted_rule += 1
                print(f"  L{line:<6} [记录] {msg}　← {cur.strip()[:70]}")
                continue
            hits += 1
            found_any = True
            print(f"  L{line:<6} {msg}")
            print(f"         命中：…{m.group(0)[:60]}…")
    if _muted_rule:
        print(f"  （另有 {_muted_rule} 处属『登记/引用』，不计违规）")
    if not found_any:
        print("  （无命中）")

    print()
    print("── 书内不一致（引用必须标口径）──")
    found_any = False
    # 已登记勘误的行不算违规：这类行同时写了「书印 X，应为 Y」，
    # 是在**记录**书的错，不是在**传播**书的错。不区分的话，
    # 越是把勘误写清楚的模块越会被自己的红线检查判死，检查就失去信号。
    # v2.7.0 扩词：实际扫描发现「记录型」行的措辞远不止"应为/勘误"。
    # 一本技术笔记里说"书印 X"「差千倍」「口径不同」「存疑」全都是**在指出问题**，
    # 不是**在传播问题**。不认这些词，检查器就会惩罚最认真的那几个模块。
    muted = 0
    _seen = set()
    for tag, pat, msg in INCONSISTENCIES:
        # 单条正则写错（如变宽 lookbehind）不能拖垮整场检查：
        # 否则崩溃的 rc=1 会和"命中违规"的 rc=1 混在一起，人以为查过了。
        try:
            re.compile(pat)
        except re.error as e:
            print(f"  [ERR] 规则「{tag}」正则无法编译：{e}")
            print(f"        该规则本次被跳过 —— 这不是『无违规』，请修规则")
            errors.append(f"{tag}: {e}")
            continue
        for m in re.finditer(pat, text):
            ls = text.rfind("\n", 0, m.start()) + 1
            le = text.find("\n", m.end())
            cur_line = text[ls: (le if le != -1 else len(text))]
            line = text[:m.start()].count("\n") + 1
            # 同一行同一 tag 只报一次：式 13.21–13.24 这类区间写法会被正则命中多次，
            # 重复输出会把真问题淹掉
            if (line, tag) in _seen:
                continue
            _seen.add((line, tag))
            # 反向判据：1/π 这条不是"出现了就错"，而是"该出现却没出现"。
            # 行里只要写了 1/π、0.318、pi/π、--sw-factor，就是已经折算了，放行。
            # ── 方向类规则前置判定（v2.7.0 结构性修正）──
            # 这两条规则的关键词（π / 校核 / 式号）在正常技术行文里到处都是，
            # 一旦交给下面的通用记录型豁免，必然被一律放行 —— 规则等于不存在。
            # 所以必须在这里**只看语义**，不看格式。
            if tag == "1/π 折算":
                # 单次能量（E_off / E_on / E_rec / E_rr）本身**不含** 1/π ——
                # 1/π 只作用在「正弦平均功率」那一层。把 E_off·f_sw 当漏折算去判，
                # 会把所有正确的单次能量核算判死（32 模块 L106 就是这么被误报的）。
                if re.search(r"\bE_?(off|on|rec|rr)\b", cur_line) and not re.search(
                        r"P_?(sw|on|off|rec)\s*[=＝]", cur_line):
                    muted += 1
                    print(f"  L{line:<6} [{tag}] 单次能量核算（本层不乘 1/π），不计违规")
                    continue
                _neg = re.search(r"(未|没|不|无|漏|缺|少|忘|忽略)[^。；;]{0,8}(折算|1\s*/\s*[πp])", cur_line)
                _has = re.search(r"1\s*/\s*π|1/pi|0\.318|0\.32|sw-factor|已折算|折算过|乘了", cur_line)
                if _has and not _neg:
                    muted += 1
                    print(f"  L{line:<6} [{tag}] 已含折算因子，不计违规")
                    continue
                # 其余情况（含"未做折算"）一律判违规：漏了 1/π 就是 3.14 倍错
                hits += 1
                found_any = True
                print(f"  L{line:<6} [{tag}] {msg}")
                continue
            if tag == "3.27≡5.1":
                # 只有在明确写"同一判据/等效/≡"时才算已经识别，否则判违规
                if re.search(r"≡|等同|同一判据|同一条|同一式|两次印刷", cur_line):
                    muted += 1
                    print(f"  L{line:<6} [{tag}] 已显式标为同一判据，不计违规")
                    continue
                hits += 1
                found_any = True
                print(f"  L{line:<6} [{tag}] {msg}")
                continue
            if _is_record(cur_line) or _is_own_finding(cur_line, tag):
                muted += 1
                _why = "记录型" if _is_record(cur_line) else "本表登记的问题本身"
                print(f"  L{line:<6} [{tag}] {_why}，不计违规"
                      f"　← {cur_line.strip()[:70]}")
                continue
            hits += 1
            found_any = True
            print(f"  L{line:<6} [{tag}] {msg}")
    if not found_any:
        print("  （无违规命中%s）" % (f"；另有 {muted} 处已标勘误" if muted else ""))

    print()
    if is_vendor:
        print("── 结构性缺项（「多项相加」的预算式必须抄全）──")
        print("  （厂商层：式 7.5「两项相加」规则不适用 —— 该规则约束的是书源层转写；"
              "厂商层用英飞凌口径，本就不含驱动传输延迟差项）")
        _vendor_skip_751 = True
    else:
        _vendor_skip_751 = False
        print("── 结构性缺项（「多项相加」的预算式必须抄全）──")
    found_any = False
    # 为什么单独做这一类：漏项不是"写错了一个数"，正则抓不到错值，只能抓形态。
    # 式 7.5（死区）在书内算例里两项各占一半，漏一项结果仍落在 1~4 us 的"合理区间"，
    # 不会报错，只会让上下管多重叠约 0.4 us。
    _lines = text.split("\n")
    for _i, _ln in enumerate(_lines):
        if not re.search(r"t_?DT", _ln):
            continue
        # 公式常跨多行书写：用括号配平界定公式块，避免把后面「另一条公式」也算进来
        seg = _ln
        _depth = _ln.count("[") + _ln.count("(") - _ln.count("]") - _ln.count(")")
        _k = _i
        while _depth > 0 and _k + 1 < len(_lines) and (_k - _i) < 3:
            _k += 1
            _nx = _lines[_k]
            seg += "\n" + _nx
            _depth += _nx.count("[") + _nx.count("(") - _nx.count("]") - _nx.count(")")
        line = _i + 1
        has_igbt_term = ("t_d(off)" in seg) or ("td_off" in seg) or ("t_doff" in seg)
        has_drv_term = bool(re.search(r"pHL|pLH|驱动.{0,8}(延迟|延时|传输)", seg, re.IGNORECASE))
        if has_igbt_term and not has_drv_term and not _vendor_skip_751:
            hits += 1
            found_any = True
            print(f"  L{line:<6} 死区式（式 7.5）只出现 IGBT 项，未见**驱动传输延迟差项**")
            print(f"         命中：…{seg.replace(chr(10), ' ')[:70]}…")
            print("         书 p228 图 7.7：该项占 50 %；漏掉则 1.200 -> 0.600 us")
        if re.search(r"t_r\s*,?\s*max", seg):
            hits += 1
            found_any = True
            print(f"  L{line:<6} 死区式（式 7.5）用了**上升时间 t_r** —— 应为关断下降时间 t_f")
            print(f"         命中：…{seg.replace(chr(10), ' ')[:70]}…")
    if not found_any:
        print("  （无命中）")

    # ── Baliga 层专项（v2.11.0）──
    # 识别方式二选一：路径含 references/baliga/，或正文声明「层归属…Baliga」。
    # 只在 Baliga 层启用：这些规则的前提是「本层不乘 1/π、式号与《IGBT 模块》无关」，
    # 施加到书源一会全量误报。
    is_baliga = ("/baliga/" in p.as_posix().replace("\\", "/")
                 or re.search(r"层归属[^\n]{0,24}Baliga", text) is not None)
    if is_baliga:
        print()
        print("── Baliga 层专项（跨层式号 / 跨书出处 / 1/π 口径）──")
        _bal = 0
        for _i, _ln in enumerate(text.split("\n"), 1):
            for _msg, _pat, _exc in BAL_LINE_RULES:
                if not re.search(_pat, _ln):
                    continue
                if _exc and re.search(_exc, _ln):
                    continue
                _bal += 1
                print(f"  L{_i:<6} {_msg}")
                print(f"         命中：…{_ln.strip()[:70]}…")
        if not _bal:
            print("  （无命中）")
        hits += _bal

    # ── 跨层裸式号（v2.11.0）──
    # 只在**同时讲两层**的文档里查：这类文档（报告 / SKILL.md / 34-formula-index）
    # 一旦裸写「式 3.27」，读者无法判断是 Baliga 的积累电荷还是《IGBT 模块》的 RBSOA。
    # Baliga 模块内部裸写属正常（那是本书自己的编号），因此 skip。
    if (not is_baliga) and re.search(r"Baliga", text, re.IGNORECASE):
        print()
        print("── 跨层裸式号（式 3.27 / 3.16 / 3.28 必须带层名）──")
        _bare = 0
        _tl = text.split("\n")
        for _i, _ln in enumerate(_tl, 1):
            if BAL_EQ_RECORD.search(_ln):
                continue
            for _m in BAL_BARE_EQ.finditer(_ln):
                _pre = _ln[max(0, _m.start() - 18): _m.start()]
                if BAL_LAYER_NAME.search(_pre):
                    continue
                _bare += 1
                print(f"  L{_i:<6} 裸写「{_m.group(0)}」—— 未在式号前标层名")
                print(f"         命中：…{_ln.strip()[:70]}…")
                print("         两书同名不同物：Baliga 式 3.27 = 积累电荷；《IGBT 模块》式 3.27 = RBSOA")
        if not _bare:
            print("  （无命中）")
        hits += _bare

    print()
    if hits and is_registry and not a.strict:
        print(_tag("判决", f"登记表命中 {hits} 处 —— 属**登记内容**，非违规。"
                            "检查对象应是你的报告/算例，不是这张表本身"))
        return 0
    if errors:
        # 规则坏了和有违规是两件事，返回码必须分开：
        # rc=1 表示"查出来问题"，rc=3 表示"没查全"。混用会让人以为查过了。
        print(_tag("判决", f"{len(errors)} 条规则无法编译，本次**未查全**："
                            + "；".join(errors)))
        return 3
    if hits:
        print(_tag("判决", f"命中 {hits} 处 —— **不得直接对外发布**，逐条改为「书未给 / 需厂商数据 / 已标口径」"))
        return 1
    print(_tag("判决", "未命中红线。注意：本检查基于正则，**不能替代人工审阅**"))
    return 0


# -------------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="书源数据的台账 / 计算器五项（带区间、带出处、带红线自检）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--json", action="store_true", help="以 JSON 输出")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("miner", help="Miner 线性累积（式 14.12）")
    m.add_argument("--n", type=float, action="append", required=True, help="各段允许周次 n_i，可重复")
    m.add_argument("--dT", type=float, action="append", help="各段摆幅 K（可选，用于重排提示）")
    m.add_argument("--label", action="append", help="各段标签，可重复")
    m.add_argument("--t-cyc", type=float, default=None, help="单个周期时长 s")
    m.add_argument("--target-years", type=float, default=None, help="目标寿命年数")
    m.set_defaults(func=cmd_miner)

    q = sub.add_parser("aqg", help="AQG 324 / AEC-Q101 试验台账骨架")
    q.add_argument("--list", action="store_true", help="列出所有产品类型")
    q.add_argument("--type", default=None, help="产品类型，见 --list")
    q.add_argument("--n-sample", type=int, default=None, help="每组样本量（不给则留空）")
    q.add_argument("--format", choices=["table", "csv"], default="table")
    q.add_argument("-o", default=None, help="CSV 输出路径")
    q.set_defaults(func=cmd_aqg)

    r = sub.add_parser("rth", help="热阻链加总与反解（两种口径）")
    r.add_argument("--rjc", type=float, default=None, help="R_th(j-c) K/W")
    r.add_argument("--rbase", type=float, default=None, help="基板本体 Rth K/W")
    r.add_argument("--rtim", type=float, default=None, help="TIM 界面 Rth K/W")
    r.add_argument("--rhs", type=float, default=None, help="散热器→冷却液 Rth K/W")
    r.add_argument("--seg", action="append", help="自定义段 name=value，可重复")
    r.add_argument("--ploss", type=float, required=True, help="损耗 W")
    r.add_argument("--tc", type=float, default=None, help="底板温度 ℃")
    r.add_argument("--tcoolant", type=float, default=None, help="冷却液温度 ℃")
    r.add_argument("--tmax", type=float, default=175.0, help="T_jmax ℃，默认 175")
    r.set_defaults(func=cmd_rth)

    c = sub.add_parser("cte", help="CTE 失配（强制声明口径）")
    c.add_argument("--a", required=True, help="材料 A（名或数值）")
    c.add_argument("--b", required=True, help="材料 B（名或数值）")
    c.add_argument("--source", choices=list(CTE_SETS.keys()), required=True,
                   help="取值口径：p50 / table42 / fig147（table42 是唯一明标 20 ℃ 的）")
    c.add_argument("--name-a", default=None)
    c.add_argument("--name-b", default=None)
    c.add_argument("--compare-to", default=None, help="替代材料（算失配降低倍数）")
    c.set_defaults(func=cmd_cte)

    u = sub.add_parser("unit", help="单位陷阱换算")
    u.add_argument("--ohm-mm2-m", type=float, default=None)
    u.add_argument("--ppm-per-k", type=float, default=None)
    u.add_argument("--dT", type=float, default=None)
    u.add_argument("--lambda-w-mk", type=float, default=None)
    u.add_argument("--mohm", type=float, default=None)
    u.add_argument("--us", type=float, default=None)
    u.set_defaults(func=cmd_unit)

    d = sub.add_parser("redline", help="书未给红线自检（扫报告文本）")
    d.add_argument("--file", required=True, help="要检查的 md/txt 文件")
    d.add_argument("--strict", action="store_true",
                   help="即使扫的是红线登记表本身（34-formula-index / material-database）也按违规判定")
    d.set_defaults(func=cmd_redline)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.json:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = args.func(args)
        print(json.dumps({"cmd": args.cmd, "returncode": rc, "output": buf.getvalue()},
                         ensure_ascii=False))
        return rc
    rc = args.func(args)
    print("\n" + "-" * 64)
    print("数据来源：Volke & Hornkamp《IGBT 模块：技术、驱动和应用》中文版")
    print("口径与红线：references/material-database.md / 34-formula-index.md §12–§13")
    return rc


if __name__ == "__main__":
    sys.exit(main())

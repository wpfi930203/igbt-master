#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""igbt_book_budget.py -- 书源判据的可执行版（零第三方依赖）

只实现《IGBT 模块：技术、驱动和应用》(Volke & Hornkamp, 中文版) 里
**给出了完整式子**的项。书没给式子的（如 E_as、驱动功率公式）本脚本一概不提供 —— 那属于"编"。
书**给了但式子本身错**的（缓冲电容式 13.9 量纲不成立），本脚本给的是**修正后的能量式**并并列显示书印值。

子命令
  desat      DESAT 消隐时间预算（式 6.17 / 6.19，p189-190）
  sc         短路能量上界与保护动作余量（式 7.6 / 7.7 的定性依赖）
  terminal   端子电压 vs 芯片耐压（式 5.1，p142）
  derate     并联降额与静态均流（式 8.1，p248-249）
  deadtime   死区时间（式 7.5，p229）
  snubber    吸收电容（式 13.9 量纲不成立 → 用能量式；书 p346-348）

示例
  python igbt_book_budget.py desat --cbl 100e-12 --uref 10 --idesat 250e-6 --tsc 10e-6
  python igbt_book_budget.py sc --udc 1100 --isc 4800 --tsc 10e-6 --tdetect 4.4e-6
  python igbt_book_budget.py terminal --uces 1700 --lsig 20e-9 --didt 5e9
  python igbt_book_budget.py derate --n 2 --i-nom 1000 --i-tot 1756
  python igbt_book_budget.py deadtime --td-off-max 0.62e-6 --tf-max 0.18e-6 --td-on-min 0.27e-6
                                    --tphl-max 0.50e-6 --tplh-min 0.10e-6 --safety 1.5
  python igbt_book_budget.py deadtime --book-example 25   # 复现书 p228 图 7.7 的 1.20 us
  python igbt_book_budget.py snubber --lsig 50e-9 --i-peak 1000 --uce-peak 1700 --udc 1100

返回码：0 = 通过；1 = 不通过（便于串联到 CI / 评审脚本）
"""

from __future__ import annotations

import argparse
import math
import sys


def _hr(title: str) -> None:
    print("\n" + "=" * 62)
    print(title)
    print("=" * 62)


def _verdict(ok: bool, msg_ok: str, msg_bad: str) -> int:
    if ok:
        print("\n[PASS] " + msg_ok)
        return 0
    print("\n[FAIL] " + msg_bad)
    return 1


# ---------------------------------------------------------------- desat
def cmd_desat(a: argparse.Namespace) -> int:
    """式 6.17：t_bl = C_bl * U_ref / I_DESAT；式 6.19：结电容额外灌流缩短 t_bl。

    书 p189-190：去饱和识别、内部处理、关断必须在 t_SC 内全部完成。
    书里没给内部处理时间的数值 —— 本脚本要求用户显式给出 --t-internal。
    """
    _hr("DESAT 消隐时间预算（式 6.17 / 6.19，书 p189-190）")

    t_bl = a.cbl * a.uref / a.idesat
    print(f"C_bl            = {a.cbl * 1e12:.1f} pF")
    print(f"U_ref           = {a.uref:.3f} V")
    print(f"I_DESAT         = {a.idesat * 1e6:.1f} uA")
    print(f"t_bl (式6.17)   = {t_bl * 1e6:.2f} us")

    over_sensitive = False
    if a.cd2 is not None and a.udelta is not None:
        # 电荷上界（不是预测值）：假设整个电压摆幅都落在消隐窗口内，
        # 这时结电容注入 Q_inj = C_D2 * ΔU。真实电路中消隐在开关瞬态常被
        # 屏蔽/复位，实际缩短量通常远小于此 —— 所以这里只作**风险上界**，
        # 不参与 PASS/FAIL 判定（判定只交给时间预算）。
        q_need = a.cbl * a.uref
        q_inj = a.cd2 * a.udelta
        ratio = q_inj / q_need if q_need else float("inf")
        print(f"\n[风险上界] 消隐所需电荷 = C_bl*U_ref = {q_need * 1e9:.2f} nC")
        print(f"[风险上界] 结电容注入   = C_D2*dU  = {a.cd2 * 1e12:.1f} pF * "
              f"{a.udelta:.0f} V = {q_inj * 1e9:.2f} nC  ({ratio:.1f} 倍)")
        print("  假设：整个摆幅都发生在消隐窗口内（最坏情况）。真实驱动在开关")
        print("  瞬态多会复位/屏蔽消隐，实际缩短量更小 —— 这一项只能作指示，")
        print("  不能当预测值。要定量必须示波器实测开通瞬间的 DESAT 引脚波形。")
        if ratio > 0.30:
            over_sensitive = True
            print("  [WARN] 上界已超过 30 %：选 VD2 时优先看结电容（pF 级），")
            print("         并在台架上专门测『最高母线 + 最高温度』下的 DESAT 波形")
        t_eff = t_bl
    else:
        t_eff = t_bl

    total = t_eff + a.t_internal
    print(f"\n内部处理时间      = {a.t_internal * 1e6:.1f} us（用户输入，书中未给数值）")
    print(f"检测+处理总耗时   = {total * 1e6:.2f} us")
    print(f"器件短路耐受 t_SC = {a.tsc * 1e6:.2f} us")

    margin = a.tsc - total
    print(f"留给关断的余量    = {margin * 1e6:+.2f} us "
          f"（{100 * margin / a.tsc:+.0f} % of t_SC）")

    if a.ucs_high:
        print("\n注意：>=3.3 kV 器件开通到饱和需数 us，标准 DESAT 根本不可行（见 31 模块）")

    if over_sensitive:
        print("\n  [提示] 时序预算本身成立，但 6.19 的风险上界偏高；")
        print("         这一项**不构成 FAIL**，但必须在台架上实测 DESAT 波形确认。")
    return _verdict(
        margin > 0,
        f"时间预算成立，余量 {margin * 1e6:.2f} us",
        f"时间预算不成立：检测+处理已吃掉 {100 * total / a.tsc:.0f} % 的 t_SC，必须减小 C_bl 或改用更快保护",
    )


# ------------------------------------------------------------------- sc
def cmd_sc(a: argparse.Namespace) -> int:
    """短路能量上界。书对 I_SC 与 t_SC 只给方向（式 7.6/7.7），未给解析式。

    E_bound = U_DC * I_SC * t_sc 是**上界粗估**：忽略导通压降与电流下降沿，
    因此结果偏高，只能用于"量级判断"和"保护必须多快动作"，不能作为器件选型依据。
    """
    _hr("短路能量上界（式 7.6 / 7.7 的定性依赖，量级估算）")
    print("警告：E = U_DC*I_SC*t_sc 是上界粗估（忽略 U_CEsat 与下降沿），")
    print("      结果为偏高的量级值，不可用于器件定型。\n")

    e_j = a.udc * a.isc * a.tsc
    e_mj = e_j * 1e3
    print(f"U_DC   = {a.udc:.0f} V")
    print(f"I_SC   = {a.isc:.0f} A  （书：4~8 x I_nom，p105-107）")
    print(f"t_SC   = {a.tsc * 1e6:.1f} us")
    print(f"\n能量上界 E_bound = {e_j:.3g} J = {e_mj:.0f} mJ")
    if a.i_nom:
        print(f"折算到额定电流   = {a.isc / a.i_nom:.1f} x I_nom")

    if a.tdetect:
        rest = a.tsc - a.tdetect
        print(f"\n保护动作时间     = {a.tdetect * 1e6:.2f} us")
        print(f"剩余可承载时间   = {rest * 1e6:+.2f} us")
        ok = rest > 0
    else:
        ok = True

    print("\n物理边界（书 p105-107）：结温越高 I_SC 越小，但结温 >=200 C 芯片即坏；")
    print("Tvj 升高会同时压缩 t_SC 的上限 —— 两项同向恶化，不是互相补偿。")
    return _verdict(ok, "保护时间窗口成立（量级）",
                    "保护动作时间已超过 t_SC：关断将发生在器件失效之后")


# ------------------------------------------------------------- terminal
def cmd_terminal(a: argparse.Namespace) -> int:
    """式 5.1（书 p142）：U_term,max = U_CES + L_sigma_CE * di_C/dt

    注意 L_sigma_CE 是**模块内部**杂散电感，不含母线（母线造成的过冲见式 13.6）。

    v2.2 新增 --temp-derate：把 U_CES 按低温降额折算后再判。
    书 p111 图 3.34：6.5 kV 器件在 -50 ℃ 时 U_CES 从 6.5 kV 降到约 5.7 kV（-12.3 %）。
    书只给了这一条曲线，**其他电压等级按比例折算是推断**，本脚本会显式提示。
    """
    _hr("端子电压 vs 芯片耐压（式 5.1，书 p142）")

    uces = a.uces
    if a.temp_derate:
        uces = a.uces * (1.0 - a.temp_derate / 100.0)
        print(f"U_CES（标称，25 ℃）  = {a.uces:.0f} V")
        print(f"低温降额             = -{a.temp_derate:.1f} %（--temp-derate）")
        print(f"U_CES（低温折算）    = {uces:.0f} V")
        print("  [书 p111 图 3.34] 6.5 kV 器件 -50 ℃ 时约 5.7 kV，即 -12.3 %")
        print("  [推断] 其他电压等级按比例折算 —— 正式设计必须查该器件自己的 U_CES(T)")
    else:
        print(f"U_CES                = {uces:.0f} V（未做低温降额）")
        print("  提示：阻断能力**随温度升高而增强**，低温最弱（书 p111 图 3.34）。")
        print("        低温工况请加 --temp-derate 12.3 再判一次。")

    spike = a.lsig * a.didt
    u_term = a.u_bus + spike if a.u_bus is not None else uces - spike
    print(f"L_sigma_CE           = {a.lsig * 1e9:.1f} nH（模块内部，不含母线）")
    print(f"di_C/dt              = {a.didt / 1e9:.2f} kA/us")
    print(f"L*di/dt              = {spike:.0f} V")
    if a.u_bus is not None:
        print(f"U_bus + L*di/dt      = {a.u_term if False else u_term:.0f} V   （式 5.1 的正向用法）")
    else:
        print(f"U_CES - L*di/dt      = {u_term:.0f} V   （= 允许的最高母线电压）")

    if a.u_bus is not None:
        usable = uces - a.u_bus
        print(f"\n母线                 = {a.u_bus:.0f} V")
        print(f"静态裕量             = {usable:.0f} V（{100 * usable / uces:.0f} % of U_CES）")
        print(f"扣掉 L*di/dt 后      = {usable - spike:.0f} V（{100 * (usable - spike) / uces:.0f} %）")
        print(f"  => 母线 + L*di/dt 合计占耐压 "
              f"{100 * (a.u_bus + spike) / uces:.0f} %")
        if a.temp_derate:
            print(f"  => 反解允许 di/dt = (U_CES,低温 - U_bus)/L = "
                  f"{(uces - a.u_bus) / a.lsig / 1e9:.2f} kA/us")
        ok = a.u_bus + spike <= uces
        return _verdict(
            ok,
            "母线 + 关断尖峰仍在芯片耐压内",
            "母线 + 关断尖峰已超芯片耐压：降 di/dt、降 L_sigma_CE 或升电压等级",
        )
    return 0


# --------------------------------------------------------------- derate
def cmd_derate(a: argparse.Namespace) -> int:
    """式 8.1（书 p248-249）：delta_der = (1 - I_tot/(n*I_nom)) * 100 %

    两种用法：
      1) 给定 I_tot 求降额比例（书里的 1000A/756A -> 1756A、12 %）
      2) 给定线性化输出特性求静态分流：V0a+ra*Ia = V0b+rb*Ib, Ia+Ib=I_tot
    第 2 种是本地模型，假设只有一个器件偏热/偏低压降，且 IGBT 在该区段可线性化。
    """
    _hr("并联降额与静态均流（式 8.1，书 p248-249）")

    if a.v0a is not None and a.v0b is not None and a.ra is not None and a.rb is not None:
        denom = a.ra + a.rb
        ia = (a.v0b - a.v0a + a.rb * a.i_tot) / denom
        ib = a.i_tot - ia
        print(f"器件 A: U = {a.v0a:.3f} + {a.ra * 1e3:.3f} mOhm * I")
        print(f"器件 B: U = {a.v0b:.3f} + {a.rb * 1e3:.3f} mOhm * I")
        print(f"总电流 {a.i_tot:.0f} A 时分流：A={ia:.0f} A / B={ib:.0f} A")
        print(f"  不均衡度 = {100 * abs(ia - ib) / a.i_tot:.1f} %（相对总量）")
        print("  假设：单点线性化、忽略温度反馈、忽略栅极回路差异 —— 只作静态校核")
        worst = max(ia, ib)
        if a.i_nom and worst > a.i_nom:
            print(f"  [FAIL] 偏流侧 {worst:.0f} A 已超单管额定 {a.i_nom:.0f} A")
            return 1
        return 0

    der = (1.0 - a.i_tot / (a.n * a.i_nom)) * 100.0
    print(f"并联数 n        = {a.n}")
    print(f"单管额定 I_nom  = {a.i_nom:.0f} A")
    print(f"实际总电流      = {a.i_tot:.0f} A")
    print(f"降额            = {der:.1f} %   （式 8.1）")
    print(f"可标称总电流    = {(1 - der / 100) * a.n * a.i_nom:.0f} A")
    print("\n书里的原例（125 C、给定 U_CEsat 差）：")
    print("  2 x 1000 A -> 1756 A，降额 12 %；3 x 1000 A -> 2512 A，降额 16 %")
    print("  **这两个数是特定算例，不是通用降额系数**（书 p248-249）")
    print("\n可替代降额的手段（书 p259）：母线杂散电感挖空调整 + 隔离驱动")
    print("  （SCALE-2 抖动 <8 ns、二次侧反馈 500 mV 偏差即失衡）做到位后，")
    print("  书中明确「就不太需要过去常用的 IGBT 并联降额方法」。")
    return 0


# ------------------------------------------------------------- baliga-derate
#
# 本子命令的数据源是 Baliga 层 references/baliga/61（交通）、69（UPS）、72（SiC 成本）里的
# "降额四档谱"，汇总在 00-index §6.3 与 MEMORY 纪律 29。
# ★ 它是四档，不是五档（曾写错过，见 MEMORY 纪律 29）。

# 约束类型 -> (V_rating / V_op 的典型比, 说明, 出处)
# 实测点共 7 个：1.32 1.58 1.62 1.625 1.71 1.74 2.13
BALIGA_DERATE = {
    "clamp":     ((1.30, 1.30), "电容钳位（HVDC / MMC 子模块）—— 电压被钳死，设备只需扛钳位电平", "61 · p149 双电压钳位"),
    "resonant":  ((1.60, 1.70), "谐振 / 软开关（ZVS/ZCS）—— 换流在零电压附近完成，过压余量小", "63 · p228 压电变压器驱动"),
    "hard-ctrl": ((1.60, 1.90), "硬开关 + 受控负载（风电等）—— 过压可预测，按最坏 di/dt 留量", "67 · p325 风电变流器"),
    "hard-emc":  ((2.00, 2.20), "硬开关 + 敏感负载（UPS / 电梯）—— 负载对跳闸极敏感，宁可用低压器件", "69 · p344 UPS"),
}


def cmd_baliga_derate(a: argparse.Namespace) -> int:
    """Baliga 层降额四档谱（★ 四档，不是五档）。"""
    _hr("Baliga 降额四档谱（按约束类型查 V_rating / V_op）")

    print("约束类型（4 档）：")
    print(f"  {'key':12s} {'倍数':14s} 场景")
    for k, (rng, desc, src) in BALIGA_DERATE.items():
        lo, hi = rng
        band = f"{lo:.2f}x" if abs(hi - lo) < 1e-9 else f"{lo:.2f}~{hi:.2f}x"
        print(f"  {k:12s} {band:14s} {desc}")
        print(f"  {'':12s} {'':14s} 出处：Baliga {src}")

    if a.constraint is None:
        print("（未指定 --constraint，只列表。计算请加 --constraint <key> --v-op <V>）")
        print("★ 这是四档谱，不是五档 —— 曾被写成「五档」而表里只有 4 行（MEMORY 纪律 29）。")
        return 0

    key = a.constraint
    if key not in BALIGA_DERATE:
        print("")
        print(f"[ERROR] 未知约束类型 {key!r}；可选：{', '.join(BALIGA_DERATE)}")
        return 3

    rng, desc, src = BALIGA_DERATE[key]
    lo, hi = rng
    vmin = lo * a.v_op
    vmax = hi * a.v_op
    print("")
    print(f"选定：{key} —— {desc}")
    print(f"工作电压 V_op        = {a.v_op:.0f} V")
    if abs(hi - lo) < 1e-9:
        # 单值档（clamp）：上下沿相同，写「520 ~ 520 V」会被误读成脚本坏了
        print(f"所需器件耐压         = {vmin:.0f} V   （固定 {lo:.2f}x，非区间）")
        print("  [说明] 本档不是「靠耐压裕量」扛过压，而是靠电容把电压钳死；")
        print("         器件只需扛钳位电平。若实际无钳位电容，请改用 hard-ctrl / hard-emc。")
    else:
        print(f"所需器件耐压         = {vmin:.0f} ~ {vmax:.0f} V   （{lo:.2f}~{hi:.2f} x）")
    if a.v_rated is not None:
        need = a.v_op and (a.v_rated / a.v_op)
        verdict = "PASS" if a.v_rated >= vmin else "FAIL"
        print(f"选用器件 V_rated     = {a.v_rated:.0f} V → 倍数 {need:.2f}x  [{verdict}]")
        if verdict == "FAIL":
            print(f"  [FAIL] 低于下沿 {vmin:.0f} V；本档不允许低于 {lo:.2f}x")
            return 1
        if need > hi:
            print(f"  [WARN] 高于上沿 {vmax:.0f} V —— 不危险，但通常意味着 V_CE(sat) 白付了")
        return 0

    print("最近的标准耐压档（建议按此取整）：")
    std = [600, 650, 750, 900, 1200, 1700, 2000, 3300, 4500, 6500]
    ok = [v for v in std if v >= vmin]
    print(f"  {ok[:4] if ok else '超出本表范围，请自行外推'}")
    if ok and hi > lo and ok[0] > vmax:
        # 主档位跳过整个区间：最小可用标准档已超上沿 → 会触发 --v-rated 的 [WARN]
        print(f"  [注意] 最小可用标准档 {ok[0]:.0f} V = {ok[0]/a.v_op:.2f}x，已高于上沿 {hi:.2f}x。")
        print("         这不是错：耐压往上取只会多付 V_CE(sat)，不会更危险；")
        print("         但若成本敏感，可考虑按上沿附近定制耐压，或改用上一档约束类型。")
    print("")
    print(f"出处：Baliga {src}；汇总见 references/baliga/00-index.md §6.3 / MEMORY 纪律 29。")
    print("实测点 7 个：1.32 / 1.58 / 1.62 / 1.625 / 1.71 / 1.74 / 2.13 —— 档间是插值建议，不是书给的连续曲线。")
    return 0


# ------------------------------------------------------------- sic-parity
#
# 数据源：references/baliga/72-wbg-cost.md（表 20.3 七行 + A2.5）
#   面积比 2.06（SiC 芯片面积是 Si 的 1/2.06）
#   单价比 12.18（SiC 每 A 成本是 Si 的 12.18 倍，两边都未加毛利）
#   → 净 5.9 $/A（12.18 / 2.06 = 5.913）
#   打平门槛：晶圆价 <= 509 $/100 mm 片


def cmd_sic_parity(a: argparse.Namespace) -> int:
    """SiC vs Si 的成本打平门槛（Baliga 72 · 表 20.3 / A2.5）。

    三个数都来自书 p463 那一行推导，且两条独立路径互校过：
      面积比 2.06  : SiC 芯片面积 = Si 的 1/2.06
      单价比 12.18 : SiC 每 A 成本 = Si 的 12.18 倍（★两边都未加毛利）
      净 5.9 $/A   : 12.18 / 2.06 = 5.913
      门槛 509 $   : 21.548 $/cm2 * 0.5 * 78.54 cm2 * 0.60 = 507.7；另一路 3000 * 0.169 = 508
    """
    _hr("SiC 与 Si 的成本打平门槛（Baliga 72 · 表 20.3 / A2.5）")

    AREA_GAIN = 2.06
    PRICE_PEN = 12.18
    net = PRICE_PEN / AREA_GAIN

    print("三个关键比（口径均为「SiC ÷ Si」，两边都未加毛利）：")
    print(f"  面积比  = 1 / {AREA_GAIN:.2f} = {1 / AREA_GAIN:.4f}"
          f"   （SiC 芯片面积只有 Si 的 {100 / AREA_GAIN:.1f} %）")
    print(f"  单价比  = {PRICE_PEN:.2f}"
          f"                        （每 A 成本差 {PRICE_PEN:.2f} 倍）")
    print(f"  净成本  = {PRICE_PEN:.2f} / {AREA_GAIN:.2f} = {net:.3f} $/A"
          f"   （书报 5.9）")

    wafer = a.wafer_price
    yld = a.yld
    area_cm2 = 3.141592653589793 * 25.0          # 100 mm 片 = pi*5cm^2 = 78.54 cm2

    # Si 基准 $/A —— 书用 3000 $ / 78.54 cm2 / 0.60 得 63.66
    si_cost = wafer / area_cm2 / yld
    print("")
    print(f"Si 基准 $/A = {wafer:.0f} $ / {area_cm2:.2f} cm2 / 良率 {yld * 100:.0f} %"
          f" = {si_cost:.2f} $/A")
    print(f"  书 p463 用 3000 $ / 100 mm / 60 % 得 63.66 $/A")
    if abs(si_cost - 63.66) > 1.0:
        print(f"  [WARN] 你的输入复现不出 63.66（差 {abs(si_cost - 63.66):.2f}），"
              f"下面的门槛会跟着偏")

    print(f"  → SiC 净成本 = {si_cost:.2f} x {net:.3f} = {si_cost * net:.2f} $/A")

    # 打平判据：SiC 的 $/A 降到 Si 的 $/A
    # 即 si_cost * PRICE_PEN' / AREA_GAIN = si_cost  ->  PRICE_PEN' = AREA_GAIN
    print("")
    print("打平条件：SiC 净成本 = Si 成本，即")
    print(f"  SiC 单价比须从 {PRICE_PEN:.2f} 降到 {AREA_GAIN:.2f}"
          f"（降至 {AREA_GAIN / PRICE_PEN * 100:.1f} %，即降 {100 - AREA_GAIN / PRICE_PEN * 100:.0f} %）")
    threshold = wafer * (AREA_GAIN / PRICE_PEN)
    print(f"  折成晶圆价 = {wafer:.0f} $ x {AREA_GAIN / PRICE_PEN:.4f} = {threshold:.0f} $/100 mm 片")
    print(f"  降幅需求   = {100 - threshold / wafer * 100:.0f} %")
    print("")
    print("书 p463：门槛 509 $/100 mm 片（从 3000 $ 降 83 %）")
    print("  两条独立路径互校：21.548 $/cm2 x 0.5 x 78.54 cm2 x 0.60 = 507.7 ~ 509")
    print("                    3000 x 0.169 = 508  —— 两条都对上才成立（72 · A2.5）")

    print("")
    print("★ 口径警告（72 · A2.5①）：12.18 是「SiC 成本 / Si 成本」，两边都未加毛利才正确。")
    print("  若误用售价比 63.66 / 10.45 = 6.09，再除面积比 2.06 得 12.55（比 5.9 大一倍）。")
    print("  同理：成本比不能与售价比混用，也不能把 150 / 125 W/cm2 与表 20.1 的")
    print("  J 列 x V_CE 端值交叉相乘（95x1.6=152 / 30x3.8=114 反单调，见 00-index §6.3 第 7 项）。")

    if a.sic_wafer_price is not None:
        print("")
        if a.sic_wafer_price <= threshold:
            print(f"[PASS] SiC 晶圆价 {a.sic_wafer_price:.0f} $ <= 门槛 {threshold:.0f} $")
            return 0
        print(f"[FAIL] SiC 晶圆价 {a.sic_wafer_price:.0f} $ > 门槛 {threshold:.0f} $"
              f"（还差 {a.sic_wafer_price - threshold:.0f} $）")
        return 1
    return 0


# ------------------------------------------------------------- deadtime
def cmd_deadtime(a: argparse.Namespace) -> int:
    """式 7.5（书 p228 图 7.7）：

        t_DT = [ (t_d(off),max + t_f,max - t_d(on),min)      <- IGBT 项
               + (t_PHL,max - t_PLH,min) ] * S               <- 驱动传输延迟差项

    **两项都要**。书内算例里驱动项与 IGBT 项恰好各占一半；漏掉它低估约 50 %。
    三个 IGBT 时间必须取自同一温度、同一电压下的极值组合（书 p228 明确）。
    """
    _hr("死区时间（式 7.5，书 p228 图 7.7）")

    book = {
        25: dict(td_off=0.50e-6, tf=0.10e-6, td_on=0.20e-6),
        150: dict(td_off=0.62e-6, tf=0.18e-6, td_on=0.27e-6),
    }
    tphl, tplh = 0.0, 0.0
    if getattr(a, 'book_example', None):
        b = book[a.book_example]
        td_off, tf, td_on = b['td_off'], b['tf'], b['td_on']
        tphl, tplh = 0.50e-6, 0.10e-6
        S = 1.5
        print(f"[书本例题] 书 p228 图 7.7，Tvj = {a.book_example} C，S = 1.5")
    else:
        if a.tr_max is not None:
            print("[DEPRECATED] --tr-max 是旧名，语义错误：死区用的是下降时间 t_f，不是上升时间 t_r。")
            print("             本次按 --tf-max 解读；请改用 --tf-max。")
        tf = a.tf_max if a.tf_max is not None else a.tr_max
        if tf is None:
            return _verdict(False, "", "必须给 --tf-max（关断下降时间）；旧名 --tr-max 仅作兼容")
        td_off, td_on, S = a.td_off_max, a.td_on_min, a.safety
        tphl, tplh = a.tphl_max, a.tplh_min

    igbt = td_off + tf - td_on
    drv = tphl - tplh
    t_dt = (igbt + drv) * S

    print(f"t_d(off),max    = {td_off * 1e6:8.3f} us")
    print(f"t_f,max         = {tf * 1e6:8.3f} us")
    print(f"t_d(on),min     = {td_on * 1e6:8.3f} us")
    print(f"  -> IGBT 项    = {igbt * 1e6:8.3f} us")
    print(f"t_PHL,max       = {tphl * 1e6:8.3f} us")
    print(f"t_PLH,min       = {tplh * 1e6:8.3f} us")
    print(f"  -> 驱动项     = {drv * 1e6:8.3f} us")
    print(f"安全系数 S      = {S}")
    print(f"\nt_DT            = {t_dt * 1e6:8.3f} us")
    if t_dt > 0 and drv > 0:
        print(f"驱动项占比      = {100 * drv * S / t_dt:.1f} %")

    print("\n--- 漏项对照（同一组输入，三种写法）---")
    miss = igbt * S
    print(f"  正确（两项相加）  = {t_dt * 1e6:8.3f} us")
    if drv > 0:
        minus = (igbt - drv) * S
        print(f"  漏驱动项          = {miss * 1e6:8.3f} us  -> 低估 {100 * (1 - miss / t_dt):.1f} %")
        print(f"  驱动项写成减号    = {minus * 1e6:8.3f} us  -> 低估 {100 * (1 - minus / t_dt):.1f} %")
    else:
        print("  [WARN] 未给 --tphl-max/--tplh-min，驱动项按 0 处理；")
        print("         真实死区通常比此值大 40~100 %（书内算例中该项占 50 %）。")

    if getattr(a, 'book_example', None):
        ref = {25: 1.20, 150: 1.40}[a.book_example]
        print(f"\n[书值核对] 书给 {ref:.2f} us，本算 {t_dt * 1e6:.3f} us，偏差 {100 * (t_dt * 1e6 / ref - 1):+.1f} %")

    print("\n核对：三个 IGBT 时间必须同温度同电压。混取的两个方向不对称——")
    print("      热关断+冷开通 -> 高估约 7.5 %（浪费占空比）；冷关断+热开通 -> 低估约 21.5 %（直通风险）。")
    print("书 p229 的实战范围：死区约 1~4 us，3.3~6.5 kV 器件更长。")

    if t_dt <= 0:
        return _verdict(False, "", "算出的死区 <= 0：参数取值有误（检查 t_d(on),min 是否过大）")
    if t_dt < 0.5e-6:
        print("\n[WARN] 死区 < 0.5 us，需核对栅极回路延时差与驱动不对称性")
    return 0


# -------------------------------------------------------------- snubber
def cmd_snubber(a: argparse.Namespace) -> int:
    """吸收电容（书 p346-348）。

    **式 13.9 量纲不成立**，本命令并列显示两个结果：
      书印式：C = L * I_peak / dU^2      -> (V*s/A)*A/V^2 = s/V，不是法拉
      正确式：C = L * I_peak^2 / dU^2    -> 由 ½CU²=½LI²；与同页式 13.11 反解一致
    """
    _hr("吸收电容（书 p347：式 13.9 量纲不成立，用能量式）")

    du = a.uce_peak - a.udc
    if a.lsig <= 0:
        return _verdict(False, "", "L_sigma 必须 > 0")
    if du <= 0:
        return _verdict(False, "",
                        "U_CE,peak 必须大于 U_DC；dU<=0 表示根本没有过压，不存在吸收电容的问题")
    if a.i_peak <= 0:
        return _verdict(False, "", "I_peak 必须 > 0")

    c_book = a.lsig * a.i_peak / du**2          # 书印式（错）
    c_ok = a.lsig * a.i_peak**2 / du**2         # 能量式（对）
    f_book = 1.0 / (2 * math.pi * math.sqrt(a.lsig * c_book))
    f_ok = 1.0 / (2 * math.pi * math.sqrt(a.lsig * c_ok))
    u_before = a.lsig * a.i_peak / a.t_off if getattr(a, "t_off", None) else None

    print(f"L_sigma_total   = {a.lsig * 1e9:8.1f} nH")
    print(f"I_peak          = {a.i_peak:8.1f} A")
    print(f"U_CE,peak       = {a.uce_peak:8.1f} V  （允许的最大集电极电压）")
    print(f"U_DC            = {a.udc:8.1f} V")
    print(f"dU = 允许过压   = {du:8.1f} V")
    print()
    print("[书印式 13.9，**不要用**]")
    print(f"  C = L*I_peak/dU^2      = {c_book * 1e12:8.2f} pF")
    print(f"  量纲：(V*s/A)*A/V^2 = s/V ≠ F（法拉 = A*s/V）→ 分子缺一个 I_peak")
    print()
    print("[能量式，用这个]  C = L*I_peak^2/dU^2")
    print(f"  C =                    = {c_ok * 1e9:8.2f} nF")
    print(f"  依据：½CU² = ½LI²；与同页式 13.11（U_osc,peak ≤ √(L*I²/C)）反解一致")
    print(f"  两者比值               = {a.i_peak:8.0f} 倍  (= I_peak)")
    print()
    print("[谐振频率（式 13.10）f_osc = 1/(2π√(L·C))]")
    print(f"  用书印式 C = {c_book * 1e12:7.2f} pF -> f_osc = {f_book / 1e6:8.2f} MHz")
    print(f"  用能量式 C = {c_ok * 1e9:7.2f} nF -> f_osc = {f_ok / 1e6:8.2f} MHz")
    print("  IGBT 开关 du/dt 的频段在 MHz 以下；算到几十 MHz 说明 LC 组合不成立。")
    print()
    print("[选型边界（书 p348，硬条件）]")
    print("  · 电容电压等级 >= 半导体器件与直流母线的电压等级")
    print("  · 1.2 kV 模块 / 母线 <800 V 的常规配法：标称不低于 1 kV")
    print("  · 标称电压随温度升高而下降；高温工况必须高于 1 kV")
    print("  · 不得超过供应商手册的 I_RMS 与最大脉冲负载")
    print("  · 型式 MKP 金属聚丙烯薄膜（自愈）；直接安装在模块上")
    print("  · 有效性判据（式 13.7 化简）：L_sigma4,Snubber < L_sigma1,DC_ESL + L_sigma2,DC")
    print()
    print("[一句必须一起说的话]")
    print("  书 p346 正文：无法靠降低杂散电感保证过压时才考虑吸收电容。")
    print("  书 p348 脚注②：吸收电容会增加成本并**降低系统的寿命**，所以最好不用。")
    print("  → 顺序是先降 L_sigma（改母排/换低感封装），不是先加电容。")

    rc = 0
    if c_book * 1e12 < 1.0:
        print(f"\n[WARN] 按书印式只有 {c_book * 1e12:.2f} pF —— 小于任何 MKP 的可用量级，")
        print("       这个数就是'式 13.9 缺 I_peak'的直接证据。")
        rc = 0
    if f_book > 20e6:
        print(f"\n[WARN] 书印式得到的 f_osc = {f_book / 1e6:.1f} MHz，远超开关频段，判为不可用。")
    return rc


# ----------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="书源判据的可执行版（只实现书中给出完整式子的项）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--json", action="store_true",
                   help="以 JSON 输出（须写在子命令之前，如 `--json desat ...`）")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("desat", help="DESAT 消隐时间预算（式 6.17/6.19）")
    d.add_argument("--cbl", type=float, required=True, help="消隐电容 F，如 100e-12")
    d.add_argument("--uref", type=float, required=True, help="比较参考电压 V")
    d.add_argument("--idesat", type=float, required=True, help="DESAT 充电电流 A，如 250e-6")
    d.add_argument("--tsc", type=float, required=True, help="器件短路耐受时间 s，如 10e-6")
    d.add_argument("--t-internal", type=float, default=2e-6,
                   help="内部处理+关断延时 s（书中未给数值，默认 2e-6 为示例）")
    d.add_argument("--cd2", type=float, default=None, help="高压二极管结电容 F（式 6.19，电荷法）")
    d.add_argument("--udelta", type=float, default=None,
                   help="关断瞬态中二极管承受的电压摆幅 V（通常≈母线电压）")
    d.add_argument("--ucs-high", action="store_true", help=">=3.3 kV 器件（标准 DESAT 不适用）")
    d.set_defaults(func=cmd_desat)

    s = sub.add_parser("sc", help="短路能量上界（量级估算）")
    s.add_argument("--udc", type=float, required=True, help="母线电压 V")
    s.add_argument("--isc", type=float, required=True, help="短路电流 A（4~8 x I_nom）")
    s.add_argument("--tsc", type=float, required=True, help="短路耐受时间 s")
    s.add_argument("--tdetect", type=float, default=None, help="保护动作时间 s")
    s.add_argument("--i-nom", type=float, default=None, help="额定电流 A（用于折算倍数）")
    s.set_defaults(func=cmd_sc)

    t = sub.add_parser("terminal", help="端子电压 vs 芯片耐压（式 5.1）")
    t.add_argument("--uces", type=float, required=True, help="芯片耐压 V")
    t.add_argument("--lsig", type=float, required=True, help="模块内部杂散电感 H，如 20e-9")
    t.add_argument("--didt", type=float, required=True, help="di/dt A/s，如 5e9")
    t.add_argument("--u-bus", type=float, default=None, help="实际母线电压 V（可选）")
    t.add_argument("--temp-derate", type=float, default=None,
                   help="低温降额百分比（如 12.3 表示 -50 ℃ 时 U_CES 降 12.3%%；"
                        "书 p111 图 3.34 只给了 6.5 kV 一条曲线）")
    t.set_defaults(func=cmd_terminal)

    r = sub.add_parser("derate", help="并联降额与静态均流（式 8.1）")
    r.add_argument("--n", type=int, default=2, help="并联数")
    r.add_argument("--i-nom", type=float, default=1000, help="单管额定电流 A")
    r.add_argument("--i-tot", type=float, required=True, help="实际总电流 A")
    r.add_argument("--v0a", type=float, default=None, help="器件 A 的 U_CE0（V）")
    r.add_argument("--v0b", type=float, default=None, help="器件 B 的 U_CE0（V）")
    r.add_argument("--ra", type=float, default=None, help="器件 A 的 r_CE（Ohm）")
    r.add_argument("--rb", type=float, default=None, help="器件 B 的 r_CE（Ohm）")
    r.set_defaults(func=cmd_derate)

    dt = sub.add_parser("deadtime", help="死区时间（式 7.5，含驱动传输延迟差项）")
    dt.add_argument("--td-off-max", type=float, default=0.0, help="关断延迟最大值 s")
    dt.add_argument("--tf-max", type=float, default=None, help="关断下降时间最大值 t_f，s")
    dt.add_argument("--tr-max", type=float, default=None,
                    help="[DEPRECATED] 旧参数名（语义错误，死区用 t_f 不用 t_r）；等价于 --tf-max")
    dt.add_argument("--td-on-min", type=float, default=0.0, help="开通延迟最小值 s")
    dt.add_argument("--tphl-max", type=float, default=0.0,
                    help="驱动 高->低 传输延迟最大值 t_PHL，s；不给会漏掉约一半死区")
    dt.add_argument("--tplh-min", type=float, default=0.0,
                    help="驱动 低->高 传输延迟最小值 t_PLH，s")
    dt.add_argument("--safety", type=float, default=1.5, help="安全系数 S，书中给 1.5")
    dt.add_argument("--book-example", type=int, choices=[25, 150], default=None,
                    help="复现书 p228 图 7.7 的内置算例（25 或 150 摄氏度）")
    dt.set_defaults(func=cmd_deadtime)

    sn = sub.add_parser("snubber", help="吸收电容（式 13.9 量纲不成立 → 能量式；p346-348）")
    sn.add_argument("--lsig", type=float, required=True, help="总杂散电感 H，如 50e-9（含模块内+母排+电容 ESL）")
    sn.add_argument("--i-peak", type=float, required=True, help="关断过程中最大峰值电流 A")
    sn.add_argument("--uce-peak", type=float, required=True, help="为保证安全裕量允许的最大集电极电压 V")
    sn.add_argument("--udc", type=float, required=True, help="直流母线电压 V")
    sn.add_argument("--t-off", type=float, default=None, help="（可选）关断时间 s，仅用于参照，不参与 C 计算")
    sn.set_defaults(func=cmd_snubber)

    bd = sub.add_parser("baliga-derate", help="Baliga 降额四档谱（★四档不是五档；61/67/69/63）")
    bd.add_argument("--constraint", default=None,
                    choices=list(BALIGA_DERATE.keys()),
                    help="clamp / resonant / hard-ctrl / hard-emc；不给则只列表")
    bd.add_argument("--v-op", type=float, default=None, help="直流母线工作电压 V")
    bd.add_argument("--v-rated", type=float, default=None, help="（可选）拟选器件的额定电压 V，用于判定")
    bd.set_defaults(func=cmd_baliga_derate)

    sp = sub.add_parser("sic-parity", help="SiC 与 Si 的成本打平门槛（72 · 表 20.3 / A2.5）")
    sp.add_argument("--wafer-price", type=float, default=3000.0, help="Si 晶圆价 $/100 mm 片（书用 3000）")
    sp.add_argument("--sic-wafer-price", type=float, default=None, help="（可选）SiC 晶圆价 $/100 mm 片，用于判定")
    sp.add_argument("--yld", type=float, default=0.60, help="良率（书用 0.60；不能用 --yield，它是 Python 保留字）")
    sp.add_argument("--margin", type=float, default=None, help="（可选）Si 毛利率，如 0.3")
    sp.set_defaults(func=cmd_sic_parity)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.json:
        import contextlib
        import io
        import json

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = args.func(args)
        print(json.dumps({"cmd": args.cmd, "returncode": rc, "output": buf.getvalue()},
                         ensure_ascii=False))
        return rc

    rc = args.func(args)
    print("\n" + "-" * 62)
    print("公式来源：Volke & Hornkamp《IGBT 模块：技术、驱动和应用》中文版；")
    print("页引与限制见 references/volke-hornkamp/34-formula-index.md。")
    print("本书未给 E_as、驱动功率显式公式、探头延时补偿 —— 本脚本不给，别外推。")
    print("缓冲电容：书 p347 式 13.9 分子缺 I_peak（量纲不成立），请用 C=L*I^2/dU^2。")
    return rc


if __name__ == "__main__":
    sys.exit(main())

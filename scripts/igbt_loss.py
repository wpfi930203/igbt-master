#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
igbt_loss.py — IGBT 损耗 / 结温 / 开关频率上限 估算器

用途
    给定工况，估算单个开关位置的通态损耗、开关损耗、总损耗、结温，
    并反解开在给定散热条件下的开关频率上限。

设计原则（重要）
    1. 纯标准库实现，无第三方依赖。
    2. 输出必须带「假设」与「数据来源」——不带条件的损耗数字在本行业等于噪声。
    3. datasheet 的 Eon/Eoff 是在特定 Rg/VCC/Tvj/Lsigma 下测的，
       本脚本用线性比例缩放（VCC、IC）做一阶修正，**不是精确模型**。
       误差可达 30%+，用于方案比选与敏感性分析，不用于设计定型。

用法示例
    python igbt_loss.py --vdc 800 --i-pk 400 --m 1.0 --cosphi 0.85 --fsw 8000 \
        --vce0 1.05 --rce 0.0032 --eon 45 --eoff 62 --vref 600 --iref 400 \
        --tc 85 --rth-jc 0.12 --tmax 175

    python igbt_loss.py --help
    python igbt_loss.py ... --json

公式来源
    2 电平 VSI 每开关的电流有效值/平均值近似（SEMIKRON Application Manual 体系）:
        IGBT:  I_avg = Ipk*(1/(2*pi) + m*cosphi/8)
               I_rms = Ipk*sqrt(1/8 + m*cosphi/(3*pi))
        Diode: I_avg = Ipk*(1/(2*pi) - m*cosphi/8)
               I_rms = Ipk*sqrt(1/8 - m*cosphi/(3*pi))
    通态损耗（线性化 VCE(sat) = VCE0 + rCE*IC）:
        P_cond = VCE0 * I_avg + rCE * I_rms^2
    开关损耗:
        P_sw = fsw * (Eon + Eoff + Erec) * (VCC/Vref) * (IC/Iref)
    结温:
        Tvj = Tc + (P_cond + P_sw) * Rth(j-c)
    开关频率上限（令 Tvj = Tjmax 解 fsw）:
        fsw_max = ( (Tjmax - Tc)/Rth - P_cond ) / E_sum_scaled
"""

import argparse
import json
import math
import sys

PI = math.pi


def compute(args):
    # ---- 1. 电流分量 ----
    # 单管/单芯片承担的部分
    ipk = args.i_pk / max(args.n_parallel, 1)
    m = args.m
    cphi = args.cosphi

    igbt_avg = ipk * (1.0 / (2 * PI) + m * cphi / 8.0)
    igbt_rms = ipk * math.sqrt(max(1.0 / 8.0 + m * cphi / (3 * PI), 0.0))
    diode_avg = ipk * (1.0 / (2 * PI) - m * cphi / 8.0)
    diode_rms = ipk * math.sqrt(max(1.0 / 8.0 - m * cphi / (3 * PI), 0.0))

    # ---- 2. 通态损耗 ----
    p_cond_igbt = args.vce0 * igbt_avg + args.rce * igbt_rms ** 2
    p_cond_diode = 0.0
    if args.vf0 is not None and args.rf is not None:
        p_cond_diode = args.vf0 * diode_avg + args.rf * diode_rms ** 2

    # ---- 3. 开关损耗（一阶缩放 + 正弦口径系数）----
    # 书 式 3.16 / 3.26 / 3.28 / 3.29 都带 1/π（p99、p104、p106 的脚注：「适用于正弦电流」）。
    # 物理来源：正弦电流下，单个器件只在半个工频周期里有显著开关损耗，
    # 对**整个**工频周期取平均 → (1/2π)·∫₀^π f_sw·E(î·sinθ)dθ = (1/π)·f_sw·E(î)。
    # 恒流工况（斩波/直流/单脉冲）没有这个系数，应显式传 --sw-factor 1.0。
    scale_v = args.vdc / args.vref
    scale_i = args.i_pk / args.iref
    scale = scale_v * scale_i * args.kt_sw * args.sw_factor

    e_sum_ref_mj = args.eon + args.eoff + args.erec      # mJ @ Vref, Iref
    p_sw_no_fsw = e_sum_ref_mj * 1e-3 * scale           # J per switching event（已含口径系数）

    p_sw = args.fsw * p_sw_no_fsw

    p_total = p_cond_igbt + p_cond_diode + p_sw

    # ---- 4. 结温 ----
    tj = args.tc + p_total * args.rth_jc
    tj_margin = args.tmax - tj

    # ---- 5. 开关频率上限 ----
    fsw_max = None
    if p_sw_no_fsw > 0 and args.rth_jc > 0:
        headroom_w = (args.tmax - args.tc) / args.rth_jc - p_cond_igbt - p_cond_diode
        fsw_max = max(headroom_w, 0.0) / p_sw_no_fsw

    return {
        "inputs": {
            "vdc_V": args.vdc,
            "i_pk_A_total": args.i_pk,
            "i_pk_A_per_device": ipk,
            "n_parallel": args.n_parallel,
            "modulation_index_m": m,
            "cos_phi": cphi,
            "fsw_Hz": args.fsw,
            "Tc_C": args.tc,
            "Rth_jc_K_per_W": args.rth_jc,
            "Tjmax_C": args.tmax,
            "sw_waveform_factor": args.sw_factor,
        },
        "currents": {
            "IGBT_I_avg_A": igbt_avg,
            "IGBT_I_rms_A": igbt_rms,
            "Diode_I_avg_A": diode_avg,
            "Diode_I_rms_A": diode_rms,
        },
        "losses_W": {
            "P_cond_IGBT": p_cond_igbt,
            "P_cond_Diode": p_cond_diode,
            "P_switching": p_sw,
            "P_total": p_total,
        },
        "thermal": {
            "Tvj_C": tj,
            "Tj_margin_K": tj_margin,
            "verdict": "PASS" if tj_margin >= 0 else "FAIL",
        },
        "fsw_limit": {
            "fsw_max_Hz": fsw_max,
            "note": "由 Tvj=Tjmax 反解；未考虑开关损耗随温度上升、未考虑死区与最小脉宽",
        },
        "assumptions": [
            "电流分量为 2 电平 VSI 每开关的近似，m 与 cosphi 需按实际调制方式修正",
            "VCE(sat) 线性化为 VCE0 + rCE*IC，需用 125C 或 150C 曲线拟合得到 VCE0/rCE",
            "Eon/Eoff/Erec 按 VCC 与 IC 线性缩放，未做 Rg 与 Lsigma 修正",
            "开关损耗含正弦口径系数（默认 1/pi，书 式3.29）；恒流斩波工况传 --sw-factor 1.0，否则差 pi 倍",
            "未计入驱动损耗、吸收电路损耗、反向恢复引起的额外开通损耗交互",
            "Rth(j-c) 视为常数，未考虑流量/TIM 厚度/安装压力影响",
        ],
    }


def render_human(r):
    L = []
    L.append("=" * 62)
    L.append("IGBT 损耗 / 结温 / 开关频率上限 估算")
    L.append("=" * 62)
    i = r["inputs"]
    L.append(f"工况: VDC={i['vdc_V']} V | Ipk={i['i_pk_A_total']} A "
             f"(每器件 {i['i_pk_A_per_device']:.1f} A, {i['n_parallel']} 并联)")
    L.append(f"      m={i['modulation_index_m']} | cosphi={i['cos_phi']} | "
             f"fsw={i['fsw_Hz'] / 1000:.2f} kHz")
    L.append(f"      Tc={i['Tc_C']} C | Rth(j-c)={i['Rth_jc_K_per_W']} K/W | "
             f"Tjmax={i['Tjmax_C']} C")
    L.append("-" * 62)
    c = r["currents"]
    L.append("电流分量:")
    L.append(f"  IGBT : I_avg={c['IGBT_I_avg_A']:.1f} A  I_rms={c['IGBT_I_rms_A']:.1f} A"
             f"   (波形系数 {c['IGBT_I_rms_A'] / c['IGBT_I_avg_A']:.2f})")
    if c["Diode_I_avg_A"] > 0.01:
        L.append(f"  Diode: I_avg={c['Diode_I_avg_A']:.1f} A  "
                 f"I_rms={c['Diode_I_rms_A']:.1f} A")
    L.append("-" * 62)
    p = r["losses_W"]
    L.append("损耗:")
    L.append(f"  通态(IGBT)   : {p['P_cond_IGBT']:8.2f} W")
    if p["P_cond_Diode"] > 0:
        L.append(f"  通态(Diode)  : {p['P_cond_Diode']:8.2f} W")
    L.append(f"  开关         : {p['P_switching']:8.2f} W")
    fac = i.get("sw_waveform_factor", 1.0)
    tag = "正弦 1/pi，书式3.29" if abs(fac - 1.0 / PI) < 1e-6 else (
        "恒流/斩波 f*E" if abs(fac - 1.0) < 1e-6 else "自定义")
    L.append(f"      （口径系数 = {fac:.4f}，{tag}）")
    L.append(f"  合计         : {p['P_total']:8.2f} W")
    L.append("-" * 62)
    t = r["thermal"]
    L.append(f"结温: Tvj = {t['Tvj_C']:.1f} C   "
             f"裕量 = {t['Tj_margin_K']:+.1f} K   [{t['verdict']}]")
    f = r["fsw_limit"]
    if f["fsw_max_Hz"] is not None:
        L.append(f"开关频率上限: {f['fsw_max_Hz'] / 1000:.2f} kHz "
                 f"({f['note']})")
    L.append("-" * 62)
    L.append("假设与局限（结论必须带这些条件）:")
    for a in r["assumptions"]:
        L.append(f"  - {a}")
    L.append("=" * 62)
    L.append("提示: 本脚本是工程估算，不是设计定型依据。必须用实测 DPT + 热仿真校核。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(
        description="IGBT 损耗 / 结温 / 开关频率上限 估算器（工程估算，非设计定型依据）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n  python igbt_loss.py --vdc 800 --i-pk 400 --m 1.0 --cosphi 0.85 "
               "--fsw 8000 --vce0 1.05 --rce 0.0032 --eon 45 --eoff 62 "
               "--vref 600 --iref 400 --tc 85 --rth-jc 0.12 --tmax 175",
    )
    ap.add_argument("--vdc", type=float, required=True, help="直流母线电压 V")
    ap.add_argument("--i-pk", type=float, required=True, help="输出电流峰值 A（总）")
    ap.add_argument("--m", type=float, default=1.0, help="调制系数 0-1，默认 1.0")
    ap.add_argument("--cosphi", type=float, default=0.85, help="功率因数，默认 0.85")
    ap.add_argument("--fsw", type=float, required=True, help="开关频率 Hz")
    ap.add_argument("--vce0", type=float, required=True,
                    help="VCE(sat) 线性化截距 V（用工作温度下的曲线拟合）")
    ap.add_argument("--rce", type=float, required=True,
                    help="VCE(sat) 线性化斜率 Ohm（用工作温度下的曲线拟合）")
    ap.add_argument("--eon", type=float, default=0.0, help="Eon mJ @ Vref/Iref")
    ap.add_argument("--eoff", type=float, default=0.0, help="Eoff mJ @ Vref/Iref")
    ap.add_argument("--erec", type=float, default=0.0, help="Erec mJ @ Vref/Iref")
    ap.add_argument("--vref", type=float, default=600.0, help="Eon/Eoff 测试电压 Vref V")
    ap.add_argument("--iref", type=float, default=400.0, help="Eon/Eoff 测试电流 Iref A")
    ap.add_argument("--kt-sw", type=float, default=1.0,
                    help="开关损耗温度修正系数（>1 为高温恶化），默认 1.0")
    ap.add_argument("--sw-factor", type=float, default=1.0 / PI,
                    help="开关损耗的电流口径系数。默认 1/pi=0.3183（正弦电流，书 式3.29："
                         "单管半周期导通，对整工频周期取平均）；恒流/斩波工况传 1.0")
    ap.add_argument("--vf0", type=float, default=None, help="二极管 VF 截距 V（可选）")
    ap.add_argument("--rf", type=float, default=None, help="二极管 VF 斜率 Ohm（可选）")
    ap.add_argument("--tc", type=float, required=True, help="壳温/散热器温度 C")
    ap.add_argument("--rth-jc", type=float, required=True, help="Rth(j-c) K/W（每器件）")
    ap.add_argument("--tmax", type=float, default=175.0, help="Tjmax C，默认 175")
    ap.add_argument("--n-parallel", type=int, default=1, help="并联器件数，默认 1")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    if args.rth_jc <= 0:
        ap.error("--rth-jc 必须 > 0")
    if args.i_pk <= 0 or args.fsw <= 0:
        ap.error("--i-pk 与 --fsw 必须 > 0")
    if not (0 < args.m <= 1.5):
        ap.error("--m 应在 (0, 1.5] 区间")

    r = compute(args)
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    print(render_human(r))
    return 0 if r["thermal"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

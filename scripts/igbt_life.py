#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
igbt_life.py — 功率循环寿命：雨流计数 / 寿命模型 / Miner 累积

★ 关于系数的诚实声明（请务必读）
    本脚本**不内置任何"通用"寿命模型系数**。
    原因：Coffin-Manson 的 C、LESIT 的 A/Ea、Bayerer 的 K/β1..β6 都是
    **拟合参数**，随封装结构、材料、工艺、芯片厚度、键合线直径而变。
    把它们写成"默认值"传下去，是这个行业最常见的造假方式之一
    ——换一个封装，同一个公式能差一个数量级。

    因此本脚本要求你：
      (a) 从你引用的**原始文献原文**抄录系数（并在报告里注明文献），或
      (b) 用 `fit` 子命令从你自己的功率循环试验数据拟合，或
      (c) 用 `--coef-file` 加载公司内部的标定系数库。

用法
    # 1) 雨流计数（从 CSV 的温度序列提取循环）
    python igbt_life.py cycles --csv mission.csv --col Tj --bin 1.0

    # 2) 单点预测（必须给系数）
    python igbt_life.py predict --model lesit --dtj 80 --tjm 125 \
        --coef A=6.4e5 --coef alpha=-5 --coef Ea=7.0e-20

    # 3) 使命剖面累积损伤
    python igbt_life.py stack --csv mission.csv --col Tj --model bayerer \
        --coef-file my_coef.json --ton 2.0 --wire-current 12 --vclass 1200 --wire-d 0.3

    # 4) 用自有试验数据拟合 LESIT
    python igbt_life.py fit --csv pctest.csv --dtj-col dTj --tjm-col Tjm --nf-col Nf

模型形式
    Coffin-Manson : Nf = C * dTj^(-n)
    LESIT         : Nf = A * dTj^alpha * exp(Ea / (k * Tjm_K))
    Bayerer       : Nf = K * dTj^b1 * exp(b2 / (Tjm_C + 273)) * ton^b3
                         * I^b4 * V^b5 * D^b6
    （Bayerer 已知局限：不含基板焊层失效；不适用于牵引厚芯片）

Miner 线性累积
    D = Σ (ni / Nfi)；D >= 1 判失效。D 的物理意义是"损伤分数"，不是寿命。
"""

import argparse
import csv
import json
import math
import sys

K_BOLTZMANN = 1.380649e-23  # J/K


# ----------------------------------------------------------------------------
# 雨流计数（ASTM E1049 简化的三点法）
# ----------------------------------------------------------------------------
def rainflow(series):
    """
    返回 [(range, mean, count), ...]
    range = 摆幅（峰谷差，不是半幅）
    count = 1.0 全循环 / 0.5 半循环
    """
    stack = []
    out = []
    for x in series:
        stack.append(float(x))
        while len(stack) >= 3:
            a, b, c = stack[-3], stack[-2], stack[-1]
            r1 = abs(b - a)
            r2 = abs(c - b)
            if r1 <= r2:
                out.append((r1, (a + b) / 2.0, 1.0))
                del stack[-3:-1]
            else:
                break
    i = 0
    n = len(stack)
    while i < n - 1:
        rng = abs(stack[i + 1] - stack[i])
        mean = (stack[i] + stack[i + 1]) / 2.0
        cnt = 0.5 if (i == 0 or i == n - 2) else 1.0
        out.append((rng, mean, cnt))
        i += 1
    return out


def bin_cycles(cycles, bin_width, min_range=0.0):
    """
    按摆幅分箱聚合：返回 [{range_bin, count, mean}]

    min_range: 最小摆幅门限（K）。低于此值的循环被丢弃。
               这是**必须**的参数——实测温度序列的测量噪声（±0.5K 甚至更大）
               会通过雨流算法产生成百上千个虚假小循环，
               它们对寿命几乎无损伤，但会淹没真实的循环分布。
    """
    cycles = [c for c in cycles if c[0] >= min_range]
    if bin_width <= 0:
        return [{"low": c[0], "high": c[0], "count": c[2], "mean": c[1]} for c in cycles]
    buckets = {}
    for rng, mean, cnt in cycles:
        key = math.floor(rng / bin_width) * bin_width
        key = max(key, math.floor(min_range / bin_width) * bin_width)
        b = buckets.setdefault(key, {"count": 0.0, "mean_sum": 0.0, "n": 0})
        b["count"] += cnt
        b["mean_sum"] += mean
        b["n"] += 1
    out = []
    for k in sorted(buckets):
        b = buckets[k]
        low = max(k, min_range)
        out.append({
            "low": low,
            "high": k + bin_width,
            "count": b["count"],
            "mean": b["mean_sum"] / b["n"] if b["n"] else 0.0,
        })
    return out


# ----------------------------------------------------------------------------
# 寿命模型
# ----------------------------------------------------------------------------
def nf_cm(dtj, coef):
    return coef["C"] * pow(dtj, -coef["n"])


def nf_lesit(dtj, tjm_c, coef):
    tjm_k = tjm_c + 273.15
    return coef["A"] * pow(dtj, coef["alpha"]) * math.exp(coef["Ea"] / (K_BOLTZMANN * tjm_k))


def nf_bayerer(dtj, tjm_c, coef, ton, wire_i, vclass, wire_d):
    # 注意: 分母中的 273 沿用 Bayerer 原文的写法定式 (Tjm+273)
    return (coef["K"]
            * pow(dtj, coef["b1"])
            * math.exp(coef["b2"] / (tjm_c + 273.0))
            * pow(ton, coef["b3"])
            * pow(wire_i, coef["b4"])
            * pow(vclass, coef["b5"])
            * pow(wire_d, coef["b6"]))


def compute_nf(model, dtj, tjm_c, coef, extra):
    if dtj <= 0:
        return float("inf")
    if model == "cm":
        return nf_cm(dtj, coef)
    if model == "lesit":
        return nf_lesit(dtj, tjm_c, coef)
    if model == "bayerer":
        return nf_bayerer(dtj, tjm_c, coef, extra["ton"], extra["wire_current"],
                          extra["vclass"], extra["wire_d"])
    raise ValueError(f"未知模型: {model}")


REQUIRED_COEF = {
    "cm": ["C", "n"],
    "lesit": ["A", "alpha", "Ea"],
    "bayerer": ["K", "b1", "b2", "b3", "b4", "b5", "b6"],
}


def load_coef(args):
    if args.coef_file:
        with open(args.coef_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 允许 {"lesit": {...}, "bayerer": {...}} 或直接 {...}
        if args.model in data and isinstance(data[args.model], dict):
            return data[args.model]
        return data
    coef = {}
    for item in (args.coef or []):
        if "=" not in item:
            raise SystemExit(f"--coef 格式应为 key=value，收到: {item}")
        k, v = item.split("=", 1)
        coef[k.strip()] = float(v)
    return coef


def check_coef(model, coef):
    missing = [k for k in REQUIRED_COEF[model] if k not in coef]
    if missing:
        raise SystemExit(
            "缺少系数: " + ", ".join(missing) + "\n"
            "本脚本不提供默认系数——请从原始文献抄录、用 `fit` 从自有数据拟合，"
            "或用 --coef-file 加载内部标定库。\n"
            f"{model} 需要的系数: {REQUIRED_COEF[model]}"
        )


# ----------------------------------------------------------------------------
# 最小二乘拟合 LESIT（3 参数，正规方程 + 高斯消元）
# ----------------------------------------------------------------------------
def solve_linear(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-15:
            raise SystemExit("拟合矩阵奇异：数据点不足或 dTj/Tjm 变化范围太小")
        m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f:
                for j in range(col, n + 1):
                    m[r][j] -= f * m[col][j]
    return [m[i][n] for i in range(n)]


def fit_lesit(rows):
    """rows = [(dtj, tjm_c, nf), ...]  ->  coef dict"""
    if len(rows) < 3:
        raise SystemExit("LESIT 三参数拟合至少需要 3 组数据（建议 >= 8 组）")
    X, Y = [], []
    for dtj, tjm_c, nf in rows:
        if dtj <= 0 or nf <= 0:
            continue
        X.append([1.0, math.log(dtj), 1.0 / (tjm_c + 273.15)])
        Y.append(math.log(nf))
    n = 3
    ata = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(n)] for i in range(n)]
    atb = [sum(X[r][i] * Y[r] for r in range(len(X))) for i in range(n)]
    beta = solve_linear(ata, atb)
    A = math.exp(beta[0])
    alpha = beta[1]
    Ea = beta[2] * K_BOLTZMANN
    # R^2
    ybar = sum(Y) / len(Y)
    ss_tot = sum((y - ybar) ** 2 for y in Y)
    ss_res = sum((Y[r] - sum(beta[i] * X[r][i] for i in range(n))) ** 2 for r in range(len(Y)))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"A": A, "alpha": alpha, "Ea": Ea}, r2, len(Y)


# ----------------------------------------------------------------------------
# 子命令
# ----------------------------------------------------------------------------
def read_csv_column(path, col, second_col=None):
    vals1, vals2 = [], []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames is None:
            raise SystemExit(f"CSV 无表头: {path}")
        if col not in rd.fieldnames:
            raise SystemExit(f"列 {col} 不存在。可用列: {rd.fieldnames}")
        for row in rd:
            try:
                vals1.append(float(row[col]))
                if second_col:
                    vals2.append(float(row[second_col]))
            except (TypeError, ValueError):
                continue
    if not vals1:
        raise SystemExit("未读到有效数据行")
    return (vals1, vals2) if second_col else vals1


def cmd_cycles(args):
    series = read_csv_column(args.csv, args.col)
    cyc = rainflow(series)
    binned = bin_cycles(cyc, args.bin, args.min_range)
    total_full = sum(c[2] for c in cyc)
    kept_full = sum(c["count"] for c in binned)
    res = {
        "mode": "rainflow",
        "points": len(series),
        "Tj_min": min(series),
        "Tj_max": max(series),
        "min_range_K": args.min_range,
        "equivalent_full_cycles": kept_full,
        "discarded_cycles": total_full - kept_full,
        "cycles": binned,
        "notes": [
            "摆幅 = 峰谷差；半循环记为 0.5",
            "min-range 用于滤除测量噪声产生的虚假小循环；建议取 2-3 倍测量不确定度",
            "雨流计数对序列的起点/终点敏感，长序列影响可忽略",
            "仅温度序列不足以外推寿命：还需 ton/电流/线径/模型系数",
        ],
    }
    return res


def cmd_predict(args):
    coef = load_coef(args)
    check_coef(args.model, coef)
    extra = {
        "ton": args.ton,
        "wire_current": args.wire_current,
        "vclass": args.vclass,
        "wire_d": args.wire_d,
    }
    if args.model == "bayerer":
        for k, v in [("--ton", args.ton), ("--wire-current", args.wire_current),
                     ("--vclass", args.vclass), ("--wire-d", args.wire_d)]:
            if v is None:
                raise SystemExit(f"Bayerer 模型需要 {k}")
    nf = compute_nf(args.model, args.dtj, args.tjm, coef, extra)
    res = {
        "mode": "predict",
        "model": args.model,
        "dtj_K": args.dtj,
        "Tjm_C": args.tjm,
        "Nf": nf,
        "coefficients_used": coef,
        "notes": [
            "Nf 是循环数，不是时间；换算时间需要使命剖面的循环频率",
            "结果对系数极敏感：必须注明系数来源（文献/自有拟合/内部标定）",
            "Bayerer 不含基板焊层失效，不适用于牵引厚芯片",
        ],
    }
    if args.model == "bayerer":
        res["bayerer_inputs"] = extra
    return res


def cmd_stack(args):
    coef = load_coef(args)
    check_coef(args.model, coef)
    series = read_csv_column(args.csv, args.col)
    cyc = rainflow(series)
    binned = bin_cycles(cyc, args.bin, args.min_range)
    extra = {
        "ton": args.ton,
        "wire_current": args.wire_current,
        "vclass": args.vclass,
        "wire_d": args.wire_d,
    }
    if args.model == "bayerer":
        for k, v in [("--ton", args.ton), ("--wire-current", args.wire_current),
                     ("--vclass", args.vclass), ("--wire-d", args.wire_d)]:
            if v is None:
                raise SystemExit(f"Bayerer 模型需要 {k}（注意：这些是单次试验的固定条件，"
                                 "使命剖面若跨多个条件需分段计算）")

    detail = []
    damage = 0.0
    for c in binned:
        dtj = (c["low"] + c["high"]) / 2.0
        nf = compute_nf(args.model, dtj, c["mean"], coef, extra)
        d = (c["count"] / nf) if nf > 0 and math.isfinite(nf) else 0.0
        damage += d
        detail.append({
            "dTj_range_K": [round(c["low"], 2), round(c["high"], 2)],
            "dTj_K": round(dtj, 3),
            "Tjm_C": round(c["mean"], 3),
            "n_i": round(c["count"], 2),
            "Nf_i": None if not math.isfinite(nf) else round(nf, 1),
            "damage_i": d,
        })
    res = {
        "mode": "stack",
        "model": args.model,
        "dtj_bin_K": args.bin,
        "total_damage_Miner": damage,
        "estimated_life_multiplier": (1.0 / damage) if damage > 0 else None,
        "verdict": ("PASS (D<0.5)" if damage < 0.5
                    else "MARGINAL (0.5<=D<1)" if damage < 1.0
                    else "FAIL (D>=1)"),
        "detail": detail,
        "coefficients_used": coef,
        "notes": [
            "D>=1 判失效是 Miner 线性累积假设，实际寿命分散性用 Weibull 给 B10",
            "'life_multiplier' 表示该剖面可重复多少次，不是年数",
            "未考虑载荷顺序效应、蠕变交互、老化导致的 Rth 上升（正反馈）",
            "系数来源必须写进报告；换封装不能沿用",
        ],
    }
    return res


def cmd_fit(args):
    dtj, tjm = read_csv_column(args.csv, args.dtj_col, args.tjm_col)
    nf = read_csv_column(args.csv, args.nf_col)
    n = min(len(dtj), len(tjm), len(nf))
    rows = [(dtj[i], tjm[i], nf[i]) for i in range(n)]
    coef, r2, used = fit_lesit(rows)
    res = {
        "mode": "fit_lesit",
        "points_used": used,
        "coefficients": coef,
        "R2_log_space": r2,
        "warnings": [
            "R2 < 0.9 说明单一模型不足以描述你的数据——可能存在多种失效机理",
            "拟合区间外的外推不可信（尤其超出试验的 dTj / Tjm 范围）",
            "LESIT 未分离键合线失效与焊层失效；若两者混在数据里，R2 会掉",
            "建议按失效机理分组分别拟合",
        ],
    }
    return res


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="IGBT 功率循环寿命计算器（不内置通用系数，必须自行提供）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="子命令: cycles | predict | stack | fit",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_model_common(p):
        p.add_argument("--model", choices=["cm", "lesit", "bayerer"], required=True)
        p.add_argument("--coef", action="append", metavar="KEY=VALUE",
                       help="系数，可重复，例: --coef A=6.4e5 --coef alpha=-5")
        p.add_argument("--coef-file", help="系数 JSON 文件")
        p.add_argument("--ton", type=float, help="加热时间 s（Bayerer 必需）")
        p.add_argument("--wire-current", type=float, help="每根键合线电流 A（Bayerer 必需）")
        p.add_argument("--vclass", type=float, help="电压等级 V（Bayerer 必需）")
        p.add_argument("--wire-d", type=float, help="键合线直径 mm（Bayerer 必需）")
        p.add_argument("--json", action="store_true")

    c = sub.add_parser("cycles", help="雨流计数")
    c.add_argument("--csv", required=True, help="含温度序列的 CSV")
    c.add_argument("--col", required=True, help="温度列名，例: Tj")
    c.add_argument("--bin", type=float, default=1.0, help="摆幅分箱宽度 K，默认 1.0")
    c.add_argument("--min-range", type=float, default=0.0,
                   help="最小摆幅门限 K，用于滤除测量噪声产生的虚假小循环（建议 2-3 倍测量不确定度）")
    c.add_argument("--json", action="store_true")

    p = sub.add_parser("predict", help="单点寿命预测")
    add_model_common(p)
    p.add_argument("--dtj", type=float, required=True, help="结温摆幅 K")
    p.add_argument("--tjm", type=float, required=True, help="平均结温 C")

    s = sub.add_parser("stack", help="使命剖面累积损伤")
    add_model_common(s)
    s.add_argument("--csv", required=True, help="温度时间序列 CSV")
    s.add_argument("--col", required=True, help="温度列名")
    s.add_argument("--bin", type=float, default=1.0, help="摆幅分箱宽度 K")
    s.add_argument("--min-range", type=float, default=0.0,
                   help="最小摆幅门限 K，滤除噪声产生的虚假小循环")

    f = sub.add_parser("fit", help="从自有试验数据拟合 LESIT")
    f.add_argument("--csv", required=True)
    f.add_argument("--dtj-col", required=True)
    f.add_argument("--tjm-col", required=True)
    f.add_argument("--nf-col", required=True)
    f.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "cycles":
        r = cmd_cycles(args)
    elif args.cmd == "predict":
        r = cmd_predict(args)
    elif args.cmd == "stack":
        r = cmd_stack(args)
    elif args.cmd == "fit":
        r = cmd_fit(args)
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    print("=" * 68)
    print(f"IGBT 寿命计算 · {r['mode']}")
    print("=" * 68)
    if r["mode"] == "rainflow":
        print(f"数据点: {r['points']}  Tj 范围: {r['Tj_min']:.1f} ~ {r['Tj_max']:.1f} C")
        print(f"等效全循环数(保留): {r['equivalent_full_cycles']:.2f}"
              f"   已滤除(<{r['min_range_K']}K): {r['discarded_cycles']:.2f}")
        print(f"\n{'摆幅区间(K)':>14}{'代表值':>9}{'平均温度(C)':>14}{'循环数':>10}")
        print("-" * 48)
        for c_ in r["cycles"][:40]:
            rng_s = (f"{c_['low']:.0f}" if c_["low"] == c_["high"]
                     else f"{c_['low']:.0f}-{c_['high']:.0f}")
            rep = (c_["low"] + c_["high"]) / 2.0
            print(f"{rng_s:>14}{rep:>9.1f}{c_['mean']:>14.1f}{c_['count']:>10.2f}")
        if len(r["cycles"]) > 40:
            print(f"  ... 共 {len(r['cycles'])} 个分箱（仅显示前 40）")
    elif r["mode"] == "predict":
        print(f"模型: {r['model']}  dTj={r['dtj_K']} K  Tjm={r['Tjm_C']} C")
        print(f"\n  => Nf = {r['Nf']:.4g} cycles")
        print(f"\n使用系数: {json.dumps(r['coefficients_used'], ensure_ascii=False)}")
        if "bayerer_inputs" in r:
            print(f"Bayerer 输入: {json.dumps(r['bayerer_inputs'], ensure_ascii=False)}")
    elif r["mode"] == "stack":
        print(f"模型: {r['model']}  分箱: {r['dtj_bin_K']} K")
        print(f"\n{'dTj区间(K)':>14}{'Tjm(C)':>9}{'n_i':>10}{'Nf_i':>14}{'损伤':>12}")
        print("-" * 61)
        for d in r["detail"][:40]:
            nf_s = "inf" if d["Nf_i"] is None else f"{d['Nf_i']:.4g}"
            rng_s = f"{d['dTj_range_K'][0]:.0f}-{d['dTj_range_K'][1]:.0f}"
            print(f"{rng_s:>14}{d['Tjm_C']:>9.1f}{d['n_i']:>10.2f}"
                  f"{nf_s:>14}{d['damage_i']:>12.2e}")
        if len(r["detail"]) > 40:
            print(f"  ... 共 {len(r['detail'])} 个分箱")
        print("-" * 61)
        print(f"Miner 累积损伤 D = {r['total_damage_Miner']:.4e}")
        print(f"该剖面可重复次数 ≈ {r['estimated_life_multiplier']}")
        print(f"判定: {r['verdict']}")
    elif r["mode"] == "fit_lesit":
        print(f"数据点: {r['points_used']}   R2(log空间) = {r['R2_log_space']:.4f}")
        print(f"\n拟合系数:")
        for k, v in r["coefficients"].items():
            print(f"  {k} = {v:.6g}")
        print("\n警告:")
        for w in r["warnings"]:
            print(f"  * {w}")

    if "notes" in r:
        print("-" * 68)
        for n in r["notes"]:
            print(f"  * {n}")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())

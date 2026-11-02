#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
igbt_thermal.py — 热阻链拆解 / 瞬态热阻抗 / 反解所需 Rth

用途
    1. chain    : 把 Rth(j-c) 按层拆开，给每层的温降与累积热阻（识别瓶颈层）
    2. zth      : 用 Foster 网络算某一时刻的瞬态热阻抗 Zth(t) 与温升
    3. require  : 给定额定损耗与允许温升，反解所需 Rth

为什么必须拆链
    "Rth(j-c) = 0.12 K/W" 这种单一数字无法指导改进。
    真正要做的是知道芯片焊层贡献 0.02、DBC 贡献 0.05、底板 0.03、TIM 0.02，
    然后才知道改哪个界面有收益。这是结构函数存在的意义。

重要局限（必须随结论一起给出）
    - Foster 网络是数学拟合，网络节点**不对应物理层**；Cauer 网络才对物理。
      Foster 参数不能直接解释为"某层的热容和热阻"。
    - 结构函数（structure function）才是把 Zth 映射到物理层的正规工具，
      本脚本不做结构函数反卷积（需专用设备与算法，如 T3Ster 体系）。
    - 本脚本的 chain 模式是"给定各层 Rth 做加总"，不是从 Zth 曲线反推。

用法
    # 1) 热阻链拆解
    python igbt_thermal.py chain --layer "die=0.02" --layer "die_attach=0.015" \
        --layer "dcb=0.05" --layer "baseplate_solder=0.02" \
        --layer "baseplate=0.03" --layer "tim=0.025" \
        --ploss 300 --tcoolant 65

    # 2) 瞬态：Foster 网络
    python igbt_thermal.py zth --foster "0.008,0.002;0.03,0.05;0.06,0.6" \
        --ploss 300 --t 0.01

    # 3) 反解所需 Rth
    python igbt_thermal.py require --ploss 300 --tc 85 --tmax 175 --safety 20
"""

import argparse
import json
import sys


def parse_layers(pairs):
    out = []
    for p in pairs:
        if "=" not in p:
            raise ValueError(f"--layer 格式应为 name=value，收到: {p}")
        k, v = p.split("=", 1)
        out.append((k.strip(), float(v)))
    return out


def parse_foster(spec):
    """spec: "R1,tau1;R2,tau2;..." """
    pts = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        r, tau = chunk.split(",")
        pts.append((float(r), float(tau)))
    return pts


def cmd_chain(args):
    layers = parse_layers(args.layer)
    if not layers:
        raise SystemExit("chain 模式至少需要一个 --layer")

    total = sum(r for _, r in layers)
    t = args.tcoolant
    rows = []
    for name, r in layers:
        drop = args.ploss * r
        t_new = t + drop
        rows.append({
            "layer": name,
            "Rth_K_per_W": r,
            "share_pct": (r / total * 100.0) if total else 0.0,
            "deltaT_K": drop,
            "T_after_C": t_new,
        })
        t = t_new

    tj = t
    margin = args.tmax - tj
    worst = max(rows, key=lambda x: x["Rth_K_per_W"]) if rows else None

    res = {
        "total_Rth_K_per_W": total,
        "ploss_W": args.ploss,
        "Tcold_C": args.tcoolant,
        "Tvj_C": tj,
        "Tjmax_C": args.tmax,
        "margin_K": margin,
        "verdict": "PASS" if margin >= 0 else "FAIL",
        "bottleneck": worst["layer"] if worst else None,
        "layers": rows,
        "notes": [
            "各层 Rth 需来自实测结构函数或热仿真，不能凭经验拍",
            "Rth 依赖 TIM 厚度、安装压力、冷却液流量——报 Rth 必须带这些条件",
            "模组 datasheet 的 Rth(j-c) 与系统 Rth(j-f) 不可直接相加",
            "本拆解是给定 Rth 的加总，不是从 Zth 反卷积得到",
        ],
    }
    return res


def cmd_zth(args):
    foster = parse_foster(args.foster)
    t = args.t
    z = sum(r * (1.0 - pow(2.718281828459045, -t / tau)) for r, tau in foster)
    rise = args.ploss * z
    res = {
        "mode": "zth_foster",
        "t_s": t,
        "Zth_K_per_W": z,
        "ploss_W": args.ploss,
        "deltaT_K": rise,
        "Tvj_C": args.tcoolant + rise if args.tcoolant is not None else None,
        "foster_terms": [{"R": r, "tau": tau} for r, tau in foster],
        "notes": [
            "Foster 网络是数学拟合，节点不对应物理层；要物理层请用结构函数",
            "tau 必须与 R 配对且按时间常数排序，否则拟合无意义",
            "单脉冲近似：假设功率为理想阶跃，未考虑实际波形上升沿",
        ],
    }
    return res


def cmd_require(args):
    dT_allow = args.tmax - args.tc - args.safety
    if dT_allow <= 0:
        raise SystemExit(
            f"可用温升 {dT_allow:.1f} K <= 0：Tjmax={args.tmax}, Tc={args.tc}, "
            f"安全裕量={args.safety}。请检查输入。"
        )
    rth_req = dT_allow / args.ploss
    res = {
        "mode": "require_rth",
        "Tjmax_C": args.tmax,
        "Tc_C": args.tc,
        "safety_K": args.safety,
        "allowed_deltaT_K": dT_allow,
        "ploss_W": args.ploss,
        "required_Rth_total_K_per_W": rth_req,
        "notes": [
            "这是总热阻（结到冷却介质）的上限，包含所有层 + TIM + 散热器",
            "车规通常留 15-25 K 裕量，本脚本用 --safety 指定",
            "若实测 Rth 接近该上限，说明没有余量应对流量下降/TIM 老化",
        ],
    }
    return res


def render_chain(r):
    L = []
    L.append("=" * 66)
    L.append(f"热阻链拆解  (Ploss={r['ploss_W']} W, Tcold={r['Tcold_C']} C)")
    L.append("=" * 66)
    L.append(f"{'层':<22}{'Rth(K/W)':>10}{'占比':>9}{'温降(K)':>10}{'累计温度(C)':>13}")
    L.append("-" * 66)
    for row in r["layers"]:
        L.append(f"{row['layer']:<22}{row['Rth_K_per_W']:>10.4f}"
                 f"{row['share_pct']:>8.1f}%{row['deltaT_K']:>10.1f}"
                 f"{row['T_after_C']:>13.1f}")
    L.append("-" * 66)
    L.append(f"{'合计':<22}{r['total_Rth_K_per_W']:>10.4f}{100.0:>8.1f}%"
             f"{r['ploss_W'] * r['total_Rth_K_per_W']:>10.1f}{r['Tvj_C']:>13.1f}")
    L.append("=" * 66)
    L.append(f"Tvj = {r['Tvj_C']:.1f} C | Tjmax = {r['Tjmax_C']} C | "
             f"裕量 = {r['margin_K']:+.1f} K  [{r['verdict']}]")
    L.append(f"瓶颈层: {r['bottleneck']}")
    L.append("-" * 66)
    for n in r["notes"]:
        L.append(f"  * {n}")
    return "\n".join(L)


def render_generic(r, title):
    L = ["=" * 66, title, "=" * 66]
    for k, v in r.items():
        if k in ("notes",):
            continue
        L.append(f"  {k}: {v}")
    if "notes" in r:
        L.append("-" * 66)
        for n in r["notes"]:
            L.append(f"  * {n}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(
        description="IGBT 热阻链 / 瞬态热阻抗 / 所需 Rth 计算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="子命令: chain | zth | require   （各自 -h 看参数）",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chain", help="热阻链拆解")
    c.add_argument("--layer", action="append", default=[], metavar="NAME=RTH",
                   help="层名=热阻，可重复；按结到环境的顺序给")
    c.add_argument("--ploss", type=float, required=True, help="器件总损耗 W")
    c.add_argument("--tcoolant", type=float, default=25.0, help="冷却介质/起始温度 C")
    c.add_argument("--tmax", type=float, default=175.0, help="Tjmax C")
    c.add_argument("--json", action="store_true")

    z = sub.add_parser("zth", help="Foster 网络瞬态热阻抗")
    z.add_argument("--foster", required=True, metavar="R1,TAU1;R2,TAU2",
                   help="Foster 项，例: 0.008,0.002;0.03,0.05;0.06,0.6")
    z.add_argument("--ploss", type=float, required=True, help="阶跃功率 W")
    z.add_argument("--t", type=float, required=True, help="时刻 s")
    z.add_argument("--tcoolant", type=float, default=None, help="起始温度 C（可选）")
    z.add_argument("--json", action="store_true")

    q = sub.add_parser("require", help="反解所需总 Rth")
    q.add_argument("--ploss", type=float, required=True)
    q.add_argument("--tc", type=float, required=True, help="壳温/冷却温度 C")
    q.add_argument("--tmax", type=float, default=175.0)
    q.add_argument("--safety", type=float, default=20.0, help="安全裕量 K，默认 20")
    q.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "chain":
        r = cmd_chain(args)
        if args.json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(render_chain(r))
        return 0 if r["verdict"] == "PASS" else 1

    if args.cmd == "zth":
        r = cmd_zth(args)
        if args.json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(render_generic(r, f"瞬态热阻抗 @ t={args.t} s"))
            print(f"  => Zth = {r['Zth_K_per_W']:.5f} K/W, "
                  f"温升 = {r['deltaT_K']:.2f} K")
        return 0

    if args.cmd == "require":
        r = cmd_require(args)
        if args.json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(render_generic(r, "所需总热阻（结到冷却介质）"))
            print(f"  => Rth_required <= "
                  f"{r['required_Rth_total_K_per_W']:.4f} K/W")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

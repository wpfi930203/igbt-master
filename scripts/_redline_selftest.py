#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""redline 自我回归测试（双向验证）。

为什么需要它：
    redline 的红线检查全靠正则。每次为了消掉误报而放宽豁免，都有把真违规一起
    放过去的风险 —— 而**假阴性不会被人发现**（没有任何输出，看着像"干净"）。
    所以每放宽一次，必须同时跑：
      (1) 全模块扫描：114 个知识模块（书源 38 + 厂商层 10 + Baliga 23 + 封装 13 + Lutz 15 + AQG 9 + 国标 6）应全部 rc=0（说明没有误报）
      (2) 反向用例：**故意写错**的句子必须全部被抓到（说明没有漏报）
    两个方向都过，才算这次改动安全。

用法：
    python _redline_selftest.py            # 跑全部
    python _redline_selftest.py --only neg # 只跑反向用例

返回码：0 全过；1 有失败项。
"""
import argparse
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "igbt_book_ledger.py"
REF = HERE.parent / "references" / "volke-hornkamp"
VENDOR = HERE.parent / "references" / "infineon"
BALIGA = HERE.parent / "references" / "baliga"
# 登记表：本身逐条登记红线，命中属"登记"而非"违规"
REGISTRY = {"34-formula-index.md", "material-database.md", "00-index.md", "SKILL.md"}

# 反向用例：(期望rc, 说明, 正文)
#   期望 rc=1 → 这是**故意写错**的，必须被抓到（漏报检测）
#   期望 rc=0 → 这是**正确写法**，必须放行（误报检测）
NEG_CASES = [
    (1, "式13.9 照抄错式（分子缺 I_peak）",
     "缓冲电容按书式 13.9：C_snub = L*I_peak/U_peak^2，代入 L=30uH、I=1000A 得 21.8 uF。\n"),
    (1, "式6.12c 用乘号（η 应是分母）",
     "驱动电源 DC-DC 功率取 P = (P_GE + P_CG) × η = 3.2 × 0.85 = 2.72 W。\n"),
    (1, "把 3.27 与 5.1 当两个独立结论引",
     "按式 3.27 判 RBSOA 的安全工作区，另按式 5.1 校核一遍，两式结论互相印证。\n"),
    (1, "正弦开关损耗漏 1/π",
     "正弦输出下开关损耗 P_sw = E_sw × f_sw，未做折算，按恒流口径算得 480 W。\n"),
    (0, "正确：式13.9 用 I_peak²",
     "缓冲电容取 C = L·I_peak²/ΔU²（式 13.11 反解），30uH×1e6/300^2 = 333 uF。\n"),
    (0, "正确：η 作分母",
     "驱动电源输入功率 P_in = (P_GE + P_CG) / η = 3.2 / 0.85 = 3.76 W。\n"),
    (0, "正确：单次能量 E_off·f_sw（本层不乘 1/π）",
     "P_saved = E_off · f_sw = 10×10⁻³ × 4000 = 40 W\n"),
    (0, "正确：已显式写 1/π",
     "正弦工况开关损耗 P_sw = (1/π) · E_sw · f_sw = 0.3183 × 0.05 × 8000 = 127 W。\n"),
    # ── Baliga 层专项（v2.11.0）：新增第四个知识源后必须同时扩反向用例，
    #    否则「71/71 全过」可能只说明规则对新来源是空转。
    (1, "Baliga 概念挂到《IGBT 模块》出处（伪造出处）",
     "**层归属**：Baliga 书源层（`50`–`72`）\n\n"
     "4H-SiC 的 BFOM 比硅高 2000 倍，据《IGBT 模块》式 3.88 可算得。\n"),
    (1, "Baliga 层误乘 1/π（本层是单脉冲能量）",
     "**层归属**：Baliga 书源层（`50`–`72`）\n\n"
     "开关损耗 P_sw = (1/π) × E_sw × f_sw = 0.3183 × 0.05 × 8000 = 127 W。\n"),
    (1, "跨层裸式号（式号前没有层名）",
     "4H-SiC 与硅按 Baliga 式 3.88 对比后，另按式 3.27 判 RBSOA 边界。\n"),
    (0, "正确：两个式号都带层名",
     "按 Baliga 式 3.27 算积累电荷，另据《IGBT 模块》式 3.27 判 RBSOA。\n"),
]


def run_redline(path: Path) -> int:
    r = subprocess.run(
        [sys.executable, str(LEDGER), "redline", "--file", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode


def test_modules() -> int:
    """99 个知识模块（书源 38 + 厂商 10 + Baliga 23 + 封装 13 + Lutz 15）应全部 rc=0。"""
    print("=" * 64)
    print("① 全模块扫描（检误报：应 125/125 rc=0 = 书源 38 + 厂商层 10 + Baliga 23 + 封装 13 + Lutz 15 + AQG 9 + 国标 6 + IEC60747-9:2019 6 + IEC60747-15:2024 5）")
    print("=" * 64)
    fails = []
    files = sorted(p for p in REF.glob("*.md") if p.name[:2].isdigit())
    files = [p for p in files if p.name[:2] not in ("00", "34") and p.name not in REGISTRY]
    # 厂商层（v2.8.0）：10 个模块，索引 00-index 不参与模块计数
    if VENDOR.exists():
        vend = sorted(p for p in VENDOR.glob("*.md") if p.name[:2].isdigit() and p.name[:2] != "00")
        print(f"  （书源 {len(files)} + 厂商层 {len(vend)}）")
        files = files + vend
    # Baliga 层（v2.10.0 起建，v2.11.0 全 23 模块）：50–72，索引 00-index 不参与模块计数
    if BALIGA.exists():
        bal = sorted(p for p in BALIGA.glob("*.md") if p.name[:2].isdigit() and p.name[:2] != "00")
        print(f"  （+ Baliga 层 {len(bal)}）")
        files = files + bal
    # 封装层（v2.12.0 起建）：73–85，索引 00-index 不参与模块计数
    PKG = HERE.parent / "references" / "packaging"
    if PKG.exists():
        pkg = sorted(p for p in PKG.glob("*.md") if p.name[:2].isdigit() and p.name[:2] != "00")
        print(f"  （+ 封装层 {len(pkg)}）")
        files = files + pkg
    # Lutz 层（v2.13.0 起建）：86–100，索引 00-index 不参与模块计数
    LZ = HERE.parent / "references" / "lutz"
    if LZ.exists():
        lz = sorted(p for p in LZ.glob("*.md") if re.match(r"^(0[1-9]|[1-9]\d{1,2})-", p.name) and p.name != "00-index.md")
        print(f"  （+ Lutz 层 {len(lz)}）")
        files = files + lz
    # AQG 标准层（v2.14.0 起建）：101–109，索引 00-index 不参与模块计数
    AQ = HERE.parent / "references" / "aqg324"
    if AQ.exists():
        aq = sorted(p for p in AQ.glob("*.md") if re.match(r"^(0[1-9]|[1-9]\d{1,2})-", p.name) and p.name != "00-index.md")
        print(f"  （+ AQG 标准层 {len(aq)}）")
        files = files + aq
    # 国标层（v2.15.0 起建）：110–115，索引 00-index 不参与模块计数
    GB = HERE.parent / "references" / "gb29332"
    if GB.exists():
        gbl = sorted(p for p in GB.glob("*.md") if re.match(r"^(0[1-9]|[1-9]\d{1,2})-", p.name) and p.name != "00-index.md")
        print(f"  （+ 国标层 {len(gbl)}）")
        files = files + gbl
    # IEC 60747-9:2019 层（v2.16.0 起建）：116–121，索引 00-index 不参与模块计数
    IEC9 = HERE.parent / "references" / "iec60747-9-2019"
    if IEC9.exists():
        i9 = sorted(p for p in IEC9.glob("*.md") if re.match(r"^(0[1-9]|[1-9]\d{1,2})-", p.name) and p.name != "00-index.md")
        print(f"  （+ IEC 60747-9:2019 层 {len(i9)}）")
        files = files + i9
    # IEC 60747-15:2024 层（v2.16.0 起建）：122–126，索引 00-index 不参与模块计数
    IEC15 = HERE.parent / "references" / "iec60747-15-2024"
    if IEC15.exists():
        i15 = sorted(p for p in IEC15.glob("*.md") if re.match(r"^(0[1-9]|[1-9]\d{1,2})-", p.name) and p.name != "00-index.md")
        print(f"  （+ IEC 60747-15:2024 层 {len(i15)}）")
        files = files + i15
    for p in files:
        rc = run_redline(p)
        if rc != 0:
            fails.append((p.name, rc))
            print(f"  [FAIL] {p.name}  rc={rc}")
        else:
            print(f"  [ OK ] {p.name}")
    print()
    print(f"小结：{len(files) - len(fails)}/{len(files)} 通过"
          + ("" if not fails else f"；失败 {[f[0] for f in fails]}"))
    return len(fails)


def test_negatives() -> int:
    """故意写错的必须抓到，正确写法必须放行。"""
    print("=" * 64)
    print(f"② 反向用例（检漏报 + 误报：必须 {len(NEG_CASES)}/{len(NEG_CASES)}）")
    print("=" * 64)
    fails = 0
    for want, name, body in NEG_CASES:
        fd, path = tempfile.mkstemp(suffix=".md", dir=tempfile.gettempdir())
        os.close(fd)
        Path(path).write_text("## 自测用例\n\n" + body, encoding="utf-8")
        rc = run_redline(Path(path))
        os.unlink(path)
        got = 1 if rc == 1 else (3 if rc == 3 else 0)
        kind = "漏报" if (want == 1 and got != 1) else ("误报" if (want == 0 and got != 0) else "")
        if got == want:
            print(f"  [ OK ] {name}")
        else:
            fails += 1
            print(f"  [FAIL] {name}：期望 rc={want} 实得 rc={rc}  ← {kind}"
                  + ("（检查器自身规则编译失败）" if rc == 3 else ""))
    print()
    print(f"小结：{len(NEG_CASES) - fails}/{len(NEG_CASES)} 通过")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["mod", "neg"], default=None)
    a = ap.parse_args()

    if not LEDGER.exists():
        print(f"[ERR] 找不到 {LEDGER}")
        return 2

    f = 0
    if a.only in (None, "mod"):
        f += test_modules()
        print()
    if a.only in (None, "neg"):
        f += test_negatives()
        print()

    print("=" * 64)
    if f == 0:
        print("[判决] 双向验证通过：无误报、无漏报")
        return 0
    print(f"[判决] {f} 项失败 —— 改动豁免/规则后必须双向都过，不能只看一边")
    return 1


if __name__ == "__main__":
    sys.exit(main())

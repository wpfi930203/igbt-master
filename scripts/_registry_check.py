# -*- coding: utf-8 -*-
"""_registry_check.py — 登记一致性总核验（改 count / 改 assets / 加模块后必跑）

为什么需要它：`redline` 只查「内容里有没有禁用值」，`struct_check` 只查「骨架是否连续」，
**两者都不会发现「磁盘上有文件但 meta 没登记」「声明 N 项但表只有 M 行」**。
v2.11.2 实测抓出 4 类真问题：checklists/07 未登记、§6.2 写 2 项而表 5 行、
55·A2.3 结论改了推导没改、磁盘 39 编号文件被当成 39 模块。

用法：
    python scripts/_registry_check.py            # 默认从脚本所在目录推技能根
    python scripts/_registry_check.py --root <技能根>
返回码：0 = 全绿 / 1 = 有不一致 / 3 = 规则自身坏（找不到文件等）

⚠ 本脚本自身踩过的坑（改它之前先读）：
  ① 模块计数**不能**直接用「两位数字开头」—— `34-formula-index` 是索引不是模块，
     `00-index` 也不是。必须**先分类再计数**，否则 38 会被数成 39。
  ② 正则里把 `sec="6.2"` 拼进 `r"6\\.%s"` 会变成 `6\\.6.2`，永远匹配不到 →
     三表行数全返回 -1，看起来像「表是空的」，其实是**检查器坏了**。
"""
import io, json, os, re, sys

# ---------- 分类常量（新增模块/索引时改这里） ----------
INDEX_ONLY = {"34-formula-index.md"}                    # 书源层纯索引的编号文件
CROSS_CUTTING = {"material-database.md", "worked-examples.md"}
# ⚠ \d{1,2} 写成 \d 会在 100 号模块上漏计（v2.13.0 实测：Lutz 层被数成 14）——
#   模块号已有三位数（100），模式必须容忍 1–3 位。
MODULE_NUM = r"^(0[1-9]|[1-9]\d{1,2})-"

EXPECTED = {
    "volke_modules": 38,
    "vendor_modules": 10,
    "baliga_modules": 23,
    "packaging_modules": 13,
    "lutz_modules": 15,
    "aqg_modules": 9,
    "gb_modules": 6,
    "iec9_modules": 6,
    "iec15_modules": 5,
    "modules_total": 125,
    "modules_in_gates": 123,
}


def load(root):
    p = os.path.join(root, "meta.json")
    if not os.path.isfile(p):
        print("[RC3] meta.json 不存在: " + p)
        sys.exit(3)
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def read(path):
    if not os.path.isfile(path):
        print("[RC3] 文件缺失: " + path)
        sys.exit(3)
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]

    d = load(root)
    fails = []

    def chk(name, cond, detail=""):
        print(("[ OK ] " if cond else "[FAIL] ") + name + (("  " + detail) if detail else ""))
        if not cond:
            fails.append(name)

    # ---------- 1) 目录实况 vs meta 登记 ----------
    print("=" * 60)
    print("① 资产目录 vs meta.assets")
    print("=" * 60)
    for sub in ("checklists", "templates"):
        p = os.path.join(root, sub)
        disk = sorted(f for f in os.listdir(p) if f.endswith(".md")) if os.path.isdir(p) else []
        reg = sorted(os.path.basename(x) for x in d.get("assets", {}).get(sub, []))
        chk("%s 目录=登记" % sub, disk == reg, "磁盘 %d / 登记 %d" % (len(disk), len(reg)))
        for m in sorted(set(disk) - set(reg)):
            print("        [缺登记] " + sub + "/" + m)
        for g in sorted(set(reg) - set(disk)):
            print("        [登记但不存在] " + sub + "/" + g)

    # ---------- 2) 模块计数（先分类再计数） ----------
    print("=" * 60)
    print("② 模块计数（索引文件不算模块）")
    print("=" * 60)

    def numbered(layer):
        p = os.path.join(root, "references", layer)
        if not os.path.isdir(p):
            print("[RC3] 目录缺失: " + p)
            sys.exit(3)
        return sorted(f for f in os.listdir(p)
                      if re.match(MODULE_NUM, f) and f.endswith(".md"))

    vh = numbered("volke-hornkamp")
    vh_mod = [f for f in vh if f not in INDEX_ONLY]
    cross = [f for f in os.listdir(os.path.join(root, "references", "volke-hornkamp"))
             if f in CROSS_CUTTING]
    infi = numbered("infineon")
    bal = numbered("baliga")
    pk = numbered("packaging")
    lz = numbered("lutz")
    aq = numbered("aqg324")
    gb = numbered("gb29332")
    iec9 = numbered("iec60747-9-2019")
    iec15 = numbered("iec60747-15-2024")

    print("        书源层 编号 %d = 模块 %d + 索引 %d；横向索引 %d"
          % (len(vh), len(vh_mod), len(vh) - len(vh_mod), len(cross)))
    print("        厂商层 %d ／ Baliga %d ／ 封装层 %d ／ Lutz %d ／ AQG %d ／ 国标 %d ／ IEC60747-9 %d ／ IEC60747-15 %d"
          % (len(infi), len(bal), len(pk), len(lz), len(aq), len(gb), len(iec9), len(iec15)))

    chk("书源模块 %d（排除 34 索引）" % EXPECTED["volke_modules"],
        len(vh_mod) == EXPECTED["volke_modules"], str(len(vh_mod)))
    chk("厂商层 %d" % EXPECTED["vendor_modules"],
        len(infi) == EXPECTED["vendor_modules"], str(len(infi)))
    chk("Baliga %d" % EXPECTED["baliga_modules"],
        len(bal) == EXPECTED["baliga_modules"], str(len(bal)))
    chk("封装层 %d" % EXPECTED["packaging_modules"],
        len(pk) == EXPECTED["packaging_modules"], str(len(pk)))
    chk("Lutz 层 %d" % EXPECTED["lutz_modules"],
        len(lz) == EXPECTED["lutz_modules"], str(len(lz)))
    chk("AQG 标准层 %d" % EXPECTED["aqg_modules"],
        len(aq) == EXPECTED["aqg_modules"], str(len(aq)))
    chk("国标层 %d" % EXPECTED["gb_modules"],
        len(gb) == EXPECTED["gb_modules"], str(len(gb)))
    chk("IEC 60747-9:2019 层 %d" % EXPECTED["iec9_modules"],
        len(iec9) == EXPECTED["iec9_modules"], str(len(iec9)))
    chk("IEC 60747-15:2024 层 %d" % EXPECTED["iec15_modules"],
        len(iec15) == EXPECTED["iec15_modules"], str(len(iec15)))
    tot = len(vh_mod) + len(infi) + len(bal) + len(pk) + len(lz) + len(aq) + len(gb) + len(iec9) + len(iec15)
    chk("九源合计 %d" % EXPECTED["modules_total"], tot == EXPECTED["modules_total"], str(tot))
    chk("meta.modules_total 一致", d.get("integration_layer", {}).get("modules_total") == tot)
    chk("meta.modules_in_gates == %d" % EXPECTED["modules_in_gates"],
        d.get("integration_layer", {}).get("modules_in_gates") == EXPECTED["modules_in_gates"])

    extra = [f for f in os.listdir(os.path.join(root, "references", "baliga"))
             if f.endswith(".md") and f not in bal and f != "00-index.md"]
    chk("Baliga 目录无未登记 md", not extra, str(extra))

    # package_layer 资产登记校验（v2.12.0）：磁盘 14 文件（00-index + 73-85）须与 meta 登记一致
    pk_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("package_layer", []))
    pk_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "packaging")) if f.endswith(".md"))
    chk("package_layer 登记=磁盘", pk_assets == pk_disk,
        "登记 %d / 磁盘 %d" % (len(pk_assets), len(pk_disk)))
    extra_pk = [f for f in pk_disk if f not in pk_assets and f != "00-index.md"]
    chk("封装层 目录无未登记 md", not extra_pk, str(extra_pk))

    # lutz_layer 资产登记校验（v2.13.0）：磁盘 16 文件（00-index + 86-100）须与 meta 登记一致
    lz_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("lutz_layer", []))
    lz_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "lutz")) if f.endswith(".md"))
    chk("lutz_layer 登记=磁盘", lz_assets == lz_disk,
        "登记 %d / 磁盘 %d" % (len(lz_assets), len(lz_disk)))
    extra_lz = [f for f in lz_disk if f not in lz_assets and f != "00-index.md"]
    chk("Lutz 目录无未登记 md", not extra_lz, str(extra_lz))

    # aqg324_layer 资产登记校验（v2.14.0）：磁盘 10 文件（00-index + 101-109）须与 meta 登记一致
    aq_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("aqg324_layer", []))
    aq_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "aqg324")) if f.endswith(".md"))
    chk("aqg324_layer 登记=磁盘", aq_assets == aq_disk,
        "登记 %d / 磁盘 %d" % (len(aq_assets), len(aq_disk)))
    extra_aq = [f for f in aq_disk if f not in aq_assets and f != "00-index.md"]
    chk("AQG 目录无未登记 md", not extra_aq, str(extra_aq))

    # gb_layer 资产登记校验（v2.15.0）：磁盘 7 文件（00-index + 110-115）须与 meta 登记一致
    gb_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("gb_layer", []))
    gb_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "gb29332")) if f.endswith(".md"))
    chk("gb_layer 登记=磁盘", gb_assets == gb_disk,
        "登记 %d / 磁盘 %d" % (len(gb_assets), len(gb_disk)))
    extra_gb = [f for f in gb_disk if f not in gb_assets and f != "00-index.md"]
    chk("国标目录无未登记 md", not extra_gb, str(extra_gb))

    # iec60747-9-2019 层资产登记校验（v2.16.0）：磁盘 7 文件（00-index + 116-121）
    iec9_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("iec9_layer", []))
    iec9_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "iec60747-9-2019")) if f.endswith(".md"))
    chk("iec9_layer 登记=磁盘", iec9_assets == iec9_disk,
        "登记 %d / 磁盘 %d" % (len(iec9_assets), len(iec9_disk)))
    extra_iec9 = [f for f in iec9_disk if f not in iec9_assets and f != "00-index.md"]
    chk("IEC60747-9 目录无未登记 md", not extra_iec9, str(extra_iec9))

    # iec60747-15-2024 层资产登记校验（v2.16.0）：磁盘 6 文件（00-index + 122-126）
    iec15_assets = sorted(os.path.basename(x) for x in d.get("assets", {}).get("iec15_layer", []))
    iec15_disk = sorted(f for f in os.listdir(os.path.join(root, "references", "iec60747-15-2024")) if f.endswith(".md"))
    chk("iec15_layer 登记=磁盘", iec15_assets == iec15_disk,
        "登记 %d / 磁盘 %d" % (len(iec15_assets), len(iec15_disk)))
    extra_iec15 = [f for f in iec15_disk if f not in iec15_assets and f != "00-index.md"]
    chk("IEC60747-15 目录无未登记 md", not extra_iec15, str(extra_iec15))

    # iec9 层登记表声明 vs 行数（references/iec60747-9-2019/00-index.md）
    iec9idx = read(os.path.join(root, "references", "iec60747-9-2019", "00-index.md"))
    iec9rc = d.get("iec60747_9_layer", {}).get("registry_counts", {})
    for key, sec, nxt in (("6_2_formula_not_quantifiable", "6.2", "6.3"),
                          ("6_3_caliber_notes", "6.3", "6.4")):
        m = re.search(r"^###\s*" + re.escape(sec) + r"\b(.*?)(?=^###\s" + re.escape(nxt) + r"|\Z)",
                      iec9idx, re.S | re.M)
        if not m:
            print("[RC3] IEC60747-9 00-index §%s 标题未找到 —— 检查器正则坏了" % sec)
            sys.exit(3)
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*`(C|N|E)\d+`", s):
                n += 1
        chk("IEC60747-9 §%s 表 %d 行 = 声明 %s" % (sec, n, iec9rc.get(key)), n == iec9rc.get(key))

    # iec15 层登记表声明 vs 行数（references/iec60747-15-2024/00-index.md）
    iec15idx = read(os.path.join(root, "references", "iec60747-15-2024", "00-index.md"))
    iec15rc = d.get("iec60747_15_layer", {}).get("registry_counts", {})
    for key, sec, nxt in (("6_2_formula_not_quantifiable", "6.2", "6.3"),
                          ("6_3_caliber_notes", "6.3", "6.4")):
        m = re.search(r"^###\s*" + re.escape(sec) + r"\b(.*?)(?=^###\s" + re.escape(nxt) + r"|\Z)",
                      iec15idx, re.S | re.M)
        if not m:
            print("[RC3] IEC60747-15 00-index §%s 标题未找到 —— 检查器正则坏了" % sec)
            sys.exit(3)
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*`(C|N|E)\d+`", s):
                n += 1
        chk("IEC60747-15 §%s 表 %d 行 = 声明 %s" % (sec, n, iec15rc.get(key)), n == iec15rc.get(key))

    # AQG 层登记表声明 vs 行数（references/aqg324/00-index.md）
    aqidx = read(os.path.join(root, "references", "aqg324", "00-index.md"))
    aqrc = d.get("aqg324_layer", {}).get("registry_counts", {})
    for key, sec, nxt in (("6_2_formula_not_quantifiable", "6.2", "6.3"),
                          ("6_3_caliber_notes", "6.3", "6.4")):
        m = re.search(r"^###\s*" + re.escape(sec) + r"\b(.*?)(?=^###\s" + re.escape(nxt) + r"|\Z)",
                      aqidx, re.S | re.M)
        if not m:
            print("[RC3] AQG 00-index §%s 标题未找到 —— 检查器正则坏了" % sec)
            sys.exit(3)
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*`(C|N|E)\d+`", s):
                n += 1
        chk("AQG §%s 表 %d 行 = 声明 %s" % (sec, n, aqrc.get(key)), n == aqrc.get(key))

    # Lutz 层登记表声明 vs 行数（references/lutz/00-index.md）
    lzidx = read(os.path.join(root, "references", "lutz", "00-index.md"))
    lzrc = d.get("lutz_layer", {}).get("registry_counts", {})
    for key, sec, nxt in (("6_2_formula_not_quantifiable", "6.2", "6.3"),
                          ("6_3_same_fact_two_numbers", "6.3", "6.4"),
                          ("6_4_broken_values", "6.4", "6.5")):
        m = re.search(r"^###\s*" + re.escape(sec) + r"\b(.*?)(?=^###\s" + re.escape(nxt) + r"|\Z)",
                      lzidx, re.S | re.M)
        if not m:
            print("[RC3] Lutz 00-index §%s 标题未找到 —— 检查器正则坏了" % sec)
            sys.exit(3)
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*`(C|N|E)\d+`", s):
                n += 1
        chk("Lutz §%s 表 %d 行 = 声明 %s" % (sec, n, lzrc.get(key)), n == lzrc.get(key))

    # 国标层登记表声明 vs 行数（references/gb29332/00-index.md）
    gbidx = read(os.path.join(root, "references", "gb29332", "00-index.md"))
    gbrc = d.get("gb_layer", {}).get("registry_counts", {})
    for key, sec, nxt in (("6_2_formula_not_quantifiable", "6.2", "6.3"),
                          ("6_3_caliber_notes", "6.3", "6.4")):
        m = re.search(r"^###\s*" + re.escape(sec) + r"\b(.*?)(?=^###\s" + re.escape(nxt) + r"|\Z)",
                      gbidx, re.S | re.M)
        if not m:
            print("[RC3] 国标 00-index §%s 标题未找到 —— 检查器正则坏了" % sec)
            sys.exit(3)
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*`(C|N|E)\d+`", s):
                n += 1
        chk("国标 §%s 表 %d 行 = 声明 %s" % (sec, n, gbrc.get(key)), n == gbrc.get(key))

    # ---------- 3) 「声明 N 项」vs 实际表格行数 ----------
    print("=" * 60)
    print("③ 三表声明 vs 表格行数")
    print("=" * 60)
    idx = read(os.path.join(root, "references", "baliga", "00-index.md"))

    def rows_of(sec):
        """sec 形如 '6.2'；标题是 ###；截到下一个 ##/### 为止。"""
        pat = r"^#{3,4}\s*" + re.escape(sec) + r"\b(.*?)(?=^#{2,4}\s|\Z)"
        m = re.search(pat, idx, re.S | re.M)
        if not m:
            return -1
        n = 0
        for ln in m.group(1).split("\n"):
            s = ln.strip()
            if not s.startswith("|"):
                continue
            if re.match(r"^\|[\s:\-|]+\|$", s):
                continue
            if re.match(r"^\|\s*(项|式号|式|#|编号|类|号|符号|位置)\s*\|", s):
                continue
            n += 1
        return n

    rc = d.get("baliga_layer", {}).get("registry_counts", {})
    for key, sec in (("6_2_formula_not_quantifiable", "6.2"),
                     ("6_3_same_fact_two_numbers", "6.3"),
                     ("6_4_broken_values", "6.4")):
        want = rc.get(key)
        got = rows_of(sec)
        if got == -1:
            print("[RC3] §%s 标题未找到 —— 检查器正则坏了，不是内容问题" % sec)
            sys.exit(3)
        chk("§%s 表 %d 行 = 声明 %s" % (sec, got, want), got == want)

    m62 = re.search(r"^#{3,4}\s*6\.2\b.*$", idx, re.M)
    chk("§6.2 标题无「2 项」残留（历史数错）",
        bool(m62) and "2 项" not in m62.group(0))
    chk("§6.5 核销表存在", "### 6.5" in idx)

    # ---------- 4) 脚本子命令与文档表述 ----------
    print("=" * 60)
    print("④ 子命令清单 vs 文档表述")
    print("=" * 60)
    subs = d.get("assets", {}).get("budget_subcommands", [])
    skill = read(os.path.join(root, "SKILL.md"))
    readme = read(os.path.join(root, "scripts", "README.md"))

    chk("meta 子命令 %d 项" % len(subs), len(subs) >= 1, str(len(subs)))
    chk("SKILL.md 写「%d 个子命令」" % len(subs), "%d 个子命令" % len(subs) in skill)
    for s in subs:
        if not ("`%s`" % s in skill or s in skill):
            chk("SKILL.md 提到子命令 %s" % s, False)
    chk("meta 含 budget_gate_map", "budget_gate_map" in d.get("assets", {}))

    print("=" * 60)
    if fails:
        print("[判决] FAIL %d 项：%s" % (len(fails), " / ".join(fails)))
        return 1
    print("[判决] PASS 全绿（登记一致、计数一致、声明=行数）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

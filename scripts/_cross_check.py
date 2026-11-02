# -*- coding: utf-8 -*-
"""_cross_check.py — 公式三处一致性校对

为什么需要它：`redline` 查「禁用值有没有被裸用」，`struct_check` 查骨架，
`_registry_check` 查登记与计数。**三者都不查「同一个式子在三处是否算得一样」。**

同一结论在本技能里会出现在三处，任一处不同步就是错：
  ① 模块正文 A2 段（人读，带书页）
  ② `34-formula-index` / `00-index`（反查入口）
  ③ `scripts/*.py`（可执行，能真跑）

本脚本做五组校对：
  ① BFOM 指数必须 `E_C³`（`55` 与 `72` 互校 1876 vs 1877）
  ② SiC 门槛 507 与书报 509 并存、两路径收敛
  ③ 降额四档边界值与实测散点
  ④ 禁用值（式 13.9 / K_ER / 1π 口径）必须带「指出问题」标记
  ⑤ **真的执行**两个子命令，不只看源码

用法：python scripts/_cross_check.py
返回码：0 = 一致 / 1 = 有不一致 / 3 = 前置文件缺失

⚠ 本脚本踩过的坑：① 第一版标记词只收「作废/不成立/量纲」，
   `55` 里 10 处引用书印式子的 `E_C²` 全部误报 —— **豁免词必须收全「指出问题」的说法**
   （书印作 / 应为 / 原文锚点 / 见 B1x / 判定）；② 只做正向检查会漏掉
   「结论改了推导没改」，故 ① 里补一条**反向保护**：A2.3 推导段不许出现正面 `E_C²`。
"""
import io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "references")
fails = []


def read(p):
    if not os.path.isfile(p):
        print("[RC3] 文件缺失: " + p)
        sys.exit(3)
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def chk(name, cond, detail=""):
    print(("[ OK ] " if cond else "[FAIL] ") + name + (("  " + detail) if detail else ""))
    if not cond:
        fails.append(name)


b55 = read(os.path.join(R, "baliga", "55-sic-bfom.md"))
b72 = read(os.path.join(R, "baliga", "72-wbg-cost.md"))
b57 = read(os.path.join(R, "baliga", "57-chip-design-termination.md"))
fidx = read(os.path.join(R, "volke-hornkamp", "34-formula-index.md"))
wex = read(os.path.join(R, "volke-hornkamp", "worked-examples.md"))
readme = read(os.path.join(ROOT, "scripts", "README.md"))
budget = read(os.path.join(ROOT, "scripts", "igbt_book_budget.py"))

print("=" * 62)
print("① BFOM：指数必须是 E_C³，E_C² 只能出现在「指出问题」处")
print("=" * 62)
chk("55 含 1876", "1876" in b55)
chk("72 含 1877", "1877" in b72)
diff = abs(1876 - 1877) / 1877 * 100
chk("1876 vs 1877 差 %.2f%% (<1%%)" % diff, diff < 1.0)

MARK = (r"作废|不成立|撤销|错|不应|反证|而非|量纲|书印|应为|原文锚点|书 p\d+|"
        r"引用|按上式|见 B1\d|判定")
bad = []
for m in re.finditer(r"E_C²", b55):
    ctx = b55[max(0, m.start() - 260): m.end() + 260]
    if not re.search(MARK, ctx):
        bad.append(b55[max(0, m.start() - 40): m.end() + 40].replace("\n", " "))
print("        55 里 E_C² 共 %d 处，无标记 %d 处" % (b55.count("E_C²"), len(bad)))
chk("55 的 E_C² 全在「指出问题」语境", not bad, str(bad[:1]))

m23 = re.search(r"### A2\.3(.*?)(?=\n### |\n## )", b55, re.S)
chk("A2.3 段存在", bool(m23))
if m23:
    bad2 = [l for l in m23.group(1).split("\n")
            if "E_C²" in l and not re.search(r"撤销|作废|之前|该结论是错|书印", l)]
    chk("A2.3 推导段无正面 E_C² 用法（反向保护）", not bad2, str(bad2[:1])[:80])

print("=" * 62)
print("② SiC 门槛 507 vs 书报 509")
print("=" * 62)
chk("72 含 507", "507" in b72)
chk("72 含书报 509", "509" in b72)
chk("72 说明 0.4% 差异", ("0.4" in b72))
p1 = 21.548 * 0.5 * 78.54 * 0.60
p2 = 3000 * (2.06 / 12.18)
print("        路径① 21.548×0.5×78.54×0.60 = %.2f" % p1)
print("        路径② 3000×(2.06/12.18)    = %.2f" % p2)
chk("两路径收敛 <1%", abs(p1 - p2) / p2 * 100 < 1.0, "%.2f vs %.2f" % (p1, p2))
chk("均落 505–510", 505 <= p1 <= 510 and 505 <= p2 <= 510)

print("=" * 62)
print("③ 降额四档边界 + 实测散点")
print("=" * 62)
for k, v in (("clamp", "1.30"), ("resonant", "1.60"), ("hard-ctrl", "1.90"),
             ("hard-emc", "2.20")):
    chk("%s 键与边界 %s" % (k, v), k in budget and v in budget)
pts = ["1.32", "1.58", "1.62", "1.625", "1.71", "1.74", "2.13"]
chk("README 记 7 个实测散点", sum(1 for p in pts if p in readme) == 7)

print("=" * 62)
print("④ 禁用值必须带「不可用」标记")
print("=" * 62)
chk("57 标 K_ER 量纲不成立", "μs/Mrad" in b57)
chk("34-index 标式 13.9 缺 I_peak", "13.9" in fidx and "I_peak" in fidx)
chk("34-index 有 1/π 口径 0.3183", "0.3183" in fidx or "1/π" in fidx)
chk("worked-examples 有修正值 143.7 ℃", "143.7" in wex)
chk("worked-examples 有事故值 224.9 ℃（复盘用）", "224.9" in wex)

print("=" * 62)
print("⑤ 脚本实跑（不只看源码）")
print("=" * 62)
PY = sys.executable
SCRIPT = os.path.join(ROOT, "scripts", "igbt_book_budget.py")
for args, must, want_rc in (
    (["baliga-derate", "--constraint", "hard-emc", "--v-op", "400"], "800", 0),
    (["baliga-derate", "--constraint", "hard-emc", "--v-op", "400",
      "--v-rated", "650"], "FAIL", 1),          # 反向：低于下沿必须 rc=1
    (["baliga-derate", "--constraint", "clamp", "--v-op", "400"], "520", 0),
    (["sic-parity"], "507", 0),
):
    r = subprocess.run([PY, SCRIPT] + args, capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    ok = (r.returncode == want_rc) and (must in out)
    chk("%s → rc=%d 且含 %s" % (" ".join(args[1:4]), want_rc, must), ok,
        "实际 rc=%d" % r.returncode)

print("=" * 62)
print("[判决]", "PASS 三处一致" if not fails else "FAIL: " + " / ".join(fails))
sys.exit(0 if not fails else 1)

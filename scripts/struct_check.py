# -*- coding: utf-8 -*-
"""结构检查：编号连续 / 空章节 / 围栏配对 / 退格符污染

红线正则（igbt_book_ledger.py redline）只管**内容**，不管**骨架**。
两者都要跑：内容对但骨架断了（标题被吞、编号跳号）一样是事故。

用法：
    python scripts/struct_check.py            # 扫全部 md + meta.json / test-prompts.json
    python scripts/struct_check.py --quiet    # 只报问题

返回码：0 = 干净 / 1 = 有结构问题
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

H2 = re.compile(r"^## +(\d+)\.(?![0-9])(.+)$")
# 允许带字母后缀：`### 12.2b xxx` / `### 12.2c xxx` 属于同一小节下的细分，不算跳号
H3NUM = re.compile(r"^### +(\d+)\.(\d+)([a-z]?)(.+)$")
ANY_H = re.compile(r"^(#{1,6}) +(.*)$")


def strip_fences(text):
    """把 ``` 围栏内的内容替换成空行，保留行号对齐（代码里的 # 注释不是标题）。"""
    out = []
    fence = False
    for l in text.split("\n"):
        if l.lstrip().startswith("```"):
            fence = not fence
            out.append("")
            continue
        out.append("" if fence else l)
    return "\n".join(out)


def check_file(path):
    """返回 (problems, info)。problems 为空表示通过。"""
    problems = []
    try:
        raw = io.open(path, encoding="utf-8").read()
    except Exception as e:  # noqa: BLE001
        return [f"读取失败：{e}"], {}

    if "\x08" in raw:
        problems.append("含退格符 \\x08（bash 转义事故）")

    # 围栏必须成对
    fences = sum(1 for l in raw.split("\n") if l.lstrip().startswith("```"))
    if fences % 2 != 0:
        problems.append(f"``` 围栏数为奇数（{fences}），有未闭合代码块")

    scan = strip_fences(raw).split("\n")

    # ① H2 编号连续
    h2nums = []
    for i, l in enumerate(scan):
        m = H2.match(l)
        if m:
            h2nums.append((i + 1, int(m.group(1))))
    for a, b in zip(h2nums, h2nums[1:]):
        if b[1] != a[1] + 1:
            problems.append(f"L{b[0]} 二级标题编号跳号 {a[1]} -> {b[1]}")

    # ② H3 编号连续（父节内）、③ 空章节
    cur_parent = None
    seen = {}
    h_count = 0
    for i, l in enumerate(scan):
        if ANY_H.match(l):
            h_count += 1
        m2 = H2.match(l)
        if m2:
            cur_parent = int(m2.group(1))
            seen = {}
            continue
        m3 = H3NUM.match(l)
        if m3:
            par, sub, suf = int(m3.group(1)), int(m3.group(2)), m3.group(3)
            if cur_parent is not None and par != cur_parent:
                problems.append(f"L{i+1} 三级标题 {par}.{sub} 与父节 {cur_parent} 不符")
            # 带字母后缀（12.2b / 12.2c）是同一小节内的细分：只要求主节号先出现
            if suf:
                if par in seen and seen[par] != sub:
                    problems.append(
                        f"L{i+1} 三级标题后缀 {par}.{sub}{suf} 的主节号 {par}.{sub} 未先出现"
                    )
            else:
                # 注意：模块内节号是「书内真实章号」，与在本文件里出现的先后无关。
                # 例如 `### 6.7` 之后直接跟 `### 6.7.1`，此时 seen[6] 已被 `6.7` 自己设成 7，
                # 子节号 1 必然 ≠ 7+1。这是**同一节的父子关系**，不是跳号。
                # 因此只在「新节号既不等于上一节+1，也不小于等于上一节」时才判跳号；
                # 真正的跳号（6.5 -> 6.9）与错置（6.5 落在 6.7 之后）由「递减」单独判。
                if par in seen:
                    prev = seen[par]
                    if sub > prev + 1:
                        problems.append(
                            f"L{i+1} 三级标题跳号 {par}.{prev} -> {par}.{sub}"
                        )
                    elif sub < prev:
                        problems.append(
                            f"L{i+1} 三级标题号回退（章节错置）{par}.{prev} -> {par}.{sub}"
                        )
                seen[par] = sub
        # 空章节：标题后紧跟另一个标题
        if ANY_H.match(l):
            nxt = scan[i + 1] if i + 1 < len(scan) else ""
            if ANY_H.match(nxt):
                problems.append(f"L{i+1} 空章节（标题后紧跟标题）-> {l[:40]}")

    return problems, {"chars": len(raw), "headings": h_count}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    quiet = "--quiet" in sys.argv

    targets = sorted(ROOT.rglob("*.md"))
    targets += [p for p in (ROOT / "meta.json", ROOT / "test-prompts.json") if p.exists()]

    total_bad = 0
    print("=" * 64)
    for p in targets:
        rel = p.relative_to(ROOT).as_posix()
        if "__pycache__" in rel:
            continue
        if p.suffix == ".json":
            try:
                json.load(io.open(p, encoding="utf-8"))
                info = {"json": "OK"}
                probs = []
            except Exception as e:  # noqa: BLE001
                probs, info = [f"JSON 解析失败：{e}"], {}
        else:
            probs, info = check_file(p)

        if probs:
            total_bad += 1
            print(f"[FAIL] {rel}")
            for x in probs:
                print(f"       - {x}")
        elif not quiet:
            extra = f"  {info.get('chars', '')} 字符 / {info.get('headings', '')} 标题" if "chars" in info else ""
            print(f"[ OK ] {rel}{extra}")

    print("=" * 64)
    if total_bad:
        print(f"[FAIL] {total_bad} / {len(targets)} 个文件有结构问题")
        sys.exit(1)
    print(f"[OK] {len(targets)} 个文件：编号连续、无空章节、围栏成对、无 \\x08")


if __name__ == "__main__":
    main()

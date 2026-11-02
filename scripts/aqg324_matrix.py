#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aqg324_matrix.py — 认证试验矩阵骨架生成器

用途
    按产品类型生成可靠性认证试验矩阵骨架（Markdown / CSV），
    作为搭计划的起点，避免漏项与用错标准。

★ 极重要的边界声明
    本脚本生成的是**骨架**，不是可直接执行的试验计划。
    具体试验条件（温度、电压、循环数、样本量、判据）**必须**以
      - 客户技术规范（最高优先级），以及
      - AQG 324 Release 04.1/2025 正文 / AEC-Q101 Rev E 正文
    为准。本脚本对条件的描述一律标注来源等级，未核实的不给数字。

产品类型
    module_si   硅基 IGBT 功率模组（车规，AQG 324 路线）
    module_sic  碳化硅功率模组（车规，AQG 324 + SiC 附录）
    module_ind  工业/牵引模组（AQG 324 参考 + IEC 60749-34-1 + 客户规范）
    discrete_auto  车规分立 IGBT 单管（AEC-Q101 路线）
    discrete_ind   工业分立 IGBT 单管（IEC 60747-9 + IEC 60749 路线）

用法
    python aqg324_matrix.py --type module_si
    python aqg324_matrix.py --type module_sic --format csv -o matrix.csv
    python aqg324_matrix.py --type discrete_auto
    python aqg324_matrix.py --list
"""

import argparse
import csv
import io
import sys

# 来源等级标记
S_STD = "标准正文"
S_STD_ANNEX = "标准附录"
S_CUST = "客户规范"
S_TODO = "待核（见 06-glossary §4）"


def matrix_module_si():
    rows = [
        # 类, 项目, 验证目的, 关键输出/判据, 来源
        ("QM", "外观检查", "出厂无可见缺陷（零公里防线）", "目检 + 尺寸", S_STD),
        ("QM", "SAM 扫描声学显微", "初始分层/空洞基线", "分层面积与空洞率基线", S_STD),
        ("QM", "初始电参数", "建立退化判定的起点", "VCE(sat)、ICES、IGES、VF", S_STD),
        ("QC", "杂散电感 Lσ", "换流回路电感是否符合设计", "nH", S_STD),
        ("QC", "热阻 Rth / Zth", "热路径是否符合设计（结构函数）", "K/W + 结构函数曲线", S_STD),
        ("QC", "短路耐受", "SCSOA 与 tSC", "tSC（μs）+ 失效模式", S_STD),
        ("QC", "绝缘耐压", "端子-底板、端子间绝缘", "耐压值 + 漏电", S_STD),
        ("QC", "局部放电 PD", "高压绝缘系统的局部缺陷", "pC 水平（1700V+ 必做）", S_STD),
        ("QE", "热冲击 / 温度循环", "大面积焊层、陶瓷、端子焊点", "ΔTc、循环数；SAM 分层", S_STD),
        ("QE", "振动", "端子与键合线的机械疲劳", "随机振动谱 + 电参数", S_STD),
        ("QE", "机械冲击", "安装与运输冲击", "g 值与方向", S_STD),
        ("QE", "湿热（非偏置）", "灌封与界面吸湿", "温湿度 + 时长", S_STD),
        ("QL", "PCsec（秒级功率循环）", "芯片附近连接（键合线、芯片焊层）", "ΔTj、Tj,mean、ton、Nf", S_STD),
        ("QL", "PCmin（分钟级功率循环）", "基板/底板焊层", "ΔTc、ton、Nf", S_STD),
        ("QL", "HTRB", "高温反偏：终端与钝化", "ICES 漂移", S_STD),
        ("QL", "HTGB", "高温栅偏：栅氧", "IGES / VGE(th) 漂移", S_STD),
        ("QL", "H3TRB", "高温高湿反偏：湿度+电场+离子迁移", "漏电与参数漂移", S_STD),
        ("QL", "HV-H3TRB", "高压变体：专攻高压模组湿度鲁棒性（光伏/风电）", "接近额定的反偏电压下漏电", S_STD),
        ("QL", "EOL 判定", "区分失效机理", "VCE(sat)↑约5% 或 Rth↑约20%（须核正文）", S_TODO),
    ]
    return rows


def matrix_module_sic():
    rows = matrix_module_si()
    extra = [
        ("QL", "DGS 动态栅极应力", "SiC 栅氧在开关栅压波动下的退化", "Vth / RDS(on) 漂移", S_STD_ANNEX),
        ("QL", "DRB 动态反偏", "湿环境 + 动态偏置下的退化（>25kHz 开关）", "漏电与 Vth 漂移", S_STD_ANNEX),
        ("QL", "dyn. H3TRB 动态 H3TRB", "动态偏置下的湿热退化", "漏电与参数漂移", S_STD_ANNEX),
        ("—", "Delta Qualification Matrix", "变更差异认证（改版不必全项重做）", "变更影响评估表", S_STD_ANNEX),
    ]
    return rows + extra


def matrix_module_ind():
    rows = [
        ("QM", "外观 + SAM + 初始电参数", "零公里与基线", "同车规 QM", S_STD),
        ("QC", "Rth / 结构函数", "热路径验证", "K/W", S_STD),
        ("QC", "绝缘耐压 / PD", "绝缘系统（牵引/电网必做 PD）", "耐压 + pC", S_STD),
        ("QC", "短路耐受", "保护配合预算", "tSC", S_STD),
        ("QE", "温度循环 TC", "焊层与陶瓷", "ΔTc、循环数", S_STD),
        ("QE", "振动 / 冲击", "牵引与工业环境", "按客户规范谱", S_CUST),
        ("QL", "功率循环 PC（IEC 60749-34-1:2025 方法）", "模组 PC 的国际标准方法", "ΔTj、ton、Nf", S_STD),
        ("QL", "HTRB / HTGB", "终端与栅氧", "漏电漂移", S_STD),
        ("QL", "H3TRB", "湿热", "漏电漂移", S_STD),
        ("QL", "高压特殊项（>2.5kV）", "宇宙射线/大气中子、PD、绝缘配合", "海拔/中子通量核算", S_STD),
        ("—", "注：IEC 60749-34-1:2025 明确允许按 AQG 324 偏离", "非车规客户可用 IEC 方法避免过度认证", "—", S_STD),
    ]
    return rows


def matrix_discrete_auto():
    rows = [
        ("A", "PC 预处理（Pre-conditioning）", "MSL 与回流模拟", "按 MSL 等级", S_STD),
        ("A", "HAST / UHAST / AC（择一）", "加速湿热", "130C/85%RH 等", S_STD),
        ("A", "H3TRB", "高温高湿反偏", "85C/85%RH + 反偏", S_STD),
        ("A", "TC 温度循环", "热机械疲劳（焊点/框架）", "-55~150C 等", S_STD),
        ("A", "IOL 间歇工作寿命（或 PTC 替代）", "开关应力退化；ΔTj>=100C", "ton=toff=2min 等", S_STD),
        ("A", "DPA / 封装完整性系列", "PD、WBP、WBS、DS 等", "按标准分组", S_STD),
        ("B", "HTGB / HTSL", "栅氧与漂移区退化", "150C 偏置 1000h", S_STD),
        ("B", "HTRB", "终端与钝化", "高温反偏", S_STD),
        ("B", "PC / PTC", "焊层与键合线疲劳", "ΔTj>=100C", S_STD),
        ("C", "介电完整性 DI（MOS/IGBT 专属）", "栅介质完整性", "按标准", S_STD),
        ("C", "UIS 无钳位电感开关（MOS/IGBT 专属）", "雪崩耐量", "EAS", S_STD),
        ("C", "ESD HBM / CDM", "抗静电", "kV 等级", S_STD),
        ("E", "可焊性 / 端子强度等", "装配适用性", "按标准", S_STD),
    ]
    return rows


def matrix_discrete_ind():
    rows = [
        ("产品规范", "IEC 60747-9:2019（单管）", "术语、额定值、特性、测量方法", "静态与动态参数定义", S_STD),
        ("中文规范", "GB/T 29332-2012（等同采用 IEC 60747-9:2007）", "国内单管产品规范", "注意采标版本滞后", S_STD),
        ("行业规范", "JB/T 8951.1-2025 单管", "机械行业单管产品规范", "国内项目可引用", S_STD),
        ("环境试验", "IEC 60749 系列", "机械与气候试验方法", "按具体分册", S_STD),
        ("寿命", "IEC 60749-34（分立器件功率循环）", "功率循环基础方法", "版号待核", S_TODO),
        ("热", "JESD51-1 电学法", "Rth/Zth 测量与结构函数", "K factor 标定", S_STD),
        ("可靠性", "客户规范（最优先）", "工业客户常自定矩阵", "以客户为准", S_CUST),
    ]
    return rows


BUILDERS = {
    "module_si": ("硅基 IGBT 功率模组 · 车规（AQG 324 Release 04.1/2025 路线）", matrix_module_si),
    "module_sic": ("SiC 功率模组 · 车规（AQG 324 + SiC 附录）", matrix_module_sic),
    "module_ind": ("工业/牵引 IGBT 模组（IEC 60749-34-1:2025 + 客户规范）", matrix_module_ind),
    "discrete_auto": ("车规分立 IGBT 单管（AEC-Q101 Rev E 路线）", matrix_discrete_auto),
    "discrete_ind": ("工业分立 IGBT 单管（IEC 60747-9:2019 路线）", matrix_discrete_ind),
}

FOOTER = """
## 使用纪律

1. **客户规范 > 行业标准 > 通用做法。** 车厂常把 AQG 324 当厂规并加严，冲突时以客户规范为准。
2. **本表是骨架。** 具体条件（温度/电压/循环数/样本量/判据）必须逐项回标准正文核对。
3. **不要混标准**：AEC-Q101 只管分立器件；AQG 324 管模组；两者互补不替代。
4. **不要用 AQG 325**：该标准不存在。WBG 通过 AQG 324 的附录覆盖。
5. **PC 必须分档**：秒级（芯片附近连接）与分钟级（基板/底板焊层）是两种机理，只做一种等于只验证一半。
6. **EOL 判据要同时记录**：通态压降上升指向键合线，热阻上升指向焊层——只报"失效了"没有工程价值。
7. 变更管理优先用 **Delta Qualification Matrix**，不必每次全项重做。
"""


def render_md(title, rows):
    buf = io.StringIO()
    buf.write(f"# {title}\n\n")
    buf.write("> 骨架由 `aqg324_matrix.py` 生成于工程规划阶段。条件栏为空或标「标准正文」者，"
              "须回标准原文填写。\n\n")
    buf.write("| 类 | 试验项目 | 验证目的 | 关键输出 / 判据 | 来源等级 |\n")
    buf.write("|---|---|---|---|---|\n")
    for cat, item, purpose, crit, src in rows:
        buf.write(f"| {cat} | {item} | {purpose} | {crit} | {src} |\n")
    buf.write(FOOTER)
    return buf.getvalue()


def render_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["类别", "试验项目", "验证目的", "关键输出/判据", "来源等级",
                "具体条件(待填)", "样本量(待填)", "判据(待填)", "责任人(待填)", "状态"])
    for cat, item, purpose, crit, src in rows:
        w.writerow([cat, item, purpose, crit, src, "", "", "", "", "TODO"])
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(
        description="IGBT 认证试验矩阵骨架生成器（骨架，非可执行计划）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--type", choices=sorted(BUILDERS.keys()), help="产品类型")
    ap.add_argument("--format", choices=["md", "csv"], default="md")
    ap.add_argument("-o", "--output", help="输出文件路径（默认打印到 stdout）")
    ap.add_argument("--list", action="store_true", help="列出支持的产品类型")
    args = ap.parse_args()

    if args.list or not args.type:
        print("支持的产品类型：")
        for k, (title, _) in BUILDERS.items():
            print(f"  {k:<16} {title}")
        return 0

    title, builder = BUILDERS[args.type]
    rows = builder()
    text = render_md(title, rows) if args.format == "md" else render_csv(rows)

    if args.output:
        with open(args.output, "w", encoding="utf-8-sig" if args.format == "csv" else "utf-8") as f:
            f.write(text)
        print(f"已写入: {args.output}  ({len(rows)} 项)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

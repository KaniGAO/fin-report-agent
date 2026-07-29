"""端到端流水线轻量验证：样例解析 → 匹配 → 回填 → 校验输出"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from docx import Document

from app.core.filler import analyze, fill_docx

SAMPLES = BASE / "samples"


def run():
    docx_path = SAMPLES / "template.docx"
    excel_paths = [SAMPLES / f"{n}.xlsx" for n in ("资产负债表", "利润表", "现金流量表")]

    reports, fill_plan, warnings = analyze(docx_path, excel_paths)
    assert not warnings, warnings
    assert len(reports) == 3, f"应识别 3 张表，实际 {len(reports)}"

    types = {r.statement_type for r in reports}
    assert types == {"资产负债表", "利润表", "现金流量表"}, types

    for r in reports:
        assert r.year_columns == ["2023", "2024"], (r.statement_type, r.year_columns)
        print(f"{r.statement_type}: matched={r.matched_count} unmatched={r.unmatched_count} "
              f"source={r.source_file}")
        # 每张表恰好 1 个模板独有项目应留空
        assert r.unmatched_count == 1, [i.docx_item for i in r.items if i.status == "unmatched"]
        for it in r.items:
            if it.status == "unmatched":
                print(f"  留空: {it.docx_item}")

    # 回填并校验关键数值
    out = SAMPLES / "filled.docx"
    fill_docx(docx_path, fill_plan, out)
    doc = Document(str(out))

    def cell_of(t_idx, item, col):
        table = doc.tables[t_idx]
        for row in table.rows:
            if row.cells[0].text.strip() == item:
                return row.cells[col].text.strip()
        raise AssertionError(f"未找到项目 {item}")

    # 资产负债表：货币资金 2023=12000 2024=15600（Excel 名「货 币 资 金」）
    assert cell_of(0, "货币资金", 1) == "12000", cell_of(0, "货币资金", 1)
    assert cell_of(0, "货币资金", 2) == "15600"
    # 同义词：所有者权益合计 ← 股东权益合计
    assert cell_of(0, "所有者权益合计", 2) == "35400"
    # 缺失项留空
    assert cell_of(0, "递延所得税资产", 1) == ""
    # 利润表：营业收入 ← 一、营业总收入
    assert cell_of(1, "营业收入", 1) == "45000"
    assert cell_of(1, "投资收益", 2) == ""
    # 现金流量表：负数保留
    assert cell_of(2, "投资活动产生的现金流量净额", 1) == "-3500"
    assert cell_of(2, "汇率变动对现金的影响", 1) == ""

    print(f"\ntest_pipeline: ALL PASS，输出 {out}")


if __name__ == "__main__":
    run()

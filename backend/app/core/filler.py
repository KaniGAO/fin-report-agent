"""匹配 + 回填：生成匹配报告并将 Excel 数值写回 Word 表格"""
from __future__ import annotations

from pathlib import Path

from ..schemas import ItemMatch, TableMatch
from .docx_parser import DocxTable, parse_docx
from .excel_parser import ExcelStatement, parse_excel
from .matcher import match_item
from .units import convert_value


def _pick_statement(
    dt: DocxTable, statements: list[ExcelStatement]
) -> ExcelStatement | None:
    """为 Word 表选择数据来源：优先同类型报表；同类型多个时选项目重合度最高者"""
    candidates = [s for s in statements if s.statement_type == dt.statement_type]
    if not candidates and dt.statement_type == "未知":
        candidates = statements
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    def overlap(s: ExcelStatement) -> int:
        count = 0
        for name in dt.item_rows.values():
            m, _ = match_item(name, s.items)
            if m:
                count += 1
        return count

    return max(candidates, key=overlap)


def build_matches(
    doc_tables: list[DocxTable], statements: list[ExcelStatement]
) -> tuple[list[TableMatch], dict[tuple[int, int, int], str], list[str]]:
    """
    生成匹配报告与回填指令。
    返回 (报告列表, {(表序号, 行, 列): 要填入的值}, 警告列表)
    """
    reports: list[TableMatch] = []
    fill_plan: dict[tuple[int, int, int], str] = {}
    warnings: list[str] = []

    for dt in doc_tables:
        src = _pick_statement(dt, statements)
        items: list[ItemMatch] = []
        matched = unmatched = 0

        for ri, docx_name in dt.item_rows.items():
            if src is None:
                items.append(ItemMatch(docx_item=docx_name, status="unmatched"))
                unmatched += 1
                continue

            excel_name, score = match_item(docx_name, src.items)
            if excel_name is None:
                items.append(
                    ItemMatch(docx_item=docx_name, confidence=score, status="unmatched")
                )
                unmatched += 1
                continue

            values: dict[str, str | None] = {}
            year_values = src.data[excel_name]
            for ci, year in dt.year_cols.items():
                v = year_values.get(year)
                values[year] = v
                if v is not None:
                    # 单位换算：来源单位(src.unit) → 目标单位(dt.unit)
                    converted = convert_value(v, src.unit, dt.unit)
                    if converted != v:
                        src_u = src.unit or "未知"
                        dt_u = dt.unit or "未知"
                        warnings.append(
                            f"[{src.source_file}] 已将「{excel_name}」"
                            f"单位由 {src_u} 换算为 {dt_u}"
                        )
                    fill_plan[(dt.table_index, ri, ci)] = converted
            items.append(
                ItemMatch(
                    docx_item=docx_name,
                    excel_item=excel_name,
                    confidence=score,
                    status="matched",
                    values=values,
                )
            )
            matched += 1

        reports.append(
            TableMatch(
                table_index=dt.table_index,
                statement_type=dt.statement_type,
                year_columns=[dt.year_cols[c] for c in sorted(dt.year_cols)],
                source_file=f"{src.source_file} / {src.sheet_name}" if src else None,
                items=items,
                matched_count=matched,
                unmatched_count=unmatched,
            )
        )

    return reports, fill_plan, warnings


def _set_cell_text(cell, text: str) -> None:
    """只改文本、保留原样式：复用第一个 run 的格式"""
    para = cell.paragraphs[0]
    if para.runs:
        first = para.runs[0]
        first.text = text
        for run in para.runs[1:]:
            run.text = ""
    else:
        para.add_run(text)
    # 清空多余段落文本（保留段落结构以免破坏样式）
    for p in cell.paragraphs[1:]:
        for run in p.runs:
            run.text = ""


def analyze(docx_path: str | Path, excel_paths: list[str | Path]):
    """解析 + 匹配，返回 (报告, 回填指令, 警告)"""
    warnings: list[str] = []
    _, doc_tables = parse_docx(str(docx_path))
    if not doc_tables:
        warnings.append("Word 模板中未找到含年份表头的表格")

    statements: list[ExcelStatement] = []
    for p in excel_paths:
        stmts = parse_excel(p)
        if not stmts:
            warnings.append(f"{Path(p).name} 中未解析到有效报表数据")
        statements.extend(stmts)

    reports, fill_plan, match_warnings = build_matches(doc_tables, statements)
    warnings.extend(match_warnings)
    return reports, fill_plan, warnings


def fill_docx(
    docx_path: str | Path,
    fill_plan: dict[tuple[int, int, int], str],
    out_path: str | Path,
) -> None:
    """按回填指令写入 docx 并保存（不改动任何样式）"""
    doc, _ = parse_docx(str(docx_path))
    for (ti, ri, ci), value in fill_plan.items():
        cell = doc.tables[ti].rows[ri].cells[ci]
        _set_cell_text(cell, str(value))
    doc.save(str(out_path))

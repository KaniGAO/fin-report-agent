"""Word 模板表格解析：识别报表类型、年份列、项目行"""
from __future__ import annotations

from dataclasses import dataclass, field

from docx import Document
from docx.table import Table

from .excel_parser import detect_statement_type, extract_year


@dataclass
class DocxTable:
    table_index: int                     # doc.tables 中的序号
    statement_type: str
    header_row: int                      # 表头行号（表内）
    year_cols: dict[int, str] = field(default_factory=dict)   # {列号: 年份}
    item_rows: dict[int, str] = field(default_factory=dict)   # {行号: 项目名}


def _table_texts(table: Table, max_rows: int = 3) -> list[str]:
    texts = []
    for row in table.rows[:max_rows]:
        for cell in row.cells:
            texts.append(cell.text)
    return texts


def _paragraphs_before(doc: Document, table: Table, n: int = 5) -> list[str]:
    """取表格前面最近的 n 个非空段落文本（用于识别报表类型，如标题「资产负债表」）"""
    texts = []
    for block in doc.element.body:
        if block is table._tbl:
            break
        if block.tag.endswith("}p"):
            t = "".join(node.text or "" for node in block.iter() if node.tag.endswith("}t"))
            if t.strip():
                texts.append(t.strip())
    return texts[-n:]


def parse_docx(path: str) -> tuple[Document, list[DocxTable]]:
    """解析 docx，返回 (Document 对象, 可填写的表格列表)。
    Document 对象保留引用以便后续 filler 直接回填并保存。"""
    doc = Document(path)
    results: list[DocxTable] = []

    for ti, table in enumerate(doc.tables):
        if not table.rows:
            continue

        # 1) 找表头行：前 3 行内年份单元格最多的行
        header_row, year_cols = None, {}
        for ri, row in enumerate(table.rows[:3]):
            cols: dict[int, str] = {}
            for ci, cell in enumerate(row.cells):
                if ci == 0:
                    continue
                y = extract_year(cell.text)
                if y:
                    cols[ci] = y
            if len(cols) > len(year_cols):
                header_row, year_cols = ri, cols
        if header_row is None or not year_cols:
            continue  # 无年份表头的表不处理

        # 2) 报表类型：从最近的段落倒序判断（避免上一章节标题干扰），
        #    仍未知时用表头行文本兜底（不含项目行，避免「未分配利润」误判）
        st_type = "未知"
        for text in reversed(_paragraphs_before(doc, table)):
            st_type = detect_statement_type(text)
            if st_type != "未知":
                break
        if st_type == "未知":
            st_type = detect_statement_type(*_table_texts(table, max_rows=1))

        # 3) 项目行：表头之下、首列非空的行
        item_rows: dict[int, str] = {}
        for ri in range(header_row + 1, len(table.rows)):
            name = table.rows[ri].cells[0].text.strip()
            if name:
                item_rows[ri] = name

        if item_rows:
            results.append(
                DocxTable(
                    table_index=ti,
                    statement_type=st_type,
                    header_row=header_row,
                    year_cols=year_cols,
                    item_rows=item_rows,
                )
            )

    return doc, results

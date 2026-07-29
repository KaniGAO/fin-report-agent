"""API 数据模型（接口契约）"""
from __future__ import annotations

from pydantic import BaseModel


class ItemMatch(BaseModel):
    docx_item: str                     # Word 模板中的项目名
    excel_item: str | None = None      # 匹配到的 Excel 项目名（未匹配为 None）
    confidence: float = 0.0            # 匹配置信度 0-100
    status: str = "unmatched"          # matched | unmatched | skipped(非数据行)
    values: dict[str, str | None] = {} # {年份列标签: 将填入的值}（None 表示留空）


class TableMatch(BaseModel):
    table_index: int                   # 表在 docx 中的序号
    statement_type: str                # 资产负债表 | 利润表 | 现金流量表 | 未知
    year_columns: list[str]            # 识别出的年份列标签（如 "2024"）
    source_file: str | None = None     # 数据来源的 Excel 文件名
    items: list[ItemMatch] = []
    matched_count: int = 0
    unmatched_count: int = 0


class AnalyzeResponse(BaseModel):
    session_id: str                    # 后续 /api/generate 使用
    tables: list[TableMatch]
    warnings: list[str] = []

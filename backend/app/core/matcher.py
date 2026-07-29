"""项目名模糊匹配引擎"""
from __future__ import annotations

from rapidfuzz import fuzz

from ..config import MATCH_THRESHOLD
from .normalize import canonical


def match_item(
    docx_item: str,
    excel_items: list[str],
    threshold: float = MATCH_THRESHOLD,
) -> tuple[str | None, float]:
    """
    在 excel_items 中为 docx_item 找最佳匹配。
    返回 (匹配到的 excel 原始项目名, 置信度 0-100)；未达阈值返回 (None, best_score)。
    """
    key = canonical(docx_item)
    if not key:
        return None, 0.0

    best_name: str | None = None
    best_score = 0.0
    for ex in excel_items:
        ex_key = canonical(ex)
        if not ex_key:
            continue
        if ex_key == key:
            return ex, 100.0
        # ratio 抓整体相似，token_sort 抓词序差异；取较高者
        score = max(fuzz.ratio(key, ex_key), fuzz.token_sort_ratio(key, ex_key))
        # 一方是另一方的完整子串时适当加分（如 "应收账款" vs "应收账款净额" 已由同义词表处理，
        # 这里兜底处理未收录的包含关系，但要求长度接近，避免 "资产" 误配 "资产总计"）
        if key in ex_key or ex_key in key:
            shorter, longer = sorted((len(key), len(ex_key)))
            if longer > 0 and shorter / longer >= 0.6:
                score = max(score, 90.0)
        if score > best_score:
            best_score = score
            best_name = ex

    if best_score >= threshold:
        return best_name, round(best_score, 1)
    return None, round(best_score, 1)

"""单位识别与换算：统一换算到「元」基准后再转换到目标单位

财务数据常见于不同量级（元 / 千元 / 万元 / 百万元 / 亿元 / 千亿元）。
本模块解决两类问题：
  1) 从文本（"单位：亿元"、"报表（万元）"）中识别报表使用的单位；
  2) 将 Excel 来源数值按来源单位换算到 Word 模板的目标单位后再回填，
     避免「模板标亿元、填进去却是万元数字」的错位。
"""
from __future__ import annotations

import re

# 单位 -> 与「元」的换算系数（基准单位）
_UNIT_FACTORS: dict[str, float] = {
    "元": 1.0,
    "千元": 1_000.0,
    "万元": 10_000.0,
    "百万元": 1_000_000.0,
    "亿元": 100_000_000.0,
    "千亿元": 100_000_000_000.0,
}

# 显式「单位：XXX」格式（XXX 可能含「人民币」等前缀）
_UNIT_RE = re.compile(r"单位[：:]\s*([\u4e00-\u9fff]+?元)")

# 非数值占位符，原样返回不换算
_NON_NUMERIC = {"-", "—", "—", "N/A", "NA", "无", "不适用", "不"}


def _unit_in_text(text: str) -> str | None:
    """从一段文本中识别单位名（优先最长匹配）"""
    # 1) 显式「单位：XXX元」
    m = _UNIT_RE.search(text)
    if m:
        token = m.group(1)
        for name in sorted(_UNIT_FACTORS, key=len, reverse=True):
            if name in token:
                return name
    # 2) 退化为直接包含单位词（含「人民币千元」等）
    for name in sorted(_UNIT_FACTORS, key=len, reverse=True):
        if name in text:
            return name
    return None


def normalize_unit(*texts: str) -> str | None:
    """从若干文本片段中识别单位，识别不到返回 None。

    优先级：先匹配含「单位」字样的片段，再扫描全部片段。
    """
    # 优先扫描显式单位片段
    for t in texts:
        if t and "单位" in t:
            u = _unit_in_text(str(t))
            if u:
                return u
    for t in texts:
        u = _unit_in_text(str(t))
        if u:
            return u
    return None


def convert_value(value_str: str, from_unit: str | None, to_unit: str | None) -> str:
    """将数值字符串从 from_unit 换算到 to_unit。

    - from_unit / to_unit 任一为 None（未能识别）时不换算，原样返回（保守策略）；
    - 两单位相同则原样返回，保留原始格式；
    - 否则按系数换算，结果保留两位小数并加千分位、去尾随零。
    """
    if from_unit is None or to_unit is None:
        return value_str
    if from_unit == to_unit:
        return value_str
    if from_unit not in _UNIT_FACTORS or to_unit not in _UNIT_FACTORS:
        return value_str

    raw = str(value_str).replace(",", "").replace("，", "").strip()
    if raw in _NON_NUMERIC or raw == "":
        return value_str
    try:
        num = float(raw)
    except ValueError:
        return value_str

    base = num * _UNIT_FACTORS[from_unit]
    result = base / _UNIT_FACTORS[to_unit]
    s = f"{result:,.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s

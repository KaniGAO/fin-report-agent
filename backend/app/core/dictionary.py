"""三大财务报表项目名中英对照词典（可按需扩充）

结构：中文标准名 -> 英文别名列表。
构建 EN_TO_ZH（英文归一化键 -> 中文标准名）供跨语言匹配使用。
词典缺失的项目名会原样返回 None，由匹配引擎按 fuzzy 兜底。
"""
import re

# 中文标准名 -> 英文别名（覆盖资产负债表 / 利润表 / 现金流量表常见项）
BILINGUAL: dict[str, list[str]] = {
    # ---------------- 资产负债表 ----------------
    "货币资金": ["Cash and Cash Equivalents", "Cash & Cash Equivalents", "Cash", "Cash and Equivalents", "Cash Equivalents"],
    "交易性金融资产": ["Trading Financial Assets", "Trading Securities", "Financial Assets Held for Trading"],
    "应收票据": ["Notes Receivable"],
    "应收账款": ["Accounts Receivable", "Trade Receivables", "Receivables"],
    "应收账款净额": ["Accounts Receivable, net", "Accounts Receivable, Net", "Trade Receivables, net"],
    "预付款项": ["Prepayments", "Prepaid Expenses"],
    "应收利息": ["Interest Receivable"],
    "应收股利": ["Dividends Receivable"],
    "其他应收款": ["Other Receivables"],
    "存货": ["Inventories", "Inventory"],
    "存货净额": ["Inventories, net", "Inventory, net"],
    "一年内到期的非流动资产": ["Non-current Assets Due within One Year", "Current Portion of Non-current Assets"],
    "其他流动资产": ["Other Current Assets"],
    "流动资产合计": ["Total Current Assets"],
    "可供出售金融资产": ["Available-for-sale Financial Assets", "Available for Sale Financial Assets"],
    "持有至到期投资": ["Held-to-maturity Investments"],
    "长期应收款": ["Long-term Receivables", "Long-term Receivables, net"],
    "长期股权投资": ["Long-term Equity Investments", "Long-term Equity Investment"],
    "投资性房地产": ["Investment Property"],
    "固定资产": ["Fixed Assets", "Property Plant and Equipment", "Property, Plant and Equipment", "PP&E"],
    "固定资产净额": ["Fixed Assets, net", "Property, Plant and Equipment, net"],
    "在建工程": ["Construction in Progress"],
    "工程物资": ["Construction Materials"],
    "固定资产清理": ["Disposal of Fixed Assets", "Fixed Assets Pending Disposal"],
    "生产性生物资产": ["Productive Biological Assets"],
    "油气资产": ["Oil and Gas Assets"],
    "无形资产": ["Intangible Assets", "Intangible Assets, net"],
    "开发支出": ["Development Expenditure", "Capitalized Development Expenditures"],
    "商誉": ["Goodwill"],
    "长期待摊费用": ["Long-term Deferred Expenses", "Long-term Prepaid Expenses"],
    "递延所得税资产": ["Deferred Tax Assets"],
    "其他非流动资产": ["Other Non-current Assets"],
    "非流动资产合计": ["Total Non-current Assets"],
    "资产总计": ["Total Assets"],
    "短期借款": ["Short-term Borrowings", "Short-term Loans", "Short-term Debt"],
    "交易性金融负债": ["Trading Financial Liabilities"],
    "应付票据": ["Notes Payable"],
    "应付账款": ["Accounts Payable", "Trade Payables", "Payables"],
    "预收款项": ["Advances from Customers", "Unearned Revenue", "Contract Liabilities"],
    "应付职工薪酬": ["Employee Benefits Payable", "Accrued Payroll"],
    "应交税费": ["Taxes Payable", "Taxes and Surcharges Payable"],
    "应付利息": ["Interest Payable"],
    "应付股利": ["Dividends Payable"],
    "其他应付款": ["Other Payables"],
    "一年内到期的非流动负债": ["Non-current Liabilities Due within One Year", "Current Portion of Non-current Liabilities"],
    "其他流动负债": ["Other Current Liabilities"],
    "流动负债合计": ["Total Current Liabilities"],
    "长期借款": ["Long-term Borrowings", "Long-term Loans", "Long-term Debt"],
    "应付债券": ["Bonds Payable"],
    "长期应付款": ["Long-term Payables", "Long-term Accounts Payable"],
    "专项应付款": ["Special Payables"],
    "预计负债": ["Estimated Liabilities", "Provisions", "Provisions for Liabilities"],
    "递延所得税负债": ["Deferred Tax Liabilities"],
    "其他非流动负债": ["Other Non-current Liabilities"],
    "非流动负债合计": ["Total Non-current Liabilities"],
    "负债合计": ["Total Liabilities"],
    "实收资本": ["Share Capital", "Paid-in Capital", "Capital Stock", "Registered Capital"],
    "资本公积": ["Capital Reserve", "Additional Paid-in Capital", "Capital Surplus"],
    "减：库存股": ["Treasury Stock", "Less: Treasury Stock"],
    "盈余公积": ["Surplus Reserve", "Surplus Reserve Fund", "Statutory Surplus Reserve"],
    "未分配利润": ["Undistributed Profit", "Retained Earnings", "Retained Profit"],
    "所有者权益合计": ["Total Owners' Equity", "Total Equity", "Total Shareholders' Equity", "Total Equity and Reserves"],
    "负债和所有者权益总计": ["Total Liabilities and Owners' Equity", "Total Liabilities and Equity", "Total Liabilities and Shareholders' Equity"],

    # ---------------- 利润表 ----------------
    "营业收入": ["Operating Revenue", "Revenue", "Sales", "Net Sales", "Total Operating Revenue"],
    "营业成本": ["Operating Cost", "Cost of Sales", "Cost of Goods Sold", "COGS"],
    "税金及附加": ["Taxes and Surcharges", "Business Taxes and Surcharges", "Taxes and Attachments"],
    "销售费用": ["Selling Expenses", "Selling and Distribution Expenses"],
    "管理费用": ["Administrative Expenses", "General and Administrative Expenses"],
    "研发费用": ["Research and Development Expenses", "R&D Expenses", "Research and Development Costs"],
    "财务费用": ["Finance Expenses", "Financial Expenses"],
    "资产减值损失": ["Asset Impairment Loss", "Impairment Losses of Assets"],
    "公允价值变动收益": ["Gains from Changes in Fair Value", "Gain on Fair Value Change", "Changes in Fair Value, Gain"],
    "投资收益": ["Investment Income", "Income from Investments"],
    "对联营企业和合营企业的投资收益": ["Investment Income from Associates and Joint Ventures"],
    "营业利润": ["Operating Profit", "Operating Income"],
    "营业外收入": ["Non-operating Income", "Non-operating Revenue"],
    "营业外支出": ["Non-operating Expenses", "Non-operating Outlays"],
    "利润总额": ["Total Profit", "Profit Before Tax", "Income Before Tax"],
    "所得税费用": ["Income Tax Expense", "Income Tax", "Taxation"],
    "净利润": ["Net Profit", "Net Income", "Net Profit (Net Loss)"],
    "归属于母公司所有者的净利润": ["Net Profit Attributable to Owners of the Parent", "Net Income Attributable to the Parent"],
    "少数股东损益": ["Minority Interest", "Profit Attributable to Minority Interests", "Minority Interests in Profit"],
    "基本每股收益": ["Basic Earnings per Share", "Basic EPS"],
    "稀释每股收益": ["Diluted Earnings per Share", "Diluted EPS"],

    # ---------------- 现金流量表 ----------------
    "销售商品、提供劳务收到的现金": ["Cash Received from Sales of Goods or Rendering of Services"],
    "收到的税费返还": ["Refunds of Taxes Received", "Tax Rebates Received"],
    "收到其他与经营活动有关的现金": ["Other Cash Received Relating to Operating Activities"],
    "经营活动现金流入小计": ["Sub-total of Cash Inflows from Operating Activities"],
    "购买商品、接受劳务支付的现金": ["Cash Paid for Goods and Services", "Cash Paid for Goods or Rendering of Services"],
    "支付给职工以及为职工支付的现金": ["Cash Paid to and for Employees", "Cash Paid to Employees"],
    "支付的各项税费": ["Taxes Paid", "Taxes and Surcharges Paid"],
    "支付其他与经营活动有关的现金": ["Other Cash Paid Relating to Operating Activities"],
    "经营活动现金流出小计": ["Sub-total of Cash Outflows from Operating Activities"],
    "经营活动产生的现金流量净额": ["Net Cash Flow from Operating Activities", "Net Cash Provided by Operating Activities"],
    "收回投资收到的现金": ["Cash Received from Disposal of Investments", "Cash from Disposal of Investments"],
    "取得投资收益收到的现金": ["Cash Received from Investment Income", "Cash Received from Returns on Investments"],
    "处置固定资产、无形资产和其他长期资产收回的现金净额": ["Net Cash Received from Disposal of Fixed Assets, Intangible Assets and Other Long-term Assets"],
    "投资活动现金流入小计": ["Sub-total of Cash Inflows from Investing Activities"],
    "购建固定资产、无形资产和其他长期资产支付的现金": ["Cash Paid to Acquire Fixed Assets, Intangible Assets and Other Long-term Assets"],
    "投资支付的现金": ["Cash Paid for Investments", "Cash Paid to Acquire Investments"],
    "投资活动现金流出小计": ["Sub-total of Cash Outflows from Investing Activities"],
    "投资活动产生的现金流量净额": ["Net Cash Flow from Investing Activities", "Net Cash Used in Investing Activities"],
    "吸收投资收到的现金": ["Cash Received from Absorbing Investments", "Cash from Capital Contributions"],
    "取得借款收到的现金": ["Cash Received from Borrowings", "Cash from Borrowings"],
    "筹资活动现金流入小计": ["Sub-total of Cash Inflows from Financing Activities"],
    "偿还债务支付的现金": ["Cash Paid to Repay Debts", "Cash Repayments of Borrowings"],
    "分配股利、利润或偿付利息支付的现金": ["Cash Paid for Dividends, Profits or Interest", "Cash Paid for Dividends and Interest"],
    "筹资活动现金流出小计": ["Sub-total of Cash Outflows from Financing Activities"],
    "筹资活动产生的现金流量净额": ["Net Cash Flow from Financing Activities", "Net Cash Used in Financing Activities"],
    "现金及现金等价物净增加额": ["Net Increase in Cash and Cash Equivalents", "Net Increase in Cash"],
    "期初现金及现金等价物余额": ["Cash and Cash Equivalents at Beginning of Period", "Cash at Beginning of Period"],
    "期末现金及现金等价物余额": ["Cash and Cash Equivalents at End of Period", "Cash at End of Period", "Cash and Cash Equivalents, End of Period"],
}


# 英文归一化：仅保留字母与数字（统一小写、去除空格与标点）
_EN_NORM = re.compile(r"[^a-z0-9]")


def _norm_en(text: str) -> str:
    return _EN_NORM.sub("", str(text).lower())


# 英文归一化键 -> 中文标准名（首条命中优先）
EN_TO_ZH: dict[str, str] = {}
for _zh, _ens in BILINGUAL.items():
    for _en in _ens:
        _k = _norm_en(_en)
        if _k:
            EN_TO_ZH.setdefault(_k, _zh)


def translate_to_zh(name: str) -> str | None:
    """把英文项目名翻译为中文标准名；非英文或词典未收录返回 None。"""
    if not name or any("\u4e00" <= c <= "\u9fff" for c in name):
        return None
    return EN_TO_ZH.get(_norm_en(name))

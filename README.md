# 财报填表 Agent

本地网页应用：上传公司 Word 财务分析模板 + 最多 3 张 Excel 财务报表（资产负债表 / 利润表 / 现金流量表），
自动按**项目名称（模糊匹配）与年份**把 Excel 数值填入 Word 表格，Excel 中没有的项目**留空不填**，
最后下载填写完成的 .docx（保留模板原有样式）。数据全程本机处理。

## 快速启动

```bash
# 1. 后端（首次需安装依赖）
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 前端（生产模式：构建后由后端统一托管，直接访问 http://127.0.0.1:8000）
cd frontend
npm install
npm run build

# 开发模式（前端热更新，访问 http://localhost:5173，API 自动代理到 8000）
npm run dev
```

## 样例验证

```bash
cd backend
./.venv/bin/python scripts/gen_samples.py     # 生成 samples/template.docx + 3 个 Excel
./.venv/bin/python tests/test_matcher.py      # 匹配引擎单测
./.venv/bin/python tests/test_pipeline.py     # 端到端：解析→匹配→回填→校验，输出 samples/filled.docx
```

样例特意包含：项目顺序打乱、命名差异（`货 币 资 金`、`一、营业总收入`、`股东权益合计`、
`利润总额（亏损总额以-号填列）`）、以及 Excel 中缺失的模板项目（`递延所得税资产`、`投资收益`、
`汇率变动对现金的影响`，应留空）。

## 匹配规则

1. **归一化**：全角转半角、去空白、统一括号、剔除序号（`一、` `(一)`）与噪声（`以-号填列` `（合并）`）
2. **同义词映射**：`营业总收入→营业收入`、`股东权益合计→所有者权益合计` 等，见
   `backend/app/core/normalize.py` 的 `SYNONYMS`，可自行扩充
3. **模糊匹配**：rapidfuzz `ratio` / `token_sort_ratio` 取高者，阈值 85（`backend/app/config.py`）
4. **保守策略**：项目名与年份**同时**对上才填；合并项（如「应收票据及应收账款」）不与单项互配；
   未达阈值标记「留空」，绝不猜数

## 中英互换

两类能力：

1. **项目名中英互译匹配**：模板是中文、Excel 是英文（或反过来）也能自动对上。
   例如 `货币资金 ↔ Cash and Cash Equivalents`、`应收账款 ↔ Accounts Receivable`、`营业收入 ↔ Operating Revenue`、
   `资产总计 ↔ Total Assets`、`经营活动产生的现金流量净额 ↔ Net Cash Flow from Operating Activities` 等。
   - 字典：`backend/app/core/dictionary.py` 的 `BILINGUAL`（中文标准名 → 英文别名），覆盖三大报表常见项，可自行扩充。
   - 原理：`normalize.py` 的 `canonical()` 会先把英文名翻译回中文标准键再比对；未收录的英文不会跨语言误配，
     仍按原有模糊匹配兜底。
2. **界面中英切换**：网页右上角「中 / EN」按钮，一键在中文 / English 之间切换，仅翻译界面文案，
   文件内的真实项目名与年份保持原样。语言偏好存储在 `localStorage`（键 `lang`）。
   - 字典：`frontend/src/i18n.ts`（含 `typeLabel` 把中文报表类型映射为英文展示名）。

## 目录结构

```
backend/
  app/core/       normalize / matcher / excel_parser / docx_parser / filler
  app/api/        /api/analyze  /api/generate/{session_id}
  scripts/        gen_samples.py 样例生成
  tests/          test_matcher.py  test_pipeline.py
frontend/         React 18 + Vite + TS + Tailwind（上传 → 匹配核对单 → 下载）
```

## 使用提示

- Word 模板要求：表格首列为项目名，表头行含 4 位年份（如 `2024`、`2024年度`、`2024/12/31`）
- Excel 要求：行 = 项目、列 = 年份/期间；支持多 sheet，一个 sheet 一张报表
- 报表类型靠标题/Sheet 名关键词识别（资产负债 / 利润·损益 / 现金流量）
- 匹配报告中「留空」项请人工核对，必要时在 `SYNONYMS` 中补充映射后重新分析

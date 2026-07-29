// 界面文案中英字典（仅翻译界面 UI，文件内的真实项目名/年份保持原样）

export type Lang = 'zh' | 'en'

export interface Dict {
  appTitle: string
  tagline: string
  heroTitle: string
  heroDesc: string
  uploadHint1: string
  uploadHint2: string
  docxLabel: string
  excelLabel: string
  maxExcel: string
  dupName: string
  unsupported: string
  notAdded: string
  needDocx: string
  needExcel: string
  analyzeBtn: string
  analyzing: string
  reviewTitle: string
  reviewDesc: string
  backBtn: string
  generateBtn: string
  warnPrefix: string
  doneTitle: string
  doneDesc: string
  downloadAgain: string
  nextOne: string
  footer: string
  steps: Record<'upload' | 'report' | 'done', string>
  sourceFrom: string
  noSource: string
  yearLabel: string
  matchedText: string
  blankText: string
  colTemplate: string
  colExcel: string
  colConfidence: string
  colStatus: string
  statusMatched: string
  statusBlank: string
}

export const i18n: Record<Lang, Dict> = {
  zh: {
    appTitle: '财报填表 Agent',
    tagline: '三表自动回填 · 本地运行',
    heroTitle: '把 Excel 三大报表，按项目与年份填进你的 Word 模板',
    heroDesc:
      '项目顺序不同、命名有出入都能对上；模板里有而报表里没有的项目会留空，绝不猜数。核对匹配结果后，一键下载填写完成的 Word 文档。',
    uploadHint1: '拖入 1 个 Word 模板 + 最多 3 个 Excel 报表',
    uploadHint2: '支持 .docx 模板与 .xlsx / .xls 报表，也可以点击选择文件',
    docxLabel: 'Word 模板',
    excelLabel: 'Excel 报表',
    maxExcel: '（最多 3 个 Excel）',
    dupName: '（重名已跳过）',
    unsupported: '（仅支持 .docx / .xlsx / .xls）',
    notAdded: '未加入：',
    needDocx: '还需 1 个 Word 模板；',
    needExcel: '还需至少 1 个 Excel 报表',
    analyzeBtn: '分析匹配',
    analyzing: '正在解析匹配…',
    reviewTitle: '匹配核对单',
    reviewDesc: '确认无误后生成文档；标记「留空」的项目不会被填写。',
    backBtn: '重新上传',
    generateBtn: '生成并下载 Word',
    warnPrefix: '提示：',
    doneTitle: '文档已生成，请查看浏览器下载',
    doneDesc: '填写完成的 Word 已保留模板原有样式，只更新了匹配到的数值单元格。',
    downloadAgain: '再次下载',
    nextOne: '填写下一份',
    footer: '数据全程在本机处理，不经过任何外部服务',
    steps: { upload: '上传文件', report: '核对匹配', done: '下载成稿' },
    sourceFrom: '数据来源 ',
    noSource: '未找到对应的 Excel 报表',
    yearLabel: '年份列 ',
    matchedText: ' 项匹配 · ',
    blankText: ' 项留空',
    colTemplate: '模板项目',
    colExcel: 'Excel 来源项',
    colConfidence: '置信度',
    colStatus: '状态',
    statusMatched: '已匹配',
    statusBlank: '留空',
  },
  en: {
    appTitle: 'Financial Report Filling Agent',
    tagline: 'Auto-fill 3 statements · Runs locally',
    heroTitle: 'Fill your Word template with Excel statements, matched by item and year',
    heroDesc:
      'Different ordering and naming variations still match. Items present in the template but missing from the statements are left blank — never guessed. Review the matches, then download the completed Word document in one click.',
    uploadHint1: 'Drop 1 Word template + up to 3 Excel statements',
    uploadHint2: 'Supports .docx templates and .xlsx / .xls statements, or click to choose',
    docxLabel: 'Word Template',
    excelLabel: 'Excel Statement',
    maxExcel: ' (max 3 Excel files)',
    dupName: ' (skipped: duplicate name)',
    unsupported: ' (only .docx / .xlsx / .xls supported)',
    notAdded: 'Not added: ',
    needDocx: 'Need 1 Word template; ',
    needExcel: 'Need at least 1 Excel statement',
    analyzeBtn: 'Analyze & Match',
    analyzing: 'Analyzing & matching…',
    reviewTitle: 'Match Review',
    reviewDesc: 'Generate after confirming. Items marked “Blank” will not be filled.',
    backBtn: 'Upload again',
    generateBtn: 'Generate & Download Word',
    warnPrefix: 'Note: ',
    doneTitle: 'Document generated — check your browser downloads',
    doneDesc: 'The completed Word keeps your original template styling and only updates the matched value cells.',
    downloadAgain: 'Download again',
    nextOne: 'Fill another',
    footer: 'All data is processed on this machine and never sent to any external service',
    steps: { upload: 'Upload', report: 'Review', done: 'Download' },
    sourceFrom: 'Source: ',
    noSource: 'No matching Excel statement found',
    yearLabel: 'Year columns ',
    matchedText: ' matched · ',
    blankText: ' left blank',
    colTemplate: 'Template Item',
    colExcel: 'Excel Source',
    colConfidence: 'Confidence',
    colStatus: 'Status',
    statusMatched: 'Matched',
    statusBlank: 'Blank',
  },
}

// 报表类型中文键 -> 展示名（按语言）
export function typeLabel(lang: Lang, type: string): string {
  const map: Record<string, [string, string]> = {
    资产负债表: ['资产负债表', 'Balance Sheet'],
    利润表: ['利润表', 'Income Statement'],
    现金流量表: ['现金流量表', 'Cash Flow Statement'],
  }
  const pair = map[type]
  if (!pair) return type
  return lang === 'en' ? pair[1] : pair[0]
}

// 把后端已知中文 warning 翻译成当前语言（文件名保留原样）
export function translateWarning(lang: Lang, text: string): string {
  if (lang === 'zh') return text
  if (text.startsWith('Word 模板中未找到含年份表头的表格')) {
    return 'No year-headed table found in the Word template.'
  }
  const m = text.match(/^(.+) 中未解析到有效报表数据$/)
  if (m) return `No valid financial data parsed from ${m[1]}.`
  return text
}

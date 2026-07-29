export interface ItemMatch {
  docx_item: string
  excel_item: string | null
  confidence: number
  status: 'matched' | 'unmatched' | 'skipped'
  values: Record<string, string | null>
}

export interface TableMatch {
  table_index: number
  statement_type: string
  year_columns: string[]
  source_file: string | null
  items: ItemMatch[]
  matched_count: number
  unmatched_count: number
}

export interface AnalyzeResponse {
  session_id: string
  tables: TableMatch[]
  warnings: string[]
}

export type Step = 'upload' | 'report' | 'done'

import { AnalyzeResponse } from './types'

export async function analyzeFiles(
  docx: File,
  excels: File[],
): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('docx', docx)
  excels.forEach((f) => form.append('excels', f))

  const res = await fetch('/api/analyze', { method: 'POST', body: form })
  if (!res.ok) {
    const detail = await res.json().then((j) => j.detail).catch(() => res.statusText)
    throw new Error(detail || '分析失败')
  }
  return res.json()
}

export async function generateDocx(sessionId: string): Promise<void> {
  const res = await fetch(`/api/generate/${sessionId}`, { method: 'POST' })
  if (!res.ok) {
    const detail = await res.json().then((j) => j.detail).catch(() => res.statusText)
    throw new Error(detail || '生成失败')
  }
  const blob = await res.blob()
  const disposition = res.headers.get('content-disposition') || ''
  const m = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i)
  const filename = m ? decodeURIComponent(m[1]) : '已填写.docx'

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

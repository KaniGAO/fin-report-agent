import { useCallback, useRef, useState } from 'react'
import { FileSpreadsheet, FileText, Trash2, UploadCloud } from 'lucide-react'
import { i18n, type Lang } from '../i18n'

interface Props {
  lang: Lang
  docx: File | null
  excels: File[]
  onDocx: (f: File | null) => void
  onExcels: (fs: File[]) => void
}

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export default function UploadZone({ lang, docx, excels, onDocx, onExcels }: Props) {
  const t = i18n[lang]
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [tip, setTip] = useState('')

  const takeFiles = useCallback(
    (list: FileList | File[]) => {
      let nextDocx = docx
      const nextExcels = [...excels]
      const rejected: string[] = []

      for (const f of Array.from(list)) {
        const name = f.name.toLowerCase()
        if (name.endsWith('.docx')) {
          nextDocx = f
        } else if (name.endsWith('.xlsx') || name.endsWith('.xls')) {
          if (nextExcels.length >= 3) {
            rejected.push(`${f.name}${t.maxExcel}`)
          } else if (nextExcels.some((e) => e.name === f.name)) {
            rejected.push(`${f.name}${t.dupName}`)
          } else {
            nextExcels.push(f)
          }
        } else {
          rejected.push(`${f.name}${t.unsupported}`)
        }
      }
      onDocx(nextDocx)
      onExcels(nextExcels)
      setTip(rejected.length ? `${t.notAdded}${rejected.join('、')}` : '')
    },
    [docx, excels, onDocx, onExcels, t],
  )

  return (
    <div className="animate-rise">
      <div
        role="button"
        tabIndex={0}
        aria-label="点击或拖拽上传文件"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          takeFiles(e.dataTransfer.files)
        }}
        className={`card flex cursor-pointer flex-col items-center gap-3 px-8 py-14 text-center transition-all duration-300 hover:shadow-lift ${
          dragging ? 'border-ledger bg-ledger/5 shadow-lift scale-[1.01]' : ''
        }`}
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-ledger to-ledger-indigo text-white shadow-lift">
          <UploadCloud size={26} strokeWidth={1.8} />
        </span>
        <p className="text-lg font-semibold text-ink">{t.uploadHint1}</p>
        <p className="text-sm text-ink-soft">{t.uploadHint2}</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".docx,.xlsx,.xls"
          className="hidden"
          onChange={(e) => {
            if (e.target.files) takeFiles(e.target.files)
            e.target.value = ''
          }}
        />
      </div>

      {tip && <p className="mt-3 text-sm text-warn">{tip}</p>}

      {(docx || excels.length > 0) && (
        <ul className="mt-5 grid gap-2.5 sm:grid-cols-2">
          {docx && (
            <FileCard
              icon={<FileText size={18} className="text-ledger-indigo" />}
              label={t.docxLabel}
              name={docx.name}
              size={fmtSize(docx.size)}
              onRemove={() => onDocx(null)}
            />
          )}
          {excels.map((f) => (
            <FileCard
              key={f.name}
              icon={<FileSpreadsheet size={18} className="text-ok" />}
              label={t.excelLabel}
              name={f.name}
              size={fmtSize(f.size)}
              onRemove={() => onExcels(excels.filter((e) => e !== f))}
            />
          ))}
        </ul>
      )}
    </div>
  )
}

function FileCard(props: {
  icon: React.ReactNode
  label: string
  name: string
  size: string
  onRemove: () => void
}) {
  return (
    <li className="card flex items-center gap-3 px-4 py-3 transition-shadow hover:shadow-lift">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100">
        {props.icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-ink">{props.name}</p>
        <p className="text-xs text-ink-faint">
          {props.label} · <span className="num">{props.size}</span>
        </p>
      </div>
      <button
        type="button"
        aria-label={`移除 ${props.name}`}
        onClick={props.onRemove}
        className="cursor-pointer rounded-md p-1.5 text-ink-faint transition-colors hover:bg-bad/10 hover:text-bad"
      >
        <Trash2 size={16} />
      </button>
    </li>
  )
}

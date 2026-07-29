import { CheckCircle2, CircleDashed, Landmark, Receipt, Waves } from 'lucide-react'
import { TableMatch } from '../types'
import { i18n, typeLabel, type Lang } from '../i18n'

const ICONS: Record<string, React.ReactNode> = {
  资产负债表: <Landmark size={17} />,
  利润表: <Receipt size={17} />,
  现金流量表: <Waves size={17} />,
}

export default function MatchReport({
  lang,
  tables,
}: {
  lang: Lang
  tables: TableMatch[]
}) {
  const t = i18n[lang]
  return (
    <div className="grid gap-6">
      {tables.map((t0, i) => (
        <section
          key={t0.table_index}
          className="card animate-rise overflow-hidden"
          style={{ animationDelay: `${i * 90}ms` }}
        >
          <header className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-slate-200/80 bg-gradient-to-r from-ledger/[.06] to-transparent px-5 py-4">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-ledger/10 text-ledger-deep">
              {ICONS[t0.statement_type] ?? <CircleDashed size={17} />}
            </span>
            <div className="mr-auto">
              <h3 className="text-base font-semibold text-ink">{typeLabel(lang, t0.statement_type)}</h3>
              <p className="text-xs text-ink-faint">
                {t0.source_file ? `${t.sourceFrom}${t0.source_file}` : t.noSource}
                {t.yearLabel}
                <span className="num">{t0.year_columns.join(' / ')}</span>
              </p>
            </div>
            <p className="text-sm">
              <span className="num font-semibold text-ok">{t0.matched_count}</span>
              <span className="text-ink-faint">{t.matchedText}</span>
              <span
                className={`num font-semibold ${t0.unmatched_count ? 'text-warn' : 'text-ink-faint'}`}
              >
                {t0.unmatched_count}
              </span>
              <span className="text-ink-faint">{t.blankText}</span>
            </p>
          </header>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs text-ink-faint">
                  <th className="px-5 py-2.5 font-medium">{t.colTemplate}</th>
                  <th className="px-3 py-2.5 font-medium">{t.colExcel}</th>
                  {t0.year_columns.map((y) => (
                    <th key={y} className="num px-3 py-2.5 text-right font-medium">
                      {y}
                    </th>
                  ))}
                  <th className="px-3 py-2.5 font-medium">{t.colConfidence}</th>
                  <th className="px-5 py-2.5 text-right font-medium">{t.colStatus}</th>
                </tr>
              </thead>
              <tbody>
                {t0.items.map((it) => (
                  <tr
                    key={it.docx_item}
                    className={`ledger-row transition-colors last:border-0 hover:bg-ledger/[.04] ${
                      it.status === 'unmatched' ? 'bg-warn/[.05]' : ''
                    }`}
                  >
                    <td className="px-5 py-2.5 font-medium text-ink">{it.docx_item}</td>
                    <td className="px-3 py-2.5 text-ink-soft">{it.excel_item ?? '—'}</td>
                    {t0.year_columns.map((y) => (
                      <td key={y} className="num px-3 py-2.5 text-right text-ink">
                        {it.values[y] ?? <span className="text-ink-faint">—</span>}
                      </td>
                    ))}
                    <td className="px-3 py-2.5">
                      {it.status === 'matched' ? (
                        <span className="flex items-center gap-2">
                          <span className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
                            <span
                              className="block h-full rounded-full bg-gradient-to-r from-ledger to-ledger-indigo"
                              style={{ width: `${it.confidence}%` }}
                            />
                          </span>
                          <span className="num text-xs text-ink-soft">{it.confidence}</span>
                        </span>
                      ) : (
                        <span className="text-xs text-ink-faint">—</span>
                      )}
                    </td>
                    <td className="px-5 py-2.5 text-right">
                      {it.status === 'matched' ? (
                        <span className="inline-flex items-center gap-1 rounded-full border border-ok/30 bg-ok/10 px-2.5 py-0.5 text-xs font-medium text-ok">
                          <CheckCircle2 size={12} /> {t.statusMatched}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full border border-warn/30 bg-warn/10 px-2.5 py-0.5 text-xs font-medium text-warn">
                          <CircleDashed size={12} /> {t.statusBlank}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  )
}

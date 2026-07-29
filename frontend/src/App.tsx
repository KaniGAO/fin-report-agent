import { useState, useEffect } from 'react'
import { ArrowLeft, Download, Languages, Loader2, ScanSearch, Sparkles } from 'lucide-react'
import UploadZone from './components/UploadZone'
import MatchReport from './components/MatchReport'
import { analyzeFiles, generateDocx } from './api'
import { AnalyzeResponse, Step } from './types'
import { i18n, translateWarning, type Lang } from './i18n'

const STEPS_NO = ['壹', '贰', '叁'] as const

const STEP_KEYS: Step[] = ['upload', 'report', 'done']

export default function App() {
  const [lang, setLang] = useState<Lang>(() => {
    const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('lang') : null
    return saved === 'en' ? 'en' : 'zh'
  })
  const t = i18n[lang]

  useEffect(() => {
    if (typeof localStorage !== 'undefined') localStorage.setItem('lang', lang)
  }, [lang])

  const [step, setStep] = useState<Step>('upload')
  const [docx, setDocx] = useState<File | null>(null)
  const [excels, setExcels] = useState<File[]>([])
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const stepIdx = STEP_KEYS.indexOf(step)
  const canAnalyze = !!docx && excels.length > 0 && !busy

  const handleAnalyze = () => {
    if (!docx) return
    setBusy(true)
    setError('')
    analyzeFiles(docx, excels)
      .then((res) => {
        setResult(res)
        setStep('report')
      })
      .catch((e: Error) => {
        console.error(e)
        setError(e.message)
      })
      .finally(() => setBusy(false))
  }

  const handleGenerate = () => {
    if (!result) return
    setBusy(true)
    setError('')
    generateDocx(result.session_id)
      .then(() => setStep('done'))
      .catch((e: Error) => {
        console.error(e)
        setError(e.message)
      })
      .finally(() => setBusy(false))
  }

  const reset = () => {
    setStep('upload')
    setResult(null)
    setError('')
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-5 pb-24 pt-24">
      {/* 顶部导航（固定） */}
      <nav className="fixed inset-x-0 top-0 z-20 border-b border-slate-200/70 bg-paper-bg/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-5xl items-center gap-4 px-5">
          <p className="flex items-center gap-2 font-mont text-[15px] font-700 font-bold tracking-tight text-ink">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-ledger to-ledger-indigo text-white">
              <Sparkles size={14} />
            </span>
            {t.appTitle}
          </p>
          <ol className="ml-auto flex items-center gap-1 sm:gap-2">
            {STEP_KEYS.map((key, i) => (
              <li key={key} className="flex items-center gap-1 sm:gap-2">
                {i > 0 && <span className="h-px w-5 bg-slate-300 sm:w-8" />}
                <span
                  className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs transition-colors ${
                    i === stepIdx
                      ? 'bg-ledger text-white shadow-card'
                      : i < stepIdx
                        ? 'text-ledger-deep'
                        : 'text-ink-faint'
                  }`}
                >
                  <span className="font-serif">{STEPS_NO[i]}</span>
                  <span className="hidden sm:inline">{t.steps[key]}</span>
                </span>
              </li>
            ))}
          </ol>
          <button
            type="button"
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className={`ml-2 flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
              'border-slate-300 text-ink-soft hover:border-ledger hover:text-ledger-deep'
            }`}
            aria-label="切换语言 / Switch language"
          >
            <Languages size={14} />
            {lang === 'zh' ? '中 / EN' : 'EN / 中'}
          </button>
        </div>
      </nav>

      {/* 步骤一：上传 */}
      {step === 'upload' && (
        <main className="flex flex-1 flex-col gap-8">
          <header className="animate-rise pt-6">
            <p className="mb-2 text-xs font-medium uppercase tracking-[.2em] text-ledger-deep">
              {t.tagline}
            </p>
            <h1 className="text-[28px] font-semibold leading-snug text-ink">{t.heroTitle}</h1>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-ink-soft">{t.heroDesc}</p>
          </header>

          <UploadZone
            lang={lang}
            docx={docx}
            excels={excels}
            onDocx={setDocx}
            onExcels={setExcels}
          />

          <div className="flex items-center gap-4">
            <button
              type="button"
              disabled={!canAnalyze}
              onClick={handleAnalyze}
              className={`flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white transition-all ${
                canAnalyze
                  ? 'cursor-pointer bg-gradient-to-r from-ledger to-ledger-indigo shadow-lift hover:-translate-y-0.5 active:translate-y-0'
                  : 'cursor-not-allowed bg-slate-300'
              }`}
            >
              {busy ? <Loader2 size={16} className="animate-spin" /> : <ScanSearch size={16} />}
              {busy ? t.analyzing : t.analyzeBtn}
            </button>
            <p className="text-xs text-ink-faint">
              {docx ? '' : t.needDocx}
              {excels.length ? '' : t.needExcel}
            </p>
          </div>
          {error && <ErrorBar text={error} />}
        </main>
      )}

      {/* 步骤二：匹配报告 */}
      {step === 'report' && result && (
        <main className="flex flex-1 flex-col gap-6 pt-6">
          <header className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="text-[22px] font-semibold text-ink">{t.reviewTitle}</h2>
              <p className="mt-1 text-sm text-ink-soft">{t.reviewDesc}</p>
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={reset}
                className="flex cursor-pointer items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-ink-soft transition-colors hover:border-ledger hover:text-ledger-deep"
              >
                <ArrowLeft size={15} /> {t.backBtn}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={handleGenerate}
                className="flex cursor-pointer items-center gap-2 rounded-xl bg-gradient-to-r from-ledger to-ledger-indigo px-5 py-2.5 text-sm font-semibold text-white shadow-lift transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {busy ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
                {t.generateBtn}
              </button>
            </div>
          </header>

          {result.warnings.length > 0 && (
            <div className="card border-warn/40 bg-warn/[.06] px-4 py-3 text-sm text-ink-soft">
              {result.warnings.map((w) => (
                <p key={w}>
                  {t.warnPrefix}
                  {translateWarning(lang, w)}
                </p>
              ))}
            </div>
          )}
          {error && <ErrorBar text={error} />}

          <MatchReport lang={lang} tables={result.tables} />
        </main>
      )}

      {/* 步骤三：完成 */}
      {step === 'done' && (
        <main className="flex flex-1 flex-col items-center justify-center gap-5 text-center">
          <span className="animate-rise flex h-16 w-16 items-center justify-center rounded-full bg-ok/10 text-ok">
            <Download size={28} />
          </span>
          <h2 className="animate-rise text-[24px] font-semibold text-ink">{t.doneTitle}</h2>
          <p className="max-w-md text-sm text-ink-soft">{t.doneDesc}</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleGenerate}
              className="cursor-pointer rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm text-ink-soft transition-colors hover:border-ledger hover:text-ledger-deep"
            >
              {t.downloadAgain}
            </button>
            <button
              type="button"
              onClick={reset}
              className="cursor-pointer rounded-xl bg-gradient-to-r from-ledger to-ledger-indigo px-5 py-2.5 text-sm font-semibold text-white shadow-lift transition-transform hover:-translate-y-0.5"
            >
              {t.nextOne}
            </button>
          </div>
        </main>
      )}

      <footer className="mt-16 text-center text-xs text-ink-faint">{t.footer}</footer>
    </div>
  )
}

function ErrorBar({ text }: { text: string }) {
  return (
    <div className="card border-bad/40 bg-bad/[.06] px-4 py-3 text-sm text-bad">{text}</div>
  )
}

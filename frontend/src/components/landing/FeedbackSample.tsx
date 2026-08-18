import { CautionMark, CheckMark } from '@/components/napkin/Marks'

const SAMPLES = [
  {
    tone: 'good' as const,
    your: '12K QPS',
    expected: '8K–15K QPS',
    verdict: 'inside the range',
    headline: 'Excellent estimate',
  },
  {
    tone: 'warn' as const,
    your: '400K QPS',
    expected: '8K–15K QPS',
    verdict: '27× high',
    headline: 'This one is worth learning',
  },
]

/** What scoring actually looks like — the product's most distinctive screen. */
export function FeedbackSample() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {SAMPLES.map((sample) => {
        const good = sample.tone === 'good'
        return (
          <div
            key={sample.your}
            className={`rounded-lg border bg-surface px-5 py-4 ${
              good ? 'border-good-line' : 'border-warn-line'
            }`}
          >
            <div
              className={`flex items-center gap-2 text-sm font-medium ${
                good ? 'text-good' : 'text-warn'
              }`}
            >
              {good ? <CheckMark /> : <CautionMark />}
              {sample.headline}
            </div>
            <dl className="mt-3 space-y-1.5 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-ink-secondary">Your answer</dt>
                <dd className="tnum font-mono font-semibold">{sample.your}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-secondary">Defensible</dt>
                <dd className="tnum font-mono">{sample.expected}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-secondary">Distance</dt>
                <dd className={`tnum font-mono ${good ? 'text-good' : 'text-warn'}`}>
                  {sample.verdict}
                </dd>
              </div>
            </dl>
          </div>
        )
      })}
    </div>
  )
}

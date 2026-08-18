import { SketchArrow } from '@/components/napkin/Sketch'

/**
 * The product in one glance: a real chain, with the operation that gets you
 * from each number to the next written in the margin — which is the actual
 * skill being taught.
 *
 * Laid out as two columns, nodes and margin, so the annotations can never
 * overflow the napkin on a narrow screen.
 */
const TONE: Record<string, string> = {
  given: 'border-line-strong bg-surface text-ink',
  solved: 'border-good-line bg-good-soft text-ink',
  current: 'border-accent bg-accent-soft text-ink',
  locked: 'border-line border-dashed bg-subtle/50 text-ink-faint',
}

interface Step {
  value: string
  label: string
  tone: keyof typeof TONE
  /** The operation that produced this number from the one above it. */
  from?: string
}

const STEPS: Step[] = [
  { value: '100M', label: 'daily active users', tone: 'given' },
  { value: '1B', label: 'feed requests / day', tone: 'solved', from: '× 10 per user' },
  { value: '10K', label: 'average QPS', tone: 'solved', from: '÷ 100K sec/day' },
  { value: '30K', label: 'peak QPS', tone: 'solved', from: '× 3 at peak' },
  { value: '6 GB/s', label: 'egress bandwidth', tone: 'current', from: '× 200 KB' },
  { value: '?', label: 'storage, servers', tone: 'locked', from: 'your turn' },
]

const NODE_COL = 'w-[190px] shrink-0 sm:w-[230px]'

export function HeroChain() {
  return (
    <div className="napkin-surface rounded-lg border border-line px-5 py-7 shadow-card sm:px-8">
      <p className="handwritten mb-4 text-[19px] text-ink-muted">Instagram feed, sized</p>

      <ol className="mx-auto w-fit">
        {STEPS.map((step, index) => (
          <li key={step.label}>
            {index > 0 && (
              <div className="flex items-center">
                <div className={`${NODE_COL} flex justify-center`}>
                  <SketchArrow tone={index <= 3 ? 'good' : 'muted'} />
                </div>
                <span className="handwritten pl-3 text-[17px] leading-tight text-accent">
                  {step.from}
                </span>
              </div>
            )}

            <div className="flex items-center">
              <div
                className={`${NODE_COL} flex items-baseline justify-between gap-2 rounded-md border px-3.5 py-2.5 ${TONE[step.tone]}`}
              >
                <span className="tnum font-mono text-[16px] font-semibold leading-none">
                  {step.value}
                </span>
                <span className="text-right text-[11px] leading-tight text-ink-secondary">
                  {step.label}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}

import { SketchArrowRight } from '@/components/napkin/Sketch'

const LOOP = [
  { step: 'Attempt', detail: 'Estimate the step' },
  { step: 'Miss', detail: '27× off' },
  { step: 'Learn', detail: 'That one concept' },
  { step: 'Reattempt', detail: 'The same step' },
  { step: 'Master', detail: 'Reflex, not recall' },
]

/** The learning loop, as a flow rather than a bulleted list. */
export function LoopDiagram() {
  return (
    <ol className="flex flex-col gap-1 sm:flex-row sm:items-stretch sm:gap-2">
      {LOOP.map((item, index) => (
        <li
          key={item.step}
          className="flex flex-col items-center gap-1 sm:flex-1 sm:flex-row sm:gap-2"
        >
          <div className="flex w-full flex-col justify-center rounded-md border border-line bg-surface px-3 py-2.5 text-center sm:h-full">
            <div className="text-[13px] font-semibold leading-tight">{item.step}</div>
            <div className="mt-1 text-[11px] leading-tight text-ink-muted">{item.detail}</div>
          </div>
          {index < LOOP.length - 1 && (
            <SketchArrowRight className="shrink-0 rotate-90 text-line-strong sm:rotate-0" />
          )}
        </li>
      ))}
    </ol>
  )
}

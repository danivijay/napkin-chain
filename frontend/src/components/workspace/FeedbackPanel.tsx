import type { Feedback } from '@/types'
import { Button } from '@/components/ui/Button'
import { CautionMark, CheckMark } from '@/components/napkin/Marks'
import { NapkinShortcut, NapkinWorking } from '@/components/napkin/NapkinNote'
import { CLASSIFICATION_LABEL, formatRatio, humanize } from '@/lib/format'

interface Props {
  feedback: Feedback
  completed: boolean
  onContinue: () => void
  onRetry: () => void
  onLearn: (conceptId: string) => void
}

/**
 * Feedback is the product's main teaching surface: what you said, what was
 * defensible, how far apart those are, and why. No celebration, no confetti.
 */
export function FeedbackPanel({ feedback, completed, onContinue, onRetry, onLearn }: Props) {
  const good = feedback.passed
  const expected =
    feedback.expectedMin !== null && feedback.expectedMax !== null
      ? `${humanize(feedback.expectedMin)}–${humanize(feedback.expectedMax, feedback.unit)}`
      : `~${humanize(feedback.expectedValue, feedback.unit)}`

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-7">
        <header className="animate-settle">
          <div
            className={`flex items-center gap-2 text-sm font-medium ${good ? 'text-good' : 'text-warn'}`}
          >
            {good ? <CheckMark /> : <CautionMark />}
            {CLASSIFICATION_LABEL[feedback.classification]}
          </div>
          <h2 className="mt-2 text-[22px] font-semibold tracking-[-0.02em]">{feedback.headline}</h2>
        </header>

        <dl className="divide-y divide-line rounded-md border border-line bg-surface">
          <Row label="Your answer" value={humanize(feedback.yourEstimate, feedback.unit)} strong />
          <Row label="Defensible" value={expected} />
          <Row
            label="Distance"
            value={
              feedback.withinRange
                ? 'inside the range'
                : `${formatRatio(feedback.ratio)} ${feedback.direction === 'over' ? 'high' : 'low'}`
            }
          />
        </dl>

        {feedback.explanationSteps.length > 0 && (
          <section>
            <h3 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-muted">
              Why
            </h3>
            <NapkinWorking steps={feedback.explanationSteps} className="mt-3" />
          </section>
        )}

        {feedback.shortcut && (
          <section className="border-t border-line pt-5">
            <NapkinShortcut>{feedback.shortcut}</NapkinShortcut>
          </section>
        )}

        {feedback.note && (
          <p className="text-sm leading-relaxed text-ink-secondary">{feedback.note}</p>
        )}

        {!good && feedback.conceptId && (
          <section className="rounded-lg border border-warn-line bg-warn-soft px-4 py-4">
            <h3 className="text-sm font-semibold">This step is worth learning.</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">
              You estimated {humanize(feedback.yourEstimate, feedback.unit)}. A defensible answer
              is {expected}.
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="mt-3"
              onClick={() => onLearn(feedback.conceptId!)}
            >
              Learn {feedback.conceptTitle ?? 'this concept'}
            </Button>
          </section>
        )}
      </div>

      <div className="sticky bottom-0 mt-6 space-y-3 bg-paper pb-[env(safe-area-inset-bottom)] pt-4">
        <Button size="lg" className="w-full" onClick={onContinue}>
          {completed ? 'See results' : 'Continue to next step'}
        </Button>
        <div className="flex items-center justify-between text-sm">
          <button type="button" onClick={onRetry} className="text-ink-muted hover:text-ink">
            Try this step again
          </button>
          {good && feedback.conceptId && (
            <button
              type="button"
              onClick={() => onLearn(feedback.conceptId!)}
              className="text-accent hover:text-accent-strong"
            >
              Review the concept
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function Row({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex justify-between px-3.5 py-2.5 text-sm">
      <dt className="text-ink-secondary">{label}</dt>
      <dd className={`tnum font-mono ${strong ? 'font-semibold' : ''}`}>{value}</dd>
    </div>
  )
}

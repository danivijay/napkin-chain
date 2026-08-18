import { useEffect, useRef, useState } from 'react'
import type { AttemptState, NodeQuestion } from '@/types'
import { Button } from '@/components/ui/Button'
import { NapkinNote } from '@/components/napkin/NapkinNote'
import { parseEstimate, humanize } from '@/lib/format'
import { draftKey, useDraftStore } from '@/stores/draftStore'

interface Props {
  state: AttemptState
  question: NodeQuestion
  onSubmit: (payload: { estimate: number; calculation: string; seconds: number }) => void
  onHint: () => void
  onLearn: (conceptId: string) => void
  submitting: boolean
  submitError?: string | null
}

export function EstimatePanel({
  state,
  question,
  onSubmit,
  onHint,
  onLearn,
  submitting,
  submitError,
}: Props) {
  const key = draftKey(state.challengeSlug, question.id)
  const draft = useDraftStore((store) => store.drafts[key])
  const setDraft = useDraftStore((store) => store.set)
  const elapsedSeconds = useDraftStore((store) => store.elapsedSeconds)

  const [showWorking, setShowWorking] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const estimateText = draft?.estimate ?? ''
  const calculation = draft?.calculation ?? question.lastCalculation ?? ''
  const parsed = parseEstimate(estimateText)
  const hintsLeft = question.hintsAvailable - question.hintsRevealed
  const hintsAllowed = state.mode !== 'interview'

  useEffect(() => {
    inputRef.current?.focus()
    // Start the clock for this step as soon as it is shown.
    if (!draft?.startedAt) setDraft(key, {})
    if (question.lastCalculation) setShowWorking(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [question.id])

  function submit() {
    if (parsed === null || parsed <= 0) return
    onSubmit({ estimate: parsed, calculation, seconds: elapsedSeconds(key) })
  }

  return (
    <form
      className="flex h-full flex-col"
      onSubmit={(event) => {
        event.preventDefault()
        submit()
      }}
    >
      <div className="flex-1 space-y-6">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-muted">
            Step {question.stepNumber} of {question.totalSteps}
          </p>
          <h2 className="mt-2 text-[22px] font-semibold tracking-[-0.02em]">{question.label}</h2>
          {question.prompt && (
            <p className="mt-2 text-[15px] leading-relaxed text-ink-secondary">
              {question.prompt}
            </p>
          )}
        </div>

        {question.givens.length > 0 && (
          <dl className="divide-y divide-line rounded-md border border-line bg-subtle/50">
            {question.givens.map((given) => (
              <div key={given.label} className="flex justify-between px-3.5 py-2 text-sm">
                <dt className="text-ink-secondary">{given.label}</dt>
                <dd className="tnum font-mono">{given.value}</dd>
              </div>
            ))}
          </dl>
        )}

        <div>
          <label htmlFor="estimate" className="text-sm font-medium">
            Your estimate
          </label>
          <div className="mt-2 flex items-center gap-3 rounded-md border border-line bg-surface px-3 focus-within:border-accent">
            <input
              id="estimate"
              ref={inputRef}
              value={estimateText}
              onChange={(event) => setDraft(key, { estimate: event.target.value })}
              inputMode="decimal"
              autoComplete="off"
              placeholder="e.g. 10K"
              className="tnum h-12 flex-1 bg-transparent font-mono text-[19px] outline-none placeholder:font-sans placeholder:text-[15px] placeholder:text-ink-faint"
            />
            <span className="shrink-0 text-sm text-ink-muted">{question.unit}</span>
          </div>
          <p className="mt-2 h-4 text-xs text-ink-muted">
            {parsed !== null && `reads as ${humanize(parsed, question.unit)}`}
          </p>
        </div>

        <div>
          <button
            type="button"
            onClick={() => setShowWorking((open) => !open)}
            className="text-sm text-accent hover:text-accent-strong"
          >
            {showWorking ? 'Hide my calculation' : 'Show my calculation'}
          </button>
          {showWorking && (
            <textarea
              value={calculation}
              onChange={(event) => setDraft(key, { calculation: event.target.value })}
              rows={4}
              placeholder={'1 day ≈ 100K seconds\n1B / 100K ≈ 10K'}
              className="handwritten mt-2 w-full resize-none rounded-md border border-dashed border-line-strong bg-subtle/60 px-3.5 py-3 text-[18px] leading-[1.5] outline-none placeholder:text-ink-faint focus:border-accent"
            />
          )}
        </div>

        {question.hints.length > 0 && (
          <div className="space-y-2">
            {question.hints.map((hint, index) => (
              <NapkinNote key={index} className="animate-settle">
                {hint}
              </NapkinNote>
            ))}
          </div>
        )}
      </div>

      <div className="sticky bottom-0 mt-6 space-y-3 bg-paper pb-[env(safe-area-inset-bottom)] pt-4">
        {submitError && (
          <p className="rounded-md border border-warn-line bg-warn-soft px-3 py-2 text-sm text-warn">
            {submitError} Your estimate is still here — try again.
          </p>
        )}
        <Button type="submit" size="lg" className="w-full" disabled={parsed === null || submitting}>
          {submitting ? 'Checking…' : 'Submit estimate'}
        </Button>
        <div className="flex items-center justify-between text-sm">
          {hintsAllowed && hintsLeft > 0 ? (
            <button type="button" onClick={onHint} className="text-ink-muted hover:text-ink">
              Need a hint? ({hintsLeft})
            </button>
          ) : (
            <span />
          )}
          {question.conceptId && (
            <button
              type="button"
              onClick={() => onLearn(question.conceptId!)}
              className="text-accent hover:text-accent-strong"
            >
              Learn {question.conceptTitle ?? 'this concept'}
            </button>
          )}
        </div>
      </div>
    </form>
  )
}

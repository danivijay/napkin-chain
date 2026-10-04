import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { SectionLabel } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { NapkinShortcut, NapkinWorking } from '@/components/napkin/NapkinNote'
import { Meter } from '@/components/ui/Meter'
import { api } from '@/lib/api'
import { humanize, parseEstimate } from '@/lib/format'
import type { DrillResult } from '@/types'

export function ConceptDetailPage() {
  const { conceptId = '' } = useParams()
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Where the user came from, so they never lose their place in a challenge.
  const fromSlug = params.get('from')
  const fromNode = params.get('node')

  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['concept', conceptId],
    queryFn: () => api.concept(conceptId),
  })

  const learn = useMutation({
    mutationFn: () => api.markLearned(conceptId),
    onSuccess: (updated) => {
      queryClient.setQueryData(['concept', conceptId], updated)
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      queryClient.invalidateQueries({ queryKey: ['home'] })
    },
  })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  const returnToChallenge = () => {
    if (!learn.isSuccess) learn.mutate()
    navigate(
      `/app/challenges/${fromSlug}/build${fromNode ? `?retry=${encodeURIComponent(fromNode)}` : ''}`,
    )
  }

  return (
    <article className="mx-auto max-w-2xl space-y-9">
      <div>
        <Link
          to={fromSlug ? `/app/challenges/${fromSlug}/build` : '/app/learn'}
          className="text-sm text-ink-muted hover:text-ink"
        >
          ← {fromSlug ? 'Back to the challenge' : 'Learn'}
        </Link>
        <h1 className="mt-4 text-[30px] font-semibold tracking-[-0.025em]">{data.title}</h1>
        <p className="mt-2 text-[17px] leading-relaxed text-ink-secondary">{data.oneLiner}</p>
        {data.attempts > 0 && (
          <div className="mt-4">
            <Meter
              value={data.mastery}
              detail={`${Math.round(data.mastery * 100)}% · ${data.attempts} attempts`}
              tone={data.mastery >= 0.7 ? 'good' : data.mastery >= 0.4 ? 'accent' : 'warn'}
            />
          </div>
        )}
      </div>

      <section className="space-y-4 text-[16px] leading-[1.7] text-ink-secondary">
        {data.explanation.map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </section>

      {data.shortcut && (
        <section className="rounded-lg border border-line bg-surface px-5 py-4">
          <NapkinShortcut>{data.shortcut}</NapkinShortcut>
          {data.shortcutNote && (
            <p className="mt-3 text-sm leading-relaxed text-ink-secondary">{data.shortcutNote}</p>
          )}
        </section>
      )}

      {data.examples.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Examples</SectionLabel>
          <ul className="space-y-3">
            {data.examples.map((example, index) => (
              <li key={index} className="rounded-lg border border-line bg-surface px-5 py-4">
                <p className="text-sm text-ink-secondary">{example.given}</p>
                {example.working.length > 0 && (
                  <NapkinWorking steps={example.working} className="mt-3" />
                )}
                <p className="mt-3 font-mono text-[15px] font-semibold">{example.result}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.pitfalls.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Where this goes wrong</SectionLabel>
          <ul className="space-y-2">
            {data.pitfalls.map((pitfall, index) => (
              <li key={index} className="flex gap-3 text-[15px] leading-relaxed text-ink-secondary">
                <span className="mt-2.5 h-1 w-1 shrink-0 rounded-full bg-warn" />
                {pitfall}
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.drill && <Drill conceptId={conceptId} drill={data.drill} />}

      <section className="space-y-3 border-t border-line pt-7">
        {fromSlug ? (
          <>
            <p className="text-[15px] text-ink-secondary">
              You've learned <span className="font-medium text-ink">{data.title}</span>.
            </p>
            <Button size="lg" onClick={returnToChallenge}>
              Reattempt this step
            </Button>
          </>
        ) : (
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="secondary" onClick={() => learn.mutate()} loading={learn.isPending}>
              {data.learned ? 'Marked as learned' : "I've got this"}
            </Button>
            {data.relatedChallenges[0] && (
              <Link
                to={`/app/challenges/${data.relatedChallenges[0].slug}`}
                className="text-sm text-accent hover:text-accent-strong"
              >
                Practise it in {data.relatedChallenges[0].title} →
              </Link>
            )}
          </div>
        )}
      </section>

      {data.relatedConcepts.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Related</SectionLabel>
          <ul className="flex flex-wrap gap-2">
            {data.relatedConcepts.map((related) => (
              <li key={related.conceptId}>
                <Link
                  to={`/app/learn/${related.conceptId}`}
                  className="inline-block rounded-md border border-line bg-surface px-3 py-1.5 text-[13px] text-ink-secondary transition-colors hover:border-line-strong hover:text-ink"
                >
                  {related.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  )
}

function Drill({
  conceptId,
  drill,
}: {
  conceptId: string
  drill: { prompt: string; given: string; unit: string }
}) {
  const queryClient = useQueryClient()
  const [value, setValue] = useState('')
  const [startedAt] = useState(() => Date.now())
  const [result, setResult] = useState<DrillResult | null>(null)

  const practice = useMutation({
    mutationFn: (estimate: number) =>
      api.practiceConcept(conceptId, estimate, Math.round((Date.now() - startedAt) / 1000)),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['concept', conceptId] })
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
    },
  })

  const parsed = parseEstimate(value)

  return (
    <section className="space-y-3">
      <SectionLabel>Try it</SectionLabel>
      <div className="rounded-lg border border-line bg-surface px-5 py-4">
        <p className="text-[15px] leading-relaxed">{drill.prompt}</p>
        <p className="mt-2 font-mono text-sm text-ink-secondary">{drill.given}</p>

        <form
          className="mt-4 flex gap-2"
          onSubmit={(event) => {
            event.preventDefault()
            if (parsed !== null && parsed > 0) practice.mutate(parsed)
          }}
        >
          <div className="flex flex-1 items-center gap-2 rounded-md border border-line px-3 focus-within:border-accent">
            <input
              value={value}
              onChange={(event) => setValue(event.target.value)}
              inputMode="decimal"
              placeholder="Your estimate"
              aria-label="Your estimate"
              className="tnum h-10 flex-1 bg-transparent font-mono text-[15px] outline-none placeholder:font-sans placeholder:text-ink-faint"
            />
            <span className="text-xs text-ink-muted">{drill.unit}</span>
          </div>
          <Button type="submit" disabled={parsed === null} loading={practice.isPending}>
            Check
          </Button>
        </form>

        {result && (
          <div className="animate-settle mt-4 border-t border-line pt-4">
            <p className={`text-sm font-medium ${result.passed ? 'text-good' : 'text-warn'}`}>
              {result.headline}
            </p>
            <p className="mt-1 text-sm text-ink-secondary">
              Defensible: {humanize(result.expectedMin)}–{humanize(result.expectedMax, drill.unit)}
            </p>
            {result.explanation.length > 0 && (
              <NapkinWorking steps={result.explanation} className="mt-3" />
            )}
          </div>
        )}
      </div>
    </section>
  )
}

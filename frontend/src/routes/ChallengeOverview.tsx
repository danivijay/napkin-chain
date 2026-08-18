import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { SectionLabel } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { ArrowDown } from '@/components/napkin/Marks'
import { api } from '@/lib/api'
import { DIFFICULTY_LABEL } from '@/lib/format'
import type { Mode } from '@/types'

const MODES: { mode: Mode; title: string; detail: string }[] = [
  { mode: 'learn', title: 'Learn', detail: 'No timer, hints, guided calculations.' },
  { mode: 'practice', title: 'Practice', detail: 'Suggested pace, limited hints, full feedback.' },
  { mode: 'interview', title: 'Interview', detail: 'Timed, no hints, minimal interface.' },
]

export function ChallengeOverview() {
  const { slug = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<Mode>('practice')

  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['challenge', slug],
    queryFn: () => api.challenge(slug),
  })

  const start = useMutation({
    mutationFn: (restart: boolean) => api.startAttempt(slug, mode, restart),
    onSuccess: (state) => {
      queryClient.setQueryData(['attempt', slug], state)
      navigate(`/app/challenges/${slug}/build`)
    },
  })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  const inProgress = data.attemptStatus === 'in_progress'

  return (
    <div className="mx-auto max-w-2xl space-y-9">
      <div>
        <Link to="/app/challenges" className="text-sm text-ink-muted hover:text-ink">
          ← Challenges
        </Link>
        <h1 className="mt-4 text-[30px] font-semibold tracking-[-0.025em]">{data.title}</h1>
        <p className="mt-1.5 text-sm text-ink-muted">
          {DIFFICULTY_LABEL[data.difficulty]} · ~{data.estimatedMinutes} min · {data.nodeCount}{' '}
          estimates
        </p>
        <p className="mt-5 text-[16px] leading-relaxed text-ink-secondary">
          {data.scenarioDescription}
        </p>
      </div>

      {data.scenarioGivens.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Given</SectionLabel>
          <dl className="divide-y divide-line rounded-lg border border-line bg-surface">
            {data.scenarioGivens.map((given) => (
              <div key={given.label} className="flex justify-between px-4 py-2.5 text-sm">
                <dt className="text-ink-secondary">{given.label}</dt>
                <dd className="tnum font-mono">{given.value}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      <section className="space-y-3">
        <SectionLabel>Chain</SectionLabel>
        <div className="flex flex-col items-start">
          {data.chain.map((node, index) => (
            <div key={node.id} className="flex flex-col items-start">
              <span className="text-[15px]">{node.label}</span>
              {index < data.chain.length - 1 && (
                <ArrowDown className="ml-1.5 h-5 text-line-strong" />
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <SectionLabel>Concepts</SectionLabel>
        <ul className="flex flex-wrap gap-2">
          {data.concepts.map((concept) => (
            <li key={concept.conceptId}>
              <Link
                to={`/app/learn/${concept.conceptId}`}
                className="inline-flex items-center gap-2 rounded-md border border-line bg-surface px-3 py-1.5 text-[13px] text-ink-secondary transition-colors hover:border-line-strong hover:text-ink"
              >
                {concept.title}
                {concept.mastery > 0 && (
                  <span className="tnum text-[11px] text-ink-faint">
                    {Math.round(concept.mastery * 100)}%
                  </span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <SectionLabel>Mode</SectionLabel>
        <div className="grid gap-2 sm:grid-cols-3">
          {MODES.filter((item) => data.modes.includes(item.mode)).map((item) => (
            <button
              key={item.mode}
              type="button"
              onClick={() => setMode(item.mode)}
              aria-pressed={mode === item.mode}
              className={`rounded-lg border px-4 py-3 text-left transition-colors ${
                mode === item.mode
                  ? 'border-accent bg-accent-soft'
                  : 'border-line bg-surface hover:border-line-strong'
              }`}
            >
              <span className="text-sm font-medium">{item.title}</span>
              <span className="mt-1 block text-xs leading-relaxed text-ink-secondary">
                {item.detail}
              </span>
            </button>
          ))}
        </div>
      </section>

      <div className="flex flex-wrap items-center gap-3 border-t border-line pt-6">
        <Button size="lg" onClick={() => start.mutate(false)} disabled={start.isPending}>
          {inProgress ? 'Resume challenge' : 'Start challenge'}
        </Button>
        {inProgress && (
          <Button variant="ghost" onClick={() => start.mutate(true)} disabled={start.isPending}>
            Start over
          </Button>
        )}
        {data.attemptStatus === 'completed' && (
          <Link
            to={`/app/challenges/${slug}/result`}
            className="text-sm text-ink-muted hover:text-ink"
          >
            View last result
          </Link>
        )}
      </div>
      {start.isError && <ErrorState error={start.error} />}
    </div>
  )
}

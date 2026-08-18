import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ButtonLink } from '@/components/ui/Button'
import { SectionLabel } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { CautionMark, CheckMark } from '@/components/napkin/Marks'
import { api } from '@/lib/api'
import { CLASSIFICATION_LABEL, formatDuration, formatRatio, humanize } from '@/lib/format'
import type { NodeResult } from '@/types'

export function Result() {
  const { slug = '' } = useParams()
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['result', slug],
    queryFn: () => api.result(slug),
  })
  const concepts = useQuery({ queryKey: ['concepts'], queryFn: api.concepts })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  const conceptTitles = new Map(
    (concepts.data ?? []).flatMap((group) =>
      group.concepts.map((concept) => [concept.conceptId, concept.title] as const),
    ),
  )
  const finished = data.status === 'completed'

  return (
    <div className="mx-auto max-w-2xl space-y-9">
      <header>
        <Link to="/app/challenges" className="text-sm text-ink-muted hover:text-ink">
          ← Challenges
        </Link>
        <h1 className="mt-4 text-[30px] font-semibold tracking-[-0.025em]">
          {data.challengeTitle}
        </h1>
        <p className="mt-1.5 text-sm text-ink-muted">
          {finished ? 'Chain complete' : 'In progress'} · {data.solvedCount} of {data.totalSteps}{' '}
          estimates
        </p>
      </header>

      <section className="grid grid-cols-2 gap-x-8 gap-y-6 rounded-lg border border-line bg-surface px-6 py-6 sm:grid-cols-4">
        <Metric
          label="Intuition"
          value={data.score !== null ? `${Math.round(data.score * 100)}%` : '—'}
        />
        <Metric
          label="Average error"
          value={data.averageRatio !== null ? formatRatio(data.averageRatio) : '—'}
        />
        <Metric
          label="Per step"
          value={data.secondsPerStep !== null ? `${Math.round(data.secondsPerStep)}s` : '—'}
        />
        <Metric label="Total" value={formatDuration(data.totalSeconds)} />
      </section>

      <section className="space-y-3">
        <SectionLabel>Every estimate</SectionLabel>
        <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
          {data.nodes.map((node) => (
            <NodeRow key={node.nodeId} node={node} />
          ))}
        </ul>
      </section>

      {data.weakConceptIds.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Worth learning</SectionLabel>
          <ul className="space-y-2">
            {data.weakConceptIds.map((conceptId) => (
              <li key={conceptId}>
                <Link
                  to={`/app/learn/${conceptId}`}
                  className="flex items-center justify-between rounded-lg border border-warn-line bg-warn-soft px-5 py-3.5 transition-colors hover:border-warn"
                >
                  <span className="text-[15px] font-medium">
                    {conceptTitles.get(conceptId) ?? conceptId}
                  </span>
                  <span className="text-sm font-medium text-warn">Learn</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="flex flex-wrap gap-3 border-t border-line pt-6">
        <ButtonLink to={`/app/challenges/${slug}`} variant="secondary">
          {finished ? 'Run it again' : 'Back to overview'}
        </ButtonLink>
        <ButtonLink to="/app/progress" variant="ghost">
          See your progress
        </ButtonLink>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="tnum text-[24px] font-semibold leading-none tracking-[-0.02em]">{value}</div>
      <div className="mt-1.5 text-xs text-ink-muted">{label}</div>
    </div>
  )
}

function NodeRow({ node }: { node: NodeResult }) {
  const weak = node.status === 'weak'
  return (
    <li className="flex items-center gap-4 px-5 py-3.5">
      <span className={weak ? 'text-warn' : 'text-good'}>
        {weak ? <CautionMark /> : <CheckMark />}
      </span>
      <div className="min-w-0 flex-1">
        <div className="text-[15px] font-medium">{node.label}</div>
        <div className="mt-0.5 text-xs text-ink-muted">
          {node.classification ? CLASSIFICATION_LABEL[node.classification] : 'Not attempted'}
          {node.attempts > 1 && ` · ${node.attempts} attempts`}
        </div>
      </div>
      <div className="shrink-0 text-right">
        <div className="tnum font-mono text-sm">
          {node.yourEstimate !== null ? humanize(node.yourEstimate, node.unit) : '—'}
        </div>
        <div className="tnum text-xs text-ink-muted">
          {node.expectedValue !== null && `vs ~${humanize(node.expectedValue)}`}
        </div>
      </div>
    </li>
  )
}

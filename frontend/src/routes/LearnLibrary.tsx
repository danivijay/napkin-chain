import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { SectionLabel } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { AREA_ICONS, type ConceptArea } from '@/components/Icons'
import { api } from '@/lib/api'
import type { ConceptSummary } from '@/types'

const STATUS_TONE: Record<string, string> = {
  untouched: 'text-ink-faint',
  learning: 'text-ink-muted',
  developing: 'text-accent',
  strong: 'text-good',
  mastered: 'text-good',
}

export function LearnLibrary() {
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['concepts'],
    queryFn: api.concepts,
  })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Learn</h1>
        <p className="mt-1.5 text-[15px] text-ink-secondary">
          One skill at a time. Each takes a minute or two.
        </p>
      </header>

      {data.map((group) => {
        const AreaIcon = AREA_ICONS[group.area as ConceptArea] ?? AREA_ICONS.traffic
        return (
        <section key={group.area} className="space-y-3">
          <div className="flex items-center gap-2 text-ink-muted">
            <AreaIcon className="h-[17px] w-[17px]" />
            <SectionLabel>{group.title}</SectionLabel>
          </div>
          <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
            {group.concepts.map((concept) => (
              <ConceptRow key={concept.conceptId} concept={concept} />
            ))}
          </ul>
        </section>
        )
      })}
    </div>
  )
}

function ConceptRow({ concept }: { concept: ConceptSummary }) {
  return (
    <li>
      <Link
        to={`/app/learn/${concept.conceptId}`}
        className="flex items-center gap-4 px-5 py-3.5 transition-colors hover:bg-subtle/60"
      >
        <div className="min-w-0 flex-1">
          <h3 className="text-[15px] font-medium">{concept.title}</h3>
          <p className="mt-0.5 truncate text-sm text-ink-secondary">{concept.oneLiner}</p>
        </div>
        <div className="shrink-0 text-right">
          <div className={`tnum text-sm font-medium ${STATUS_TONE[concept.status]}`}>
            {concept.attempts > 0 ? `${Math.round(concept.mastery * 100)}%` : '—'}
          </div>
          <div className="text-[11px] text-ink-faint">
            {concept.attempts > 0 ? `${concept.attempts} tried` : `${concept.readMinutes} min`}
          </div>
        </div>
      </Link>
    </li>
  )
}

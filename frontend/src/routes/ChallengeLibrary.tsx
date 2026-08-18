import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { SectionLabel } from '@/components/ui/Card'
import { api } from '@/lib/api'
import { DIFFICULTY_LABEL } from '@/lib/format'
import type { ChallengeSummary, Difficulty } from '@/types'

const ORDER: Difficulty[] = ['foundation', 'builder', 'system', 'interview']

const BLURB: Record<Difficulty, string> = {
  foundation: 'One or two connected estimates.',
  builder: 'A short chain, three to five steps.',
  system: 'Branching dependencies across several skills.',
  interview: 'Ambiguous. You set the assumptions.',
}

export function ChallengeLibrary() {
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['challenges'],
    queryFn: api.challenges,
  })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  const groups = ORDER.map((level) => ({
    level,
    items: data.filter((challenge) => challenge.difficulty === level),
  })).filter((group) => group.items.length > 0)

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Challenges</h1>
        <p className="mt-1.5 text-[15px] text-ink-secondary">
          Real systems, each one a chain of connected estimates.
        </p>
      </header>

      {groups.map((group) => (
        <section key={group.level} className="space-y-3">
          <div className="flex items-baseline gap-3">
            <SectionLabel>{DIFFICULTY_LABEL[group.level]}</SectionLabel>
            <span className="text-xs text-ink-muted">{BLURB[group.level]}</span>
          </div>
          <ul className="grid gap-2.5 sm:grid-cols-2">
            {group.items.map((challenge) => (
              <ChallengeCard key={challenge.slug} challenge={challenge} />
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}

/** The shape of the chain, so the card shows a chain rather than describing one. */
function ChainPreview({ labels }: { labels: string[] }) {
  const shown = labels.slice(0, 3)
  const remaining = labels.length - shown.length

  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-1.5 gap-y-1 font-mono text-[11px] text-ink-muted">
      {shown.map((label, index) => (
        <span key={label} className="flex items-center gap-1.5">
          <span>{label}</span>
          {index < shown.length - 1 && <span className="text-ink-faint">→</span>}
        </span>
      ))}
      {remaining > 0 && <span className="text-ink-faint">→ +{remaining} more</span>}
    </div>
  )
}

function ChallengeCard({ challenge }: { challenge: ChallengeSummary }) {
  const inProgress = challenge.attemptStatus === 'in_progress'
  const completed = challenge.attemptStatus === 'completed'

  return (
    <li>
      <Link
        to={`/app/challenges/${challenge.slug}`}
        className="flex h-full flex-col rounded-lg border border-line bg-surface px-5 py-4 transition-colors hover:border-line-strong"
      >
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-[17px] font-semibold tracking-[-0.01em]">{challenge.title}</h3>
          {completed && <span className="mt-1 text-xs font-medium text-good">Solved</span>}
          {inProgress && (
            <span className="tnum mt-1 shrink-0 text-xs text-accent">
              {challenge.solvedCount}/{challenge.nodeCount}
            </span>
          )}
        </div>
        <p className="mt-1.5 line-clamp-2 text-sm leading-relaxed text-ink-secondary">
          {challenge.description}
        </p>

        <ChainPreview labels={challenge.chainLabels} />

        <p className="mt-auto pt-3 text-xs text-ink-muted">
          {challenge.nodeCount} estimates · ~{challenge.estimatedMinutes} min
        </p>
      </Link>
    </li>
  )
}

import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, SectionLabel } from '@/components/ui/Card'
import { ButtonLink } from '@/components/ui/Button'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { DIFFICULTY_LABEL, relativeTime } from '@/lib/format'
import type { Recommendation } from '@/types'

export function Home() {
  const { user } = useAuth()
  const { data, isPending, error, refetch } = useQuery({ queryKey: ['home'], queryFn: api.home })

  if (isPending) return <LoadingScreen />
  if (error) return <ErrorState error={error} onRetry={() => refetch()} />

  const { overview, continueCard, recommendations } = data
  const firstName = user?.name?.split(' ')[0]
  const conceptRecommendations = recommendations.filter((r) => r.conceptId)
  const challengeRecommendation = recommendations.find((r) => r.challengeSlug)

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">
          {firstName ? `Hello, ${firstName}` : 'Napkin Chain'}
        </h1>
        <p className="mt-1.5 text-[15px] text-ink-secondary">
          {overview.totalEstimates === 0
            ? 'Start anywhere. You can learn the concepts as you hit them.'
            : `${overview.skillsStrong} of ${overview.skillsTotal} skills strong · ${overview.chainsSolved} chain${overview.chainsSolved === 1 ? '' : 's'} solved`}
        </p>
      </header>

      <section className="space-y-3">
        <SectionLabel>Your progress</SectionLabel>
        <Link
          to="/app/progress"
          className="flex items-center gap-5 rounded-lg border border-line bg-surface px-5 py-4 transition-colors hover:border-line-strong"
        >
          <div>
            <div className="tnum text-[30px] font-semibold leading-none tracking-[-0.02em]">
              {Math.round(overview.intuition * 100)}%
            </div>
            <div className="mt-1 text-xs text-ink-muted">System design intuition</div>
          </div>
          <div className="ml-auto hidden gap-8 sm:flex">
            <Stat label="Accuracy" value={overview.averageRatio ? `${overview.averageRatio.toFixed(1)}x` : '—'} />
            <Stat
              label="Speed"
              value={overview.secondsPerStep ? `${Math.round(overview.secondsPerStep)}s` : '—'}
            />
            <Stat label="Streak" value={overview.streakDays ? `${overview.streakDays}d` : '—'} />
          </div>
        </Link>
      </section>

      {continueCard && (
        <section className="space-y-3">
          <SectionLabel>Continue</SectionLabel>
          <Card className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
            <div>
              <h3 className="text-[17px] font-semibold tracking-[-0.01em]">
                {continueCard.challengeTitle}
              </h3>
              <p className="mt-1 text-sm text-ink-secondary">
                {continueCard.solvedCount} / {continueCard.totalSteps} estimates ·{' '}
                {DIFFICULTY_LABEL[continueCard.difficulty]} · {relativeTime(continueCard.lastActivityAt)}
              </p>
            </div>
            <ButtonLink to={`/app/challenges/${continueCard.challengeSlug}/build`}>
              Continue
            </ButtonLink>
          </Card>
        </section>
      )}

      {conceptRecommendations.length > 0 && (
        <section className="space-y-3">
          <SectionLabel>Recommended</SectionLabel>
          <ul className="space-y-2">
            {conceptRecommendations.map((item) => (
              <RecommendationRow key={item.conceptId} item={item} />
            ))}
          </ul>
        </section>
      )}

      {challengeRecommendation && (
        <section className="space-y-3">
          <SectionLabel>
            {challengeRecommendation.kind === 'level_up' ? 'Step up' : 'New challenge'}
          </SectionLabel>
          <Card className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
            <div>
              <h3 className="text-[17px] font-semibold tracking-[-0.01em]">
                {challengeRecommendation.title}
              </h3>
              <p className="mt-1 text-sm text-ink-secondary">{challengeRecommendation.reason}</p>
            </div>
            <ButtonLink
              to={`/app/challenges/${challengeRecommendation.challengeSlug}`}
              variant="secondary"
            >
              Start
            </ButtonLink>
          </Card>
        </section>
      )}

      <Link
        to="/app/challenges"
        className="block text-sm text-accent transition-colors hover:text-accent-strong"
      >
        Browse all challenges →
      </Link>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="tnum text-[17px] font-semibold leading-none">{value}</div>
      <div className="mt-1.5 text-xs text-ink-muted">{label}</div>
    </div>
  )
}

function RecommendationRow({ item }: { item: Recommendation }) {
  return (
    <li>
      <Link
        to={`/app/learn/${item.conceptId}`}
        className="flex items-center justify-between gap-4 rounded-lg border border-line bg-surface px-5 py-3.5 transition-colors hover:border-line-strong"
      >
        <div>
          <h3 className="text-[15px] font-medium">{item.title}</h3>
          <p className="mt-0.5 text-sm text-ink-secondary">{item.reason}</p>
        </div>
        <span className="shrink-0 text-sm font-medium text-accent">{item.actionLabel}</span>
      </Link>
    </li>
  )
}

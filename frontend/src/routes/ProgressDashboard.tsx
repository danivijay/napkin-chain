import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { SectionLabel } from '@/components/ui/Card'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { Meter } from '@/components/ui/Meter'
import { AREA_ICONS, type ConceptArea } from '@/components/Icons'
import { api } from '@/lib/api'
import { formatRatio } from '@/lib/format'

export function ProgressDashboard() {
  const overview = useQuery({ queryKey: ['progress'], queryFn: api.progress })
  const skills = useQuery({ queryKey: ['skills'], queryFn: api.skills })

  if (overview.isPending || skills.isPending) return <LoadingScreen />
  if (overview.error) return <ErrorState error={overview.error} onRetry={() => overview.refetch()} />
  if (skills.error) return <ErrorState error={skills.error} onRetry={() => skills.refetch()} />

  const data = overview.data

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Progress</h1>
        <p className="mt-1.5 text-[15px] text-ink-secondary">
          What you can reason about quickly, and what still slows you down.
        </p>
      </header>

      <section>
        <SectionLabel>System design intuition</SectionLabel>
        <div className="mt-3 flex flex-wrap items-end gap-x-12 gap-y-6">
          <div>
            <div className="tnum text-[52px] font-semibold leading-none tracking-[-0.03em]">
              {Math.round(data.intuition * 100)}%
            </div>
            {data.interviewReady && (
              <p className="mt-2 text-sm text-good">Interview-ready across your practised areas.</p>
            )}
          </div>
          <dl className="grid grid-cols-2 gap-x-10 gap-y-4 sm:grid-cols-4">
            <Metric
              label="Accuracy"
              value={data.averageRatio ? `${formatRatio(data.averageRatio)} avg error` : '—'}
            />
            <Metric
              label="Speed"
              value={data.secondsPerStep ? `${Math.round(data.secondsPerStep)} sec / step` : '—'}
            />
            <Metric label="Chains solved" value={String(data.chainsSolved)} />
            <Metric label="Skills strong" value={`${data.skillsStrong} / ${data.skillsTotal}`} />
          </dl>
        </div>
      </section>

      <section className="space-y-3">
        <SectionLabel>Strength by area</SectionLabel>
        <div className="space-y-2.5 rounded-lg border border-line bg-surface px-5 py-5">
          {data.areas.map((area) => {
            const AreaIcon = AREA_ICONS[area.area as ConceptArea] ?? AREA_ICONS.traffic
            return (
              <div key={area.area} className="flex items-center gap-2.5">
                <AreaIcon className="h-4 w-4 shrink-0 text-ink-faint" />
                <Meter
                  label={area.title}
                  value={area.strength}
                  detail={`${area.practicedCount}/${area.conceptCount} practised`}
                  tone={area.strength >= 0.7 ? 'good' : area.strength >= 0.35 ? 'accent' : 'warn'}
                />
              </div>
            )
          })}
        </div>
      </section>

      <section className="space-y-3">
        <SectionLabel>Skills</SectionLabel>
        <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
          {skills.data.concepts.map((concept) => (
            <li key={concept.conceptId}>
              <Link
                to={`/app/learn/${concept.conceptId}`}
                className="flex items-center gap-4 px-5 py-3 transition-colors hover:bg-subtle/60"
              >
                <span className="flex-1 text-[15px]">{concept.title}</span>
                <Meter
                  value={concept.mastery}
                  tone={concept.mastery >= 0.7 ? 'good' : concept.mastery >= 0.4 ? 'accent' : 'warn'}
                />
                <span className="tnum w-10 text-right text-xs text-ink-muted">
                  {concept.attempts > 0 ? `${Math.round(concept.mastery * 100)}%` : '—'}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="flex flex-wrap gap-x-10 gap-y-4 border-t border-line pt-6 text-sm text-ink-secondary">
        <span>
          <span className="tnum font-medium text-ink">{data.streakDays}</span> day streak
          {data.bestStreakDays > data.streakDays && (
            <span className="text-ink-muted"> · best {data.bestStreakDays}</span>
          )}
        </span>
        <span>
          <span className="tnum font-medium text-ink">{data.totalEstimates}</span> estimates made
        </span>
        {data.weeklyImprovement !== null && (
          <span>
            <span className="tnum font-medium text-ink">
              {data.weeklyImprovement > 0 ? '+' : ''}
              {Math.round(data.weeklyImprovement * 100)}%
            </span>{' '}
            accuracy this week
          </span>
        )}
      </section>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-muted">{label}</dt>
      <dd className="tnum mt-1 text-[15px] font-medium">{value}</dd>
    </div>
  )
}

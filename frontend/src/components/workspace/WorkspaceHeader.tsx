import { Link } from 'react-router-dom'
import type { AttemptState } from '@/types'
import { MODE_LABEL, formatDuration } from '@/lib/format'

export function WorkspaceHeader({
  state,
  elapsed,
}: {
  state: AttemptState
  elapsed: number
}) {
  const timed = state.mode !== 'learn'

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-line bg-paper/90 px-4 backdrop-blur sm:px-6">
      <Link
        to={`/app/challenges/${state.challengeSlug}`}
        className="text-sm text-ink-muted transition-colors hover:text-ink"
        aria-label="Leave the workspace"
      >
        ←
      </Link>
      <h1 className="truncate text-[15px] font-semibold tracking-[-0.01em]">
        {state.challengeTitle}
      </h1>
      <span className="hidden text-xs text-ink-muted sm:inline">{MODE_LABEL[state.mode]}</span>

      <div className="ml-auto flex items-center gap-4">
        <span className="tnum text-sm text-ink-secondary">
          {state.solvedCount} / {state.totalSteps}
        </span>
        {timed && (
          <span className="tnum font-mono text-sm text-ink-muted" aria-label="Elapsed time">
            {formatDuration(elapsed)}
          </span>
        )}
      </div>
    </header>
  )
}

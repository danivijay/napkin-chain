import type { ChainNode } from '@/types'
import { CautionMark, CheckMark, LockMark } from '@/components/napkin/Marks'

const TONE: Record<string, string> = {
  locked: 'border-line bg-subtle/50 text-ink-faint',
  available: 'border-line-strong bg-surface text-ink-secondary border-dashed',
  active: 'border-accent bg-accent-soft text-ink shadow-card',
  solved: 'border-good-line bg-good-soft text-ink',
  mastered: 'border-good-line bg-good-soft text-ink',
  weak: 'border-warn-line bg-warn-soft text-ink',
}

function StatusRow({ node }: { node: ChainNode }) {
  switch (node.status) {
    case 'mastered':
      return (
        <span className="flex shrink-0 items-center gap-1 text-[10px] font-medium text-good">
          <CheckMark className="h-3.5 w-3.5" /> Mastered
        </span>
      )
    case 'solved':
      return <CheckMark className="h-3.5 w-3.5 text-good" />
    case 'weak':
      return (
        <span className="flex items-center gap-1 text-[11px] font-medium text-warn">
          <CautionMark className="h-3.5 w-3.5" /> Needs review
        </span>
      )
    case 'active':
      return <span className="text-[11px] font-medium text-accent">Your turn</span>
    case 'available':
      return <span className="text-[11px] text-ink-muted">Open</span>
    default:
      return <LockMark className="h-3.5 w-3.5 text-ink-faint" />
  }
}

export function ChainNodeCard({
  node,
  onSelect,
  compact = false,
}: {
  node: ChainNode
  onSelect?: (node: ChainNode) => void
  compact?: boolean
}) {
  const interactive = Boolean(onSelect) && node.status !== 'locked'
  const value =
    node.displayValue ?? (node.status === 'active' || node.status === 'available' ? '?' : '')

  return (
    <button
      type="button"
      disabled={!interactive}
      onClick={() => onSelect?.(node)}
      aria-current={node.status === 'active' ? 'step' : undefined}
      className={`flex h-full w-full flex-col justify-between rounded-md border px-3 py-2.5 text-left transition-[box-shadow,border-color,background-color] duration-200 ${
        TONE[node.status]
      } ${interactive ? 'cursor-pointer hover:border-ink-muted' : 'cursor-default'} ${
        compact ? 'gap-1' : ''
      }`}
    >
      <span className="line-clamp-2 text-[12px] font-medium leading-tight">{node.label}</span>
      <span className="flex items-end justify-between gap-2">
        <span className="tnum truncate font-mono text-[15px] font-semibold leading-none">
          {value}
        </span>
        <StatusRow node={node} />
      </span>
    </button>
  )
}

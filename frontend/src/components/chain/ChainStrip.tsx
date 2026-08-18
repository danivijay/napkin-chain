import type { ChainNode } from '@/types'

const DOT: Record<string, string> = {
  locked: 'bg-sunken',
  available: 'bg-line-strong',
  active: 'bg-accent',
  solved: 'bg-good',
  mastered: 'bg-good',
  weak: 'bg-warn',
}

/**
 * Mobile: the chain as a progress spine, not a graph. The current step is
 * named; everything else is a mark. Tapping opens the full chain.
 */
export function ChainStrip({
  chain,
  currentNodeId,
  onOpen,
}: {
  chain: ChainNode[]
  currentNodeId: string | null
  onOpen: () => void
}) {
  const estimates = chain.filter((node) => node.type === 'estimate')
  const current = chain.find((node) => node.id === currentNodeId)
  const solved = estimates.filter((node) =>
    ['solved', 'mastered', 'weak'].includes(node.status),
  ).length

  return (
    <button
      type="button"
      onClick={onOpen}
      className="flex w-full items-center gap-3 border-b border-line bg-surface/90 px-4 py-2.5 backdrop-blur"
    >
      <div className="flex flex-1 items-center gap-[3px]" aria-hidden>
        {estimates.map((node) => (
          <span
            key={node.id}
            className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${DOT[node.status]}`}
          />
        ))}
      </div>
      <span className="tnum shrink-0 text-xs text-ink-muted">
        {solved} / {estimates.length}
      </span>
      <span className="shrink-0 text-xs font-medium text-accent">
        {current ? 'View chain' : 'Chain'}
      </span>
    </button>
  )
}

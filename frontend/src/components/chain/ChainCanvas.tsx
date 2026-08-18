import { useMemo } from 'react'
import type { ChainNode } from '@/types'
import { ChainNodeCard } from './ChainNodeCard'
import { NODE_HEIGHT, NODE_WIDTH, edgePath, layoutChain } from './layout'

const EDGE_TONE: Record<string, string> = {
  locked: 'stroke-line-strong',
  available: 'stroke-line-strong',
  active: 'stroke-accent',
  solved: 'stroke-good-line',
  mastered: 'stroke-good-line',
  weak: 'stroke-warn-line',
}

/** The napkin itself: the whole chain, drawn. Desktop and tablet. */
export function ChainCanvas({
  chain,
  onSelect,
  className = '',
}: {
  chain: ChainNode[]
  onSelect?: (node: ChainNode) => void
  className?: string
}) {
  const layout = useMemo(() => layoutChain(chain), [chain])

  return (
    // The napkin never forces the page to scroll sideways - it scrolls itself.
    <div className={`flex justify-center overflow-x-auto ${className}`}>
      <div
        className="relative shrink-0"
        style={{ width: layout.width, height: layout.height }}
        role="list"
        aria-label="Estimation chain"
      >
        <svg
          className="pointer-events-none absolute inset-0 overflow-visible"
          width={layout.width}
          height={layout.height}
          aria-hidden
        >
          <defs>
            <marker
              id="nc-arrow"
              markerWidth="7"
              markerHeight="7"
              refX="3.2"
              refY="3.2"
              orient="auto"
            >
              <path
                d="M1 1.2 L5.4 3.2 L1 5.2"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.1"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </marker>
          </defs>
          {layout.edges.map(({ from, to }) => (
            <path
              key={`${from.node.id}-${to.node.id}`}
              d={edgePath(from, to)}
              fill="none"
              strokeWidth="1.5"
              strokeLinecap="round"
              markerEnd="url(#nc-arrow)"
              className={`${EDGE_TONE[from.node.status] ?? 'stroke-line'} text-current transition-colors duration-300`}
            />
          ))}
        </svg>

        {layout.nodes.map(({ node, x, y }) => (
          <div
            key={node.id}
            role="listitem"
            className="absolute"
            style={{ left: x, top: y, width: NODE_WIDTH, height: NODE_HEIGHT }}
          >
            <ChainNodeCard node={node} onSelect={onSelect} />
          </div>
        ))}
      </div>
    </div>
  )
}

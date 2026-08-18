import type { ChainNode } from '@/types'

export interface PlacedNode {
  node: ChainNode
  rank: number
  column: number
  x: number
  y: number
}

export interface ChainLayout {
  nodes: PlacedNode[]
  edges: { from: PlacedNode; to: PlacedNode }[]
  width: number
  height: number
}

export const NODE_WIDTH = 172
export const NODE_HEIGHT = 82
const GAP_X = 28
const GAP_Y = 52

/**
 * Lays the chain out as a DAG: rank is the longest dependency path to a node,
 * so an estimate always sits below everything it depends on. Deterministic,
 * so the napkin looks the same every time you open it.
 */
export function layoutChain(chain: ChainNode[]): ChainLayout {
  const byId = new Map(chain.map((node) => [node.id, node]))
  const ranks = new Map<string, number>()

  const rankOf = (id: string, seen = new Set<string>()): number => {
    if (ranks.has(id)) return ranks.get(id)!
    if (seen.has(id)) return 0 // defensive: content should never contain a cycle
    seen.add(id)
    const node = byId.get(id)
    const deps = node?.dependsOn.filter((dep) => byId.has(dep)) ?? []
    const rank = deps.length ? Math.max(...deps.map((dep) => rankOf(dep, seen))) + 1 : 0
    ranks.set(id, rank)
    return rank
  }
  chain.forEach((node) => rankOf(node.id))

  const rows = new Map<number, ChainNode[]>()
  chain.forEach((node) => {
    const rank = ranks.get(node.id)!
    rows.set(rank, [...(rows.get(rank) ?? []), node])
  })

  const widest = Math.max(...[...rows.values()].map((row) => row.length))
  const width = widest * NODE_WIDTH + (widest - 1) * GAP_X
  const placed: PlacedNode[] = []

  ;[...rows.keys()]
    .sort((a, b) => a - b)
    .forEach((rank) => {
      const row = rows.get(rank)!
      const rowWidth = row.length * NODE_WIDTH + (row.length - 1) * GAP_X
      const offset = (width - rowWidth) / 2
      row.forEach((node, column) => {
        placed.push({
          node,
          rank,
          column,
          x: offset + column * (NODE_WIDTH + GAP_X),
          y: rank * (NODE_HEIGHT + GAP_Y),
        })
      })
    })

  const placedById = new Map(placed.map((item) => [item.node.id, item]))
  const edges = placed.flatMap((to) =>
    to.node.dependsOn
      .map((dep) => placedById.get(dep))
      .filter((from): from is PlacedNode => Boolean(from))
      .map((from) => ({ from, to })),
  )

  const depth = Math.max(...placed.map((item) => item.rank)) + 1
  return { nodes: placed, edges, width, height: depth * NODE_HEIGHT + (depth - 1) * GAP_Y }
}

/** A hand-drawn-feeling connector: a slight bow, never a straight ruler line. */
export function edgePath(from: PlacedNode, to: PlacedNode): string {
  const x1 = from.x + NODE_WIDTH / 2
  const y1 = from.y + NODE_HEIGHT
  const x2 = to.x + NODE_WIDTH / 2
  const y2 = to.y
  const midY = (y1 + y2) / 2
  const bow = x1 === x2 ? 2.5 : 0
  return `M ${x1} ${y1} C ${x1 + bow} ${midY}, ${x2 - bow} ${midY}, ${x2} ${y2 - 6}`
}

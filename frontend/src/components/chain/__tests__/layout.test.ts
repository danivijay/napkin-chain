import { describe, expect, it } from 'vitest'
import { layoutChain } from '@/components/chain/layout'
import { chainNode } from '@/test/fixtures'

const CHAIN = [
  chainNode({ id: 'dau', type: 'input', dependsOn: [] }),
  chainNode({ id: 'requests', dependsOn: ['dau'] }),
  chainNode({ id: 'storage', dependsOn: ['dau'] }),
  chainNode({ id: 'qps', dependsOn: ['requests'] }),
]

describe('layoutChain', () => {
  it('places a node below everything it depends on', () => {
    const { nodes } = layoutChain(CHAIN)
    const rank = (id: string) => nodes.find((n) => n.node.id === id)!.rank

    expect(rank('dau')).toBe(0)
    expect(rank('requests')).toBe(1)
    expect(rank('storage')).toBe(1) // a parallel branch, same row
    expect(rank('qps')).toBe(2)
  })

  it('draws one edge per dependency', () => {
    const { edges } = layoutChain(CHAIN)
    expect(edges).toHaveLength(3)
    expect(edges.map((e) => `${e.from.node.id}->${e.to.node.id}`)).toContain('dau->storage')
  })

  it('is deterministic', () => {
    expect(layoutChain(CHAIN)).toEqual(layoutChain(CHAIN))
  })
})

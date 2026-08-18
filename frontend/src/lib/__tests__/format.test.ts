import { describe, expect, it } from 'vitest'
import { formatRatio, humanize, parseEstimate } from '@/lib/format'

describe('parseEstimate', () => {
  it('accepts what an engineer would actually type', () => {
    expect(parseEstimate('1B')).toBe(1e9)
    expect(parseEstimate('12k')).toBe(12_000)
    expect(parseEstimate('1.5 M')).toBe(1.5e6)
    expect(parseEstimate('12,000')).toBe(12_000)
    expect(parseEstimate('3e9')).toBe(3e9)
    expect(parseEstimate('50')).toBe(50)
  })

  it('returns null when there is no number', () => {
    expect(parseEstimate('')).toBeNull()
    expect(parseEstimate('   ')).toBeNull()
    expect(parseEstimate('about a million')).toBeNull()
  })
})

describe('humanize', () => {
  it('reads as magnitudes, not as digits', () => {
    expect(humanize(1e9, 'req/day')).toBe('1B req/day')
    expect(humanize(12_500, 'QPS')).toBe('12.5K QPS')
    expect(humanize(30_000)).toBe('30K')
    expect(humanize(350, 'GB/s')).toBe('350 GB/s')
  })
})

describe('formatRatio', () => {
  it('keeps one decimal until the number stops mattering', () => {
    expect(formatRatio(1.2)).toBe('1.2x')
    expect(formatRatio(26.7)).toBe('27x')
  })
})

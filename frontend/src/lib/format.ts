/** Human-readable magnitudes, matching how the backend labels chain nodes. */
export function humanize(value: number, unit = ''): string {
  const magnitude = Math.abs(value)
  const units: [number, string][] = [
    [1e12, 'T'],
    [1e9, 'B'],
    [1e6, 'M'],
    [1e3, 'K'],
  ]
  let text: string
  const scale = units.find(([threshold]) => magnitude >= threshold)
  if (scale) {
    text = trimZeros((value / scale[0]).toFixed(1)) + scale[1]
  } else if (magnitude >= 100 || Number.isInteger(value)) {
    text = value.toLocaleString('en-US', { maximumFractionDigits: 0 })
  } else if (magnitude >= 1) {
    text = trimZeros(value.toFixed(1))
  } else {
    text = value.toPrecision(2).replace(/0+$/, '').replace(/\.$/, '')
  }
  return unit ? `${text} ${unit}` : text
}

function trimZeros(text: string): string {
  return text.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1')
}

/**
 * Parses what an engineer would actually type: "1B", "12k", "1.5 M", "3e9",
 * "12,000". Returns null when there is no number in there.
 */
export function parseEstimate(input: string): number | null {
  const cleaned = input.trim().toLowerCase().replace(/,/g, '').replace(/\s+/g, '')
  if (!cleaned) return null

  const match = cleaned.match(/^(-?\d*\.?\d+(?:e[-+]?\d+)?)([kmbt])?/)
  if (!match) return null

  const value = Number(match[1])
  if (!Number.isFinite(value)) return null

  const multiplier = { k: 1e3, m: 1e6, b: 1e9, t: 1e12 }[match[2] ?? ''] ?? 1
  return value * multiplier
}

export function formatRatio(ratio: number): string {
  return ratio < 10 ? `${ratio.toFixed(1)}x` : `${Math.round(ratio)}x`
}

export function formatDuration(seconds: number): string {
  const total = Math.max(0, Math.round(seconds))
  const minutes = Math.floor(total / 60)
  return `${minutes}:${String(total % 60).padStart(2, '0')}`
}

export function relativeTime(iso: string): string {
  const then = new Date(iso).getTime()
  const minutes = Math.round((Date.now() - then) / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.round(hours / 24)
  return days === 1 ? 'yesterday' : `${days}d ago`
}

export const CLASSIFICATION_LABEL: Record<string, string> = {
  excellent: 'Excellent',
  very_good: 'Very good',
  good: 'Good',
  developing: 'Developing',
  needs_review: 'Needs review',
}

export const DIFFICULTY_LABEL: Record<string, string> = {
  foundation: 'Foundation',
  builder: 'Builder',
  system: 'System',
  interview: 'Interview',
}

export const MODE_LABEL: Record<string, string> = {
  learn: 'Learn',
  practice: 'Practice',
  interview: 'Interview',
}

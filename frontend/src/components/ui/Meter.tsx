/** A strength bar. Blocks, not a gradient - it should read like a gauge. */
export function Meter({
  value,
  label,
  detail,
  tone = 'accent',
}: {
  value: number
  label?: string
  detail?: string
  tone?: 'accent' | 'good' | 'warn'
}) {
  const filled = Math.round(Math.max(0, Math.min(1, value)) * 12)
  const color =
    tone === 'good' ? 'bg-good' : tone === 'warn' ? 'bg-warn' : 'bg-accent'

  return (
    <div className="flex items-center gap-3">
      {label && <span className="w-24 shrink-0 text-sm text-ink-secondary">{label}</span>}
      <div className="flex gap-[3px]" role="meter" aria-valuenow={Math.round(value * 100)} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
        {Array.from({ length: 12 }, (_, i) => (
          <span
            key={i}
            className={`h-3 w-[6px] rounded-[1px] ${i < filled ? color : 'bg-sunken'}`}
          />
        ))}
      </div>
      {detail && <span className="tnum text-xs text-ink-muted">{detail}</span>}
    </div>
  )
}

/**
 * `tone="current"` follows the surrounding text colour, so a spinner reads on
 * any button, dark or light.
 */
export function Spinner({
  className = '',
  tone = 'default',
}: {
  className?: string
  tone?: 'default' | 'current'
}) {
  const colours = tone === 'current' ? 'border-current border-r-transparent' : 'border-line-strong border-t-ink'
  return (
    <span
      className={`inline-block h-4 w-4 shrink-0 animate-spin rounded-full border-2 ${colours} ${className}`}
      aria-hidden
    />
  )
}

/** Cold-start friendly: says what is happening without exposing infrastructure. */
export function LoadingScreen({ message = 'Loading' }: { message?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-ink-muted"
    >
      <Spinner />
      <p className="text-sm">{message}</p>
    </div>
  )
}

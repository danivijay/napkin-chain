export function Spinner({ className = '' }: { className?: string }) {
  return (
    <span
      className={`inline-block h-4 w-4 animate-spin rounded-full border-2 border-line-strong border-t-ink ${className}`}
      aria-hidden
    />
  )
}

/** Cold-start friendly: says what is happening without exposing infrastructure. */
export function LoadingScreen({ message = 'Loading' }: { message?: string }) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-ink-muted">
      <Spinner />
      <p className="text-sm">{message}</p>
    </div>
  )
}

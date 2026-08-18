import { ApiError } from '@/lib/api'
import { Button } from './Button'

/** Infrastructure never leaks into the copy - only what the user can do next. */
export function ErrorState({
  error,
  onRetry,
  className = '',
}: {
  error: unknown
  onRetry?: () => void
  className?: string
}) {
  const transient = error instanceof ApiError && error.isTransient
  const message = transient
    ? 'The server is taking a moment to wake up.'
    : error instanceof ApiError
      ? error.detail
      : 'Something went wrong.'

  return (
    <div className={`rounded-lg border border-line bg-surface px-5 py-6 text-center ${className}`}>
      <p className="text-sm text-ink-secondary">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  )
}

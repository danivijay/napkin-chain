import { useState } from 'react'
import { Link, Navigate, useLocation, useSearchParams } from 'react-router-dom'
import { Wordmark } from '@/components/Logo'
import { Button, buttonClass } from '@/components/ui/Button'
import { GoogleGlyph } from './Landing'
import { api } from '@/lib/api'
import { useAuth, useDevLogin } from '@/hooks/useAuth'

const ERRORS: Record<string, string> = {
  auth_failed: "That sign-in didn't complete. Try again.",
  auth_denied: 'Google declined that sign-in. If this app is still unpublished, your address has to be added as a test user.',
  auth_state: 'That sign-in took too long, or cookies were blocked. Try again.',
  auth_exchange: "We couldn't confirm that account with Google.",
  google_not_configured: 'Google sign-in is not configured on this server.',
}

export function Login() {
  const { isAuthenticated, isPending, googleEnabled, devLoginEnabled } = useAuth()
  const [params] = useSearchParams()
  const location = useLocation()
  const devLogin = useDevLogin()
  const [email, setEmail] = useState('dev@napkinchain.app')

  const from = (location.state as { from?: string } | null)?.from ?? '/app'
  if (!isPending && isAuthenticated) return <Navigate to={from} replace />

  const error = params.get('error')

  return (
    <div className="flex min-h-dvh flex-col napkin-surface">
      <header className="mx-auto flex h-16 w-full max-w-5xl items-center px-5">
        <Link to="/" className="text-ink">
          <Wordmark />
        </Link>
      </header>

      <main className="flex flex-1 items-center justify-center px-5 pb-24">
        <div className="w-full max-w-sm">
          <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Sign in</h1>
          <p className="mt-2 text-sm text-ink-secondary">
            One click, then straight into the product.
          </p>

          {error && (
            <p className="mt-5 rounded-md border border-warn-line bg-warn-soft px-3 py-2.5 text-sm text-warn">
              {ERRORS[error] ?? 'Something went wrong signing in.'}
            </p>
          )}

          <a
            href={api.googleStartUrl(from)}
            className={buttonClass('primary', 'lg', 'mt-7 w-full')}
            aria-disabled={!googleEnabled}
          >
            <GoogleGlyph /> Continue with Google
          </a>

          {!googleEnabled && (
            <p className="mt-3 text-xs text-ink-muted">
              Google credentials are not configured on this server yet.
            </p>
          )}

          {devLoginEnabled && (
            <form
              className="mt-8 border-t border-line pt-6"
              onSubmit={(event) => {
                event.preventDefault()
                devLogin.mutate({ email, name: 'Local Dev' })
              }}
            >
              <label className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-muted">
                Local development
              </label>
              <div className="mt-3 flex gap-2">
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  type="email"
                  className="h-10 flex-1 rounded-md border border-line bg-surface px-3 text-sm outline-none focus:border-accent"
                  aria-label="Development email"
                />
                <Button type="submit" variant="secondary" disabled={devLogin.isPending}>
                  Sign in
                </Button>
              </div>
              {devLogin.isError && (
                <p className="mt-2 text-xs text-danger">{devLogin.error.message}</p>
              )}
            </form>
          )}
        </div>
      </main>
    </div>
  )
}

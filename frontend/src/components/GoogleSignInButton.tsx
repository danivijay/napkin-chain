import { useEffect, useState } from 'react'
import { buttonClass } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'

/**
 * A plain link, because sign-in is a full-page redirect through the server.
 * On a cold start the first hop can take several seconds, so the button says
 * it is working rather than looking dead.
 */
export function GoogleSignInButton({
  redirectTo,
  disabled = false,
  className = '',
}: {
  redirectTo?: string
  disabled?: boolean
  className?: string
}) {
  const [redirecting, setRedirecting] = useState(false)

  // Coming back with the browser's Back button restores this page from the
  // back/forward cache with the spinner still showing; reset it.
  useEffect(() => {
    const reset = (event: PageTransitionEvent) => event.persisted && setRedirecting(false)
    window.addEventListener('pageshow', reset)
    return () => window.removeEventListener('pageshow', reset)
  }, [])

  return (
    <a
      href={api.googleStartUrl(redirectTo)}
      onClick={(event) => {
        if (disabled || redirecting) {
          event.preventDefault()
          return
        }
        setRedirecting(true)
      }}
      className={buttonClass('primary', 'lg', `${className} ${redirecting ? 'pointer-events-none opacity-80' : ''}`)}
      aria-disabled={disabled || undefined}
      aria-busy={redirecting || undefined}
    >
      {redirecting ? <Spinner tone="current" /> : <GoogleGlyph />}
      {redirecting ? 'Connecting to Google…' : 'Continue with Google'}
    </a>
  )
}

export function GoogleGlyph() {
  return (
    <svg viewBox="0 0 18 18" className="h-4 w-4" aria-hidden>
      <path fill="#4285F4" d="M17.6 9.2c0-.6-.1-1.3-.2-1.9H9v3.5h4.8a4.1 4.1 0 0 1-1.8 2.7v2.2h2.9c1.7-1.6 2.7-3.9 2.7-6.5Z" />
      <path fill="#34A853" d="M9 18c2.4 0 4.5-.8 6-2.2l-2.9-2.3c-.8.6-1.9.9-3.1.9-2.4 0-4.4-1.6-5.1-3.8H.9v2.3A9 9 0 0 0 9 18Z" />
      <path fill="#FBBC05" d="M3.9 10.7a5.4 5.4 0 0 1 0-3.4V5H.9a9 9 0 0 0 0 8l3-2.3Z" />
      <path fill="#EA4335" d="M9 3.6c1.3 0 2.5.5 3.4 1.3l2.6-2.6A9 9 0 0 0 .9 5l3 2.3C4.6 5.2 6.6 3.6 9 3.6Z" />
    </svg>
  )
}

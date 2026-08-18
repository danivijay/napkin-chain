import { Link, Navigate } from 'react-router-dom'
import { Wordmark } from '@/components/Logo'
import { buttonClass } from '@/components/ui/Button'
import { ArrowDown } from '@/components/napkin/Marks'
import { api } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'

const DEMO_CHAIN = [
  { label: '100M users', tone: 'given' },
  { label: '1B requests / day', tone: 'solved' },
  { label: '10K QPS', tone: 'solved' },
  { label: '30K peak QPS', tone: 'solved' },
  { label: 'Bandwidth', tone: 'open' },
  { label: 'Storage', tone: 'locked' },
]

const TONE: Record<string, string> = {
  given: 'border-line-strong bg-surface text-ink',
  solved: 'border-good-line bg-good-soft text-ink',
  open: 'border-accent bg-accent-soft text-ink',
  locked: 'border-line border-dashed bg-subtle/60 text-ink-faint',
}

export function Landing() {
  const { isAuthenticated, isPending } = useAuth()
  if (!isPending && isAuthenticated) return <Navigate to="/app" replace />

  return (
    <div className="min-h-dvh napkin-surface">
      <header className="mx-auto flex h-16 max-w-5xl items-center justify-between px-5">
        <Wordmark />
        <Link to="/login" className="text-sm text-ink-secondary hover:text-ink">
          Sign in
        </Link>
      </header>

      <main className="mx-auto max-w-5xl px-5 pb-24">
        <section className="grid items-center gap-12 pt-12 sm:pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
          <div>
            <h1 className="text-[40px] font-semibold leading-[1.05] tracking-[-0.03em] sm:text-[56px]">
              Build systems
              <br />
              on a <span className="annotated">napkin</span>.
            </h1>
            <p className="mt-6 max-w-md text-[17px] leading-relaxed text-ink-secondary">
              Practice real system-design estimation one step at a time. Every number you
              produce becomes the input to the next.
            </p>

            <div className="mt-9 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
              <a href={api.googleStartUrl()} className={buttonClass('primary', 'lg')}>
                <GoogleGlyph /> Continue with Google
              </a>
              <Link to="/login" className="text-sm text-ink-muted hover:text-ink">
                Other sign-in options
              </Link>
            </div>

            <p className="mt-6 text-sm text-ink-muted">
              No registration form. No course to enrol in.
            </p>
          </div>

          <div className="flex justify-center lg:justify-end">
            <div className="flex flex-col items-center">
              {DEMO_CHAIN.map((item, index) => (
                <div key={item.label} className="flex flex-col items-center">
                  <div
                    className={`w-52 rounded-md border px-4 py-3 text-center font-mono text-[14px] ${TONE[item.tone]}`}
                  >
                    {item.label}
                  </div>
                  {index < DEMO_CHAIN.length - 1 && (
                    <ArrowDown className="text-line-strong" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-24 border-t border-line pt-10">
          <p className="handwritten text-[26px] leading-[1.35] text-ink-secondary">
            Real systems. Connected estimates. Better intuition.
          </p>
          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            <Pitch
              title="Chains, not quizzes"
              body="Solve a whole system's capacity path, where each estimate feeds the next."
            />
            <Pitch
              title="Order of magnitude"
              body="Scored on how many times away you were, not on exact arithmetic."
            />
            <Pitch
              title="Learn where you fail"
              body="Miss a step, learn that one concept, and land back on the exact step."
            />
          </div>
        </section>
      </main>
    </div>
  )
}

function Pitch({ title, body }: { title: string; body: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-ink-secondary">{body}</p>
    </div>
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

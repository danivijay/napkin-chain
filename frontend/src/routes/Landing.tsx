import { Link, Navigate } from 'react-router-dom'
import { GoogleSignInButton } from '@/components/GoogleSignInButton'
import { Wordmark } from '@/components/Logo'
import { CircledNumber, TornEdge } from '@/components/napkin/Sketch'
import { HeroChain } from '@/components/landing/HeroChain'
import { QuizVsChain } from '@/components/landing/QuizVsChain'
import { FeedbackSample } from '@/components/landing/FeedbackSample'
import { LoopDiagram } from '@/components/landing/LoopDiagram'
import { AREA_ICONS } from '@/components/Icons'
import { useAuth } from '@/hooks/useAuth'

const AREAS = [
  { area: 'traffic', title: 'Traffic', detail: 'DAU → requests → QPS → peak' },
  { area: 'storage', title: 'Storage', detail: 'Payload sizes, retention, replication' },
  { area: 'bandwidth', title: 'Bandwidth', detail: 'Egress at peak, not at average' },
  { area: 'capacity', title: 'Capacity', detail: 'QPS per server, headroom, fleet size' },
  { area: 'assumptions', title: 'Assumptions', detail: 'Choosing them, and defending them' },
] as const

const SYSTEMS = ['Instagram feed', 'Chat system', 'URL shortener']
const SYSTEMS_COMING = ['WhatsApp', 'YouTube', 'Rate limiter', 'Video streaming']

export function Landing() {
  const { isAuthenticated, isPending } = useAuth()
  if (!isPending && isAuthenticated) return <Navigate to="/app" replace />

  return (
    <div className="min-h-dvh bg-paper">
      <header className="sticky top-0 z-20 border-b border-line bg-paper/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-5">
          <Wordmark />
          <div className="flex items-center gap-5">
            <a href="#how" className="hidden text-sm text-ink-secondary hover:text-ink sm:block">
              How it works
            </a>
            <Link to="/login" className="text-sm text-ink-secondary hover:text-ink">
              Sign in
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* ---------------------------------------------------------- hero */}
        <section className="napkin-surface border-b border-line">
          <div className="mx-auto grid max-w-5xl items-center gap-12 px-5 py-14 lg:grid-cols-[1.02fr_0.98fr] lg:gap-14 lg:py-20">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-accent">
                System-design estimation, drilled
              </p>
              <h1 className="mt-4 text-[42px] font-semibold leading-[1.03] tracking-[-0.035em] sm:text-[56px]">
                Build systems
                <br />
                on a <span className="annotated">napkin</span>.
              </h1>
              <p className="mt-6 max-w-md text-[17px] leading-relaxed text-ink-secondary">
                Most engineers can draw the boxes. Far fewer can answer{' '}
                <span className="text-ink">“roughly how many servers?”</span> without stalling.
                Napkin Chain drills that reflex on real systems — every estimate feeding the
                next.
              </p>

              <div className="mt-8 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
                <GoogleSignInButton />
                <a href="#how" className="text-sm text-ink-muted hover:text-ink">
                  See how it works
                </a>
              </div>

              <p className="mt-6 text-sm text-ink-muted">
                No registration form. No course to enrol in. Start on any challenge.
              </p>
            </div>

            <HeroChain />
          </div>
        </section>

        {/* ------------------------------------------------------- problem */}
        <section className="mx-auto max-w-5xl px-5 py-16 lg:py-20">
          <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:gap-14">
            <div>
              <h2 className="text-[28px] font-semibold leading-tight tracking-[-0.025em]">
                The question that ends interviews.
              </h2>
              <p className="mt-5 text-[16px] leading-[1.7] text-ink-secondary">
                You have the load balancer, the cache, the sharded database. The design is
                sound and you can defend every box on the board.
              </p>
              <p className="mt-4 text-[16px] leading-[1.7] text-ink-secondary">
                Then comes the follow-up, and it is not about architecture at all. It is
                arithmetic, out loud, under time pressure — a genuinely separate skill, and
                one almost nobody practises deliberately.
              </p>
              <p className="mt-4 text-[16px] leading-[1.7] text-ink-secondary">
                The same gap shows up long after the interview: in a design review, when
                someone asks whether the thing holds at ten times the load, and the honest
                answer is a shrug.
              </p>
            </div>

            <div className="napkin-surface flex items-center rounded-lg border border-line px-6 py-8 shadow-hair sm:px-9">
              <div className="handwritten space-y-4 text-[21px] leading-[1.45] text-ink">
                <p className="text-ink-muted">“Looks good. Quick sanity check —”</p>
                <p className="text-[24px]">How much storage does this need in year one?</p>
                <p className="text-ink-muted">“…and how many servers at peak?”</p>
                <div className="pt-2">
                  <span className="annotated text-[22px]">Everything stops here.</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <TornEdge />

        {/* -------------------------------------------------------- thesis */}
        <section className="bg-subtle/40 py-16 lg:py-20">
          <div className="mx-auto max-w-5xl px-5">
            <h2 className="text-[28px] font-semibold leading-tight tracking-[-0.025em]">
              Estimates are a chain, not a quiz.
            </h2>
            <p className="mt-4 max-w-2xl text-[16px] leading-[1.7] text-ink-secondary">
              This is the whole bet. Practice tools ask disconnected questions; real
              estimation carries one number through an entire system, and every step
              inherits the last step’s error.
            </p>
            <div className="mt-10">
              <QuizVsChain />
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------- mechanics */}
        <section id="how" className="mx-auto max-w-5xl scroll-mt-20 px-5 py-16 lg:py-20">
          <h2 className="text-[28px] font-semibold leading-tight tracking-[-0.025em]">
            How a session goes.
          </h2>

          <ol className="mt-10 space-y-10">
            <li className="grid gap-5 sm:grid-cols-[auto_1fr] sm:gap-7">
              <CircledNumber n={1} />
              <div>
                <h3 className="text-[17px] font-semibold">Pick a real system.</h3>
                <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
                  Not an abstract exercise — an Instagram feed at 100M DAU, a WhatsApp-scale
                  message store, a URL shortener’s read path. Choose Learn, Practice, or a
                  timed Interview run.
                </p>
                <ul className="mt-4 flex flex-wrap items-center gap-2">
                  {SYSTEMS.map((system) => (
                    <li
                      key={system}
                      className="rounded-md border border-line bg-surface px-3 py-1.5 text-[13px] text-ink-secondary"
                    >
                      {system}
                    </li>
                  ))}
                  {SYSTEMS_COMING.map((system) => (
                    <li
                      key={system}
                      className="rounded-md border border-dashed border-line px-3 py-1.5 text-[13px] text-ink-faint"
                    >
                      {system}
                    </li>
                  ))}
                  <li className="text-[13px] text-ink-faint">dashed = being written</li>
                </ul>
              </div>
            </li>

            <li className="grid gap-5 sm:grid-cols-[auto_1fr] sm:gap-7">
              <CircledNumber n={2} />
              <div>
                <h3 className="text-[17px] font-semibold">
                  Build the chain, one estimate at a time.
                </h3>
                <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
                  Each node unlocks the next. Your rough working is kept alongside the
                  number, because the reasoning is the part worth reviewing — and branches
                  are real: storage and traffic diverge from the same user count.
                </p>
              </div>
            </li>

            <li className="grid gap-5 sm:grid-cols-[auto_1fr] sm:gap-7">
              <CircledNumber n={3} />
              <div>
                <h3 className="text-[17px] font-semibold">Get scored on magnitude.</h3>
                <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
                  Nobody sizes a system to three significant figures. You are scored on how
                  many times away you were — within 1.5× is excellent, and 27× is a concept
                  you have not learned yet.
                </p>
                <div className="mt-5 max-w-2xl">
                  <FeedbackSample />
                </div>
              </div>
            </li>

            <li className="grid gap-5 sm:grid-cols-[auto_1fr] sm:gap-7">
              <CircledNumber n={4} />
              <div>
                <h3 className="text-[17px] font-semibold">
                  Miss a step, learn that step, land back on it.
                </h3>
                <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
                  A bad estimate opens the one concept behind it — two minutes, one page,
                  with the shortcut worth memorising — and returns you to the exact step you
                  left. No lost place, and no grinding a whole course to close one gap.
                </p>
                <div className="mt-6 max-w-3xl">
                  <LoopDiagram />
                </div>
              </div>
            </li>
          </ol>
        </section>

        <TornEdge />

        {/* --------------------------------------------------------- areas */}
        <section className="bg-subtle/40 py-16 lg:py-20">
          <div className="mx-auto max-w-5xl px-5">
            <h2 className="text-[28px] font-semibold leading-tight tracking-[-0.025em]">
              What you end up fluent in.
            </h2>
            <p className="mt-4 max-w-2xl text-[16px] leading-[1.7] text-ink-secondary">
              Mastery is tracked per concept, from your actual attempts — accuracy,
              consistency and speed — so you can see which of these you would not want to be
              asked about tomorrow.
            </p>

            <ul className="mt-10 grid gap-x-8 gap-y-6 sm:grid-cols-2 lg:grid-cols-3">
              {AREAS.map(({ area, title, detail }) => {
                const AreaIcon = AREA_ICONS[area]
                return (
                  <li key={area} className="flex gap-3.5">
                    <AreaIcon className="mt-0.5 h-5 w-5 shrink-0 text-accent" />
                    <div>
                      <h3 className="text-[15px] font-semibold">{title}</h3>
                      <p className="mt-1 text-sm leading-relaxed text-ink-secondary">{detail}</p>
                    </div>
                  </li>
                )
              })}
            </ul>
          </div>
        </section>

        {/* ----------------------------------------------------------- cta */}
        <section className="mx-auto max-w-5xl px-5 py-20 text-center">
          <p className="handwritten text-[28px] leading-[1.35] text-ink-secondary">
            Real systems. Connected estimates. Better intuition.
          </p>
          <h2 className="mx-auto mt-6 max-w-lg text-[26px] font-semibold leading-tight tracking-[-0.025em]">
            Stop freezing on the follow-up question.
          </h2>
          <div className="mt-8 flex justify-center">
            <GoogleSignInButton />
          </div>
          <p className="mt-5 text-sm text-ink-muted">
            Free while it is in early access. Your progress is yours.
          </p>
        </section>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-5 py-8 text-sm text-ink-muted sm:flex-row sm:items-center sm:justify-between">
          <Wordmark className="text-ink-secondary" />
          <p>Built for engineers who would rather be approximately right, fast.</p>
          <Link to="/privacy" className="hover:text-ink">
            Privacy
          </Link>
        </div>
      </footer>
    </div>
  )
}

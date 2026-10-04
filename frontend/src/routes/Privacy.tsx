import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Wordmark } from '@/components/Logo'

const CONTACT = 'danimvijay@gmail.com'
const UPDATED = '4 October 2026'

export function Privacy() {
  return (
    <div className="flex min-h-dvh flex-col napkin-surface">
      <header className="mx-auto flex h-16 w-full max-w-5xl items-center px-5">
        <Link to="/" className="text-ink">
          <Wordmark />
        </Link>
      </header>

      <main className="mx-auto w-full max-w-2xl flex-1 px-5 pb-24 pt-6">
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Privacy</h1>
        <p className="mt-2 text-sm text-ink-muted">Last updated {UPDATED}</p>

        <Section title="What we collect">
          <p>
            You sign in with Google. From that sign-in we keep your Google account ID, email
            address, name and profile picture URL. We ask Google for nothing beyond basic profile
            information, and we never see your Google password.
          </p>
          <p>
            As you use Napkin Chain we store the estimates you submit, your scores and progress,
            your preferences, and simple usage events (for example, that a challenge was started or
            finished) so we can see which parts of the product help.
          </p>
        </Section>

        <Section title="How we use it">
          <p>
            Only to run the product: to sign you in, save your work, score your answers and show
            your progress. We do not sell your data, show ads, or share it with anyone for their own
            use. There are no third-party analytics or tracking scripts.
          </p>
        </Section>

        <Section title="Cookies">
          <p>
            We set a signed session cookie to keep you signed in, and short-lived cookies during
            the Google sign-in itself. Nothing else.
          </p>
        </Section>

        <Section title="Where it lives">
          <p>
            The app runs on Amazon Web Services and stores data in MongoDB Atlas. Both act only as
            our service providers.
          </p>
        </Section>

        <Section title="Your choices">
          <p>
            You can reset your progress from your profile at any time. To have your account and all
            of its data deleted, or to ask what we hold about you, email{' '}
            <a href={`mailto:${CONTACT}`} className="text-accent underline underline-offset-2">
              {CONTACT}
            </a>
            .
          </p>
        </Section>
      </main>
    </div>
  )
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mt-8">
      <h2 className="text-base font-semibold">{title}</h2>
      <div className="mt-2 space-y-3 text-sm leading-relaxed text-ink-secondary">{children}</div>
    </section>
  )
}

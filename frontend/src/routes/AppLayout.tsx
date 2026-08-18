import { NavLink, Outlet } from 'react-router-dom'
import { Wordmark } from '@/components/Logo'
import {
  ChallengesIcon,
  HomeIcon,
  LearnIcon,
  ProgressIcon,
} from '@/components/Icons'
import { useAuth } from '@/hooks/useAuth'

const NAV = [
  { to: '/app', label: 'Home', end: true, Icon: HomeIcon },
  { to: '/app/challenges', label: 'Challenges', end: false, Icon: ChallengesIcon },
  { to: '/app/learn', label: 'Learn', end: false, Icon: LearnIcon },
  { to: '/app/progress', label: 'Progress', end: false, Icon: ProgressIcon },
]

function navClass({ isActive }: { isActive: boolean }) {
  return `relative py-1 text-sm transition-colors ${
    isActive ? 'text-ink font-medium' : 'text-ink-muted hover:text-ink-secondary'
  }`
}

export function AppLayout() {
  const { user } = useAuth()
  const initial = (user?.name ?? user?.email ?? '?').trim().charAt(0).toUpperCase()

  return (
    <div className="min-h-dvh bg-paper">
      <header className="sticky top-0 z-30 border-b border-line bg-paper/85 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <NavLink to="/app" className="text-ink">
            <Wordmark />
          </NavLink>

          <nav className="hidden items-center gap-6 sm:flex">
            {NAV.map(({ to, label, end, Icon }) => (
              <NavLink key={to} to={to} end={end} className={navClass}>
                <span className="flex items-center gap-1.5">
                  <Icon className="h-[17px] w-[17px]" />
                  {label}
                </span>
              </NavLink>
            ))}
          </nav>

          <NavLink
            to="/app/profile"
            className="flex h-8 w-8 items-center justify-center rounded-full border border-line bg-subtle text-xs font-medium text-ink-secondary transition-colors hover:border-ink-muted"
            aria-label="Profile"
          >
            {user?.avatarUrl ? (
              <img src={user.avatarUrl} alt="" className="h-full w-full rounded-full object-cover" />
            ) : (
              initial
            )}
          </NavLink>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 pb-24 pt-7 sm:px-6 sm:pb-16">
        <Outlet />
      </main>

      {/* Mobile: navigation lives at the thumb, not the top. */}
      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-4 border-t border-line bg-paper/95 pb-[env(safe-area-inset-bottom)] backdrop-blur sm:hidden">
        {NAV.map(({ to, label, end, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 py-2.5 text-[11px] ${
                isActive ? 'font-medium text-ink' : 'text-ink-muted'
              }`
            }
          >
            <Icon className="h-[19px] w-[19px]" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}

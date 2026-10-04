import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { SectionLabel } from '@/components/ui/Card'
import { api } from '@/lib/api'
import { useAuth, useLogout } from '@/hooks/useAuth'
import { useDraftStore } from '@/stores/draftStore'

export function Profile() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const logout = useLogout()

  const reset = useMutation({
    mutationFn: api.resetProgress,
    onSuccess: () => {
      useDraftStore.setState({ drafts: {} })
      queryClient.invalidateQueries()
    },
  })

  return (
    <div className="mx-auto max-w-lg space-y-9">
      <header>
        <h1 className="text-[26px] font-semibold tracking-[-0.02em]">Profile</h1>
      </header>

      <section className="space-y-3">
        <SectionLabel>Account</SectionLabel>
        <dl className="divide-y divide-line rounded-lg border border-line bg-surface">
          <Row label="Name" value={user?.name ?? '—'} />
          <Row label="Email" value={user?.email ?? '—'} />
          <Row label="Sign-in" value="Google" />
        </dl>
      </section>

      <section className="space-y-3">
        <SectionLabel>Data</SectionLabel>
        <div className="rounded-lg border border-line bg-surface px-5 py-4">
          <p className="text-sm leading-relaxed text-ink-secondary">
            Resetting clears every attempt and all mastery. Challenge content is unaffected.
          </p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-3"
            onClick={() => reset.mutate()}
            loading={reset.isPending}
          >
            {reset.isSuccess ? 'Progress reset' : 'Reset my progress'}
          </Button>
        </div>
      </section>

      <div className="border-t border-line pt-6">
        <Button
          variant="ghost"
          onClick={() => logout.mutate(undefined, { onSuccess: () => navigate('/') })}
          loading={logout.isPending}
        >
          Sign out
        </Button>
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 px-5 py-3 text-sm">
      <dt className="text-ink-secondary">{label}</dt>
      <dd className="truncate">{value}</dd>
    </div>
  )
}

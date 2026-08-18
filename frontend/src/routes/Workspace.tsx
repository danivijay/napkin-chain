import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ChainCanvas } from '@/components/chain/ChainCanvas'
import { ChainSheet } from '@/components/chain/ChainSheet'
import { ChainStrip } from '@/components/chain/ChainStrip'
import { EstimatePanel } from '@/components/workspace/EstimatePanel'
import { FeedbackPanel } from '@/components/workspace/FeedbackPanel'
import { WorkspaceHeader } from '@/components/workspace/WorkspaceHeader'
import { ErrorState } from '@/components/ui/ErrorState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { ApiError, api } from '@/lib/api'
import { draftKey, useDraftStore } from '@/stores/draftStore'
import type { ChainNode, Feedback } from '@/types'

export function Workspace() {
  const { slug = '' } = useParams()
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const [answeredNodeId, setAnsweredNodeId] = useState<string | null>(null)
  const [completed, setCompleted] = useState(false)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const clearDraft = useDraftStore((store) => store.clear)

  const {
    data: state,
    isPending,
    error,
    refetch,
  } = useQuery({
    queryKey: ['attempt', slug],
    queryFn: () => api.attemptState(slug),
    retry: (count, err) => !(err instanceof ApiError && err.status === 404) && count < 2,
  })

  // A user arriving from a concept page ("reattempt this step") lands here
  // with the node they were sent away from.
  const retryParam = params.get('retry')

  const retry = useMutation({
    mutationFn: (nodeId: string) => api.retryNode(slug, nodeId),
    onSuccess: (next) => {
      queryClient.setQueryData(['attempt', slug], next)
      setFeedback(null)
      setCompleted(false)
    },
  })

  useEffect(() => {
    if (!retryParam || !state) return
    setParams({}, { replace: true })
    if (state.currentNodeId !== retryParam) retry.mutate(retryParam)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [retryParam, Boolean(state)])

  useEffect(() => {
    if (!state) return
    const startedAt = new Date(state.startedAt).getTime()
    const tick = () => setElapsed(Math.round((Date.now() - startedAt) / 1000))
    tick()
    const timer = window.setInterval(tick, 1000)
    return () => window.clearInterval(timer)
  }, [state?.startedAt])

  const submit = useMutation({
    mutationFn: (payload: { nodeId: string; estimate: number; calculation: string; seconds: number }) =>
      api.estimate(slug, payload.nodeId, {
        estimate: payload.estimate,
        calculation: payload.calculation || null,
        timeSpentSeconds: payload.seconds,
      }),
    onSuccess: (response, variables) => {
      queryClient.setQueryData(['attempt', slug], response.state)
      queryClient.invalidateQueries({ queryKey: ['home'] })
      queryClient.invalidateQueries({ queryKey: ['challenge', slug] })
      clearDraft(draftKey(slug, variables.nodeId))
      setAnsweredNodeId(variables.nodeId)
      setFeedback(response.feedback)
      setCompleted(response.challengeCompleted)
    },
  })

  const hint = useMutation({
    mutationFn: (nodeId: string) => api.hint(slug, nodeId),
    onSuccess: () => refetch(),
  })

  const question = state?.question ?? null
  const chain = useMemo(() => state?.chain ?? [], [state])

  if (isPending) return <LoadingScreen message="Opening your napkin" />
  if (error || !state) {
    return (
      <div className="mx-auto max-w-md px-5 py-16">
        <ErrorState
          error={error}
          onRetry={
            error instanceof ApiError && error.status === 404
              ? () => navigate(`/app/challenges/${slug}`)
              : () => refetch()
          }
        />
      </div>
    )
  }

  // Sending the user away to learn always records which step to come back to.
  const goToConcept = (conceptId: string) => {
    const nodeId = feedback ? answeredNodeId : question?.id
    navigate(`/app/learn/${conceptId}?from=${slug}${nodeId ? `&node=${nodeId}` : ''}`)
  }

  const onContinue = () => {
    setFeedback(null)
    if (completed) navigate(`/app/challenges/${slug}/result`)
  }

  const onSelectNode = (node: ChainNode) => {
    setSheetOpen(false)
    if (node.type === 'estimate' && node.status !== 'locked' && node.id !== state.currentNodeId) {
      retry.mutate(node.id)
    }
  }

  const panel = feedback ? (
    <FeedbackPanel
      feedback={feedback}
      completed={completed}
      onContinue={onContinue}
      onRetry={() => answeredNodeId && retry.mutate(answeredNodeId)}
      onLearn={goToConcept}
    />
  ) : question ? (
    <EstimatePanel
      state={state}
      question={question}
      submitting={submit.isPending}
      submitError={submit.isError ? "We couldn't save your estimate." : null}
      onSubmit={({ estimate, calculation, seconds }) =>
        submit.mutate({ nodeId: question.id, estimate, calculation, seconds })
      }
      onHint={() => hint.mutate(question.id)}
      onLearn={goToConcept}
    />
  ) : (
    <CompletedPanel slug={slug} />
  )

  return (
    <div className="flex h-dvh flex-col bg-paper">
      <WorkspaceHeader state={state} elapsed={elapsed} />

      <div className="lg:hidden">
        <ChainStrip
          chain={chain}
          currentNodeId={state.currentNodeId}
          onOpen={() => setSheetOpen(true)}
        />
      </div>

      <div className="flex min-h-0 flex-1 lg:divide-x lg:divide-line">
        {/* Desktop: the napkin stays visible while you work. */}
        <section className="napkin-surface hidden flex-1 overflow-auto p-10 lg:block">
          <ChainCanvas chain={chain} onSelect={onSelectNode} />
        </section>

        <section className="flex w-full flex-col overflow-auto px-5 py-6 sm:px-8 lg:w-[420px] lg:shrink-0 xl:w-[460px]">
          {panel}
        </section>
      </div>

      <ChainSheet
        chain={chain}
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onSelect={onSelectNode}
      />
    </div>
  )
}

function CompletedPanel({ slug }: { slug: string }) {
  const navigate = useNavigate()
  return (
    <div className="flex flex-1 flex-col items-start justify-center gap-4">
      <h2 className="text-[22px] font-semibold tracking-[-0.02em]">Chain complete</h2>
      <p className="text-[15px] text-ink-secondary">
        Every estimate in this system has an answer.
      </p>
      <button
        type="button"
        onClick={() => navigate(`/app/challenges/${slug}/result`)}
        className="text-sm font-medium text-accent"
      >
        See your results →
      </button>
    </div>
  )
}

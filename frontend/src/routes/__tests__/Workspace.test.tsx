/**
 * The flow the product exists for, driven through the real Workspace route:
 * answer a step, get it wrong, be sent to the concept, come back to that exact
 * step, retry it, and succeed.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Workspace } from '@/routes/Workspace'
import { renderRoute } from '@/test/render'
import { attemptState, chainNode, feedback, question } from '@/test/fixtures'
import { api } from '@/lib/api'

const SLUG = 'instagram-feed'

function renderWorkspace(route = `/app/challenges/${SLUG}/build`) {
  return renderRoute(<Workspace />, { path: '/app/challenges/:slug/build', route })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('Workspace', () => {
  it('shows the current step and the chain around it', async () => {
    vi.spyOn(api, 'attemptState').mockResolvedValue(attemptState())
    renderWorkspace()

    expect(await screen.findByRole('heading', { name: 'Average QPS' })).toBeInTheDocument()
    expect(screen.getByText('100M DAU')).toBeInTheDocument()
    expect(screen.getByText('0 / 7')).toBeInTheDocument()
  })

  it('walks the user from a failed estimate to the concept and back to the same step', async () => {
    const user = userEvent.setup()
    const weakState = attemptState({
      chain: [
        chainNode({ id: 'dau', type: 'input', status: 'solved', displayValue: '100M DAU' }),
        chainNode({ id: 'avg_qps', status: 'weak', displayValue: '400K', attempts: 1 }),
        chainNode({ id: 'peak_qps', label: 'Peak QPS', dependsOn: ['avg_qps'], status: 'active' }),
      ],
      currentNodeId: 'peak_qps',
      solvedCount: 1,
    })

    vi.spyOn(api, 'attemptState').mockResolvedValue(attemptState())
    const estimate = vi
      .spyOn(api, 'estimate')
      .mockResolvedValue({
        feedback: feedback(),
        state: weakState,
        unlockedNodeIds: ['peak_qps'],
        challengeCompleted: false,
      })

    renderWorkspace()
    await screen.findByRole('heading', { name: 'Average QPS' })

    await user.type(screen.getByLabelText('Your estimate'), '400K')
    await user.click(screen.getByRole('button', { name: /submit estimate/i }))

    // Feedback, with the distance and the reason.
    expect(await screen.findByText('This one is worth learning')).toBeInTheDocument()
    expect(screen.getByText('27x high')).toBeInTheDocument()
    expect(estimate).toHaveBeenCalledWith(
      SLUG,
      'avg_qps',
      expect.objectContaining({ estimate: 400_000 }),
    )

    // The lesson link carries the step to come back to.
    await user.click(screen.getByRole('button', { name: /^learn requests\/day to qps$/i }))
    expect(await screen.findByTestId('elsewhere')).toBeInTheDocument()
  })

  it('reopens the exact step when returning from a concept', async () => {
    vi.spyOn(api, 'attemptState').mockResolvedValue(
      attemptState({ currentNodeId: 'peak_qps', question: question({ id: 'peak_qps', label: 'Peak QPS' }) }),
    )
    const retry = vi.spyOn(api, 'retryNode').mockResolvedValue(attemptState())

    renderWorkspace(`/app/challenges/${SLUG}/build?retry=avg_qps`)

    await waitFor(() => expect(retry).toHaveBeenCalledWith(SLUG, 'avg_qps'))
    expect(await screen.findByRole('heading', { name: 'Average QPS' })).toBeInTheDocument()
  })

  it('keeps the estimate on screen when saving it fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'attemptState').mockResolvedValue(attemptState())
    vi.spyOn(api, 'estimate').mockRejectedValue(new Error('offline'))

    renderWorkspace()
    await screen.findByRole('heading', { name: 'Average QPS' })

    const input = screen.getByLabelText('Your estimate')
    await user.type(input, '10K')
    await user.click(screen.getByRole('button', { name: /submit estimate/i }))

    expect(await screen.findByText(/couldn't save your estimate/i)).toBeInTheDocument()
    expect(input).toHaveValue('10K')
  })

  it('reveals a hint on request', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'attemptState').mockResolvedValue(attemptState())
    const hint = vi
      .spyOn(api, 'hint')
      .mockResolvedValue({ hint: '1 day ~ 100K seconds.', hintsRevealed: 1, hintsAvailable: 2 })

    renderWorkspace()
    await screen.findByRole('heading', { name: 'Average QPS' })
    await user.click(screen.getByRole('button', { name: /need a hint/i }))

    await waitFor(() => expect(hint).toHaveBeenCalledWith(SLUG, 'avg_qps'))
  })

  it('sends the user to results after the last step', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'attemptState').mockResolvedValue(attemptState())
    vi.spyOn(api, 'estimate').mockResolvedValue({
      feedback: feedback({ passed: true, classification: 'excellent', headline: 'Excellent estimate' }),
      state: attemptState({ status: 'completed', currentNodeId: null, question: null, solvedCount: 7 }),
      unlockedNodeIds: [],
      challengeCompleted: true,
    })

    renderWorkspace()
    await screen.findByRole('heading', { name: 'Average QPS' })
    await user.type(screen.getByLabelText('Your estimate'), '10K')
    await user.click(screen.getByRole('button', { name: /submit estimate/i }))

    await user.click(await screen.findByRole('button', { name: /see results/i }))
    expect(await screen.findByTestId('elsewhere')).toBeInTheDocument()
  })
})

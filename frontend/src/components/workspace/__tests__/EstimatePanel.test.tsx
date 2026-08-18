import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EstimatePanel } from '@/components/workspace/EstimatePanel'
import { useDraftStore } from '@/stores/draftStore'
import { attemptState, question } from '@/test/fixtures'

function setup(overrides: Partial<Parameters<typeof EstimatePanel>[0]> = {}) {
  const props = {
    state: attemptState(),
    question: question(),
    onSubmit: vi.fn(),
    onHint: vi.fn(),
    onLearn: vi.fn(),
    submitting: false,
    ...overrides,
  }
  render(<EstimatePanel {...props} />)
  return props
}

describe('EstimatePanel', () => {
  it('shows the step, the prompt and what the user was given', () => {
    setup()
    expect(screen.getByText('Step 2 of 7')).toBeInTheDocument()
    expect(screen.getByText('What is the average feed request rate?')).toBeInTheDocument()
    expect(screen.getByText('~1B / day')).toBeInTheDocument()
  })

  it('will not submit until there is a number', async () => {
    setup()
    expect(screen.getByRole('button', { name: /submit estimate/i })).toBeDisabled()
  })

  it('submits the parsed estimate, not the raw text', async () => {
    const user = userEvent.setup()
    const { onSubmit } = setup()

    await user.type(screen.getByLabelText('Your estimate'), '12k')
    expect(screen.getByText('reads as 12K QPS')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /submit estimate/i }))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ estimate: 12_000, calculation: '' }),
    )
  })

  it('keeps typed input in local storage so a reload never loses it', async () => {
    const user = userEvent.setup()
    setup()

    await user.type(screen.getByLabelText('Your estimate'), '10K')
    await user.click(screen.getByRole('button', { name: /show my calculation/i }))
    await user.type(screen.getByRole('textbox', { name: '' }), '1B / 100K')

    const draft = useDraftStore.getState().drafts['instagram-feed:avg_qps']
    expect(draft.estimate).toBe('10K')
    expect(draft.calculation).toBe('1B / 100K')
  })

  it('offers hints in practice mode', () => {
    setup()
    expect(screen.getByRole('button', { name: /need a hint/i })).toBeInTheDocument()
  })

  it('withholds hints in interview mode', () => {
    setup({ state: attemptState({ mode: 'interview' }) })
    expect(screen.queryByRole('button', { name: /need a hint/i })).not.toBeInTheDocument()
  })

  it('offers the concept behind the step', async () => {
    const user = userEvent.setup()
    const { onLearn } = setup()
    await user.click(screen.getByRole('button', { name: /learn requests\/day to qps/i }))
    expect(onLearn).toHaveBeenCalledWith('qps')
  })

  it('shows revealed hints as napkin notes', () => {
    setup({ question: question({ hints: ['1 day ~ 100K seconds.'], hintsRevealed: 1 }) })
    expect(screen.getByText('1 day ~ 100K seconds.')).toBeInTheDocument()
  })
})

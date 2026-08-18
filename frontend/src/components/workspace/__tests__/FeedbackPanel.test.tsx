import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FeedbackPanel } from '@/components/workspace/FeedbackPanel'
import { feedback } from '@/test/fixtures'

function setup(overrides: Partial<Parameters<typeof FeedbackPanel>[0]> = {}) {
  const props = {
    feedback: feedback(),
    completed: false,
    onContinue: vi.fn(),
    onRetry: vi.fn(),
    onLearn: vi.fn(),
    ...overrides,
  }
  render(<FeedbackPanel {...props} />)
  return props
}

describe('FeedbackPanel', () => {
  it('reports the distance rather than a right/wrong verdict', () => {
    setup()
    expect(screen.getByText('400K QPS')).toBeInTheDocument()
    expect(screen.getByText('8K–15K QPS')).toBeInTheDocument()
    expect(screen.getByText('27x high')).toBeInTheDocument()
  })

  it('says the estimate landed inside the range when it did', () => {
    setup({ feedback: feedback({ withinRange: true, ratio: 1, passed: true }) })
    expect(screen.getByText('inside the range')).toBeInTheDocument()
  })

  it('shows the working and the shortcut', () => {
    setup()
    expect(screen.getByText('1B / 100K seconds')).toBeInTheDocument()
    expect(screen.getByText('1 day ~ 100K seconds')).toBeInTheDocument()
  })

  it('pushes the user toward the concept when the step went badly', async () => {
    const user = userEvent.setup()
    const { onLearn } = setup()

    expect(screen.getByText('This step is worth learning.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /^learn requests\/day to qps$/i }))
    expect(onLearn).toHaveBeenCalledWith('qps')
  })

  it('does not push a lesson when the estimate was good', () => {
    setup({ feedback: feedback({ passed: true, classification: 'excellent', ratio: 1.2 }) })
    expect(screen.queryByText('This step is worth learning.')).not.toBeInTheDocument()
  })

  it('offers retrying the step just answered', async () => {
    const user = userEvent.setup()
    const { onRetry } = setup()
    await user.click(screen.getByRole('button', { name: /try this step again/i }))
    expect(onRetry).toHaveBeenCalled()
  })

  it('sends the user to results once the chain is finished', async () => {
    const user = userEvent.setup()
    const { onContinue } = setup({ completed: true })
    await user.click(screen.getByRole('button', { name: /see results/i }))
    expect(onContinue).toHaveBeenCalled()
  })
})

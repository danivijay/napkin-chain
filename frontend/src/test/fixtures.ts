import type { AttemptState, ChainNode, Feedback, NodeQuestion } from '@/types'

export function chainNode(overrides: Partial<ChainNode> = {}): ChainNode {
  return {
    id: 'avg_qps',
    label: 'Average QPS',
    unit: 'QPS',
    type: 'estimate',
    dependsOn: [],
    conceptId: 'qps',
    status: 'active',
    displayValue: null,
    attempts: 0,
    classification: null,
    ...overrides,
  }
}

export function question(overrides: Partial<NodeQuestion> = {}): NodeQuestion {
  return {
    id: 'avg_qps',
    label: 'Average QPS',
    unit: 'QPS',
    type: 'estimate',
    status: 'active',
    prompt: 'What is the average feed request rate?',
    givens: [{ label: 'Requests', value: '~1B / day' }],
    dependsOn: ['actions_day'],
    conceptId: 'qps',
    conceptTitle: 'Requests/day to QPS',
    attempts: 0,
    hintsRevealed: 0,
    hintsAvailable: 2,
    hints: [],
    lastEstimate: null,
    lastCalculation: null,
    stepNumber: 2,
    totalSteps: 7,
    ...overrides,
  }
}

export function attemptState(overrides: Partial<AttemptState> = {}): AttemptState {
  return {
    attemptId: 'attempt-1',
    challengeSlug: 'instagram-feed',
    challengeTitle: 'Instagram Feed',
    mode: 'practice',
    status: 'in_progress',
    chain: [
      chainNode({ id: 'dau', label: 'Daily active users', type: 'input', status: 'solved', displayValue: '100M DAU', conceptId: null }),
      chainNode({ id: 'avg_qps', dependsOn: ['dau'] }),
      chainNode({ id: 'peak_qps', label: 'Peak QPS', dependsOn: ['avg_qps'], status: 'locked', conceptId: 'peak-traffic' }),
    ],
    currentNodeId: 'avg_qps',
    question: question(),
    solvedCount: 0,
    totalSteps: 7,
    startedAt: new Date().toISOString(),
    lastActivityAt: new Date().toISOString(),
    timeSpentSeconds: 0,
    suggestedSecondsPerNode: 110,
    score: null,
    averageRatio: null,
    ...overrides,
  }
}

export function feedback(overrides: Partial<Feedback> = {}): Feedback {
  return {
    headline: 'This one is worth learning',
    classification: 'needs_review',
    passed: false,
    ratio: 26.7,
    direction: 'over',
    withinRange: false,
    yourEstimate: 400000,
    expectedValue: 10954,
    expectedMin: 8000,
    expectedMax: 15000,
    unit: 'QPS',
    explanationSteps: ['1B / 100K seconds', '~ 10K QPS'],
    shortcut: '1 day ~ 100K seconds',
    note: null,
    conceptId: 'qps',
    conceptTitle: 'Requests/day to QPS',
    nodeStatus: 'weak',
    ...overrides,
  }
}

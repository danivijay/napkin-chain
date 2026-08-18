export type Difficulty = 'foundation' | 'builder' | 'system' | 'interview'
export type Mode = 'learn' | 'practice' | 'interview'
export type NodeType = 'input' | 'estimate'
export type NodeStatus = 'locked' | 'available' | 'active' | 'solved' | 'weak' | 'mastered'
export type Classification = 'excellent' | 'very_good' | 'good' | 'developing' | 'needs_review'
export type MasteryStatus = 'untouched' | 'learning' | 'developing' | 'strong' | 'mastered'
export type AttemptStatus = 'in_progress' | 'completed' | 'abandoned'

export interface User {
  id: string
  email: string
  name: string | null
  avatarUrl: string | null
  createdAt: string
  preferences: Record<string, unknown>
}

export interface AuthStatus {
  authenticated: boolean
  user: User | null
  googleEnabled: boolean
  devLoginEnabled: boolean
}

export interface Given {
  label: string
  value: string
}

export interface ChainNode {
  id: string
  label: string
  unit: string
  type: NodeType
  dependsOn: string[]
  conceptId: string | null
  status: NodeStatus
  displayValue: string | null
  attempts: number
  classification: Classification | null
}

export interface ChallengeSummary {
  id: string
  slug: string
  title: string
  subtitle: string
  description: string
  difficulty: Difficulty
  estimatedMinutes: number
  modes: Mode[]
  nodeCount: number
  chainLabels: string[]
  conceptIds: string[]
  attemptStatus: AttemptStatus | null
  attemptMode: Mode | null
  solvedCount: number
  lastActivityAt: string | null
}

export interface ConceptSummary {
  conceptId: string
  title: string
  area: string
  oneLiner: string
  readMinutes: number
  order: number
  mastery: number
  status: MasteryStatus
  attempts: number
  learned: boolean
  lastPracticedAt: string | null
}

export interface ChallengeDetail extends ChallengeSummary {
  scenarioDescription: string
  scenarioGivens: Given[]
  chain: ChainNode[]
  concepts: ConceptSummary[]
  suggestedSecondsPerNode: number
}

export interface NodeQuestion {
  id: string
  label: string
  unit: string
  type: NodeType
  status: NodeStatus
  prompt: string | null
  givens: Given[]
  dependsOn: string[]
  conceptId: string | null
  conceptTitle: string | null
  attempts: number
  hintsRevealed: number
  hintsAvailable: number
  hints: string[]
  lastEstimate: number | null
  lastCalculation: string | null
  stepNumber: number
  totalSteps: number
}

export interface AttemptState {
  attemptId: string
  challengeSlug: string
  challengeTitle: string
  mode: Mode
  status: AttemptStatus
  chain: ChainNode[]
  currentNodeId: string | null
  question: NodeQuestion | null
  solvedCount: number
  totalSteps: number
  startedAt: string
  lastActivityAt: string
  timeSpentSeconds: number
  suggestedSecondsPerNode: number
  score: number | null
  averageRatio: number | null
}

export interface Feedback {
  headline: string
  classification: Classification
  passed: boolean
  ratio: number
  direction: 'over' | 'under' | 'within'
  withinRange: boolean
  yourEstimate: number
  expectedValue: number
  expectedMin: number | null
  expectedMax: number | null
  unit: string
  explanationSteps: string[]
  shortcut: string | null
  note: string | null
  conceptId: string | null
  conceptTitle: string | null
  nodeStatus: NodeStatus
}

export interface EstimateResponse {
  feedback: Feedback
  state: AttemptState
  unlockedNodeIds: string[]
  challengeCompleted: boolean
}

export interface NodeResult {
  nodeId: string
  label: string
  unit: string
  status: NodeStatus
  attempts: number
  yourEstimate: number | null
  expectedValue: number | null
  ratio: number | null
  classification: Classification | null
  conceptId: string | null
  timeSpentSeconds: number
}

export interface ChallengeResult {
  attemptId: string
  challengeSlug: string
  challengeTitle: string
  mode: Mode
  status: AttemptStatus
  score: number | null
  averageRatio: number | null
  totalSeconds: number
  secondsPerStep: number | null
  solvedCount: number
  totalSteps: number
  masteredCount: number
  weakCount: number
  nodes: NodeResult[]
  weakConceptIds: string[]
}

export interface ConceptExample {
  given: string
  working: string[]
  result: string
}

export interface ConceptDetail extends ConceptSummary {
  explanation: string[]
  shortcut: string | null
  shortcutNote: string | null
  examples: ConceptExample[]
  pitfalls: string[]
  drill: { prompt: string; given: string; unit: string } | null
  relatedConcepts: ConceptSummary[]
  relatedChallenges: {
    slug: string
    title: string
    difficulty: Difficulty
    estimatedMinutes: number
  }[]
}

export interface DrillResult {
  passed: boolean
  ratio: number
  classification: Classification
  headline: string
  expectedMin: number
  expectedMax: number
  explanation: string[]
  mastery: number
  status: MasteryStatus
}

export interface ConceptGroup {
  area: string
  title: string
  concepts: ConceptSummary[]
}

export interface AreaStrength {
  area: string
  title: string
  strength: number
  conceptCount: number
  practicedCount: number
}

export interface ProgressOverview {
  intuition: number
  skillsTotal: number
  skillsStrong: number
  skillsMastered: number
  chainsSolved: number
  chainsInProgress: number
  averageRatio: number | null
  secondsPerStep: number | null
  totalEstimates: number
  streakDays: number
  bestStreakDays: number
  weeklyEstimates: number
  weeklyImprovement: number | null
  interviewReady: boolean
  areas: AreaStrength[]
}

export interface Recommendation {
  kind: 'practice_concept' | 'learn_concept' | 'review_concept' | 'new_challenge' | 'level_up'
  title: string
  reason: string
  actionLabel: string
  conceptId: string | null
  challengeSlug: string | null
  priority: number
}

export interface HomeData {
  overview: ProgressOverview
  continueCard: {
    challengeSlug: string
    challengeTitle: string
    difficulty: Difficulty
    mode: Mode
    solvedCount: number
    totalSteps: number
    lastActivityAt: string
  } | null
  recommendations: Recommendation[]
  suggestedChallengeSlug: string | null
}

export interface Skills {
  concepts: ConceptSummary[]
  areas: AreaStrength[]
}

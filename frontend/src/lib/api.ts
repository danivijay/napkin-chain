import type {
  AttemptState,
  AuthStatus,
  ChallengeDetail,
  ChallengeResult,
  ChallengeSummary,
  ConceptDetail,
  ConceptGroup,
  DrillResult,
  EstimateResponse,
  HomeData,
  Mode,
  NodeQuestion,
  ProgressOverview,
  Recommendation,
  Skills,
} from '@/types'

/**
 * Empty by default: requests are relative, so the API is whatever origin
 * served the page. In production FastAPI serves both; in dev Vite proxies
 * /api through to the backend. Set VITE_API_BASE_URL only for a genuinely
 * split deployment.
 */
const BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

/** Thrown for any non-2xx response. `detail` is already user-safe. */
export class ApiError extends Error {
  readonly status: number
  readonly detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }

  /** A cold Render instance or a dropped connection, rather than a real failure. */
  get isTransient() {
    return this.status === 0 || this.status === 502 || this.status === 503 || this.status === 504
  }
}

function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)nc_csrf=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = init.method ?? 'GET'
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  if (method !== 'GET') headers.set('X-CSRF-Token', csrfToken())

  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, { ...init, headers, credentials: 'include' })
  } catch {
    throw new ApiError(0, "We couldn't reach the server.")
  }

  if (response.status === 204) return undefined as T
  const body = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(response.status, body?.detail ?? 'Something went wrong.')
  }
  return body as T
}

const post = <T,>(path: string, body?: unknown) =>
  request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })

export const api = {
  me: () => request<AuthStatus>('/api/auth/me'),
  devLogin: (email: string, name: string) =>
    post<AuthStatus>('/api/auth/dev-login', { email, name }),
  logout: () => post<void>('/api/auth/logout'),
  googleStartUrl: (redirectTo = '/app') =>
    `${BASE}/api/auth/google/start?redirectTo=${encodeURIComponent(redirectTo)}`,

  challenges: () => request<ChallengeSummary[]>('/api/challenges'),
  challenge: (slug: string) => request<ChallengeDetail>(`/api/challenges/${slug}`),

  startAttempt: (slug: string, mode: Mode, restart = false) =>
    post<AttemptState>(`/api/challenges/${slug}/attempts`, { mode, restart }),
  attemptState: (slug: string) => request<AttemptState>(`/api/challenges/${slug}/progress`),
  resume: (slug: string) => post<AttemptState>(`/api/challenges/${slug}/resume`),
  node: (slug: string, nodeId: string) =>
    request<NodeQuestion>(`/api/challenges/${slug}/nodes/${nodeId}`),
  estimate: (
    slug: string,
    nodeId: string,
    payload: { estimate: number; calculation?: string | null; timeSpentSeconds: number },
  ) => post<EstimateResponse>(`/api/challenges/${slug}/nodes/${nodeId}/estimate`, payload),
  retryNode: (slug: string, nodeId: string) =>
    post<AttemptState>(`/api/challenges/${slug}/nodes/${nodeId}/retry`),
  hint: (slug: string, nodeId: string) =>
    post<{ hint: string; hintsRevealed: number; hintsAvailable: number }>(
      `/api/challenges/${slug}/nodes/${nodeId}/hint`,
    ),
  saveDraft: (slug: string, nodeId: string, calculation: string) =>
    post<void>(`/api/challenges/${slug}/nodes/${nodeId}/draft`, { calculation }),
  result: (slug: string) => request<ChallengeResult>(`/api/challenges/${slug}/result`),

  concepts: () => request<ConceptGroup[]>('/api/concepts'),
  concept: (conceptId: string) => request<ConceptDetail>(`/api/concepts/${conceptId}`),
  markLearned: (conceptId: string) => post<ConceptDetail>(`/api/concepts/${conceptId}/learned`),
  practiceConcept: (conceptId: string, estimate: number, timeSpentSeconds: number) =>
    post<DrillResult>(`/api/concepts/${conceptId}/practice`, { estimate, timeSpentSeconds }),

  home: () => request<HomeData>('/api/progress/home'),
  progress: () => request<ProgressOverview>('/api/progress'),
  skills: () => request<Skills>('/api/progress/skills'),
  recommendations: () => request<Recommendation[]>('/api/progress/recommendations'),
  resetProgress: () => request<void>('/api/users/me/progress', { method: 'DELETE' }),
}

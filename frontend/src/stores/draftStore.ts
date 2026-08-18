import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Draft {
  estimate: string
  calculation: string
  startedAt: number
}

interface DraftState {
  drafts: Record<string, Draft>
  get: (key: string) => Draft
  set: (key: string, patch: Partial<Omit<Draft, 'startedAt'>>) => void
  clear: (key: string) => void
  elapsedSeconds: (key: string) => number
}

const EMPTY: Draft = { estimate: '', calculation: '', startedAt: 0 }

export const draftKey = (slug: string, nodeId: string) => `${slug}:${nodeId}`

/**
 * Unsent input lives here, mirrored to localStorage. A dropped connection or
 * an accidental reload must never cost the user their rough work.
 */
export const useDraftStore = create<DraftState>()(
  persist(
    (set, get) => ({
      drafts: {},

      get: (key) => get().drafts[key] ?? EMPTY,

      set: (key, patch) =>
        set((state) => {
          const existing = state.drafts[key] ?? { ...EMPTY, startedAt: Date.now() }
          return {
            drafts: {
              ...state.drafts,
              [key]: { ...existing, ...patch, startedAt: existing.startedAt || Date.now() },
            },
          }
        }),

      clear: (key) =>
        set((state) => {
          const { [key]: _removed, ...rest } = state.drafts
          return { drafts: rest }
        }),

      elapsedSeconds: (key) => {
        const draft = get().drafts[key]
        if (!draft?.startedAt) return 0
        return Math.round((Date.now() - draft.startedAt) / 1000)
      },
    }),
    { name: 'napkin-chain-drafts' },
  ),
)

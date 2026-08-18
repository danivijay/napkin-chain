import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'
import { useDraftStore } from '@/stores/draftStore'

afterEach(() => {
  cleanup()
  localStorage.clear()
  // The draft store is a module singleton; leaking it between tests would
  // make them order-dependent.
  useDraftStore.setState({ drafts: {} })
})

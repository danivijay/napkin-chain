import { useEffect } from 'react'
import type { ChainNode } from '@/types'
import { ChainCanvas } from './ChainCanvas'

/** The full napkin on demand, as a bottom sheet. Mobile only. */
export function ChainSheet({
  chain,
  open,
  onClose,
  onSelect,
}: {
  chain: ChainNode[]
  open: boolean
  onClose: () => void
  onSelect?: (node: ChainNode) => void
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end lg:hidden">
      <button
        type="button"
        aria-label="Close chain"
        onClick={onClose}
        className="absolute inset-0 bg-ink/20"
      />
      <div className="animate-settle relative max-h-[82vh] overflow-auto rounded-t-lg border-t border-line bg-paper napkin-surface px-4 pb-8 pt-3">
        <div className="mx-auto mb-4 h-1 w-9 rounded-full bg-line-strong" />
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Your chain</h2>
          <button type="button" onClick={onClose} className="text-sm text-accent">
            Done
          </button>
        </div>
        <ChainCanvas chain={chain} onSelect={onSelect} />
      </div>
    </div>
  )
}

import type { ReactNode } from 'react'

/**
 * A surface with a hairline border. Used sparingly - most of the app is plain
 * type on paper, and a card should mean "this is a discrete object".
 */
export function Card({
  children,
  className = '',
  as: Tag = 'div',
}: {
  children: ReactNode
  className?: string
  as?: 'div' | 'section' | 'article' | 'li'
}) {
  return (
    <Tag className={`rounded-lg border border-line bg-surface shadow-hair ${className}`}>
      {children}
    </Tag>
  )
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-muted">
      {children}
    </h2>
  )
}

export function Divider({ className = '' }: { className?: string }) {
  return <hr className={`border-0 border-t border-line ${className}`} />
}

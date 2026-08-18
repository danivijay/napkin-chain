import type { ReactNode } from 'react'

/**
 * Rough work, rendered as rough work. The handwritten face is reserved for
 * calculations, shortcuts and annotations - never for interface text.
 */
export function NapkinNote({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={`handwritten rounded-md border border-dashed border-line-strong bg-subtle/60 px-4 py-3 text-[17px] leading-[1.5] text-ink-secondary ${className}`}
    >
      {children}
    </div>
  )
}

/** A calculation shown one line at a time, the way you'd write it on a napkin. */
export function NapkinWorking({ steps, className = '' }: { steps: string[]; className?: string }) {
  return (
    <div className={`handwritten space-y-0.5 text-[19px] leading-[1.45] text-ink ${className}`}>
      {steps.map((step, index) => (
        <div key={index} className={index === steps.length - 1 ? 'font-semibold' : ''}>
          {step}
        </div>
      ))}
    </div>
  )
}

/** The one line worth remembering. */
export function NapkinShortcut({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-baseline gap-2.5">
      <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-accent">
        Shortcut
      </span>
      <span className="handwritten annotated text-[19px] text-ink">{children}</span>
    </div>
  )
}

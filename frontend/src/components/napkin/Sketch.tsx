/**
 * Napkin-flavoured structural pieces: torn edges, drawn arrows, circled
 * numbers. Used to make explanatory diagrams feel drawn rather than rendered.
 */
import type { ReactNode } from 'react'

/** A rough circle, the way you'd ring a number on paper. */
export function CircledNumber({ n }: { n: number }) {
  return (
    <span className="relative inline-flex h-8 w-8 shrink-0 items-center justify-center">
      <svg viewBox="0 0 32 32" className="absolute inset-0 h-full w-full text-accent" aria-hidden>
        <path
          d="M16.6 2.4c7.9-.5 13.6 5.2 13.2 13.2-.4 8-5.6 13.9-13.9 14C7.4 29.7 2 24 2.2 15.9 2.4 8.2 8 3 16.6 2.4Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinecap="round"
          opacity=".75"
        />
      </svg>
      <span className="relative font-mono text-[13px] font-semibold text-accent">{n}</span>
    </span>
  )
}

/** A drawn arrow between two stacked things. */
export function SketchArrow({
  className = '',
  tone = 'muted',
}: {
  className?: string
  tone?: 'muted' | 'accent' | 'good'
}) {
  const color =
    tone === 'accent' ? 'text-accent' : tone === 'good' ? 'text-good' : 'text-line-strong'
  return (
    <svg viewBox="0 0 14 34" className={`h-8 w-3.5 ${color} ${className}`} fill="none" aria-hidden>
      <path d="M7 2c-.5 9 .6 18 .2 26" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path
        d="M3.4 24.6c1.6 2.2 2.9 4.7 4 7.6 1.1-2.9 2.4-5.4 3.8-7.5"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/** A sideways drawn arrow, for horizontal flows. */
export function SketchArrowRight({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 14" className={`h-3.5 w-10 ${className}`} fill="none" aria-hidden>
      <path d="M2 7.2c9-.6 18 .5 34 .1" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path
        d="M28.6 3.2c2.4 1.5 5 2.8 7.9 3.9-2.9 1.1-5.5 2.4-7.7 3.8"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/** A hand-drawn box, for diagram nodes that should not look like UI. */
export function SketchBox({
  children,
  tone = 'plain',
  className = '',
}: {
  children: ReactNode
  tone?: 'plain' | 'accent' | 'good' | 'warn' | 'faint'
  className?: string
}) {
  const tones: Record<string, string> = {
    plain: 'text-line-strong',
    accent: 'text-accent-line',
    good: 'text-good-line',
    warn: 'text-warn-line',
    faint: 'text-line',
  }
  return (
    <span className={`relative inline-block px-4 py-2.5 ${className}`}>
      <svg
        viewBox="0 0 200 56"
        preserveAspectRatio="none"
        className={`absolute inset-0 h-full w-full ${tones[tone]}`}
        aria-hidden
      >
        <path
          d="M5 7c60-3 128-3 191-1.5 2 14 2.5 30 .8 44.5-64 2-129 2.4-192 .6C3 36 3.2 21 5 7Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
        />
      </svg>
      <span className="relative">{children}</span>
    </span>
  )
}

/** A torn napkin edge, for section boundaries. */
export function TornEdge({ className = '' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 1200 12"
      preserveAspectRatio="none"
      className={`h-3 w-full text-line ${className}`}
      aria-hidden
    >
      <path
        d="M0 6.5c48-3.6 96 3 144-.4 48-3.4 96 2.8 144 1.2 48-1.6 96-5.2 144-2.4 48 2.8 96 6 144 3.2 48-2.8 96-7 144-4.6 48 2.4 96 6.6 144 4.2 48-2.4 96-6.4 144-4.8 48 1.6 96 5.4 144 3"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
      />
    </svg>
  )
}

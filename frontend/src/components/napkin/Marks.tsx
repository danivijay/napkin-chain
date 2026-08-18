/** Hand-drawn status marks. A tick, a caution, a lock - drawn, not iconified. */

export function CheckMark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-4 w-4 ${className}`} fill="none" aria-hidden>
      <path
        d="M2.5 8.6c1.3 1 2.4 2 3.4 3.3C7.8 8.7 10 5.6 13.4 3.2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function CautionMark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-4 w-4 ${className}`} fill="none" aria-hidden>
      <path
        d="M8 2.4 14.2 13H1.8L8 2.4Z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M8 6.4v3.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="8" cy="11.3" r=".8" fill="currentColor" />
    </svg>
  )
}

export function LockMark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-4 w-4 ${className}`} fill="none" aria-hidden>
      <rect x="3.2" y="7" width="9.6" height="6.4" rx="1.4" stroke="currentColor" strokeWidth="1.3" />
      <path d="M5.6 7V5.2a2.4 2.4 0 0 1 4.8 0V7" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  )
}

export function ArrowDown({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 12 28" className={`h-7 w-3 ${className}`} fill="none" aria-hidden>
      <path
        d="M6 1.5c-.4 7 .5 14 .2 21"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      <path
        d="M2.6 19.4c1.5 1.9 2.7 4 3.6 6.6 1-2.5 2.2-4.6 3.5-6.5"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

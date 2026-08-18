/** The mark: three nodes on a chain, drawn by hand. */
export function Logo({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 26 26" className={`h-[22px] w-[22px] ${className}`} fill="none" aria-hidden>
      <rect x="3" y="2.5" width="9" height="6" rx="1.6" stroke="currentColor" strokeWidth="1.4" />
      <rect x="14" y="10" width="9" height="6" rx="1.6" stroke="currentColor" strokeWidth="1.4" />
      <rect x="3" y="17.5" width="9" height="6" rx="1.6" stroke="currentColor" strokeWidth="1.4" />
      <path
        d="M12 5.6c3.6.2 5.4 1.8 5.8 4.2"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
      <path
        d="M14 13.2c-3.6.2-5.5 1.9-6 4.2"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
    </svg>
  )
}

export function Wordmark({ className = '' }: { className?: string }) {
  return (
    <span className={`flex items-center gap-2 ${className}`}>
      <Logo />
      <span className="text-[15px] font-semibold tracking-[-0.01em]">Napkin Chain</span>
    </span>
  )
}

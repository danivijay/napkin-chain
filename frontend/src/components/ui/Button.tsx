import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Spinner } from './Spinner'

type Variant = 'primary' | 'secondary' | 'ghost' | 'quiet'
type Size = 'sm' | 'md' | 'lg'

const VARIANTS: Record<Variant, string> = {
  primary:
    'bg-ink text-paper border-ink hover:bg-ink-secondary hover:border-ink-secondary shadow-hair',
  secondary: 'bg-surface text-ink border-line-strong hover:border-ink-muted hover:bg-subtle',
  ghost: 'bg-transparent text-ink-secondary border-transparent hover:text-ink hover:bg-subtle',
  quiet: 'bg-transparent text-accent border-transparent hover:bg-accent-soft',
}

const SIZES: Record<Size, string> = {
  sm: 'h-8 px-3 text-[13px]',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-5 text-[15px]',
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-md border font-medium ' +
  'transition-colors duration-150 disabled:opacity-40 disabled:pointer-events-none select-none ' +
  // A busy button is disabled too, but stays legible: it is working, not unavailable.
  'disabled:aria-busy:opacity-80'

export function buttonClass(variant: Variant = 'primary', size: Size = 'md', extra = '') {
  return `${BASE} ${VARIANTS[variant]} ${SIZES[size]} ${extra}`
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  /** Shows a spinner and blocks repeat clicks while a request is in flight. */
  loading?: boolean
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  loading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={buttonClass(variant, size, className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && <Spinner tone="current" />}
      {children}
    </button>
  )
}

export function ButtonLink({
  to,
  variant = 'primary',
  size = 'md',
  className = '',
  children,
}: {
  to: string
  variant?: Variant
  size?: Size
  className?: string
  children: ReactNode
}) {
  return (
    <Link to={to} className={buttonClass(variant, size, className)}>
      {children}
    </Link>
  )
}

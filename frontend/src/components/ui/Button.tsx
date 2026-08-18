import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Link } from 'react-router-dom'

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
  'transition-colors duration-150 disabled:opacity-40 disabled:pointer-events-none select-none'

export function buttonClass(variant: Variant = 'primary', size: Size = 'md', extra = '') {
  return `${BASE} ${VARIANTS[variant]} ${SIZES[size]} ${extra}`
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
}

export function Button({ variant = 'primary', size = 'md', className = '', ...props }: ButtonProps) {
  return <button className={buttonClass(variant, size, className)} {...props} />
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

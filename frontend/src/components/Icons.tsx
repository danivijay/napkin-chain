/**
 * Hand-drawn icon set.
 *
 * Every icon is stroked, never filled, at a consistent 1.5 weight with round
 * caps — so they read as pen marks on a napkin rather than as UI furniture.
 * All inherit currentColor.
 */
import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function Icon({ children, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      {...props}
      className={`h-5 w-5 ${props.className ?? ''}`}
    >
      {children}
    </svg>
  )
}

/* ---------------------------------------------------------------- concepts */

export const TrafficIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 17c2.6.3 4.1-1.2 5.4-4.1C9.7 10 11 7 13.4 7c2.3 0 3.4 2.4 4.2 5 .6 1.9 1.4 3.4 3.4 3.6" />
    <path d="M3.2 20.4c5.8.5 11.7.5 17.6.1" opacity=".45" />
  </Icon>
)

export const StorageIcon = (p: IconProps) => (
  <Icon {...p}>
    <ellipse cx="12" cy="6.2" rx="7.4" ry="2.9" />
    <path d="M4.6 6.4v5.2c0 1.6 3.3 2.9 7.4 2.9s7.4-1.3 7.4-2.9V6.4" />
    <path d="M4.6 11.8v5.3c0 1.6 3.3 2.9 7.4 2.9s7.4-1.3 7.4-2.9v-5.3" />
  </Icon>
)

export const BandwidthIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M2.6 12h3.1l2-5.3L11 17.4l2.4-8 1.8 5.1 1.4-2.5h4.8" />
  </Icon>
)

export const CapacityIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3.2" y="4" width="17.6" height="5.4" rx="1.6" />
    <rect x="3.2" y="13.4" width="17.6" height="5.4" rx="1.6" />
    <path d="M6.6 6.7h.01M6.6 16.1h.01" />
    <path d="M10.4 6.7h6.2M10.4 16.1h6.2" opacity=".45" />
  </Icon>
)

export const AssumptionsIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M9.3 8.6c.2-1.6 1.4-2.6 2.9-2.6 1.7 0 2.9 1 2.9 2.5 0 2.4-2.8 2.4-2.8 4.7" />
    <path d="M12.2 17.6h.01" />
    <path d="M4.5 20.2c-.8-2.4-1.1-4.9-.8-7.5C4.3 7 8 3.2 12.6 3.2c4.8 0 7.9 3.6 7.9 8.3 0 4.2-2.4 7.5-6.4 8.6" opacity=".45" />
  </Icon>
)

/* -------------------------------------------------------------- navigation */

export const HomeIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3.6 10.6 12 4l8.4 6.6" />
    <path d="M5.6 9.6v9.2a1 1 0 0 0 1 1h10.8a1 1 0 0 0 1-1V9.6" />
  </Icon>
)

export const ChallengesIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3.4" y="3.6" width="7" height="5" rx="1.4" />
    <rect x="13.6" y="9.6" width="7" height="5" rx="1.4" />
    <rect x="3.4" y="15.6" width="7" height="5" rx="1.4" />
    <path d="M10.4 6.4c2.6.2 3.9 1.3 4.2 3.2M13.6 12.6c-2.6.2-4 1.3-4.4 3" opacity=".55" />
  </Icon>
)

export const LearnIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 5.2c2.7-.7 5.4-.7 8 .6 2.6-1.3 5.3-1.3 8-.6v12.4c-2.7-.7-5.4-.7-8 .6-2.6-1.3-5.3-1.3-8-.6Z" />
    <path d="M12 5.8v12.4" opacity=".45" />
  </Icon>
)

export const ProgressIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3.6 20.2h16.8" opacity=".45" />
    <path d="M6.6 20V13.8M11 20V8.2M15.4 20v-4M19.8 20V5.4" />
  </Icon>
)

/* ------------------------------------------------------------------- misc */

export const ChainIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M9.6 13.8a3.5 3.5 0 0 0 5.3.4l2.4-2.4a3.5 3.5 0 0 0-4.9-4.9l-1.4 1.3" />
    <path d="M14.4 10.2a3.5 3.5 0 0 0-5.3-.4l-2.4 2.4a3.5 3.5 0 0 0 4.9 4.9l1.4-1.3" />
  </Icon>
)

export const StopwatchIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="13.4" r="7.2" />
    <path d="M12 9.8v3.6l2.3 1.6M9.6 2.8h4.8M18.6 7.4l1.4-1.5" />
  </Icon>
)

export const TargetIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="8.2" />
    <circle cx="12" cy="12" r="4.2" opacity=".6" />
    <circle cx="12" cy="12" r=".6" />
  </Icon>
)

export const PencilIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4.2 16.4 15.6 5a2.4 2.4 0 0 1 3.4 3.4L7.6 19.8l-4.4 1z" />
    <path d="M14.2 6.6 17.4 9.8" opacity=".5" />
  </Icon>
)

export const AREA_ICONS = {
  traffic: TrafficIcon,
  storage: StorageIcon,
  bandwidth: BandwidthIcon,
  capacity: CapacityIcon,
  assumptions: AssumptionsIcon,
} as const

export type ConceptArea = keyof typeof AREA_ICONS

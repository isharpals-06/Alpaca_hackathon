// ==========================================================================
// ALPACA AI — MOTION SYSTEM
// One disciplined vocabulary so "motion everywhere" reads as intentional,
// not busy. Framer Motion variants + shared easings. Reduced-motion aware.
// ==========================================================================
import type { Variants, Transition } from 'framer-motion'

// Shared easings (mirror the CSS custom props in tokens.css)
export const EASE_OUT = [0.16, 1, 0.3, 1] as const
export const EASE_IO = [0.65, 0, 0.35, 1] as const
export const EASE_SEAL = [0.34, 1.56, 0.64, 1] as const

export const spring: Transition = { type: 'spring', stiffness: 340, damping: 30 }

// Fade + rise — the workhorse entrance.
export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EASE_OUT } },
}

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.5, ease: EASE_OUT } },
}

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: EASE_OUT } },
}

// Stagger a group of children (use with staggerItem on each child).
export const staggerContainer = (stagger = 0.08, delay = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: stagger, delayChildren: delay } },
})

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE_OUT } },
}

// The struck copper seal — an overshoot "stamp" landing slightly rotated.
export const sealStamp: Variants = {
  hidden: { opacity: 0, scale: 1.9, rotate: 12 },
  show: {
    opacity: 1,
    scale: 1,
    rotate: -3,
    transition: { duration: 0.55, ease: EASE_SEAL },
  },
}

// Engraving lines that "draw in".
export const drawPath: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  show: {
    pathLength: 1,
    opacity: 1,
    transition: { pathLength: { duration: 1.6, ease: EASE_OUT }, opacity: { duration: 0.3 } },
  },
}

// Page transition for route changes.
export const pageVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: EASE_OUT } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.22, ease: EASE_IO } },
}

// Common viewport config for whileInView reveals.
export const inViewOnce = { once: true, amount: 0.25 } as const

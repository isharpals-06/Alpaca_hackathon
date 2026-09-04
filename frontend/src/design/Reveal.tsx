// ==========================================================================
// Reveal — scroll-triggered entrance wrapper. Fades + rises into view once.
// Respects reduced-motion (renders static). The default motion primitive.
// ==========================================================================
import type { CSSProperties, ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { EASE_OUT, inViewOnce } from './motion'

interface RevealProps {
  children: ReactNode
  delay?: number
  y?: number
  className?: string
  style?: CSSProperties
}

export function Reveal({ children, delay = 0, y = 18, className, style }: RevealProps) {
  const reduce = useReducedMotion()
  if (reduce) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    )
  }
  return (
    <motion.div
      className={className}
      style={style}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={inViewOnce}
      transition={{ duration: 0.6, ease: EASE_OUT, delay }}
    >
      {children}
    </motion.div>
  )
}

export default Reveal

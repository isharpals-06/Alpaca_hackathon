// ==========================================================================
// PageTransition — wraps a route's content for enter/exit animation.
// Use inside <AnimatePresence mode="wait"> keyed on location.pathname.
// ==========================================================================
import type { ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { pageVariants } from './motion'

export function PageTransition({ children }: { children: ReactNode }) {
  const reduce = useReducedMotion()
  if (reduce) return <>{children}</>
  return (
    <motion.div variants={pageVariants} initial="hidden" animate="show" exit="exit">
      {children}
    </motion.div>
  )
}

export default PageTransition

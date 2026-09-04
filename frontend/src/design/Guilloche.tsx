// ==========================================================================
// Guilloche — hand-rolled banknote/security engraving (nested rosettes).
// The signature texture of "The Certified Instrument". No dependencies.
// ==========================================================================
import { useMemo, useId } from 'react'
import type { CSSProperties } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { EASE_OUT } from './motion'

/** Parametric rosette: a circle radius modulated by two cosine harmonics. */
export function rosettePath(
  cx: number,
  cy: number,
  baseR: number,
  amp: number,
  lobes: number,
  phase: number,
  steps = 360,
): string {
  let d = ''
  for (let i = 0; i <= steps; i++) {
    const th = (i / steps) * Math.PI * 2
    const rr =
      baseR +
      amp * Math.cos(lobes * th + phase) +
      amp * 0.42 * Math.cos(lobes * 2 * th - phase * 1.7)
    const x = cx + rr * Math.cos(th)
    const y = cy + rr * Math.sin(th)
    d += (i === 0 ? 'M' : 'L') + x.toFixed(2) + ' ' + y.toFixed(2) + ' '
  }
  return d + 'Z'
}

interface GuillocheProps {
  size?: number
  color?: string
  opacity?: number
  strokeWidth?: number
  rings?: number
  petals?: number
  animate?: boolean
  className?: string
  style?: CSSProperties
}

export function Guilloche({
  size = 320,
  color = 'var(--copper)',
  opacity = 0.14,
  strokeWidth = 0.7,
  rings = 7,
  petals = 12,
  animate = false,
  className,
  style,
}: GuillocheProps) {
  const uid = useId().replace(/:/g, '')
  const reduce = useReducedMotion()
  const cx = size / 2
  const cy = size / 2

  const paths = useMemo(() => {
    const R = size / 2 - strokeWidth
    return Array.from({ length: rings }, (_, i) => {
      const baseR = R * (1 - (i * 0.44) / rings)
      const amp = baseR * 0.055
      const lobes = petals + (i % 3) * 2
      const phase = i * 0.6
      return rosettePath(cx, cy, baseR, amp, lobes, phase)
    })
  }, [size, rings, petals, strokeWidth, cx, cy])

  const doAnimate = animate && !reduce

  return (
    <svg
      className={className}
      style={style}
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      fill="none"
      aria-hidden="true"
    >
      <g stroke={color} strokeWidth={strokeWidth} opacity={opacity} fill="none">
        {paths.map((d, i) =>
          doAnimate ? (
            <motion.path
              key={`${uid}-${i}`}
              d={d}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{
                pathLength: { duration: 2.2, ease: EASE_OUT, delay: i * 0.12 },
                opacity: { duration: 0.4, delay: i * 0.12 },
              }}
            />
          ) : (
            <path key={`${uid}-${i}`} d={d} />
          ),
        )}
      </g>
    </svg>
  )
}

export default Guilloche

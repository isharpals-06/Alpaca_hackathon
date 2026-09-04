// ==========================================================================
// Seal — a struck copper certification medallion. The single boldest mark in
// the system: it lands on every certified decision with an overshoot "stamp".
// Guilloché core, reeded edge, curved legend, letterpressed verdict.
// ==========================================================================
import { useId } from 'react'
import type { CSSProperties } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { sealStamp } from './motion'
import { rosettePath } from './Guilloche'

type SealTone = 'copper' | 'oxblood' | 'olive' | 'slate'

const TONES: Record<SealTone, [string, string, string]> = {
  copper: ['#DBA45E', '#B5651D', '#743F0D'],
  oxblood: ['#BC6D61', '#8C3B2E', '#57221A'],
  olive: ['#9CA97B', '#6B7A4F', '#414D2E'],
  slate: ['#828C98', '#434E5A', '#28303A'],
}

interface SealProps {
  label?: string
  sub?: string
  serial?: string
  size?: number
  tone?: SealTone
  animate?: boolean
  className?: string
  style?: CSSProperties
}

export function Seal({
  label = 'CERTIFIED',
  sub = 'ALPACA · COUNCIL',
  serial,
  size = 132,
  tone = 'copper',
  animate = true,
  className,
  style,
}: SealProps) {
  const uid = useId().replace(/:/g, '')
  const reduce = useReducedMotion()
  const [light, mid, dark] = TONES[tone]
  const S = size
  const cx = S / 2
  const cy = S / 2
  const R = S / 2 - 1

  const rt = R * 0.78 // radius for curved legend
  const topArc = `M ${cx - rt} ${cy} A ${rt} ${rt} 0 0 1 ${cx + rt} ${cy}`
  const cream = '#FBF3E7'

  const labelSize = Math.min(S * 0.185, (S * 1.15) / Math.max(label.length, 4))

  return (
    <motion.svg
      className={className}
      style={style}
      width={S}
      height={S}
      viewBox={`0 0 ${S} ${S}`}
      role="img"
      aria-label={`${label} seal`}
      variants={animate && !reduce ? sealStamp : undefined}
      initial={animate && !reduce ? 'hidden' : false}
      whileInView={animate && !reduce ? 'show' : undefined}
      viewport={{ once: true, amount: 0.6 }}
    >
      <defs>
        <radialGradient id={`g-${uid}`} cx="38%" cy="32%" r="72%">
          <stop offset="0%" stopColor={light} />
          <stop offset="55%" stopColor={mid} />
          <stop offset="100%" stopColor={dark} />
        </radialGradient>
        <filter id={`e-${uid}`} x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1.4" stdDeviation="0.6" floodColor="#000" floodOpacity="0.35" />
        </filter>
      </defs>

      {/* Struck disc */}
      <circle cx={cx} cy={cy} r={R} fill={`url(#g-${uid})`} />
      {/* Reeded coin edge */}
      <circle
        cx={cx}
        cy={cy}
        r={R - 1.5}
        fill="none"
        stroke={dark}
        strokeWidth={2.5}
        strokeDasharray="1.4 3"
        opacity="0.7"
      />
      {/* Bright rim highlight (top-left light source) */}
      <circle cx={cx} cy={cy} r={R - 3.5} fill="none" stroke={cream} strokeWidth="0.8" opacity="0.32" />

      {/* Guilloché core */}
      <path
        d={rosettePath(cx, cy, R * 0.5, R * 0.5 * 0.06, 14, 0)}
        fill="none"
        stroke={cream}
        strokeWidth="0.5"
        opacity="0.26"
      />
      <path
        d={rosettePath(cx, cy, R * 0.4, R * 0.4 * 0.07, 10, 0.7)}
        fill="none"
        stroke={cream}
        strokeWidth="0.5"
        opacity="0.2"
      />

      {/* Inner legend ring */}
      <circle cx={cx} cy={cy} r={R * 0.62} fill="none" stroke={cream} strokeWidth="0.8" opacity="0.4" />
      <circle cx={cx} cy={cy} r={R * 0.6} fill="none" stroke={dark} strokeWidth="0.8" opacity="0.5" />

      {/* Curved top legend */}
      <path id={`arc-${uid}`} d={topArc} fill="none" />
      <text
        fill={cream}
        fontFamily="var(--font-mono)"
        fontSize={S * 0.072}
        fontWeight={600}
        letterSpacing={S * 0.028}
        opacity="0.92"
      >
        <textPath href={`#arc-${uid}`} startOffset="50%" textAnchor="middle">
          {sub}
        </textPath>
      </text>

      {/* Center verdict — letterpressed */}
      <text
        x={cx}
        y={cy + labelSize * 0.02}
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="var(--font-display)"
        fontSize={labelSize}
        fontWeight={800}
        letterSpacing={-0.5}
        fill={dark}
        opacity="0.5"
        transform="translate(0 1.4)"
      >
        {label}
      </text>
      <text
        x={cx}
        y={cy + labelSize * 0.02}
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="var(--font-display)"
        fontSize={labelSize}
        fontWeight={800}
        letterSpacing={-0.5}
        fill={cream}
        filter={`url(#e-${uid})`}
      >
        {label}
      </text>

      {/* Star flourish above verdict */}
      <text
        x={cx}
        y={cy - R * 0.28}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={S * 0.09}
        fill={cream}
        opacity="0.8"
      >
        ★
      </text>

      {/* Serial at base */}
      {serial && (
        <text
          x={cx}
          y={cy + R * 0.34}
          textAnchor="middle"
          fontFamily="var(--font-mono)"
          fontSize={S * 0.052}
          letterSpacing={S * 0.006}
          fill={cream}
          opacity="0.8"
        >
          {serial}
        </text>
      )}
    </motion.svg>
  )
}

export default Seal

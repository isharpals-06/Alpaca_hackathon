// ==========================================================================
// SecurityStrip — banknote microprint band. A hairline-bounded strip of tiny
// repeated legend text. Reads as security microtext, not a nav meta string.
// ==========================================================================
import type { CSSProperties } from 'react'

interface SecurityStripProps {
  text?: string
  variant?: 'paper' | 'ink'
  className?: string
  style?: CSSProperties
}

export function SecurityStrip({
  text = 'ALPACA CAPITAL — CERTIFIED TRADING INSTRUMENT — EVERY DECISION RECORDED —',
  variant = 'paper',
  className,
  style,
}: SecurityStripProps) {
  const ink = variant === 'ink'
  const line = ink ? 'var(--copper-line)' : 'var(--copper-line)'
  const color = ink ? 'var(--ink-faint)' : 'var(--faint-ink)'
  const repeated = Array.from({ length: 8 }).map(() => text).join(' ')
  return (
    <div
      className={className}
      aria-hidden="true"
      style={{
        overflow: 'hidden',
        whiteSpace: 'nowrap',
        borderTop: `1px solid ${line}`,
        borderBottom: `1px solid ${line}`,
        padding: '3px 0',
        ...style,
      }}
    >
      <span
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 8.5,
          letterSpacing: '0.18em',
          color,
          textTransform: 'uppercase',
        }}
      >
        {repeated}
      </span>
    </div>
  )
}

export default SecurityStrip

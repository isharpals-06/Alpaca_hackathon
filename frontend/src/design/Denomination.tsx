// ==========================================================================
// Denomination — a banknote-style figure block: a small engraved field label
// over a large tabular numeral. Used for stats, balances, P&L.
// ==========================================================================
import type { CSSProperties, ReactNode } from 'react'

type DenomTone = 'ink' | 'gain' | 'loss' | 'copper' | 'neutral' | 'paper'

const COLOR: Record<DenomTone, string> = {
  ink: 'var(--espresso)',
  gain: 'var(--olive)',
  loss: 'var(--oxblood)',
  copper: 'var(--copper-ink)',
  neutral: 'var(--warm-taupe)',
  paper: 'var(--ink-text)',
}

interface DenominationProps {
  label: string
  value: ReactNode
  sub?: ReactNode
  tone?: DenomTone
  size?: number
  icon?: ReactNode
  className?: string
  style?: CSSProperties
}

export function Denomination({
  label,
  value,
  sub,
  tone = 'ink',
  size = 30,
  icon,
  className,
  style,
}: DenominationProps) {
  return (
    <div className={className} style={style}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        {icon && <span style={{ color: 'var(--copper)', display: 'inline-flex' }}>{icon}</span>}
        <span className="field-label">{label}</span>
      </div>
      <div
        className="num"
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: size,
          fontWeight: 600,
          lineHeight: 1,
          letterSpacing: '-0.02em',
          color: COLOR[tone],
        }}
      >
        {value}
      </div>
      {sub && (
        <div style={{ marginTop: 6, fontSize: 12.5, color: 'var(--warm-taupe)' }}>{sub}</div>
      )}
    </div>
  )
}

export default Denomination

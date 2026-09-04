import type { FC } from 'react'

export interface DecisionStampProps {
  decision: string
  className?: string
}

export const DecisionStamp: FC<DecisionStampProps> = ({ decision, className = '' }) => {
  const normalized = (decision || '').toUpperCase().replace(/_/g, ' ').trim()

  // Tone by outcome — a struck, letterpressed certificate stamp.
  let bg = 'rgba(122, 106, 93, 0.10)'
  let color = 'var(--warm-taupe)'
  let border = 'rgba(122, 106, 93, 0.38)'
  let label = normalized || 'NO TRADE'

  if (normalized === 'EXECUTED' || normalized === 'TRADE' || normalized === 'FILLED') {
    bg = 'var(--copper-wash)'
    color = 'var(--copper-ink)'
    border = 'rgba(181, 101, 29, 0.42)'
    label = 'EXECUTED'
  } else if (normalized.includes('VETO') || normalized.includes('RISK') || normalized === 'BLOCKED' || normalized === 'REJECTED') {
    bg = 'var(--oxblood-wash)'
    color = 'var(--oxblood)'
    border = 'rgba(140, 59, 46, 0.44)'
    label = 'RISK VETO'
  } else if (normalized === 'NO TRADE' || normalized === 'HOLD') {
    bg = 'rgba(122, 106, 93, 0.10)'
    color = 'var(--warm-taupe)'
    border = 'rgba(122, 106, 93, 0.35)'
    label = 'NO TRADE'
  }

  return (
    <span
      className={`decision-stamp ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3px 9px',
        borderRadius: 'var(--r-xs)',
        fontSize: '10.5px',
        fontWeight: 700,
        letterSpacing: '0.1em',
        fontFamily: 'var(--font-mono)',
        textTransform: 'uppercase',
        backgroundColor: bg,
        color: color,
        border: `1.5px solid ${border}`,
        boxShadow: 'inset 0 1px 0 rgba(255, 253, 249, 0.55)',
        textShadow: '0 1px 0 rgba(255, 253, 249, 0.5)',
        transform: 'rotate(-1.5deg)',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  )
}

export default DecisionStamp

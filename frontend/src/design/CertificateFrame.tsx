// ==========================================================================
// CertificateFrame — a security-bordered container: double engraved rule,
// copper corner registration marks, optional guilloché watermark.
// variant="paper" for records, variant="ink" for live/vault moments.
// ==========================================================================
import type { CSSProperties, ReactNode } from 'react'
import Guilloche from './Guilloche'

interface CertificateFrameProps {
  children: ReactNode
  variant?: 'paper' | 'ink'
  watermark?: boolean
  padding?: number | string
  radius?: number
  className?: string
  style?: CSSProperties
}

function Corner({ pos, color }: { pos: 'tl' | 'tr' | 'bl' | 'br'; color: string }) {
  const base: CSSProperties = { position: 'absolute', width: 14, height: 14, pointerEvents: 'none' }
  const map: Record<string, CSSProperties> = {
    tl: { top: 6, left: 6 },
    tr: { top: 6, right: 6, transform: 'scaleX(-1)' },
    bl: { bottom: 6, left: 6, transform: 'scaleY(-1)' },
    br: { bottom: 6, right: 6, transform: 'scale(-1)' },
  }
  return (
    <svg style={{ ...base, ...map[pos] }} viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M1 6 V1 H6" stroke={color} strokeWidth="1.4" />
      <circle cx="1.5" cy="1.5" r="1.1" fill={color} />
    </svg>
  )
}

export function CertificateFrame({
  children,
  variant = 'paper',
  watermark = false,
  padding = 28,
  radius = 12,
  className,
  style,
}: CertificateFrameProps) {
  const ink = variant === 'ink'
  const outer = ink ? 'var(--ink-line-strong)' : 'var(--hairline-strong)'
  const inner = ink ? 'var(--ink-line)' : 'var(--hairline)'
  const corner = ink ? 'var(--copper-foil)' : 'var(--copper)'
  const bg = ink ? 'var(--ink)' : 'var(--surface)'

  return (
    <div
      className={`${ink ? 'on-ink ' : ''}${className ?? ''}`}
      style={{
        position: 'relative',
        background: bg,
        border: `1px solid ${outer}`,
        borderRadius: radius,
        boxShadow: ink ? 'var(--shadow-press)' : 'var(--shadow-paper)',
        ...style,
      }}
    >
      <div
        style={{
          position: 'relative',
          border: `1px solid ${inner}`,
          borderRadius: radius - 4,
          margin: 5,
          padding,
          overflow: 'hidden',
        }}
      >
        {watermark && (
          <Guilloche
            size={420}
            color={ink ? 'var(--copper-foil)' : 'var(--copper)'}
            opacity={ink ? 0.07 : 0.05}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'none',
            }}
          />
        )}
        <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
      </div>
      <Corner pos="tl" color={corner} />
      <Corner pos="tr" color={corner} />
      <Corner pos="bl" color={corner} />
      <Corner pos="br" color={corner} />
    </div>
  )
}

export default CertificateFrame

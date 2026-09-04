import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function LedgerTabNav() {
  const [isHovered, setIsHovered] = useState(false)
  const location = useLocation()

  const tabs = [
    { label: 'Live Desk', path: '/dashboard', init: 'L' },
    { label: 'History', path: '/dashboard/history', init: 'H' },
    { label: 'P&L', path: '/dashboard/performance', init: 'P' },
  ]

  return (
    <nav
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'fixed',
        right: 0,
        top: '50%',
        transform: 'translateY(-50%)',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--surface)',
        border: '1px solid var(--hairline-strong)',
        borderRight: 0,
        boxShadow: '-6px 0 22px rgba(54, 33, 26, 0.10)',
        transition: 'width var(--dur-base) var(--ease-out)',
        width: isHovered ? '150px' : '44px',
        zIndex: 100,
        borderTopLeftRadius: 'var(--r-lg)',
        borderBottomLeftRadius: 'var(--r-lg)',
        overflow: 'hidden'
      }}
    >
      {tabs.map((tab, idx) => {
        const isActive = location.pathname === tab.path
        return (
          <Link
            key={tab.path}
            to={tab.path}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: isHovered ? 'flex-start' : 'center',
              gap: '10px',
              padding: '15px 14px',
              textDecoration: 'none',
              color: isActive ? 'var(--copper-ink)' : 'var(--warm-taupe)',
              background: isActive ? 'var(--copper-wash)' : 'transparent',
              borderLeft: isActive ? '3px solid var(--copper)' : '3px solid transparent',
              borderBottom: idx < tabs.length - 1 ? '1px solid var(--hairline)' : 'none',
              transition: 'background var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out)',
              fontWeight: isActive ? 700 : 500,
            }}
          >
            {isHovered ? (
              <span style={{ whiteSpace: 'nowrap', fontFamily: 'var(--font-body)', fontSize: '13.5px', letterSpacing: '-0.01em' }}>{tab.label}</span>
            ) : (
              <span style={{ transform: 'rotate(-90deg)', fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 600, letterSpacing: '0.1em', display: 'inline-block' }}>{tab.init}</span>
            )}
          </Link>
        )
      })}
    </nav>
  )
}

import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth, clearSession } from '../../lib/useAuth'
import { Seal } from '../../design'
import LedgerTabNav from '../nav/LedgerTabNav'
import '../../styles/shell.css'

type HealthState = 'checking' | 'online' | 'offline'

interface AppShellProps {
  children: React.ReactNode
  /** Short page label shown in the topbar beside the brand (e.g. "Live Desk"). */
  section?: string
}

/**
 * The persistent chrome for every authenticated page — a certified "desk".
 * Owns the top ledger bar (brand, backend seal-of-health, trader identity)
 * and the edge tab rail. Each page fetches its own content; the shell only
 * pings /api/health so the status light is consistent everywhere.
 */
export const AppShell: React.FC<AppShellProps> = ({ children, section }) => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [health, setHealth] = useState<HealthState>('checking')

  useEffect(() => {
    let alive = true
    const ping = async () => {
      try {
        const res = await fetch('/api/health')
        if (!alive) return
        setHealth(res.ok ? 'online' : 'offline')
      } catch {
        if (alive) setHealth('offline')
      }
    }
    ping()
    const t = setInterval(ping, 20000)
    return () => {
      alive = false
      clearInterval(t)
    }
  }, [])

  const traderName =
    (user?.user_metadata as any)?.display_name ||
    user?.email?.split('@')[0] ||
    'Trader'

  const handleSignOut = () => {
    clearSession()
    navigate('/')
  }

  const statusLabel =
    health === 'online' ? 'Desk Online' : health === 'offline' ? 'Desk Offline' : 'Connecting'

  return (
    <div className="shell">
      <header className="shell-topbar">
        <div className="shell-topbar-inner">
          <div className="shell-brand-group">
            <Link to="/dashboard" className="shell-brand">
              <Seal size={32} label="A" sub="" animate={false} />
              <span className="shell-brand-text">Alpaca<b>AI</b></span>
            </Link>
            {section && (
              <>
                <span className="shell-brand-div" aria-hidden />
                <span className="shell-section">{section}</span>
              </>
            )}
          </div>

          <div className="shell-topbar-right">
            <span className={`shell-status shell-status--${health}`}>
              <span className="shell-status-dot" />
              <span className="shell-status-label">{statusLabel}</span>
            </span>

            <span className="shell-topbar-div" aria-hidden />

            <span className="shell-trader" title={user?.email || traderName}>
              <span className="shell-trader-label">Trader</span>
              <span className="shell-trader-name">{traderName}</span>
            </span>

            <button type="button" className="btn btn--quiet btn--sm shell-signout" onClick={handleSignOut}>
              <LogOut size={14} />
              <span className="shell-signout-text">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      <main className="shell-main">{children}</main>

      <LedgerTabNav />
    </div>
  )
}

export default AppShell

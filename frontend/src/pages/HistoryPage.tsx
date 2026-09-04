import { useEffect, useState } from 'react'
import AppShell from '../components/layout/AppShell'
import DecisionLedgerTable from '../components/history/DecisionLedgerTable'
import { Decision } from '../types'
import '../styles/history.css'

export default function HistoryPage() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Load Decisions
  useEffect(() => {
    setLoading(true)
    setError('')
    fetch('/api/decisions')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch decisions')
        return res.json()
      })
      .then((data) => {
        setDecisions(Array.isArray(data) ? data : [])
      })
      .catch((err) => {
        console.error('Decisions fetch error:', err)
        setError('Failed to load decisions history.')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <AppShell section="History">
      {/* SECTION HEADER */}
      <header className="rr-head">
        <div className="rr-head__text">
          <h1 className="rr-head__title">Council Decision History</h1>
          <p className="rr-head__sub">
            Full chronological ledger of every AI debate decision, covered call overlay, and risk governance veto.
          </p>
        </div>

        <div className="rr-head__aside">
          <div className="rr-figure">
            <span className="field-label">Records on file</span>
            <span className="rr-figure__num num">{decisions.length}</span>
          </div>
        </div>
      </header>

      {/* LEDGER TABLE */}
      <DecisionLedgerTable decisions={decisions} loading={loading} error={error} />
    </AppShell>
  )
}

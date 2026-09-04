import { useEffect, useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import AppShell from '../components/layout/AppShell'
import PnLSummary from '../components/performance/PnLSummary'
import PnLChart from '../components/performance/PnLChart'
import { PerformanceData } from '../types'
import { Reveal, Seal, EASE_OUT, inViewOnce } from '../design'
import '../styles/performance.css'

export default function PerformancePage() {
  const [performance, setPerformance] = useState<PerformanceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const reduce = useReducedMotion()

  // Load Performance Data
  useEffect(() => {
    setLoading(true)
    setError('')
    fetch('/api/performance')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch performance metrics')
        return res.json()
      })
      .then((data) => {
        setPerformance(data)
      })
      .catch((err) => {
        console.error('Performance fetch error:', err)
        setError('Failed to load performance data.')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const formatMoney = (val: number) => {
    const formatted = Math.abs(val).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
    const sign = val >= 0 ? '+$' : '-$'
    return `${sign}${formatted}`
  }

  // Relative magnitude for the engraved tally bars (display only).
  const maxAbs =
    performance?.breakdown && performance.breakdown.length > 0
      ? Math.max(...performance.breakdown.map((i) => Math.abs(i.realized_pnl)), 1)
      : 1

  return (
    <AppShell section="P&L">
      {/* SECTION HEADER */}
      <header className="rr-head">
        <div className="rr-head__text">
          <h1 className="rr-head__title">Portfolio Performance</h1>
          <p className="rr-head__sub">
            Track cumulative options overlay returns, realized cash premium, and strategy win rates.
          </p>
        </div>

        <div className="rr-head__aside">
          <Seal size={58} tone="copper" sub="ALPACA CAPITAL" animate={!reduce} />
        </div>
      </header>

      {error && <div className="perf-error">{error}</div>}

      {/* SUMMARY — denomination statement */}
      <Reveal>
        <PnLSummary performance={performance} loading={loading} />
      </Reveal>

      {/* CUMULATIVE P&L CHART */}
      <Reveal delay={0.06}>
        <PnLChart history={performance?.history || []} loading={loading} />
      </Reveal>

      {/* POSITIONS BREAKDOWN TABLE */}
      {performance?.breakdown && performance.breakdown.length > 0 && (
        <Reveal delay={0.12}>
          <section className="eng-panel pnl-panel">
            <div className="eng-panel__head">
              <div>
                <div className="eng-panel__title">Position Breakdown &amp; Closed Trades</div>
                <div className="eng-panel__sub">Individual P&amp;L contribution by contract and underlying symbol.</div>
              </div>
            </div>

            <div className="pnl-scroll">
              <table className="pnl-table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Entry Date</th>
                    <th>Strategy</th>
                    <th className="is-right">Realized P&L</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {performance.breakdown.map((item, idx) => {
                    const gain = item.realized_pnl >= 0
                    const pct = Math.min(100, (Math.abs(item.realized_pnl) / maxAbs) * 100)
                    return (
                      <tr key={idx}>
                        <td className="pnl-cell-symbol">{item.symbol}</td>
                        <td className="pnl-cell-date">{item.entry_date}</td>
                        <td className="pnl-cell-strategy">{item.strategy.replace(/_/g, ' ')}</td>
                        <td className="pnl-cell-realized">
                          <span className={`pnl-realized-num ${gain ? 'is-gain' : 'is-loss'}`}>
                            {formatMoney(item.realized_pnl)}
                          </span>
                          <div className="pnl-tally">
                            {reduce ? (
                              <div
                                className={`pnl-tally__fill pnl-tally__fill--${gain ? 'gain' : 'loss'}`}
                                style={{ width: `${pct}%` }}
                              />
                            ) : (
                              <motion.div
                                className={`pnl-tally__fill pnl-tally__fill--${gain ? 'gain' : 'loss'}`}
                                initial={{ width: 0 }}
                                whileInView={{ width: `${pct}%` }}
                                viewport={inViewOnce}
                                transition={{ duration: 0.7, ease: EASE_OUT }}
                              />
                            )}
                          </div>
                        </td>
                        <td>
                          <span className={`pnl-status ${item.status === 'OPEN' ? 'pnl-status--open' : 'pnl-status--closed'}`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </Reveal>
      )}
    </AppShell>
  )
}

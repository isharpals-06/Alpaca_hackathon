import { useState } from 'react'
import type { FC } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { Decision } from '../../types'
import DecisionStamp from '../shared/DecisionStamp'
import { staggerContainer, staggerItem, inViewOnce } from '../../design'

interface DecisionLedgerTableProps {
  decisions: Decision[]
  loading?: boolean
  error?: string
}

export const DecisionLedgerTable: FC<DecisionLedgerTableProps> = ({
  decisions,
  loading = false,
  error = '',
}) => {
  const [filter, setFilter] = useState<'all' | 'executed'>('all')
  const reduce = useReducedMotion()

  const isExecuted = (action: string) => {
    const norm = (action || '').toUpperCase().replace(/_/g, ' ')
    return norm === 'EXECUTED' || norm === 'TRADE' || norm === 'FILLED'
  }

  // Sort most recent first
  const sortedDecisions = [...decisions].sort((a, b) => {
    const dateA = new Date(a.created_at || 0).getTime()
    const dateB = new Date(b.created_at || 0).getTime()
    return dateB - dateA
  })

  const filteredDecisions = sortedDecisions.filter((d) => {
    if (filter === 'executed') {
      return isExecuted(d.action)
    }
    return true
  })

  const formatDate = (isoString: string) => {
    if (!isoString) return '—'
    const date = new Date(isoString)
    if (isNaN(date.getTime())) return isoString
    return date.toLocaleDateString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const formatMoney = (val?: number) => {
    if (val === undefined || val === null || isNaN(val)) return '—'
    return `$${val.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`
  }

  const renderCells = (item: Decision) => {
    const orderText = item.order_spec || item.recommended_strategy || '—'
    const statusText = (item.status || (isExecuted(item.action) ? 'FILLED' : item.action.includes('VETO') ? 'BLOCKED' : 'RECORDED')).toUpperCase()
    const statusClass =
      statusText === 'FILLED' ? 'ledger-status--filled' : statusText === 'BLOCKED' ? 'ledger-status--blocked' : 'ledger-status--recorded'

    return (
      <>
        <td className="ledger-cell-date">{formatDate(item.created_at)}</td>
        <td className="ledger-cell-symbol">{item.symbol || 'SPY'}</td>
        <td>
          <DecisionStamp decision={item.action} />
        </td>
        <td className="ledger-cell-order">{orderText}</td>
        <td className="ledger-cell-premium">{formatMoney(item.premium)}</td>
        <td>
          <span className={`ledger-status ${statusClass}`}>{statusText}</span>
        </td>
      </>
    )
  }

  return (
    <div className="eng-panel ledger-panel">
      {/* Header & Segmented Filter */}
      <div className="eng-panel__head">
        <div>
          <div className="eng-panel__title">Decision Ledger</div>
          <div className="eng-panel__sub">
            Complete audit trail of autonomous AI agent recommendations &amp; risk decisions.
          </div>
        </div>

        <div className="ledger-filter" role="group" aria-label="Filter decisions">
          <button
            type="button"
            className={`ledger-filter__btn ${filter === 'all' ? 'is-active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Decisions <span className="ledger-filter__count">({decisions.length})</span>
          </button>
          <button
            type="button"
            className={`ledger-filter__btn ${filter === 'executed' ? 'is-active' : ''}`}
            onClick={() => setFilter('executed')}
          >
            Executed Only <span className="ledger-filter__count">({decisions.filter((d) => isExecuted(d.action)).length})</span>
          </button>
        </div>
      </div>

      {error && <div className="ledger-error">{error}</div>}

      {loading ? (
        <div className="ledger-state">Loading decision ledger…</div>
      ) : filteredDecisions.length === 0 ? (
        <div className="ledger-state">No decisions yet.</div>
      ) : (
        <div className="ledger-scroll">
          <table className="ledger-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Symbol</th>
                <th>Decision</th>
                <th>Order</th>
                <th className="is-right">Premium</th>
                <th>Status</th>
              </tr>
            </thead>
            {reduce ? (
              <tbody>
                {filteredDecisions.map((item) => (
                  <tr key={item.id}>{renderCells(item)}</tr>
                ))}
              </tbody>
            ) : (
              <motion.tbody
                variants={staggerContainer(0.05)}
                initial="hidden"
                whileInView="show"
                viewport={inViewOnce}
              >
                {filteredDecisions.map((item) => (
                  <motion.tr key={item.id} variants={staggerItem}>
                    {renderCells(item)}
                  </motion.tr>
                ))}
              </motion.tbody>
            )}
          </table>
        </div>
      )}
    </div>
  )
}

export default DecisionLedgerTable

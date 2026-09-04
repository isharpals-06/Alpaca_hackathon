import type { FC } from 'react'
import { TrendingUp, DollarSign, Activity, Percent } from 'lucide-react'
import { PerformanceData } from '../../types'
import { CertificateFrame, Denomination, SecurityStrip } from '../../design'

interface PnLSummaryProps {
  performance: PerformanceData | null
  loading?: boolean
}

export const PnLSummary: FC<PnLSummaryProps> = ({ performance, loading = false }) => {
  const totalPnl = performance?.total_pnl ?? 0
  const realizedPnl = performance?.realized_pnl ?? 0
  const unrealizedPnl = performance?.unrealized_pnl ?? 0
  const winRate = performance?.win_rate_pct ?? 0
  const totalTrades = performance?.total_trades_count ?? 0

  const formatMoney = (val: number) => {
    const formatted = Math.abs(val).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
    const sign = val >= 0 ? '+$' : '-$'
    return `${sign}${formatted}`
  }

  // Positive → gain (olive), negative → loss (oxblood), flat → ink (espresso).
  const toneFor = (val: number): 'gain' | 'loss' | 'ink' => {
    if (val > 0) return 'gain'
    if (val < 0) return 'loss'
    return 'ink'
  }

  return (
    <CertificateFrame variant="paper" watermark padding={26} className="perf-block">
      <div className="pnl-summary">
        <Denomination
          className="pnl-denom"
          label="Total P&L"
          icon={<TrendingUp size={16} />}
          tone={toneFor(totalPnl)}
          value={loading ? '…' : formatMoney(totalPnl)}
        />
        <Denomination
          className="pnl-denom"
          label="Realized P&L"
          icon={<DollarSign size={16} />}
          tone={toneFor(realizedPnl)}
          value={loading ? '…' : formatMoney(realizedPnl)}
        />
        <Denomination
          className="pnl-denom"
          label="Unrealized P&L"
          icon={<Activity size={16} />}
          tone={toneFor(unrealizedPnl)}
          value={loading ? '…' : formatMoney(unrealizedPnl)}
        />
        <Denomination
          className="pnl-denom"
          label="Win Rate"
          icon={<Percent size={16} />}
          tone="copper"
          value={loading ? '…' : `${winRate.toFixed(0)}%`}
          sub={`${totalTrades} trades`}
        />
      </div>
      <SecurityStrip className="pnl-statement-strip" text="ALPACA CAPITAL — STATEMENT OF PROFIT & LOSS — CERTIFIED —" />
    </CertificateFrame>
  )
}

export default PnLSummary

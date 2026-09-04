import type { FC } from 'react'
import { useReducedMotion } from 'framer-motion'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { PerformanceHistoryPoint } from '../../types'

interface PnLChartProps {
  history: PerformanceHistoryPoint[]
  loading?: boolean
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const pnl = payload[0].value
    const isPositive = pnl >= 0
    return (
      <div className="pnl-tooltip">
        <p className="pnl-tooltip__label">{label}</p>
        <p className={`pnl-tooltip__value ${isPositive ? 'is-gain' : 'is-loss'}`}>
          {isPositive ? '+$' : '-$'}
          {Math.abs(pnl).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </div>
    )
  }
  return null
}

export const PnLChart: FC<PnLChartProps> = ({ history = [], loading = false }) => {
  const hasData = history && history.length > 0
  const reduce = useReducedMotion()

  return (
    <div className="eng-panel perf-block">
      <div className="eng-panel__head">
        <div>
          <div className="eng-panel__title">Cumulative P&L Over Time</div>
          <div className="eng-panel__sub">Net options income and strategy returns trajectory.</div>
        </div>
      </div>

      <div className="eng-panel__body">
        {loading ? (
          <div className="pnl-state">Loading performance chart…</div>
        ) : !hasData ? (
          <div className="pnl-state">No performance data yet.</div>
        ) : (
          <div className="pnl-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid stroke="rgba(54, 33, 26, 0.10)" strokeDasharray="2 4" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="var(--hairline-strong)"
                  tick={{ fill: '#7A6A5D', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                  axisLine={{ stroke: 'rgba(54, 33, 26, 0.26)' }}
                  tickLine={false}
                />
                <YAxis
                  stroke="var(--hairline-strong)"
                  tick={{ fill: '#7A6A5D', fontSize: 11, fontFamily: 'var(--font-mono)' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `$${val}`}
                  domain={['auto', 'auto']}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(181, 101, 29, 0.35)', strokeWidth: 1 }} />
                <Line
                  type="monotone"
                  dataKey="cumulative_pnl"
                  stroke="#B5651D"
                  strokeWidth={2.5}
                  isAnimationActive={!reduce}
                  dot={{ r: 3.5, fill: '#B5651D', stroke: '#FFFDF9', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#B5651D', stroke: '#FBF3E7', strokeWidth: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}

export default PnLChart

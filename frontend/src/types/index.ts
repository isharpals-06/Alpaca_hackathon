export interface Opportunity {
  id: string
  symbol: string
  underlying_price: number
  implied_volatility: number
  iv_percentile: number
  liquidity_score: number
  scanned_at: string
}

export interface AgentOutput {
  agent_name: string
  stance: string
  confidence: number
  thesis: string
  key_metrics?: Record<string, any>
  timestamp: string
}

export interface Debate {
  id: string
  opportunity_id: string
  agent_outputs: AgentOutput[]
  cross_examination: Array<{ speaker: string; message: string }>
  summary: string
  created_at: string
}

export interface Decision {
  id: string
  opportunity_id: string
  symbol?: string
  action: 'TRADE' | 'NO_TRADE' | 'HOLD' | 'CLOSE' | 'ROLL' | 'EXECUTED' | 'RISK_VETO' | 'RISK VETO' | string
  rationale: string
  confidence_score: number
  recommended_strategy?: 'COVERED_CALL' | 'CASH_SECURED_PUT' | string
  order_spec?: string
  premium?: number
  status?: string
  created_at: string
}

export interface Position {
  id: string
  symbol: string
  strategy: string
  entry_price: number
  current_price: number
  unrealized_pnl: number
  realized_pnl: number
  days_to_expiration: number
  recommendation: string
  opened_at: string
}

export interface PerformanceHistoryPoint {
  date: string
  cumulative_pnl: number
  daily_pnl?: number
}

export interface PerformanceBreakdownItem {
  symbol: string
  entry_date: string
  exit_date?: string
  strategy: string
  realized_pnl: number
  unrealized_pnl?: number
  status: string
}

export interface PerformanceData {
  total_pnl: number
  realized_pnl: number
  unrealized_pnl: number
  win_rate_pct: number
  total_trades_count: number
  history: PerformanceHistoryPoint[]
  breakdown: PerformanceBreakdownItem[]
}

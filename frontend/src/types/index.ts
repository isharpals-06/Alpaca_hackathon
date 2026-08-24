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
  action: 'TRADE' | 'NO_TRADE' | 'HOLD' | 'CLOSE' | 'ROLL'
  rationale: string
  confidence_score: number
  recommended_strategy?: 'COVERED_CALL' | 'CASH_SECURED_PUT'
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

import { useEffect, useState } from 'react'
import {
  Activity,
  BarChart3,
  Brain,
  Briefcase,
  CheckCircle2,
  CircleDollarSign,
  Play,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  Users,
  XCircle,
} from 'lucide-react'
import './styles/dashboard.css'

type Status = 'Connecting...' | 'healthy' | 'Backend Offline'

interface Opportunity {
  id: string
  symbol: string
  underlying_price: number
  historical_volatility?: number
  implied_volatility: number
  iv_percentile: number
  liquidity_score: number
  sector?: string
  scanned_at: string
  candidate_contracts?: Array<{
    symbol: string
    option_type: string
    strike_price: number
    expiration_date: string
    days_to_expiration: number
    bid: number
    ask: number
    mid_price: number
    open_interest: number
    volume: number
    implied_volatility: number
    delta: number
    liquidity_score: number
  }>
}

interface Portfolio {
  cash?: number
  buying_power?: number
  portfolio_value?: number
  unrealized_pnl?: number
  realized_pnl?: number
  open_positions_count?: number
}

interface Position {
  id: string
  symbol: string
  underlying_symbol?: string
  strategy: string
  entry_premium?: number
  entry_price?: number
  current_premium?: number
  current_price?: number
  unrealized_pnl?: number
  realized_pnl?: number
  days_to_expiration?: number
  recommendation?: string
  recommendation_reason?: string
  opened_at?: string
}

interface AgentOutput {
  agent_name: string
  stance: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  confidence: number
  thesis: string
  claims?: string[]
  risks?: string[]
  recommendation?: string
}

interface ChallengeItem {
  target_agent: string
  question: string
  critical_point: string
}

interface ResponseItem {
  from_agent: string
  rebuttal: string
  adjusted_confidence?: number
}

interface Debate {
  id: string
  symbol: string
  phase1_agents: Record<string, AgentOutput>
  phase2_challenges?: ChallengeItem[]
  phase2_responses?: ResponseItem[]
  phase3_synthesis?: Record<string, any>
  created_at: string
}

interface Decision {
  id: string
  opportunity_id?: string
  symbol?: string
  action: 'TRADE' | 'NO_TRADE' | 'HOLD' | 'CLOSE' | 'ROLL'
  rationale: string
  confidence_score: number
  recommended_strategy?: string
  created_at?: string
}

interface RiskCheckItem {
  check_name: string
  passed: boolean
  details: string
}

interface RiskAssessment {
  approved: boolean
  checks_run: string[]
  checks_passed: string[]
  checks_failed: string[]
  veto_reason?: string
  portfolio_exposure_pct: number
  max_loss_potential: number
  detailed_checks: RiskCheckItem[]
}

interface PerformanceMetrics {
  total_realized_pnl: number
  total_unrealized_pnl: number
  win_rate_pct: number
  total_trades_count: number
  winning_trades_count: number
  average_premium_captured_pct: number
}

function App() {
  const [status, setStatus] = useState<Status>('Connecting...')
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loadingOpportunities, setLoadingOpportunities] = useState(true)
  const [opportunityError, setOpportunityError] = useState('')
  const [positions, setPositions] = useState<Position[]>([])
  const [loadingPositions, setLoadingPositions] = useState(true)
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null)

  // Live Cycle & Debate State
  const [activeDebate, setActiveDebate] = useState<Debate | null>(null)
  const [activeRiskAssessment, setActiveRiskAssessment] = useState<RiskAssessment | null>(null)
  const [activeOrder, setActiveOrder] = useState<any | null>(null)
  const [scanning, setScanning] = useState(false)
  const [runningCycle, setRunningCycle] = useState(false)
  const [cycleStatusMessage, setCycleStatusMessage] = useState('')

  // 1. Health
  const checkHealth = () => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error('Offline')
        return res.json()
      })
      .then((data) => setStatus(data.status || 'healthy'))
      .catch(() => setStatus('Backend Offline'))
  }

  // 2. Portfolio
  const loadPortfolio = () => {
    fetch('/api/portfolio')
      .then((res) => res.ok ? res.json() : null)
      .then((data) => { if (data) setPortfolio(data) })
      .catch((e) => console.error('Portfolio error:', e))
  }

  // 3. Opportunities
  const loadOpportunities = async () => {
    setLoadingOpportunities(true)
    setOpportunityError('')
    try {
      const res = await fetch('/api/opportunities')
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      setOpportunities(Array.isArray(data) ? data : [])
    } catch {
      setOpportunityError('Unable to load opportunities')
    } finally {
      setLoadingOpportunities(false)
    }
  }

  // 4. Positions
  const loadPositions = async () => {
    try {
      const res = await fetch('/api/positions')
      if (res.ok) {
        const data = await res.json()
        setPositions(Array.isArray(data) ? data : [])
      }
    } catch (e) {
      console.error('Positions error:', e)
    } finally {
      setLoadingPositions(false)
    }
  }

  // 5. Decisions
  const loadDecisions = async () => {
    try {
      const res = await fetch('/api/decisions')
      if (res.ok) {
        const data = await res.json()
        setDecisions(Array.isArray(data) ? data : [])
      }
    } catch (e) {
      console.error('Decisions error:', e)
    }
  }

  // 6. Performance
  const loadPerformance = async () => {
    try {
      const res = await fetch('/api/performance')
      if (res.ok) {
        const data = await res.json()
        setPerformance(data)
      }
    } catch (e) {
      console.error('Performance fetch error:', e)
    }
  }

  // Initial Load
  useEffect(() => {
    checkHealth()
    loadPortfolio()
    loadOpportunities()
    loadPositions()
    loadDecisions()
    loadPerformance()
  }, [])

  // Scan Universe
  const handleRunScan = async () => {
    setScanning(true)
    setOpportunityError('')
    try {
      const res = await fetch('/api/opportunities/scan', { method: 'POST' })
      if (!res.ok) throw new Error('Scan failed')
      await res.json()
      await loadOpportunities()
    } catch {
      setOpportunityError('Market scan encountered an issue')
    } finally {
      setScanning(false)
    }
  }

  // Trigger End-to-End Pipeline Cycle
  const handleRunCycle = async (symbol: string = 'SPY', simulateVeto: boolean = false) => {
    setRunningCycle(true)
    setCycleStatusMessage(`Running Full AI Cycle for ${symbol}...`)
    try {
      const url = `/api/pipeline/run-cycle?symbol=${symbol}&simulate_risk_veto=${simulateVeto}`
      const res = await fetch(url, { method: 'POST' })
      if (!res.ok) throw new Error('Cycle failed')
      const data = await res.json()

      setActiveDebate(data.debate || null)
      setActiveRiskAssessment(data.risk_assessment || null)
      setActiveOrder(data.order || null)
      setCycleStatusMessage(
        `Cycle Finished: ${data.symbol} -> Decision: ${data.action_taken} ${
          data.risk_assessment ? (data.risk_assessment.approved ? '(Risk Gate: APPROVED)' : '(Risk Gate: VETOED)') : ''
        }`
      )

      await loadOpportunities()
      await loadDecisions()
      await loadPositions()
      await loadPerformance()
      loadPortfolio()
    } catch {
      setCycleStatusMessage('Cycle execution error')
    } finally {
      setRunningCycle(false)
    }
  }

  // Tick Position Monitor
  const handleTickPositions = async () => {
    try {
      await fetch('/api/positions/tick-all', { method: 'POST' })
      await loadPositions()
      await loadPerformance()
      loadPortfolio()
    } catch (e) {
      console.error('Tick error:', e)
    }
  }

  // Close Position
  const handleClosePosition = async (id: string) => {
    try {
      await fetch(`/api/positions/${id}/close`, { method: 'POST' })
      await loadPositions()
      await loadPerformance()
      loadPortfolio()
    } catch (e) {
      console.error('Close error:', e)
    }
  }

  // Formatters
  const formatMoney = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(Number(val))) return '$0.00'
    return `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatPercent = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(Number(val))) return '0%'
    return `${(Number(val) * 100).toFixed(0)}%`
  }

  const totalPortfolioPnl = (portfolio?.unrealized_pnl ?? 0) + (portfolio?.realized_pnl ?? 0)
  const latestDecision = decisions.length > 0 ? decisions[0] : null

  return (
    <div className="app">
      {/* TOP HEADER WITH DEMO CONTROLS */}
      <header className="topbar">
        <div>
          <div className="brand">ALPACA AI</div>
          <div className="subtitle">Options Income Overlay & Autonomous Trading Council</div>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            className="primary-btn"
            style={{ padding: '6px 12px', fontSize: '12px', display: 'flex', gap: '6px', alignItems: 'center' }}
            onClick={() => handleRunCycle('SPY', false)}
            disabled={runningCycle}
          >
            <Play size={13} />
            Run Auto Cycle (SPY)
          </button>

          <button
            className="outline-btn"
            style={{ padding: '6px 12px', fontSize: '12px', borderColor: '#ef4444', color: '#ef4444', display: 'flex', gap: '6px', alignItems: 'center' }}
            onClick={() => handleRunCycle('TSLA', true)}
            disabled={runningCycle}
          >
            <ShieldAlert size={13} />
            Simulate Risk Veto
          </button>

          <button
            className="outline-btn"
            style={{ padding: '6px 12px', fontSize: '12px', display: 'flex', gap: '6px', alignItems: 'center' }}
            onClick={handleTickPositions}
          >
            <RefreshCw size={13} />
            Tick Monitor
          </button>

          <div className="status-pill">
            <span className={`status-dot ${status === 'healthy' ? 'online' : 'offline'}`} />
            {status}
          </div>
        </div>
      </header>

      <main className="dashboard">
        {/* HERO SECTION */}
        <section className="hero">
          <div>
            <p className="eyebrow">AUTONOMOUS OPTIONS TRADING ENGINE</p>
            <h1>AI Council Debate & Execution Platform</h1>
            <p className="hero-text">
              Real-time multi-agent options income overlay governing Cash-Secured Puts & Covered Calls with 5-stage deterministic risk gates and live Alpaca paper trading.
            </p>
            {cycleStatusMessage && (
              <div style={{ marginTop: '12px', padding: '8px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: '#10b981', fontWeight: 600, fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={16} />
                {cycleStatusMessage}
              </div>
            )}
          </div>

          <div className="hero-icon">
            <Brain size={44} />
          </div>
        </section>

        {/* PORTFOLIO STATS GRID */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon"><CircleDollarSign size={20} /></div>
            <div>
              <span>Cash Available</span>
              <strong>{portfolio ? formatMoney(portfolio.cash) : 'Loading...'}</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><Briefcase size={20} /></div>
            <div>
              <span>Portfolio Value</span>
              <strong>{portfolio ? formatMoney(portfolio.portfolio_value) : 'Loading...'}</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><TrendingUp size={20} /></div>
            <div>
              <span>Total P&L</span>
              <strong className={totalPortfolioPnl >= 0 ? 'positive' : ''}>
                {portfolio ? formatMoney(totalPortfolioPnl) : 'Loading...'}
              </strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><Activity size={20} /></div>
            <div>
              <span>Win Rate & Trades</span>
              <strong>{performance ? `${performance.win_rate_pct}% (${performance.total_trades_count} trades)` : '100%'}</strong>
            </div>
          </div>
        </section>

        {/* AI COUNCIL DEBATE ARENA */}
        <section className="panel">
          <div className="section-heading">
            <div>
              <p className="section-label">AI DECISION ENGINE</p>
              <h2>AI Council Debate Arena</h2>
            </div>
            <span className="live-badge">
              <Users size={15} />
              {activeDebate ? `ACTIVE DEBATE: ${activeDebate.symbol}` : 'READY'}
            </span>
          </div>

          {/* Council Agent Cards */}
          <div className="agents-grid">
            {activeDebate && activeDebate.phase1_agents ? (
              Object.entries(activeDebate.phase1_agents).map(([role, out]) => (
                <div className="agent-card" key={role}>
                  <div className="agent-header">
                    <span className="agent-name">
                      {role === 'Quant' && <BarChart3 size={18} />}
                      {role === 'Volatility' && <Activity size={18} />}
                      {role === 'Bull' && <TrendingUp size={18} />}
                      {role === 'Bear' && <ShieldCheck size={18} />}
                      {role === 'Risk Officer' && <ShieldAlert size={18} />}
                      {role.toUpperCase()}
                    </span>
                    <span className="confidence">{(out.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <p><strong>Stance:</strong> <span className={out.stance === 'BULLISH' ? 'positive' : ''}>{out.stance}</span></p>
                  <p style={{ fontSize: '13px', marginTop: '4px' }}>{out.thesis}</p>
                  <div className="agent-bar">
                    <div className="agent-progress" style={{ width: `${out.confidence * 100}%` }} />
                  </div>
                </div>
              ))
            ) : (
              ['QUANT', 'VOLATILITY', 'BULL', 'BEAR', 'RISK OFFICER'].map((name) => (
                <div className="agent-card" key={name}>
                  <div className="agent-header">
                    <span className="agent-name">
                      {name === 'QUANT' && <BarChart3 size={18} />}
                      {name === 'VOLATILITY' && <Activity size={18} />}
                      {name === 'BULL' && <TrendingUp size={18} />}
                      {name === 'BEAR' && <ShieldCheck size={18} />}
                      {name === 'RISK OFFICER' && <ShieldAlert size={18} />}
                      {name}
                    </span>
                    <span className="confidence">READY</span>
                  </div>
                  <p style={{ fontSize: '13px' }}>Standby for debate trigger. Click &quot;Initiate Council Debate&quot; or &quot;Run Auto Cycle&quot;.</p>
                  <div className="agent-bar">
                    <div className="agent-progress" style={{ width: '100%' }} />
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Phase 2: Cross Examination Showcase */}
          {activeDebate && activeDebate.phase2_challenges && activeDebate.phase2_challenges.length > 0 && (
            <div style={{ marginTop: '18px', padding: '14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <span className="decision-label">PHASE 2: CROSS-EXAMINATION ROUND</span>
              <div style={{ marginTop: '8px', display: 'grid', gap: '8px' }}>
                {activeDebate.phase2_challenges.map((c, i) => (
                  <div key={i} style={{ fontSize: '13px', borderLeft: '3px solid #f59e0b', paddingLeft: '10px' }}>
                    <strong style={{ color: '#f59e0b' }}>Bear Challenge ➔ {c.target_agent}:</strong> {c.question}
                  </div>
                ))}
                {activeDebate.phase2_responses?.map((r, i) => (
                  <div key={i} style={{ fontSize: '13px', borderLeft: '3px solid #10b981', paddingLeft: '10px' }}>
                    <strong style={{ color: '#10b981' }}>{r.from_agent} Rebuttal:</strong> {r.rebuttal}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Portfolio Manager Decision Box */}
          {latestDecision && (
            <div className="decision-card" style={{ marginTop: '18px' }}>
              <div>
                <span className="decision-label">PORTFOLIO MANAGER SYNTHESIS</span>
                <h3 style={{ color: latestDecision.action === 'TRADE' ? '#10b981' : '#f59e0b' }}>
                  {latestDecision.action}: {latestDecision.recommended_strategy || 'CAPITAL PRESERVATION'}
                </h3>
                <p>{latestDecision.rationale}</p>
              </div>
              <div className="decision-meta">
                <span>Council Confidence</span>
                <strong>{(Number(latestDecision.confidence_score ?? 0) * 100).toFixed(0)}%</strong>
                <small>{latestDecision.symbol || 'SPY'}</small>
              </div>
            </div>
          )}
        </section>

        {/* DETERMINISTIC RISK GATE AUDIT */}
        {activeRiskAssessment && (
          <section className="panel" style={{ border: activeRiskAssessment.approved ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)' }}>
            <div className="section-heading">
              <div>
                <p className="section-label">SAFETY GATEKEEPER</p>
                <h2>Deterministic Risk Gate (5 Sequential Code Checks)</h2>
              </div>
              <span className={`status-pill ${activeRiskAssessment.approved ? 'online' : 'offline'}`}>
                {activeRiskAssessment.approved ? 'RISK GATE: APPROVED' : 'RISK GATE: VETOED'}
              </span>
            </div>

            {activeRiskAssessment.veto_reason && (
              <div style={{ marginBottom: '14px', padding: '10px 14px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', color: '#ef4444', fontWeight: 600, fontSize: '13px' }}>
                <ShieldAlert size={16} style={{ display: 'inline', marginRight: '6px' }} />
                VETO REASON: {activeRiskAssessment.veto_reason}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
              {activeRiskAssessment.detailed_checks.map((chk, i) => (
                <div key={i} style={{ padding: '10px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, fontSize: '13px' }}>
                    {chk.passed ? <CheckCircle2 size={16} color="#10b981" /> : <XCircle size={16} color="#ef4444" />}
                    <span style={{ color: chk.passed ? '#10b981' : '#ef4444' }}>{chk.check_name}</span>
                  </div>
                  <p style={{ fontSize: '11px', marginTop: '4px', color: 'rgba(255, 255, 255, 0.7)' }}>{chk.details}</p>
                </div>
              ))}
            </div>

            {activeOrder && (
              <div style={{ marginTop: '14px', padding: '10px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '6px', fontSize: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span><strong>Alpaca Paper Order Submitted:</strong> {activeOrder.contract_symbol} (Qty: {activeOrder.qty}, Limit: ${activeOrder.limit_price})</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>STATUS: {activeOrder.status}</span>
              </div>
            )}
          </section>
        )}

        {/* OPPORTUNITY SCANNER TABLE */}
        <section className="panel">
          <div className="section-heading">
            <div>
              <p className="section-label">MARKET SCANNER</p>
              <h2>Live Opportunities</h2>
            </div>

            <button className="primary-btn" onClick={handleRunScan} disabled={scanning}>
              {scanning ? 'Scanning...' : 'Scan Universe'}
            </button>
          </div>

          {loadingOpportunities && <div className="empty-state">Loading opportunities...</div>}
          {opportunityError && <div className="error-state">{opportunityError}</div>}

          {!loadingOpportunities && !opportunityError && opportunities.length > 0 && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Price</th>
                    <th>Implied Vol.</th>
                    <th>IV Percentile</th>
                    <th>Liquidity</th>
                    <th>Sector</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {opportunities.map((item) => (
                    <tr key={item.id}>
                      <td className="symbol">{item.symbol}</td>
                      <td>{formatMoney(item.underlying_price)}</td>
                      <td>{formatPercent(item.implied_volatility)}</td>
                      <td>{Number(item.iv_percentile ?? 0).toFixed(0)}%</td>
                      <td><span className="score">{(Number(item.liquidity_score ?? 0) * 100).toFixed(0)}</span></td>
                      <td>{item.sector || '—'}</td>
                      <td>
                        <button
                          className="outline-btn"
                          style={{ padding: '4px 10px', fontSize: '12px' }}
                          onClick={() => handleRunCycle(item.symbol, false)}
                          disabled={runningCycle}
                        >
                          Initiate Council Debate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* POSITIONS & MONITORING */}
        <section className="panel">
          <div className="section-heading">
            <div>
              <p className="section-label">ACTIVE PORTFOLIO & MONITORING</p>
              <h2>Live Positions</h2>
            </div>
            <button className="outline-btn" onClick={handleTickPositions} style={{ padding: '4px 10px', fontSize: '12px' }}>
              Tick Monitor
            </button>
          </div>

          {loadingPositions && <div className="empty-state">Loading positions...</div>}
          {!loadingPositions && positions.length === 0 && (
            <div className="empty-state">No open positions. Run an AI cycle to initiate and execute options trades.</div>
          )}
          {!loadingPositions && positions.length > 0 && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Strategy</th>
                    <th>Entry Premium</th>
                    <th>Current Premium</th>
                    <th>P&L</th>
                    <th>DTE</th>
                    <th>Monitoring Recommendation</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((pos) => {
                    const entry = pos.entry_premium ?? pos.entry_price ?? 0
                    const curr = pos.current_premium ?? pos.current_price ?? 0
                    const totalPnl = (pos.unrealized_pnl ?? 0) + (pos.realized_pnl ?? 0)
                    return (
                      <tr key={pos.id}>
                        <td className="symbol">{pos.symbol}</td>
                        <td>{pos.strategy}</td>
                        <td>{formatMoney(entry)}</td>
                        <td>{formatMoney(curr)}</td>
                        <td className={totalPnl >= 0 ? 'positive' : ''}>{formatMoney(totalPnl)}</td>
                        <td>{pos.days_to_expiration ?? '—'}</td>
                        <td>
                          <span className={`status-pill ${pos.recommendation === 'CLOSE' ? 'online' : ''}`}>
                            {pos.recommendation || 'HOLD'}
                          </span>
                          <span style={{ fontSize: '11px', display: 'block', color: 'rgba(255, 255, 255, 0.6)', marginTop: '2px' }}>
                            {pos.recommendation_reason}
                          </span>
                        </td>
                        <td>
                          <button
                            className="outline-btn"
                            style={{ padding: '4px 8px', fontSize: '11px', color: '#ef4444', borderColor: '#ef4444' }}
                            onClick={() => handleClosePosition(pos.id)}
                          >
                            Close
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App

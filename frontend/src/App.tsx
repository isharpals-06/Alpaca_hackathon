import { useEffect, useState } from 'react'
import {
  Activity,
  BarChart3,
  Brain,
  Briefcase,
  CircleDollarSign,
  ShieldCheck,
  TrendingUp,
  Users,
  X,
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
  cash: number
  buying_power: number
  portfolio_value: number
  unrealized_pnl: number
  realized_pnl: number
  open_positions_count: number
}

interface Position {
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

interface Decision {
  id: string
  opportunity_id: string
  action: 'TRADE' | 'NO_TRADE' | 'HOLD' | 'CLOSE' | 'ROLL'
  rationale: string
  confidence_score: number
  recommended_strategy?: 'COVERED_CALL' | 'CASH_SECURED_PUT'
  created_at: string
}

interface Agent {
  name: string
  icon: React.ReactNode
  confidence: string
  text: string
}

function App() {
  const [status, setStatus] = useState<Status>('Connecting...')

  const [portfolio, setPortfolio] =
    useState<Portfolio | null>(null)

  const [opportunities, setOpportunities] =
    useState<Opportunity[]>([])

  const [loadingOpportunities, setLoadingOpportunities] =
    useState(true)

  const [opportunityError, setOpportunityError] =
    useState('')

  const [selectedOpportunity, setSelectedOpportunity] =
    useState<Opportunity | null>(null)

  const [loadingDetails, setLoadingDetails] =
    useState(false)

  const [detailsError, setDetailsError] =
    useState('')

  const [positions, setPositions] =
    useState<Position[]>([])

  const [loadingPositions, setLoadingPositions] =
    useState(true)

  const [decisions, setDecisions] =
    useState<Decision[]>([])

  const [loadingDecisions, setLoadingDecisions] =
    useState(true)

  const [scanning, setScanning] =
    useState(false)

  // =========================
  // BACKEND HEALTH
  // =========================

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Backend error')
        }

        return res.json()
      })
      .then((data) => {
        setStatus(data.status || 'healthy')
      })
      .catch(() => {
        setStatus('Backend Offline')
      })
  }, [])

  // =========================
  // PORTFOLIO
  // =========================

  useEffect(() => {
    fetch('/api/portfolio')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to fetch portfolio')
        }

        return res.json()
      })
      .then((data) => {
        setPortfolio(data)
      })
      .catch((error) => {
        console.error(
          'Portfolio API error:',
          error
        )
      })
  }, [])

  // =========================
  // LOAD OPPORTUNITIES
  // =========================

  const loadOpportunities = async () => {
    setLoadingOpportunities(true)
    setOpportunityError('')

    try {
      const res = await fetch('/api/opportunities')

      if (!res.ok) {
        throw new Error(
          'Failed to fetch opportunities'
        )
      }

      const data = await res.json()

      setOpportunities(
        Array.isArray(data) ? data : []
      )
    } catch (error) {
      console.error(
        'Opportunities API error:',
        error
      )

      setOpportunityError(
        'Unable to load opportunities'
      )
    } finally {
      setLoadingOpportunities(false)
    }
  }

  useEffect(() => {
    loadOpportunities()
  }, [])

  // =========================
  // RUN SCAN
  // =========================

  const handleRunScan = async () => {
    setScanning(true)
    setOpportunityError('')

    try {
      const res = await fetch(
        '/api/opportunities/scan',
        {
          method: 'POST',
        }
      )

      if (!res.ok) {
        throw new Error('Scan failed')
      }

      await res.json()

      await loadOpportunities()
    } catch (error) {
      console.error(
        'Scan error:',
        error
      )

      setOpportunityError(
        'Unable to run market scan'
      )
    } finally {
      setScanning(false)
    }
  }

  // =========================
  // POSITIONS
  // =========================

  useEffect(() => {
    fetch('/api/positions')
      .then((res) => {
        if (!res.ok) {
          throw new Error(
            'Failed to fetch positions'
          )
        }

        return res.json()
      })
      .then((data) => {
        setPositions(
          Array.isArray(data) ? data : []
        )
      })
      .catch((error) => {
        console.error(
          'Positions API error:',
          error
        )

        setPositions([])
      })
      .finally(() => {
        setLoadingPositions(false)
      })
  }, [])

  // =========================
  // DECISIONS
  // =========================

  useEffect(() => {
    fetch('/api/decisions')
      .then((res) => {
        if (!res.ok) {
          throw new Error(
            'Failed to fetch decisions'
          )
        }

        return res.json()
      })
      .then((data) => {
        setDecisions(
          Array.isArray(data) ? data : []
        )
      })
      .catch((error) => {
        console.error(
          'Decisions API error:',
          error
        )

        setDecisions([])
      })
      .finally(() => {
        setLoadingDecisions(false)
      })
  }, [])

  // =========================
  // ANALYZE OPPORTUNITY
  // =========================

  const handleAnalyze = async (
    id: string
  ) => {
    setLoadingDetails(true)
    setDetailsError('')
    setSelectedOpportunity(null)

    try {
      const res = await fetch(
        `/api/opportunities/${id}`
      )

      if (!res.ok) {
        throw new Error(
          'Failed to fetch opportunity details'
        )
      }

      const data = await res.json()

      setSelectedOpportunity(data)
    } catch (error) {
      console.error(
        'Opportunity details error:',
        error
      )

      setDetailsError(
        'Unable to load opportunity details'
      )
    } finally {
      setLoadingDetails(false)
    }
  }

  // =========================
  // AI COUNCIL
  // =========================

  const agents: Agent[] = [
    {
      name: 'QUANT',
      icon: <BarChart3 size={18} />,
      confidence: '78%',
      text:
        'Volatility and liquidity conditions support the opportunity.',
    },
    {
      name: 'BULL',
      icon: <TrendingUp size={18} />,
      confidence: '82%',
      text:
        'Premium collection looks attractive under current market conditions.',
    },
    {
      name: 'BEAR',
      icon: <ShieldCheck size={18} />,
      confidence: '64%',
      text:
        'Downside risk remains if volatility expands unexpectedly.',
    },
    {
      name: 'RISK OFFICER',
      icon: <Activity size={18} />,
      confidence: '76%',
      text:
        'Risk exposure remains within the portfolio limits.',
    },
  ]

  // =========================
  // FORMATTING
  // =========================

  const formatMoney = (
    value: number
  ) => {
    return `$${value.toLocaleString(
      'en-US',
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    )}`
  }

  const formatPercent = (
    value: number
  ) => {
    return `${(
      value * 100
    ).toFixed(0)}%`
  }

  const formatDate = (
    value: string
  ) => {
    if (!value) return '—'

    const date = new Date(value)

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return value
    }

    return date.toLocaleString()
  }

  const latestDecision =
    decisions.length > 0
      ? decisions[0]
      : null

  // =========================
  // UI
  // =========================

  return (
    <div className="app">

      {/* TOP BAR */}

      <header className="topbar">

        <div>
          <div className="brand">
            ALPACA AI
          </div>

          <div className="subtitle">
            Trading Council & Execution
          </div>
        </div>

        <div className="status-pill">

          <span
            className={`status-dot ${
              status === 'healthy'
                ? 'online'
                : 'offline'
            }`}
          />

          Backend: {status}

        </div>

      </header>

      <main className="dashboard">

        {/* HERO */}

        <section className="hero">

          <div>

            <p className="eyebrow">
              AI-POWERED TRADING PLATFORM
            </p>

            <h1>
              Trading Intelligence Dashboard
            </h1>

            <p className="hero-text">
              Monitor opportunities, AI council
              debates, risk decisions and portfolio
              performance from one place.
            </p>

          </div>

          <div className="hero-icon">
            <Brain size={42} />
          </div>

        </section>

        {/* PORTFOLIO */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-icon">
              <CircleDollarSign size={20} />
            </div>

            <div>

              <span>
                Cash
              </span>

              <strong>
                {portfolio
                  ? formatMoney(
                      portfolio.cash
                    )
                  : 'Loading...'}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              <Briefcase size={20} />
            </div>

            <div>

              <span>
                Portfolio Value
              </span>

              <strong>
                {portfolio
                  ? formatMoney(
                      portfolio.portfolio_value
                    )
                  : 'Loading...'}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              <TrendingUp size={20} />
            </div>

            <div>

              <span>
                Total P&L
              </span>

              <strong
                className={
                  portfolio &&
                  portfolio.unrealized_pnl +
                    portfolio.realized_pnl >=
                    0
                    ? 'positive'
                    : ''
                }
              >
                {portfolio
                  ? formatMoney(
                      portfolio.unrealized_pnl +
                        portfolio.realized_pnl
                    )
                  : 'Loading...'}
              </strong>

            </div>

          </div>

          <div className="stat-card">

            <div className="stat-icon">
              <Activity size={20} />
            </div>

            <div>

              <span>
                Active Positions
              </span>

              <strong>
                {portfolio
                  ? portfolio.open_positions_count
                  : 'Loading...'}
              </strong>

            </div>

          </div>

        </section>

        {/* OPPORTUNITIES */}

        <section className="panel">

          <div className="section-heading">

            <div>

              <p className="section-label">
                MARKET SCANNER
              </p>

              <h2>
                Opportunities
              </h2>

            </div>

            <button
              className="primary-btn"
              onClick={handleRunScan}
              disabled={scanning}
            >
              {scanning
                ? 'Scanning...'
                : 'Run Scan'}
            </button>

          </div>

          {loadingOpportunities && (
            <div className="empty-state">
              Loading opportunities...
            </div>
          )}

          {opportunityError && (
            <div className="error-state">
              {opportunityError}
            </div>
          )}

          {!loadingOpportunities &&
            !opportunityError &&
            opportunities.length === 0 && (
              <div className="empty-state">
                No opportunities available.
              </div>
            )}

          {!loadingOpportunities &&
            !opportunityError &&
            opportunities.length > 0 && (

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
                      <th>Scanned At</th>
                      <th>Action</th>
                    </tr>

                  </thead>

                  <tbody>

                    {opportunities.map(
                      (item) => (

                        <tr
                          key={item.id}
                        >

                          <td className="symbol">
                            {item.symbol}
                          </td>

                          <td>
                            {formatMoney(
                              item.underlying_price
                            )}
                          </td>

                          <td>
                            {formatPercent(
                              item.implied_volatility
                            )}
                          </td>

                          <td>
                            {item.iv_percentile.toFixed(
                              0
                            )}
                            %
                          </td>

                          <td>

                            <span className="score">
                              {(
                                item.liquidity_score *
                                100
                              ).toFixed(0)}
                            </span>

                          </td>

                          <td>
                            {item.sector ||
                              '—'}
                          </td>

                          <td>
                            {formatDate(
                              item.scanned_at
                            )}
                          </td>

                          <td>

                            <button
                              className="outline-btn"
                              onClick={() =>
                                handleAnalyze(
                                  item.id
                                )
                              }
                            >
                              Analyze
                            </button>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          {/* OPPORTUNITY DETAILS */}

          {loadingDetails && (
            <div className="empty-state">
              Loading opportunity details...
            </div>
          )}

          {detailsError && (
            <div className="error-state">
              {detailsError}
            </div>
          )}

          {selectedOpportunity &&
            !loadingDetails && (

              <div className="decision-card">

                <div>

                  <span className="decision-label">
                    OPPORTUNITY ANALYSIS
                  </span>

                  <h3>
                    {selectedOpportunity.symbol}
                  </h3>

                  <p>
                    Detailed market opportunity
                    data loaded from the backend.
                  </p>

                  <div className="detail-grid">

                    <div>
                      <span>
                        Underlying Price
                      </span>

                      <strong>
                        {formatMoney(
                          selectedOpportunity
                            .underlying_price
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Implied Volatility
                      </span>

                      <strong>
                        {formatPercent(
                          selectedOpportunity
                            .implied_volatility
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        IV Percentile
                      </span>

                      <strong>
                        {selectedOpportunity
                          .iv_percentile
                          .toFixed(0)}
                        %
                      </strong>
                    </div>

                    <div>
                      <span>
                        Liquidity
                      </span>

                      <strong>
                        {(
                          selectedOpportunity
                            .liquidity_score *
                          100
                        ).toFixed(0)}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Sector
                      </span>

                      <strong>
                        {selectedOpportunity.sector ||
                          '—'}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Scanned At
                      </span>

                      <strong>
                        {formatDate(
                          selectedOpportunity
                            .scanned_at
                        )}
                      </strong>
                    </div>

                  </div>

                </div>

                <button
                  className="close-btn"
                  onClick={() =>
                    setSelectedOpportunity(
                      null
                    )
                  }
                >
                  <X size={18} />
                </button>

              </div>

            )}

        </section>

        {/* AI COUNCIL */}

        <section className="panel">

          <div className="section-heading">

            <div>

              <p className="section-label">
                AI DECISION ENGINE
              </p>

              <h2>
                AI Council
              </h2>

            </div>

            <span className="live-badge">
              <Users size={15} />
              LIVE DEBATE
            </span>

          </div>

          <div className="agents-grid">

            {agents.map(
              (agent) => (

                <div
                  className="agent-card"
                  key={agent.name}
                >

                  <div className="agent-header">

                    <span className="agent-name">
                      {agent.icon}
                      {agent.name}
                    </span>

                    <span className="confidence">
                      {agent.confidence}
                    </span>

                  </div>

                  <p>
                    {agent.text}
                  </p>

                  <div className="agent-bar">

                    <div
                      className="agent-progress"
                      style={{
                        width:
                          agent.confidence,
                      }}
                    />

                  </div>

                </div>

              )
            )}

          </div>

          {loadingDecisions && (
            <div className="empty-state">
              Loading AI decisions...
            </div>
          )}

          {!loadingDecisions &&
            latestDecision && (

              <div className="decision-card">

                <div>

                  <span className="decision-label">
                    PORTFOLIO MANAGER DECISION
                  </span>

                  <h3>
                    {latestDecision.action}
                  </h3>

                  <p>
                    {latestDecision.rationale}
                  </p>

                </div>

                <div className="decision-meta">

                  <span>
                    Confidence
                  </span>

                  <strong>
                    {(
                      latestDecision
                        .confidence_score *
                      100
                    ).toFixed(0)}
                    %
                  </strong>

                  <small>
                    {latestDecision
                      .recommended_strategy ||
                      'NO STRATEGY'}
                  </small>

                </div>

              </div>

            )}

          {!loadingDecisions &&
            decisions.length === 0 && (

              <div className="empty-state">
                No AI council decisions yet.
              </div>

            )}

        </section>

        {/* POSITIONS */}

        <section className="panel">

          <div className="section-heading">

            <div>

              <p className="section-label">
                LIVE PORTFOLIO
              </p>

              <h2>
                Positions
              </h2>

            </div>

          </div>

          {loadingPositions && (
            <div className="empty-state">
              Loading positions...
            </div>
          )}

          {!loadingPositions &&
            positions.length === 0 && (

              <div className="empty-state">
                No open positions.
              </div>

            )}

          {!loadingPositions &&
            positions.length > 0 && (

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Symbol</th>
                      <th>Strategy</th>
                      <th>Entry</th>
                      <th>Current</th>
                      <th>P&L</th>
                      <th>Days Left</th>
                      <th>Recommendation</th>
                      <th>Opened</th>
                    </tr>

                  </thead>

                  <tbody>

                    {positions.map(
                      (position) => {

                        const totalPnl =
                          position.unrealized_pnl +
                          position.realized_pnl

                        return (

                          <tr
                            key={
                              position.id
                            }
                          >

                            <td className="symbol">
                              {position.symbol}
                            </td>

                            <td>
                              {position.strategy}
                            </td>

                            <td>
                              {formatMoney(
                                position.entry_price
                              )}
                            </td>

                            <td>
                              {formatMoney(
                                position.current_price
                              )}
                            </td>

                            <td
                              className={
                                totalPnl >= 0
                                  ? 'positive'
                                  : ''
                              }
                            >
                              {formatMoney(
                                totalPnl
                              )}
                            </td>

                            <td>
                              {
                                position.days_to_expiration
                              }
                            </td>

                            <td>
                              {
                                position.recommendation
                              }
                            </td>

                            <td>
                              {formatDate(
                                position.opened_at
                              )}
                            </td>

                          </tr>

                        )
                      }
                    )}

                  </tbody>

                </table>

              </div>

            )}

        </section>

        {/* PERFORMANCE */}

        <section className="performance-grid">

          <div className="panel performance-card">

            <p className="section-label">
              PERFORMANCE
            </p>

            <h2>
              P&L Overview
            </h2>

            <div className="pnl-row">

              <span>
                Total P&L
              </span>

              <strong
                className={
                  portfolio &&
                  portfolio.unrealized_pnl +
                    portfolio.realized_pnl >=
                    0
                    ? 'positive'
                    : ''
                }
              >
                {portfolio
                  ? formatMoney(
                      portfolio.unrealized_pnl +
                        portfolio.realized_pnl
                    )
                  : 'Loading...'}
              </strong>

            </div>

            <div className="pnl-row">

              <span>
                Realized P&L
              </span>

              <strong
                className={
                  portfolio &&
                  portfolio.realized_pnl >= 0
                    ? 'positive'
                    : ''
                }
              >
                {portfolio
                  ? formatMoney(
                      portfolio.realized_pnl
                    )
                  : 'Loading...'}
              </strong>

            </div>

            <div className="pnl-row">

              <span>
                Unrealized P&L
              </span>

              <strong
                className={
                  portfolio &&
                  portfolio.unrealized_pnl >= 0
                    ? 'positive'
                    : ''
                }
              >
                {portfolio
                  ? formatMoney(
                      portfolio.unrealized_pnl
                    )
                  : 'Loading...'}
              </strong>

            </div>

          </div>

          {/* EXECUTION PIPELINE */}

          <div className="panel journey-card">

            <p className="section-label">
              EXECUTION PIPELINE
            </p>

            <h2>
              Decision Journey
            </h2>

            <div className="journey">

              <span>
                Opportunity
              </span>

              <span>→</span>

              <span>
                Debate
              </span>

              <span>→</span>

              <span>
                Decision
              </span>

              <span>→</span>

              <span>
                Risk Gate
              </span>

              <span>→</span>

              <span>
                Trade
              </span>

              <span>→</span>

              <span>
                Position
              </span>

            </div>

          </div>

        </section>

      </main>

    </div>
  )
}

export default App
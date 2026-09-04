import { useEffect, useState } from 'react'
import {
  Activity,
  BarChart3,
  Briefcase,
  CircleDollarSign,
  Gavel,
  MessagesSquare,
  Radar,
  Search,
  ShieldCheck,
  TrendingUp,
  Users,
  X,
  Zap,
} from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import AppShell from '../components/layout/AppShell'
import DecisionStamp from '../components/shared/DecisionStamp'
import {
  Reveal,
  Denomination,
  Seal,
  CertificateFrame,
  staggerContainer,
  staggerItem,
} from '../design'
import '../styles/dashboard.css'

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

const PIPELINE_STEPS = [
  { icon: <Search size={16} />, label: 'Opportunity' },
  { icon: <MessagesSquare size={16} />, label: 'Debate' },
  { icon: <Gavel size={16} />, label: 'Decision' },
  { icon: <ShieldCheck size={16} />, label: 'Risk Gate' },
  { icon: <Zap size={16} />, label: 'Trade' },
  { icon: <Briefcase size={16} />, label: 'Position' },
]

export default function DashboardPage() {
  const reduce = useReducedMotion()

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

  const totalPnl = portfolio
    ? portfolio.unrealized_pnl + portfolio.realized_pnl
    : 0

  const sessionDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  // =========================
  // UI
  // =========================

  return (
    <AppShell section="Live Desk">
      {/* MASTHEAD */}
      <Reveal>
        <section className="dk-masthead">
          <div className="dk-masthead-copy">
            <div className="dk-masthead-eyebrow">
              <span className="dk-live-dot" />
              Council standing by
            </div>
            <h1 className="dk-title">The Trading Desk</h1>
            <p className="dk-sub">
              Live opportunities, council deliberation, risk clearance and portfolio
              performance — issued and recorded from one certified desk.
            </p>
          </div>
          <div className="dk-masthead-seal">
            <Seal size={92} label="DESK" sub="ALPACA · COUNCIL" tone="copper" animate={!reduce} />
            <div className="dk-session">
              <span className="field-label">Session</span>
              <span className="num dk-session-date">{sessionDate}</span>
            </div>
          </div>
        </section>
      </Reveal>

      {/* PORTFOLIO — denomination strip */}
      <Reveal delay={0.05}>
        <motion.section
          className="dk-strip"
          variants={staggerContainer(0.08, 0.05)}
          initial={reduce ? undefined : 'hidden'}
          whileInView={reduce ? undefined : 'show'}
          viewport={{ once: true, amount: 0.4 }}
        >
          <motion.div className="dk-strip-cell" variants={staggerItem}>
            <Denomination
              label="Cash"
              icon={<CircleDollarSign size={15} />}
              value={portfolio ? formatMoney(portfolio.cash) : '—'}
              tone="ink"
            />
          </motion.div>
          <motion.div className="dk-strip-cell" variants={staggerItem}>
            <Denomination
              label="Portfolio Value"
              icon={<Briefcase size={15} />}
              value={portfolio ? formatMoney(portfolio.portfolio_value) : '—'}
              tone="ink"
            />
          </motion.div>
          <motion.div className="dk-strip-cell" variants={staggerItem}>
            <Denomination
              label="Total P&L"
              icon={<TrendingUp size={15} />}
              value={portfolio ? formatMoney(totalPnl) : '—'}
              tone={portfolio ? (totalPnl >= 0 ? 'gain' : 'loss') : 'neutral'}
            />
          </motion.div>
          <motion.div className="dk-strip-cell" variants={staggerItem}>
            <Denomination
              label="Active Positions"
              icon={<Activity size={15} />}
              value={portfolio ? portfolio.open_positions_count : '—'}
              tone="copper"
            />
          </motion.div>
        </motion.section>
      </Reveal>

      {/* OPPORTUNITIES */}
      <Reveal delay={0.05}>
        <section className="eng-panel dk-panel">
          <div className="eng-panel__head">
            <div>
              <div className="eng-panel__title">Opportunities</div>
              <div className="eng-panel__sub">Live Alpaca options scan for sellable edge</div>
            </div>
            <button
              className="btn btn--copper"
              onClick={handleRunScan}
              disabled={scanning}
            >
              <Radar size={15} className={scanning ? 'dk-spin' : ''} />
              {scanning ? 'Scanning…' : 'Run Scan'}
            </button>
          </div>

          <div className="eng-panel__body">
            {loadingOpportunities && (
              <div className="dk-empty">Loading opportunities…</div>
            )}

            {opportunityError && (
              <div className="dk-error">{opportunityError}</div>
            )}

            {!loadingOpportunities &&
              !opportunityError &&
              opportunities.length === 0 && (
                <div className="dk-empty">No opportunities available. Run a scan to source new edge.</div>
              )}

            {!loadingOpportunities &&
              !opportunityError &&
              opportunities.length > 0 && (
                <div className="dk-table-wrap">
                  <table className="dk-table">
                    <thead>
                      <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Implied Vol.</th>
                        <th>IV Pctl.</th>
                        <th>Liquidity</th>
                        <th>Sector</th>
                        <th>Scanned</th>
                        <th aria-label="Action" />
                      </tr>
                    </thead>
                    <tbody>
                      {opportunities.map((item) => (
                        <tr key={item.id}>
                          <td className="dk-symbol">{item.symbol}</td>
                          <td className="num">{formatMoney(item.underlying_price)}</td>
                          <td className="num">{formatPercent(item.implied_volatility)}</td>
                          <td className="num">{item.iv_percentile.toFixed(0)}%</td>
                          <td>
                            <span className="dk-score">
                              {(item.liquidity_score * 100).toFixed(0)}
                            </span>
                          </td>
                          <td className="dk-muted">{item.sector || '—'}</td>
                          <td className="num dk-muted dk-nowrap">{formatDate(item.scanned_at)}</td>
                          <td>
                            <button
                              className="btn btn--ghost btn--sm"
                              onClick={() => handleAnalyze(item.id)}
                            >
                              Analyze
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

            {/* OPPORTUNITY DETAILS */}
            {loadingDetails && (
              <div className="dk-empty" style={{ marginTop: 18 }}>Loading opportunity details…</div>
            )}

            {detailsError && (
              <div className="dk-error" style={{ marginTop: 18 }}>{detailsError}</div>
            )}

            <AnimatePresence>
              {selectedOpportunity && !loadingDetails && (
                <motion.div
                  key={selectedOpportunity.id}
                  initial={reduce ? false : { opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={reduce ? undefined : { opacity: 0, y: -8 }}
                  transition={{ duration: 0.32 }}
                  style={{ marginTop: 22 }}
                >
                  <CertificateFrame watermark padding={24}>
                    <div className="dk-detail-head">
                      <div>
                        <span className="field-label">Opportunity Analysis</span>
                        <h3 className="dk-detail-ticker">{selectedOpportunity.symbol}</h3>
                        <p className="dk-detail-note">
                          Detailed market opportunity data loaded from the desk.
                        </p>
                      </div>
                      <button
                        className="dk-close"
                        aria-label="Close analysis"
                        onClick={() => setSelectedOpportunity(null)}
                      >
                        <X size={16} />
                      </button>
                    </div>

                    <hr className="rule" style={{ margin: '18px 0' }} />

                    <div className="dk-detail-grid">
                      <Denomination
                        label="Underlying Price"
                        value={formatMoney(selectedOpportunity.underlying_price)}
                        tone="ink"
                        size={22}
                      />
                      <Denomination
                        label="Implied Volatility"
                        value={formatPercent(selectedOpportunity.implied_volatility)}
                        tone="ink"
                        size={22}
                      />
                      <Denomination
                        label="IV Percentile"
                        value={`${selectedOpportunity.iv_percentile.toFixed(0)}%`}
                        tone="ink"
                        size={22}
                      />
                      <Denomination
                        label="Liquidity"
                        value={(selectedOpportunity.liquidity_score * 100).toFixed(0)}
                        tone="copper"
                        size={22}
                      />
                      <Denomination
                        label="Sector"
                        value={selectedOpportunity.sector || '—'}
                        tone="neutral"
                        size={18}
                      />
                      <Denomination
                        label="Scanned At"
                        value={<span style={{ fontSize: 14 }}>{formatDate(selectedOpportunity.scanned_at)}</span>}
                        tone="neutral"
                        size={14}
                      />
                    </div>
                  </CertificateFrame>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>
      </Reveal>

      {/* AI COUNCIL */}
      <Reveal delay={0.05}>
        <section className="eng-panel dk-panel">
          <div className="eng-panel__head">
            <div>
              <div className="eng-panel__title">AI Council</div>
              <div className="eng-panel__sub">Five specialists deliberate every thesis</div>
            </div>
            <span className="dk-live-badge">
              <Users size={14} />
              Live Debate
            </span>
          </div>

          <div className="eng-panel__body">
            <motion.div
              className="dk-agents"
              variants={staggerContainer(0.08)}
              initial={reduce ? undefined : 'hidden'}
              whileInView={reduce ? undefined : 'show'}
              viewport={{ once: true, amount: 0.3 }}
            >
              {agents.map((agent) => (
                <motion.div className="dk-agent" key={agent.name} variants={staggerItem}>
                  <div className="dk-agent-head">
                    <span className="dk-agent-name">
                      <span className="dk-agent-icon">{agent.icon}</span>
                      {agent.name}
                    </span>
                    <span className="num dk-agent-conf">{agent.confidence}</span>
                  </div>
                  <p className="dk-agent-text">{agent.text}</p>
                  <div className="dk-agent-track">
                    <motion.div
                      className="dk-agent-fill"
                      initial={reduce ? false : { width: '0%' }}
                      whileInView={{ width: agent.confidence }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.15 }}
                      style={reduce ? { width: agent.confidence } : undefined}
                    />
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {loadingDecisions && (
              <div className="dk-empty" style={{ marginTop: 20 }}>Loading council decisions…</div>
            )}

            {!loadingDecisions && latestDecision && (
              <div className="dk-verdict">
                <div className="dk-verdict-body">
                  <span className="field-label">Portfolio Manager Verdict</span>
                  <div className="dk-verdict-action">
                    <DecisionStamp decision={latestDecision.action} />
                    <span className="dk-verdict-strategy">
                      {latestDecision.recommended_strategy
                        ? latestDecision.recommended_strategy.replace(/_/g, ' ')
                        : 'No strategy'}
                    </span>
                  </div>
                  <p className="dk-verdict-rationale">{latestDecision.rationale}</p>
                </div>
                <div className="dk-verdict-conf">
                  <span className="field-label">Confidence</span>
                  <span className="num dk-verdict-conf-val">
                    {(latestDecision.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}

            {!loadingDecisions && decisions.length === 0 && (
              <div className="dk-empty" style={{ marginTop: 20 }}>No council decisions yet.</div>
            )}
          </div>
        </section>
      </Reveal>

      {/* POSITIONS */}
      <Reveal delay={0.05}>
        <section className="eng-panel dk-panel">
          <div className="eng-panel__head">
            <div>
              <div className="eng-panel__title">Positions</div>
              <div className="eng-panel__sub">Open contracts held on the desk</div>
            </div>
          </div>

          <div className="eng-panel__body">
            {loadingPositions && <div className="dk-empty">Loading positions…</div>}

            {!loadingPositions && positions.length === 0 && (
              <div className="dk-empty">No open positions.</div>
            )}

            {!loadingPositions && positions.length > 0 && (
              <div className="dk-table-wrap">
                <table className="dk-table">
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
                    {positions.map((position) => {
                      const posPnl =
                        position.unrealized_pnl + position.realized_pnl

                      return (
                        <tr key={position.id}>
                          <td className="dk-symbol">{position.symbol}</td>
                          <td className="dk-muted">{position.strategy}</td>
                          <td className="num">{formatMoney(position.entry_price)}</td>
                          <td className="num">{formatMoney(position.current_price)}</td>
                          <td className={`num ${posPnl >= 0 ? 'dk-gain' : 'dk-loss'}`}>
                            {formatMoney(posPnl)}
                          </td>
                          <td className="num">{position.days_to_expiration}</td>
                          <td className="dk-muted">{position.recommendation}</td>
                          <td className="num dk-muted dk-nowrap">{formatDate(position.opened_at)}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </Reveal>

      {/* PERFORMANCE + PIPELINE */}
      <div className="dk-grid-2">
        <Reveal delay={0.05}>
          <section className="eng-panel dk-panel dk-fill">
            <div className="eng-panel__head">
              <div>
                <div className="eng-panel__title">P&amp;L Overview</div>
                <div className="eng-panel__sub">Mark-to-market on the book</div>
              </div>
            </div>
            <div className="eng-panel__body dk-pnl">
              <div className="dk-pnl-row">
                <span className="field-label">Total P&amp;L</span>
                <span className={`num dk-pnl-val ${portfolio && totalPnl >= 0 ? 'dk-gain' : portfolio ? 'dk-loss' : ''}`}>
                  {portfolio ? formatMoney(totalPnl) : '—'}
                </span>
              </div>
              <hr className="rule" />
              <div className="dk-pnl-row">
                <span className="field-label">Realized P&amp;L</span>
                <span className={`num dk-pnl-val ${portfolio && portfolio.realized_pnl >= 0 ? 'dk-gain' : portfolio ? 'dk-loss' : ''}`}>
                  {portfolio ? formatMoney(portfolio.realized_pnl) : '—'}
                </span>
              </div>
              <hr className="rule" />
              <div className="dk-pnl-row">
                <span className="field-label">Unrealized P&amp;L</span>
                <span className={`num dk-pnl-val ${portfolio && portfolio.unrealized_pnl >= 0 ? 'dk-gain' : portfolio ? 'dk-loss' : ''}`}>
                  {portfolio ? formatMoney(portfolio.unrealized_pnl) : '—'}
                </span>
              </div>
            </div>
          </section>
        </Reveal>

        <Reveal delay={0.1}>
          <section className="eng-panel dk-panel dk-fill">
            <div className="eng-panel__head">
              <div>
                <div className="eng-panel__title">Decision Journey</div>
                <div className="eng-panel__sub">The auditable chain of custody</div>
              </div>
            </div>
            <div className="eng-panel__body">
              <div className="dk-journey">
                <div className="dk-journey-rail" />
                {PIPELINE_STEPS.map((step, i) => (
                  <div className="dk-journey-step" key={step.label}>
                    <div className="dk-journey-dot">{step.icon}</div>
                    <span className="dk-journey-idx">{String(i + 1).padStart(2, '0')}</span>
                    <span className="dk-journey-label">{step.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </Reveal>
      </div>
    </AppShell>
  )
}

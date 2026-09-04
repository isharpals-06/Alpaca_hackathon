import React, { useState, useEffect, useRef } from 'react'
import { Calculator, Activity, TrendingUp, TrendingDown, ShieldCheck } from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { Seal, Guilloche } from '../../design'
import '../../styles/chamber.css'

interface AgentDef {
  id: string
  name: string
  role: string
  icon: React.ReactNode
  iconClass: string
  gridClass: string
  thesis: string
  confidence: number
}

const AGENTS: AgentDef[] = [
  {
    id: 'quant', name: 'Quant', role: 'Analyst',
    icon: <Calculator size={15} />, iconClass: 'icon-quant', gridClass: 'node-pos-top-left',
    thesis: 'IV percentile 58%. Liquidity 0.89/1.0, bid-ask under $0.03. Clean fill expected.',
    confidence: 85,
  },
  {
    id: 'vol', name: 'Volatility', role: 'Analyst',
    icon: <Activity size={15} />, iconClass: 'icon-vol', gridClass: 'node-pos-top-right',
    thesis: 'IV/HV spread positive at 1.25×. Volatility risk premium favours net option selling.',
    confidence: 82,
  },
  {
    id: 'bull', name: 'Bull', role: 'Advocate',
    icon: <TrendingUp size={15} />, iconClass: 'icon-bull', gridClass: 'node-pos-mid-left',
    thesis: 'Holds above the 50-day. The $520 level is heavy institutional support — sell the put.',
    confidence: 80,
  },
  {
    id: 'bear', name: 'Bear', role: 'Skeptic',
    icon: <TrendingDown size={15} />, iconClass: 'icon-bear', gridClass: 'node-pos-mid-right',
    thesis: 'Resistance at $550. I demand a 4.5% downside cushion before I sign off on this.',
    confidence: 74,
  },
  {
    id: 'risk', name: 'Risk Officer', role: 'Gatekeeper',
    icon: <ShieldCheck size={15} />, iconClass: 'icon-risk', gridClass: 'node-pos-bottom-center',
    thesis: 'Options exposure 12% — well under the 40% cap. Cushion satisfied. Capital approved.',
    confidence: 90,
  },
]

export const AnimatedChamber: React.FC = () => {
  const [step, setStep] = useState(0)
  const [cycle, setCycle] = useState(0)
  const reduce = useReducedMotion()
  const timerRef = useRef<any>(null)
  const total = AGENTS.length

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setStep((prev) => {
        const next = (prev + 1) % total
        if (next === 0) setCycle((c) => c + 1)
        return next
      })
    }, 2600)
    return () => clearInterval(timerRef.current)
  }, [total])

  const challenged = step === 3 // Bear challenges Bull
  const cleared = step === total - 1 // Risk officer speaking → verdict struck
  const active = AGENTS[step]

  return (
    <div className="chamber-arena">
      <div className="chamber-stage">
        <Guilloche
          className="chamber-stage-watermark"
          size={520}
          color="var(--copper-foil)"
          opacity={0.06}
          rings={8}
          petals={18}
        />
        <div className="chamber-grid">
          {AGENTS.map((agent, i) => {
            const isSpeaker = step === i
            const isChallenged = agent.id === 'bull' && challenged
            return (
              <motion.div
                key={agent.id}
                className={`agent-node ${agent.gridClass} ${isSpeaker ? 'active-speaker' : ''} ${isChallenged ? 'challenged' : ''}`}
                onClick={() => setStep(i)}
                animate={reduce ? undefined : { scale: isSpeaker ? 1.03 : 1 }}
                transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              >
                <div className="agent-node-top">
                  <div className="agent-avatar-wrap">
                    <div className={`agent-icon-circle ${agent.iconClass}`}>{agent.icon}</div>
                    <div>
                      <div className="agent-node-name">{agent.name}</div>
                      <div className="agent-node-role">{agent.role}</div>
                    </div>
                  </div>
                  {isSpeaker && (
                    <div className="speaking-wave">
                      <span className="wave-bar" /><span className="wave-bar" /><span className="wave-bar" />
                    </div>
                  )}
                </div>
                <p className="agent-node-thesis">{agent.thesis}</p>
                <div className="agent-node-conf">
                  <span>CONF {agent.confidence}%</span>
                  <span className="node-conf-track">
                    <span className="node-conf-fill" style={{ width: `${agent.confidence}%` }} />
                  </span>
                </div>
              </motion.div>
            )
          })}

          {/* Central ledger pod */}
          <div className="central-ledger-pod">
            <div className="pod-label">Matter Before the Council</div>
            <div className="pod-ticker-title">SPY</div>
            <div className="pod-ticker-quote">$545.50</div>
            <div className="pod-ticker-sub">Cash-Secured Put · $520 · 30 DTE</div>
            <div className="pod-stamp-area">
              <AnimatePresence mode="wait">
                {cleared ? (
                  <Seal key={`seal-${cycle}`} size={110} label="EXECUTED" sub="RISK · CLEARED" serial="Nº 0247" tone="copper" />
                ) : (
                  <motion.div
                    key="pending"
                    className="pod-pending"
                    initial={reduce ? false : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={reduce ? undefined : { opacity: 0 }}
                  >
                    <div className="pod-pending-dots"><span /><span /><span /></div>
                    <div className="pod-pending-text">Deliberating</div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Live dialogue */}
        <div className="chamber-dialogue">
          <div className="dialogue-head">
            <span className="dialogue-speaker">{active.name} · {active.role}</span>
            <span className="dialogue-step">{String(step + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}</span>
          </div>
          <AnimatePresence mode="wait">
            <motion.p
              key={step}
              className="dialogue-text"
              initial={reduce ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={reduce ? undefined : { opacity: 0, y: -6 }}
              transition={{ duration: 0.32 }}
            >
              “{active.thesis}”
            </motion.p>
          </AnimatePresence>
        </div>

        <div className="chamber-stepper">
          {AGENTS.map((_, i) => (
            <span
              key={i}
              className={`stepper-dot ${step === i ? 'active' : i < step ? 'passed' : ''}`}
              onClick={() => setStep(i)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default AnimatedChamber

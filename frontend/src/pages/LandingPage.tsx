import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Search,
  MessagesSquare,
  Gavel,
  ShieldCheck,
  Zap,
  Briefcase,
} from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import AnimatedChamber from '../components/landing/AnimatedChamber'
import { Reveal, Seal, Guilloche, CertificateFrame, SecurityStrip, staggerContainer, staggerItem } from '../design'
import '../styles/landing.css'

const WALL_STREET_QUOTES = [
  { text: 'Bulls make money, bears make money, pigs get slaughtered.', author: 'Wall Street Maxim' },
  { text: 'Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.', author: 'Warren Buffett' },
  { text: 'Markets can remain irrational longer than you can remain solvent.', author: 'J. M. Keynes' },
  { text: "Risk comes from not knowing what you're doing.", author: 'Wall Street Proverb' },
]

const PIPELINE = [
  { icon: <Search size={19} />, name: 'Opportunity', desc: 'Scan live Alpaca options for edge.' },
  { icon: <MessagesSquare size={19} />, name: 'Debate', desc: 'Five specialist agents argue it out.' },
  { icon: <Gavel size={19} />, name: 'Decision', desc: 'The council rules on the thesis.' },
  { icon: <ShieldCheck size={19} />, name: 'Risk Gate', desc: 'Deterministic limits, no exceptions.' },
  { icon: <Zap size={19} />, name: 'Trade', desc: 'Certified orders route to Alpaca.' },
  { icon: <Briefcase size={19} />, name: 'Position', desc: 'Outcome recorded to the ledger.' },
]

const SPEC_VOTES = [
  { name: 'Quant', val: 85 },
  { name: 'Volatility', val: 82 },
  { name: 'Bull', val: 80 },
  { name: 'Bear', val: 74 },
  { name: 'Risk Officer', val: 90 },
]

export const LandingPage: React.FC = () => {
  const [quoteIdx, setQuoteIdx] = useState(0)
  const reduce = useReducedMotion()

  useEffect(() => {
    const timer = setInterval(() => setQuoteIdx((p) => (p + 1) % WALL_STREET_QUOTES.length), 5200)
    return () => clearInterval(timer)
  }, [])

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`)
    document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`)
  }, [])

  const quote = WALL_STREET_QUOTES[quoteIdx]

  return (
    <div className="lp" onMouseMove={handleMouseMove}>
      <div className="lp-spotlight" />

      <div className="lp-content">
        {/* Nav */}
        <header className="lp-nav">
          <div className="lp-nav-inner">
            <Link to="/" className="lp-brand">
              <Seal size={34} label="A" sub="EST · MMXXVI" animate={false} />
              <span className="lp-brand-text">Alpaca<b>AI</b></span>
            </Link>
            <div className="lp-nav-actions">
              <Link to="/auth?mode=login" className="btn btn--ghost">Log In</Link>
              <Link to="/auth?mode=signup" className="btn btn--copper">
                Launch App <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        </header>

        <div className="lp-strip-wrap">
          <SecurityStrip />
        </div>

        {/* Hero */}
        <section className="lp-hero">
          <div className="lp-hero-inner">
            <motion.div
              className="lp-hero-copy"
              variants={staggerContainer(0.1, 0.05)}
              initial={reduce ? undefined : 'hidden'}
              animate={reduce ? undefined : 'show'}
            >
              <motion.div className="lp-kicker" variants={staggerItem}>
                <span>Certificate of Autonomous Trading</span>
              </motion.div>
              <motion.h1 className="lp-headline" variants={staggerItem}>
                Every Trade <span className="ul">Debated</span>.<br />
                Every Decision <span className="ul">Recorded</span>.
              </motion.h1>
              <motion.p className="lp-sub" variants={staggerItem}>
                An autonomous options-income desk that scans real Alpaca market data, debates risk and
                reward through five specialist agents, clears deterministic risk gates, and certifies
                every outcome into a verifiable ledger.
              </motion.p>

              <motion.div className="lp-quote" variants={staggerItem}>
                <div className="lp-quote-rule" />
                <div className="lp-quote-body">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={quoteIdx}
                      initial={reduce ? false : { opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={reduce ? undefined : { opacity: 0, y: -6 }}
                      transition={{ duration: 0.4 }}
                    >
                      <div className="lp-quote-text">“{quote.text}”</div>
                      <div className="lp-quote-author">— {quote.author}</div>
                    </motion.div>
                  </AnimatePresence>
                </div>
              </motion.div>

              <motion.div className="lp-cta-row" variants={staggerItem}>
                <Link to="/auth?mode=signup" className="btn btn--copper btn--lg">
                  Start Paper Trading <ArrowRight size={16} />
                </Link>
                <Link to="/auth?mode=login" className="btn btn--ghost btn--lg">Enter the Desk</Link>
              </motion.div>
            </motion.div>

            {/* Emblem */}
            <Reveal className="lp-emblem" delay={0.15} y={0}>
              <div className="lp-emblem-guilloche">
                <Guilloche size={400} rings={9} petals={16} opacity={0.16} animate />
              </div>
              <div className="lp-emblem-ring" />
              <Seal size={210} label="CERTIFIED" sub="ALPACA · COUNCIL" serial="Nº 0001" tone="copper" />
              <div className="lp-denom tl">Serial<b>Nº 0001</b></div>
              <div className="lp-denom br">Series<b>MMXXVI</b></div>
            </Reveal>
          </div>
        </section>

        {/* Dark council chamber */}
        <section className="lp-dark">
          <div className="lp-section">
            <Reveal className="lp-section-head">
              <div className="lp-section-kicker">The Council in Session</div>
              <h2 className="lp-section-title">Five agents. One certified verdict.</h2>
              <p className="lp-section-sub">
                Watch the desk deliberate live — each specialist stakes a position, the bench is
                challenged, and the seal is struck only when risk clears.
              </p>
            </Reveal>
            <AnimatedChamber />
          </div>
        </section>

        {/* Pipeline */}
        <section className="lp-section">
          <Reveal className="lp-section-head">
            <div className="lp-section-kicker">Chain of Custody</div>
            <h2 className="lp-section-title">From signal to certified position</h2>
            <p className="lp-section-sub">Every trade travels the same auditable path — nothing skips the record.</p>
          </Reveal>
          <motion.div
            className="lp-pipeline"
            variants={staggerContainer(0.09)}
            initial={reduce ? undefined : 'hidden'}
            whileInView={reduce ? undefined : 'show'}
            viewport={{ once: true, amount: 0.3 }}
          >
            <div className="lp-pipeline-rail" />
            {PIPELINE.map((s, i) => (
              <motion.div className="lp-step" key={s.name} variants={staggerItem}>
                <div className="lp-step-dot">{s.icon}</div>
                <span className="lp-step-idx">STEP {String(i + 1).padStart(2, '0')}</span>
                <div className="lp-step-name">{s.name}</div>
                <div className="lp-step-desc">{s.desc}</div>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Specimen certificate */}
        <section className="lp-section" style={{ paddingTop: 20 }}>
          <Reveal className="lp-section-head">
            <div className="lp-section-kicker">Specimen</div>
            <h2 className="lp-section-title">What a certified decision looks like</h2>
            <p className="lp-section-sub">Every recommendation is issued as a tamper-evident instrument.</p>
          </Reveal>

          <Reveal className="lp-specimen" delay={0.1}>
            <CertificateFrame watermark padding={30}>
              <div className="spec-head">
                <div>
                  <div className="field-label" style={{ marginBottom: 6 }}>Underlying</div>
                  <div className="spec-ticker">SPY</div>
                  <div className="spec-name">SPDR S&amp;P 500 ETF · 30 DTE</div>
                </div>
                <Seal size={104} label="EXECUTED" sub="RISK · CLEARED" serial="Nº 0247" tone="copper" />
              </div>

              <hr className="rule" style={{ margin: '18px 0' }} />

              <div className="spec-grid">
                <div>
                  <div className="field-label" style={{ marginBottom: 6 }}>Strategy</div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--espresso)' }}>Cash-Secured Put</div>
                </div>
                <div>
                  <div className="field-label" style={{ marginBottom: 6 }}>Strike</div>
                  <div className="num" style={{ fontSize: 20, fontWeight: 600, color: 'var(--espresso)' }}>$520.00</div>
                </div>
                <div>
                  <div className="field-label" style={{ marginBottom: 6 }}>Net Premium</div>
                  <div className="num" style={{ fontSize: 20, fontWeight: 600, color: 'var(--olive)' }}>+$412.00</div>
                </div>
              </div>

              <div className="field-label" style={{ margin: '4px 0 10px' }}>Council Tally</div>
              <div className="spec-tally">
                {SPEC_VOTES.map((v, i) => (
                  <Reveal key={v.name} delay={0.05 * i} y={8}>
                    <div className="spec-vote">
                      <span className="spec-vote-name">{v.name}</span>
                      <span className="spec-bar-track">
                        <motion.span
                          className="spec-bar-fill"
                          initial={reduce ? false : { width: 0 }}
                          whileInView={{ width: `${v.val}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.1 + i * 0.05 }}
                          style={{ display: 'block' }}
                        />
                      </span>
                      <span className="spec-vote-val">{v.val}%</span>
                    </div>
                  </Reveal>
                ))}
              </div>

              <div className="spec-foot">
                <span className="field-label">Certified · Series MMXXVI</span>
                <span className="field-label" style={{ color: 'var(--copper-ink)' }}>Alpaca Council of Agents</span>
              </div>
            </CertificateFrame>
          </Reveal>
        </section>

        {/* CTA band */}
        <section className="lp-dark">
          <div className="lp-cta-band">
            <Reveal>
              <h2 className="lp-section-title" style={{ color: 'var(--ink-text)', marginBottom: 14 }}>
                Open the desk. Watch it deliberate.
              </h2>
              <p className="lp-section-sub" style={{ color: 'var(--ink-muted)', maxWidth: 520, margin: '0 auto 26px' }}>
                Paper-traded, fully recorded, and certified end to end. No capital at risk.
              </p>
              <Link to="/auth?mode=signup" className="btn btn--copper btn--lg">
                Start Paper Trading <ArrowRight size={16} />
              </Link>
            </Reveal>
          </div>
        </section>

        {/* Footer */}
        <footer className="lp-footer">
          <div className="lp-footer-inner">
            <div className="lp-footer-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Seal size={30} label="A" sub="" animate={false} />
                <span className="lp-footer-brand">Alpaca AI</span>
              </div>
              <div className="lp-footer-copy">Autonomous Options-Income Council</div>
            </div>
            <SecurityStrip variant="ink" />
            <div className="lp-footer-copy" style={{ marginTop: 18, textAlign: 'center' }}>
              © {new Date().getFullYear()} Alpaca AI · Paper trading only · Not investment advice
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default LandingPage

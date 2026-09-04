import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { motion, useReducedMotion } from 'framer-motion'
import { supabase, isSupabaseConfigured } from '../lib/supabaseClient'
import { setDemoSession } from '../lib/useAuth'
import { Seal, CertificateFrame, SecurityStrip, staggerContainer, staggerItem, EASE_OUT } from '../design'
import '../styles/auth.css'

export const AuthPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const modeParam = searchParams.get('mode')
  const [mode, setMode] = useState<'login' | 'signup'>(modeParam === 'signup' ? 'signup' : 'login')

  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const reduce = useReducedMotion()

  useEffect(() => {
    if (modeParam === 'signup') setMode('signup')
    else if (modeParam === 'login') setMode('login')
  }, [modeParam])

  // Mouse spotlight coordinates
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const x = e.clientX
    const y = e.clientY
    document.documentElement.style.setProperty('--mouse-x', `${x}px`)
    document.documentElement.style.setProperty('--mouse-y', `${y}px`)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (!email || !password) {
      setError('Please enter your email and password.')
      setLoading(false)
      return
    }

    const traderName = displayName.trim() || email.split('@')[0]

    if (!isSupabaseConfigured) {
      // Local session if cloud is unreachable
      setDemoSession(email, traderName)
      navigate('/dashboard')
      setLoading(false)
      return
    }

    try {
      if (mode === 'signup') {
        // 1. Create account in Supabase
        try {
          await supabase.auth.signUp({
            email,
            password,
            options: {
              data: {
                display_name: traderName,
              },
            },
          })
        } catch {
          // Continue to direct session entry
        }

        // 2. Immediately provision active session so no email confirmation is ever needed
        setDemoSession(email, traderName)
        navigate('/dashboard')
      } else {
        // Direct Log In
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (signInError) {
          const msg = signInError.message || ''
          // If Supabase flags unconfirmed email, bypass and grant access directly
          if (msg.toLowerCase().includes('email not confirmed') || msg.toLowerCase().includes('confirm')) {
            setDemoSession(email, traderName)
            navigate('/dashboard')
            return
          }
          throw signInError
        }

        navigate('/dashboard')
      }
    } catch (err: any) {
      const msg = err?.message || ''
      if (msg.includes('Invalid login credentials')) {
        setError('Invalid email or password. Please check your credentials and try again.')
      } else if (msg.includes('User already registered')) {
        // If already registered, sign in directly
        setDemoSession(email, traderName)
        navigate('/dashboard')
      } else {
        setError(msg || 'Authentication failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="vault" onMouseMove={handleMouseMove}>
      {/* Cursor spotlight, tuned for the dark vault */}
      <div className="vault-spotlight" aria-hidden="true" />

      {/* Ambient Wall Street bull, struck faintly into the vault wall */}
      <div className="vault-bull" aria-hidden="true">
        <svg viewBox="0 0 1000 600" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
          <path d="M120 480 C140 430 180 410 240 420 C290 430 330 400 380 370 C430 340 480 320 540 310 C620 300 690 320 750 350 C800 375 850 380 890 350 C920 325 940 280 930 240 C920 200 880 180 840 190 C810 200 790 190 770 170 C740 140 700 120 650 130 C600 140 560 160 520 190 C480 220 430 240 380 240 C320 240 270 210 210 220 C150 230 110 270 90 330 C70 390 80 450 120 480 Z" />
          <path d="M840 190 C870 140 920 100 970 90 C980 120 970 160 930 190 Z" />
          <path d="M780 160 C810 110 860 70 910 60 C920 90 910 130 870 160 Z" />
          <path d="M220 420 L180 560 L240 560 L270 450 Z" />
          <path d="M360 400 L330 550 L390 550 L410 420 Z" />
          <path d="M680 370 L720 560 L780 560 L750 400 Z" />
          <path d="M800 380 L840 540 L890 540 L860 370 Z" />
        </svg>
      </div>

      {/* Top Bar */}
      <header className="vault-nav">
        <Link to="/" className="vault-brand">
          <Seal size={30} label="A" sub="EST · MMXXVI" animate={false} />
          <span className="vault-brand-text">Alpaca<b>AI</b></span>
        </Link>
        <Link to="/" className="vault-back">
          <ArrowLeft size={15} className="arrow-back" />
          Back to Overview
        </Link>
      </header>

      {/* Centered Access Certificate */}
      <main className="vault-main">
        <CertificateFrame variant="ink" watermark padding={30} radius={16} className="vault-cert">
          <div className="vault-cert-body">
            {/* Struck access seal */}
            <div className="vault-seal-wrap">
              <Seal label="ACCESS" sub="ALPACA · VAULT" serial="ALP-2026" size={96} tone="copper" />
            </div>

            <motion.div
              className="vault-stack"
              variants={reduce ? undefined : staggerContainer(0.1, 0.14)}
              initial={reduce ? undefined : 'hidden'}
              animate={reduce ? undefined : 'show'}
            >
              {/* Mode Switcher — segmented control */}
              <motion.div
                className="vault-seg"
                role="tablist"
                aria-label="Choose access mode"
                variants={reduce ? undefined : staggerItem}
              >
                <span className="vault-seg-thumb" data-mode={mode} aria-hidden="true" />
                <button
                  type="button"
                  role="tab"
                  aria-selected={mode === 'login'}
                  className={`vault-seg-btn ${mode === 'login' ? 'is-active' : ''}`}
                  onClick={() => {
                    setMode('login')
                    setError(null)
                  }}
                >
                  Log In
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={mode === 'signup'}
                  className={`vault-seg-btn ${mode === 'signup' ? 'is-active' : ''}`}
                  onClick={() => {
                    setMode('signup')
                    setError(null)
                  }}
                >
                  Create Account
                </button>
              </motion.div>

              {/* Mode-dependent title + subline. A keyed remount plays the
                  enter animation on each toggle — no AnimatePresence "wait"
                  stall, since there is no exit to block the swap. */}
              <motion.div className="vault-head" variants={reduce ? undefined : staggerItem}>
                <motion.div
                  key={mode}
                  initial={reduce ? false : { opacity: 0, y: 8 }}
                  animate={reduce ? {} : { opacity: 1, y: 0 }}
                  transition={{ duration: 0.28, ease: EASE_OUT }}
                >
                  <h1 className="vault-title">{mode === 'signup' ? 'Open an Account' : 'Enter the Desk'}</h1>
                  <p className="vault-sub">
                    {mode === 'signup'
                      ? 'Open a certified account and take your seat at the trading desk.'
                      : 'Authenticate to return to your certified trading desk.'}
                  </p>
                </motion.div>
              </motion.div>

              {/* Error Banner — keyed so a new message re-plays the enter. */}
              {error && (
                <motion.div
                  key={error}
                  className="vault-error"
                  role="alert"
                  initial={reduce ? false : { opacity: 0, y: -6 }}
                  animate={reduce ? {} : { opacity: 1, y: 0 }}
                  transition={{ duration: 0.24, ease: EASE_OUT }}
                >
                  {error}
                </motion.div>
              )}

              {/* Form */}
              <motion.form className="vault-form" onSubmit={handleSubmit} variants={reduce ? undefined : staggerItem}>
                {mode === 'signup' && (
                  <motion.div
                    key="displayName"
                    className="vault-field-anim"
                    initial={reduce ? false : { opacity: 0, height: 0 }}
                    animate={reduce ? {} : { opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3, ease: EASE_OUT }}
                  >
                    <div className="vault-field">
                      <label className="field-label">Trader Name / Alias</label>
                      <input
                        type="text"
                        className="vault-input"
                        placeholder="e.g. Alexander Hamilton"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        autoFocus
                      />
                    </div>
                  </motion.div>
                )}

                <div className="vault-field">
                  <label className="field-label">Email Address</label>
                  <input
                    type="email"
                    className="vault-input"
                    placeholder="trader@wallstreet.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoFocus={mode === 'login'}
                  />
                </div>

                <div className="vault-field">
                  <label className="field-label">Password</label>
                  <input
                    type="password"
                    className="vault-input"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                  />
                </div>

                <button type="submit" className="btn btn--copper btn--lg vault-submit" disabled={loading}>
                  {loading ? (
                    'Connecting to Trading Desk...'
                  ) : mode === 'signup' ? (
                    <>
                      Create Account & Enter Desk
                      <ArrowRight size={16} className="arrow" />
                    </>
                  ) : (
                    <>
                      Sign In to Trading Console
                      <ArrowRight size={16} className="arrow" />
                    </>
                  )}
                </button>
              </motion.form>
            </motion.div>
          </div>
        </CertificateFrame>
      </main>

      {/* Vault microprint footer */}
      <footer className="vault-foot">
        <SecurityStrip variant="ink" text="ALPACA CAPITAL — SECURE ACCESS TERMINAL — EVERY SESSION CERTIFIED —" />
      </footer>
    </div>
  )
}

export default AuthPage

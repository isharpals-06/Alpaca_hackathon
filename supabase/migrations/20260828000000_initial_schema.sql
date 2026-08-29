-- ============================================================================
-- ThetaCouncil AI — Full Supabase Database Schema
-- Matches backend/models/contracts.py Pydantic Data Contracts
-- ============================================================================

-- 1. Opportunities Table
CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    underlying_price NUMERIC NOT NULL,
    historical_volatility NUMERIC,
    implied_volatility NUMERIC NOT NULL,
    iv_percentile NUMERIC NOT NULL,
    liquidity_score NUMERIC NOT NULL,
    sector TEXT,
    candidate_contracts JSONB NOT NULL DEFAULT '[]'::jsonb,
    scanned_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX IF NOT EXISTS idx_opportunities_scanned_at ON opportunities(scanned_at DESC);

-- 2. Debates Table
CREATE TABLE IF NOT EXISTS debates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    phase1_agents JSONB NOT NULL DEFAULT '{}'::jsonb,
    phase2_challenges JSONB NOT NULL DEFAULT '[]'::jsonb,
    phase2_responses JSONB NOT NULL DEFAULT '[]'::jsonb,
    phase3_synthesis JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_debates_symbol ON debates(symbol);
CREATE INDEX IF NOT EXISTS idx_debates_created_at ON debates(created_at DESC);

-- 3. Decisions Table
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    rationale TEXT NOT NULL,
    confidence_score NUMERIC NOT NULL,
    recommended_strategy TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_decisions_symbol ON decisions(symbol);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at DESC);

-- 4. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES decisions(id) ON DELETE SET NULL,
    alpaca_order_id TEXT,
    status TEXT NOT NULL,
    contract_symbol TEXT NOT NULL,
    underlying_symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    qty INTEGER NOT NULL,
    limit_price NUMERIC,
    filled_avg_price NUMERIC,
    submitted_at TIMESTAMPTZ DEFAULT now(),
    filled_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_orders_alpaca_id ON orders(alpaca_order_id);
CREATE INDEX IF NOT EXISTS idx_orders_submitted_at ON orders(submitted_at DESC);

-- 5. Positions Table
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    underlying_symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    option_type TEXT NOT NULL,
    strike_price NUMERIC NOT NULL,
    expiration_date TEXT NOT NULL,
    qty INTEGER NOT NULL DEFAULT 1,
    entry_premium NUMERIC NOT NULL,
    current_premium NUMERIC NOT NULL,
    unrealized_pnl NUMERIC NOT NULL DEFAULT 0,
    realized_pnl NUMERIC NOT NULL DEFAULT 0,
    days_to_expiration INTEGER NOT NULL,
    recommendation TEXT DEFAULT 'HOLD',
    recommendation_reason TEXT,
    opened_at TIMESTAMPTZ DEFAULT now(),
    last_checked_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_underlying ON positions(underlying_symbol);

-- 6. Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_realized_pnl NUMERIC NOT NULL DEFAULT 0,
    total_unrealized_pnl NUMERIC NOT NULL DEFAULT 0,
    win_rate_pct NUMERIC NOT NULL DEFAULT 100,
    total_trades_count INTEGER NOT NULL DEFAULT 0,
    winning_trades_count INTEGER NOT NULL DEFAULT 0,
    average_premium_captured_pct NUMERIC NOT NULL DEFAULT 0,
    as_of TIMESTAMPTZ DEFAULT now()
);

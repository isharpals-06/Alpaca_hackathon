-- Initial schema for Alpaca AI Trading Pipeline

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    underlying_price NUMERIC NOT NULL,
    implied_volatility NUMERIC NOT NULL,
    iv_percentile NUMERIC NOT NULL,
    liquidity_score NUMERIC NOT NULL,
    scanned_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS debates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    agent_outputs JSONB NOT NULL DEFAULT '[]'::jsonb,
    cross_examination JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    rationale TEXT NOT NULL,
    confidence_score NUMERIC NOT NULL,
    recommended_strategy TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES decisions(id) ON DELETE SET NULL,
    alpaca_order_id TEXT,
    status TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    qty INTEGER NOT NULL,
    filled_avg_price NUMERIC,
    submitted_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_price NUMERIC NOT NULL,
    current_price NUMERIC NOT NULL,
    unrealized_pnl NUMERIC NOT NULL DEFAULT 0,
    realized_pnl NUMERIC NOT NULL DEFAULT 0,
    days_to_expiration INTEGER NOT NULL,
    recommendation TEXT DEFAULT 'HOLD',
    opened_at TIMESTAMPTZ DEFAULT now()
);

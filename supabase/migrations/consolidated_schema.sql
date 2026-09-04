-- =====================================================================
-- ALPACA AI — CONSOLIDATED MASTER SUPABASE SCHEMA MIGRATION (V2)
-- Safe, Idempotent, and updates pre-existing tables with all columns!
-- Run this in your Supabase Project SQL Editor.
-- =====================================================================

-- 1. Create Tables If Not Present
CREATE TABLE IF NOT EXISTS public.opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    underlying_price NUMERIC NOT NULL,
    historical_volatility NUMERIC DEFAULT 0,
    implied_volatility NUMERIC NOT NULL DEFAULT 0,
    iv_percentile NUMERIC NOT NULL DEFAULT 50,
    liquidity_score NUMERIC NOT NULL DEFAULT 0,
    sector TEXT DEFAULT 'Equities',
    candidate_contracts JSONB DEFAULT '[]'::jsonb,
    scanned_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.profiles (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    display_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.portfolios (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    cash NUMERIC NOT NULL DEFAULT 100000.00,
    buying_power NUMERIC NOT NULL DEFAULT 100000.00,
    portfolio_value NUMERIC NOT NULL DEFAULT 100000.00,
    unrealized_pnl NUMERIC NOT NULL DEFAULT 0,
    realized_pnl NUMERIC NOT NULL DEFAULT 0,
    open_positions_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.debates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    rationale TEXT NOT NULL,
    confidence_score NUMERIC NOT NULL DEFAULT 0.70,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL DEFAULT 'sell_to_open',
    qty INTEGER NOT NULL DEFAULT 1,
    submitted_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_price NUMERIC NOT NULL DEFAULT 0,
    current_price NUMERIC NOT NULL DEFAULT 0,
    unrealized_pnl NUMERIC NOT NULL DEFAULT 0,
    realized_pnl NUMERIC NOT NULL DEFAULT 0,
    days_to_expiration INTEGER NOT NULL DEFAULT 30,
    opened_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================================================
-- 2. ALTER Pre-existing Tables to Guarantee all Columns and user_id exist
-- =====================================================================

-- Debates table columns
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS symbol TEXT;
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS agent_outputs JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS cross_examination JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE public.debates ADD COLUMN IF NOT EXISTS round_count INTEGER DEFAULT 1;

-- Decisions table columns
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS symbol TEXT;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS recommended_strategy TEXT;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS debate_id UUID;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS order_spec TEXT;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS premium NUMERIC;
ALTER TABLE public.decisions ADD COLUMN IF NOT EXISTS status TEXT;

-- Orders table columns
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS decision_id UUID;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS alpaca_order_id TEXT;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS contract_symbol TEXT;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS underlying_symbol TEXT;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS limit_price NUMERIC;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS filled_avg_price NUMERIC;
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS filled_at TIMESTAMPTZ;

-- Positions table columns
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS underlying_symbol TEXT;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS option_type TEXT DEFAULT 'put';
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS strike_price NUMERIC DEFAULT 0;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS entry_premium NUMERIC DEFAULT 0;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS current_premium NUMERIC DEFAULT 0;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS expiration_date TEXT;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS qty INTEGER DEFAULT 1;
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS recommendation TEXT DEFAULT 'HOLD';
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS recommendation_reason TEXT DEFAULT 'Position healthy, monitoring decay.';
ALTER TABLE public.positions ADD COLUMN IF NOT EXISTS last_checked_at TIMESTAMPTZ DEFAULT now();

-- =====================================================================
-- 3. AUTH TRIGGER: Automatic $100k Virtual Paper Allocation on Sign Up
-- =====================================================================
CREATE OR REPLACE FUNCTION public.on_auth_user_created()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (user_id, display_name)
  VALUES (new.id, COALESCE(new.raw_user_meta_data->>'display_name', 'Trader'))
  ON CONFLICT (user_id) DO NOTHING;

  INSERT INTO public.portfolios (user_id, cash, buying_power, portfolio_value)
  VALUES (new.id, 100000.00, 100000.00, 100000.00)
  ON CONFLICT (user_id) DO NOTHING;

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.on_auth_user_created();

-- =====================================================================
-- 4. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.debates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;

-- Shared Opportunities Policy
DROP POLICY IF EXISTS "Opportunities are viewable by all authenticated users." ON public.opportunities;
CREATE POLICY "Opportunities are viewable by all authenticated users."
  ON public.opportunities FOR SELECT
  TO authenticated, anon
  USING (true);

-- User-scoped Profiles
DROP POLICY IF EXISTS "Users can manage their own profiles." ON public.profiles;
CREATE POLICY "Users can manage their own profiles."
  ON public.profiles FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

-- User-scoped Portfolios
DROP POLICY IF EXISTS "Users can manage their own portfolios." ON public.portfolios;
CREATE POLICY "Users can manage their own portfolios."
  ON public.portfolios FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

-- User-scoped Positions
DROP POLICY IF EXISTS "Users can manage their own positions." ON public.positions;
CREATE POLICY "Users can manage their own positions."
  ON public.positions FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

-- User-scoped Orders
DROP POLICY IF EXISTS "Users can manage their own orders." ON public.orders;
CREATE POLICY "Users can manage their own orders."
  ON public.orders FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

-- User-scoped Decisions
DROP POLICY IF EXISTS "Users can manage their own decisions." ON public.decisions;
CREATE POLICY "Users can manage their own decisions."
  ON public.decisions FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

-- User-scoped Debates
DROP POLICY IF EXISTS "Users can manage their own debates." ON public.debates;
CREATE POLICY "Users can manage their own debates."
  ON public.debates FOR ALL TO authenticated, anon
  USING (true) WITH CHECK (true);

CREATE TABLE IF NOT EXISTS public.profiles (
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  display_name TEXT
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

CREATE OR REPLACE FUNCTION public.on_auth_user_created()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (user_id, display_name)
  VALUES (new.id, new.raw_user_meta_data->>'display_name');

  INSERT INTO public.portfolios (user_id, cash, buying_power, portfolio_value)
  VALUES (new.id, 100000.00, 100000.00, 100000.00);

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.on_auth_user_created();

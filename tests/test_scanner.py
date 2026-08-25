import pytest
from backend.scanner.universe import get_curated_symbols, get_symbol_metadata
from backend.scanner.options_scanner import OptionsScanner

def test_universe_configuration():
    symbols = get_curated_symbols()
    assert "SPY" in symbols
    assert "AAPL" in symbols
    assert "NVDA" in symbols
    
    spy_meta = get_symbol_metadata("SPY")
    assert spy_meta["sector"] == "Index ETF"

def test_osi_symbol_parsing():
    scanner = OptionsScanner()
    parsed = scanner._parse_osi_symbol("SPY260918P00540000")
    assert parsed is not None
    assert parsed["option_type"] == "put"
    assert parsed["strike_price"] == 540.0
    assert parsed["expiration_date"].strftime("%y%m%d") == "260918"

@pytest.mark.asyncio
async def test_options_scanner_fallback_generation():
    scanner = OptionsScanner()
    opp = await scanner.scan_symbol("AAPL")
    
    assert opp is not None
    assert opp.symbol == "AAPL"
    assert opp.underlying_price > 0
    assert len(opp.candidate_contracts) > 0
    
    # Verify contracts have both CALLs and PUTs within 14-45 DTE
    has_call = any(c.option_type.value == "call" for c in opp.candidate_contracts)
    has_put = any(c.option_type.value == "put" for c in opp.candidate_contracts)
    assert has_call
    assert has_put
    assert all(14 <= c.days_to_expiration <= 45 for c in opp.candidate_contracts)

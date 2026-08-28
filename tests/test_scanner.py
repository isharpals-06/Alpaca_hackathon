import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from backend.scanner.universe import get_curated_symbols, get_symbol_metadata
from backend.scanner.options_scanner import OptionsScanner
from backend.models.contracts import OptionTypeEnum

class TestScanner(unittest.TestCase):
    def test_universe_configuration(self):
        symbols = get_curated_symbols()
        self.assertIn("SPY", symbols)
        self.assertIn("AAPL", symbols)
        self.assertIn("NVDA", symbols)
        
        spy_meta = get_symbol_metadata("SPY")
        self.assertEqual(spy_meta["sector"], "Index ETF")

    def test_osi_symbol_parsing(self):
        scanner = OptionsScanner()
        parsed = scanner._parse_osi_symbol("SPY260918P00540000")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["option_type"], "put")
        self.assertEqual(parsed["strike_price"], 540.0)
        self.assertEqual(parsed["expiration_date"].strftime("%y%m%d"), "260918")

    def test_options_scanner_fallback_generation(self):
        async def run_test():
            scanner = OptionsScanner()
            opp = await scanner.scan_symbol("AAPL")
            
            self.assertIsNotNone(opp)
            self.assertEqual(opp.symbol, "AAPL")
            self.assertGreater(opp.underlying_price, 0)
            self.assertGreater(len(opp.candidate_contracts), 0)
            
            has_call = any(c.option_type == OptionTypeEnum.CALL for c in opp.candidate_contracts)
            has_put = any(c.option_type == OptionTypeEnum.PUT for c in opp.candidate_contracts)
            self.assertTrue(has_call)
            self.assertTrue(has_put)
            self.assertTrue(all(14 <= c.days_to_expiration <= 45 for c in opp.candidate_contracts))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

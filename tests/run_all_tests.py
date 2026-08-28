import sys
import os
import unittest
import time

sys.path.insert(0, os.path.abspath("."))

def run_all_tests():
    print("=" * 70)
    print(" ALPACA AI TRADING ENGINE — MASTER TEST SUITE (DAYS 1 to 6)")
    print("=" * 70)

    test_modules = [
        "tests.test_contracts_and_db",
        "tests.test_scanner",
        "tests.test_strategy",
        "tests.test_risk_engine",
        "tests.test_position_monitor",
        "tests.test_performance",
        "tests.test_positions_api",
        "tests.test_api",
        "tests.test_integration_e2e",
    ]

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    for module_name in test_modules:
        try:
            mod_suite = loader.loadTestsFromName(module_name)
            suite.addTests(mod_suite)
        except Exception as e:
            print(f"[!] Error loading {module_name}: {e}")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f" MASTER TEST RUNNER SUMMARY: Ran {result.testsRun} tests in {elapsed:.2f}s")
    print(f" Status: {'ALL PASSED (100% SUCCESS)' if result.wasSuccessful() else 'FAILURES DETECTED'}")
    print("=" * 70)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

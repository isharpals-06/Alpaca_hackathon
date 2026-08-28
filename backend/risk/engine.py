import logging
from typing import Optional, List
from datetime import datetime

from backend.models.contracts import (
    ContractSpec,
    PortfolioState,
    RiskAssessment,
    RiskCheckItem,
)
from backend.risk.checks import (
    check_contract_validity,
    check_position_sizing,
    check_total_options_exposure,
    check_sector_concentration,
    check_assignment_collateral,
)

logger = logging.getLogger("backend.risk.engine")

class DeterministicRiskEngine:
    """
    Code-governed, non-negotiable Risk Gatekeeper.
    Runs 5 sequential checks with unilateral veto authority before any trade reaches Alpaca.
    """

    def evaluate_trade(
        self,
        contract_spec: ContractSpec,
        portfolio_state: Optional[PortfolioState] = None,
        simulate_veto: bool = False,
    ) -> RiskAssessment:
        portfolio = portfolio_state or PortfolioState(
            cash=100000.0,
            buying_power=400000.0,
            portfolio_value=100000.0,
            options_collateral_used=0.0,
            open_positions_count=0,
            positions=[],
            as_of=datetime.utcnow(),
        )

        checks_run: List[str] = []
        checks_passed: List[str] = []
        checks_failed: List[str] = []
        detailed_checks: List[RiskCheckItem] = []
        veto_reason: Optional[str] = None

        # 1. Contract Validity
        res1 = check_contract_validity(contract_spec)
        self._record_check(res1, checks_run, checks_passed, checks_failed, detailed_checks)

        # 2. Position Sizing
        res2 = check_position_sizing(contract_spec, portfolio)
        self._record_check(res2, checks_run, checks_passed, checks_failed, detailed_checks)

        # 3. Total Options Exposure
        res3 = check_total_options_exposure(contract_spec, portfolio)
        self._record_check(res3, checks_run, checks_passed, checks_failed, detailed_checks)

        # 4. Sector / Single Ticker Concentration
        res4 = check_sector_concentration(contract_spec, portfolio)
        self._record_check(res4, checks_run, checks_passed, checks_failed, detailed_checks)

        # 5. Assignment Collateral Check
        res5 = check_assignment_collateral(contract_spec, portfolio)
        self._record_check(res5, checks_run, checks_passed, checks_failed, detailed_checks)

        # Presentation Lever: Simulate Veto for judging demonstrations
        if simulate_veto:
            veto_sim = RiskCheckItem(
                check_name="Position Sizing (Simulated)",
                passed=False,
                details="RISK VETO: Trade size exceeds emergency portfolio volatility stress buffer (Simulated Veto for Demo).",
            )
            checks_run.append("Position Sizing (Simulated)")
            checks_failed.append("Position Sizing (Simulated)")
            detailed_checks.append(veto_sim)

        all_passed = len(checks_failed) == 0

        if not all_passed:
            failed_details = [c.details for c in detailed_checks if not c.passed]
            veto_reason = " | ".join(failed_details)
            logger.warning("RISK GATE VETO for %s: %s", contract_spec.symbol, veto_reason)
        else:
            logger.info("RISK GATE APPROVED for %s: All %d checks passed", contract_spec.symbol, len(checks_run))

        capital_required = contract_spec.strike_price * 100.0 * contract_spec.contracts_count
        portfolio_exposure_pct = round((capital_required / max(portfolio.portfolio_value, 1.0)) * 100.0, 2)

        return RiskAssessment(
            approved=all_passed,
            checks_run=checks_run,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            veto_reason=veto_reason,
            portfolio_exposure_pct=portfolio_exposure_pct,
            max_loss_potential=contract_spec.max_loss_estimate,
            detailed_checks=detailed_checks,
            reviewed_at=datetime.utcnow(),
        )

    def _record_check(
        self,
        item: RiskCheckItem,
        checks_run: List[str],
        checks_passed: List[str],
        checks_failed: List[str],
        detailed_checks: List[RiskCheckItem],
    ):
        checks_run.append(item.check_name)
        if item.passed:
            checks_passed.append(item.check_name)
        else:
            checks_failed.append(item.check_name)
        detailed_checks.append(item)

# Singleton risk engine
risk_engine = DeterministicRiskEngine()

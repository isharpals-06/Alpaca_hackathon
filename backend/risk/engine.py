import logging
from typing import List
from datetime import datetime
import uuid

from backend.models.contracts import ContractSpec, PortfolioState, RiskAssessment, RiskCheckItem
from backend.risk.checks import (
    check_position_size,
    check_options_exposure,
    check_sector_concentration,
    check_contract_parameters,
    check_collateral_sufficiency,
)

logger = logging.getLogger("backend.risk")

class RiskEngine:
    """
    Deterministic Risk Gatekeeper.
    Executes sequential, non-negotiable risk rules before any order can reach execution.
    Can veto any trade approved by the Portfolio Manager.
    """

    def validate_trade(self, contract: ContractSpec, portfolio: PortfolioState) -> RiskAssessment:
        checks: List[RiskCheckItem] = [
            check_position_size(contract, portfolio),
            check_options_exposure(contract, portfolio),
            check_sector_concentration(contract, portfolio),
            check_contract_parameters(contract),
            check_collateral_sufficiency(contract, portfolio),
        ]

        passed_checks = [c.check_name for c in checks if c.passed]
        failed_checks = [c.check_name for c in checks if not c.passed]
        
        approved = len(failed_checks) == 0
        veto_reason = None

        if not approved:
            failed_details = [c.details for c in checks if not c.passed]
            veto_reason = f"Risk Gate VETO: {'; '.join(failed_details)}"
            logger.warning("Trade on %s rejected by Risk Gate: %s", contract.symbol, veto_reason)
        else:
            logger.info("Trade on %s approved by Risk Gate. All 5 checks passed.", contract.symbol)

        exposure_pct = round((contract.max_loss_estimate / max(portfolio.portfolio_value, 1.0)) * 100, 2)

        return RiskAssessment(
            id=str(uuid.uuid4()),
            approved=approved,
            checks_run=[c.check_name for c in checks],
            checks_passed=passed_checks,
            checks_failed=failed_checks,
            veto_reason=veto_reason,
            portfolio_exposure_pct=exposure_pct,
            max_loss_potential=contract.max_loss_estimate,
            detailed_checks=checks,
            reviewed_at=datetime.utcnow(),
        )

risk_engine = RiskEngine()
DeterministicRiskEngine = RiskEngine


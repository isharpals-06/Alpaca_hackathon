import logging
from typing import Optional
from backend.models.contracts import (
    Opportunity,
    Decision,
    PortfolioState,
    ContractSpec,
    StrategyEnum,
    ActionEnum,
)
from backend.strategy.cash_secured_put import select_best_csp_contract
from backend.strategy.covered_call import select_best_covered_call_contract

logger = logging.getLogger("backend.strategy.engine")

class OptionsStrategyEngine:
    """
    Translates an approved TRADE decision into a concrete, order-ready ContractSpec.
    Applies Wheel strategy logic:
    - Cash-Secured Put if cash available and holding 0 shares
    - Covered Call if holding 100+ shares
    """

    def build_contract_spec(
        self,
        opportunity: Opportunity,
        decision: Decision,
        portfolio_state: Optional[PortfolioState] = None,
    ) -> Optional[ContractSpec]:
        if decision.action != ActionEnum.TRADE:
            logger.info("Strategy Engine skipped: Decision action is %s", decision.action)
            return None

        # Determine strategy type from decision or portfolio state
        strategy_type = decision.recommended_strategy or StrategyEnum.CASH_SECURED_PUT

        if strategy_type == StrategyEnum.COVERED_CALL:
            logger.info("Building Covered Call contract spec for %s", opportunity.symbol)
            return select_best_covered_call_contract(opportunity)
        else:
            logger.info("Building Cash-Secured Put contract spec for %s", opportunity.symbol)
            return select_best_csp_contract(opportunity)

# Singleton strategy engine
strategy_engine = OptionsStrategyEngine()

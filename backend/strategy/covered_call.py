import logging
from typing import Optional, List
from backend.models.contracts import (
    Opportunity,
    CandidateContract,
    ContractSpec,
    StrategyEnum,
    OptionTypeEnum,
)

logger = logging.getLogger("backend.strategy.covered_call")

def select_best_covered_call_contract(
    opportunity: Opportunity,
    target_delta: float = 0.25,
) -> Optional[ContractSpec]:
    """
    Selects the optimal Covered Call contract from the opportunity's candidate contracts.
    Filters: CALL options, 14-45 DTE, strike above underlying price, delta near target_delta (~0.25).
    """
    call_candidates: List[CandidateContract] = [
        c for c in opportunity.candidate_contracts
        if c.option_type == OptionTypeEnum.CALL and 14 <= c.days_to_expiration <= 45
    ]

    if not call_candidates:
        logger.warning("No call candidates found for %s within 14-45 DTE", opportunity.symbol)
        return None

    best_candidate: Optional[CandidateContract] = None
    best_score: float = -1.0

    for contract in call_candidates:
        contract_delta = contract.delta if contract.delta is not None else 0.25
        delta_diff = abs(contract_delta - target_delta)
        delta_score = max(0.0, 1.0 - (delta_diff / 0.15))

        dte = max(contract.days_to_expiration, 1)
        annualized_yield = (contract.mid_price / max(opportunity.underlying_price, 1.0)) * (365.0 / dte)
        yield_score = min(1.0, annualized_yield / 0.25)

        liq_score = contract.liquidity_score
        total_score = (yield_score * 0.40) + (delta_score * 0.35) + (liq_score * 0.25)

        if total_score > best_score:
            best_score = total_score
            best_candidate = contract

    if not best_candidate:
        best_candidate = call_candidates[0]

    return ContractSpec(
        symbol=best_candidate.symbol,
        underlying_symbol=opportunity.symbol,
        strategy_type=StrategyEnum.COVERED_CALL,
        option_type=OptionTypeEnum.CALL,
        strike_price=best_candidate.strike_price,
        expiration_date=best_candidate.expiration_date,
        days_to_expiration=best_candidate.days_to_expiration,
        delta=best_candidate.delta if best_candidate.delta is not None else 0.25,
        premium_estimate=best_candidate.mid_price,
        contracts_count=1,
        max_loss_estimate=round(opportunity.underlying_price * 100.0, 2),
        liquidity_score=best_candidate.liquidity_score,
    )

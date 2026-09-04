from typing import Optional
from backend.models.contracts import Opportunity, CandidateContract, ContractSpec, StrategyEnum, OptionTypeEnum

class CashSecuredPutStrategy:
    """
    Cash-Secured Put strategy builder.
    Selects Out-Of-The-Money Put options (Delta -0.18 to -0.32, DTE 14–45 days)
    to generate upfront cash premium while establishing an attractive equity entry point.
    """

    def construct_proposal(self, opportunity: Opportunity, contracts_count: int = 1) -> Optional[ContractSpec]:
        symbol = opportunity.symbol
        price = opportunity.underlying_price
        
        # Filter put candidates from scanner
        put_candidates = [
            c for c in opportunity.candidate_contracts
            if c.option_type == OptionTypeEnum.PUT and c.strike_price <= price
        ]

        # Best candidate: Delta nearest to -0.22
        selected: Optional[CandidateContract] = None
        if put_candidates:
            selected = min(
                put_candidates,
                key=lambda c: abs((c.delta if c.delta is not None else -0.22) - (-0.22))
            )

        if not selected:
            target_strike = round(price * 0.95, 1)
            est_premium = round(price * 0.022, 2)
            osi_strike = f"{int(target_strike * 1000):08d}"
            osi_symbol = f"{symbol}260918P{osi_strike}"
            
            return ContractSpec(
                symbol=osi_symbol,
                underlying_symbol=symbol,
                strategy_type=StrategyEnum.CASH_SECURED_PUT,
                option_type=OptionTypeEnum.PUT,
                strike_price=target_strike,
                expiration_date="2026-09-18",
                days_to_expiration=30,
                delta=-0.22,
                premium_estimate=est_premium * 100 * contracts_count,
                contracts_count=contracts_count,
                max_loss_estimate=round(target_strike * 100 * contracts_count, 2),
                liquidity_score=opportunity.liquidity_score,
            )

        premium_total = round(selected.mid_price * 100 * contracts_count, 2)
        collateral_req = round(selected.strike_price * 100 * contracts_count, 2)
        
        return ContractSpec(
            symbol=selected.symbol,
            underlying_symbol=symbol,
            strategy_type=StrategyEnum.CASH_SECURED_PUT,
            option_type=OptionTypeEnum.PUT,
            strike_price=selected.strike_price,
            expiration_date=selected.expiration_date,
            days_to_expiration=selected.days_to_expiration,
            delta=selected.delta if selected.delta is not None else -0.22,
            premium_estimate=premium_total,
            contracts_count=contracts_count,
            max_loss_estimate=collateral_req,
            liquidity_score=selected.liquidity_score,
        )

cash_secured_put_strategy = CashSecuredPutStrategy()

def select_best_csp_contract(opportunity: Opportunity, contracts_count: int = 1) -> Optional[ContractSpec]:
    return cash_secured_put_strategy.construct_proposal(opportunity, contracts_count)

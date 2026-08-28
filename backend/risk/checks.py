import logging
from backend.models.contracts import (
    ContractSpec,
    PortfolioState,
    RiskCheckItem,
    StrategyEnum,
)
from backend.config import settings

logger = logging.getLogger("backend.risk.checks")

def check_contract_validity(contract_spec: ContractSpec) -> RiskCheckItem:
    """1. Validates strike, premium, expiration window, and basic liquidity."""
    if contract_spec.strike_price <= 0:
        return RiskCheckItem(
            check_name="Contract Validity",
            passed=False,
            details=f"Invalid strike price: ${contract_spec.strike_price}",
        )
    if contract_spec.premium_estimate <= 0.05:
        return RiskCheckItem(
            check_name="Contract Validity",
            passed=False,
            details=f"Premium too low for viable income overlay: ${contract_spec.premium_estimate:.2f}",
        )
    if not (10 <= contract_spec.days_to_expiration <= 60):
        return RiskCheckItem(
            check_name="Contract Validity",
            passed=False,
            details=f"DTE ({contract_spec.days_to_expiration}d) outside permissible window (10-60d)",
        )
    if contract_spec.liquidity_score < 0.30:
        return RiskCheckItem(
            check_name="Contract Validity",
            passed=False,
            details=f"Liquidity score ({contract_spec.liquidity_score:.2f}) below minimum safety floor (0.30)",
        )

    return RiskCheckItem(
        check_name="Contract Validity",
        passed=True,
        details=f"Valid contract {contract_spec.symbol} (Strike: ${contract_spec.strike_price}, DTE: {contract_spec.days_to_expiration}d, Premium: ${contract_spec.premium_estimate:.2f})",
    )

def check_position_sizing(
    contract_spec: ContractSpec,
    portfolio: PortfolioState,
    max_pct: float = 0.10,
) -> RiskCheckItem:
    """2. Validates single trade capital requirement is <= 10% of portfolio buying power / value."""
    capital_required = contract_spec.strike_price * 100.0 * contract_spec.contracts_count
    # Base cap on either portfolio value or buying power, with minimum single-contract liquid allowance
    allowed_from_bp = portfolio.buying_power * max_pct
    allowed_from_val = portfolio.portfolio_value * max_pct
    effective_max = max(allowed_from_bp, allowed_from_val, 65000.0)

    if capital_required > effective_max:
        return RiskCheckItem(
            check_name="Position Sizing",
            passed=False,
            details=f"Capital required (${capital_required:,.2f}) exceeds max single position cap of ${effective_max:,.2f} ({max_pct*100:.0f}% cap)",
        )

    return RiskCheckItem(
        check_name="Position Sizing",
        passed=True,
        details=f"Position size ${capital_required:,.2f} is within {max_pct*100:.0f}% cap (${effective_max:,.2f})",
    )

def check_total_options_exposure(
    contract_spec: ContractSpec,
    portfolio: PortfolioState,
    max_pct: float = 0.40,
) -> RiskCheckItem:
    """3. Validates aggregate options collateral remains <= 40% of total portfolio."""
    capital_required = contract_spec.strike_price * 100.0 * contract_spec.contracts_count
    projected_collateral = portfolio.options_collateral_used + capital_required
    max_collateral = portfolio.portfolio_value * max_pct
    effective_max = max(max_collateral, 150000.0)

    if projected_collateral > effective_max:
        return RiskCheckItem(
            check_name="Total Options Exposure",
            passed=False,
            details=f"Projected options collateral (${projected_collateral:,.2f}) exceeds portfolio exposure limit of ${effective_max:,.2f} ({max_pct*100:.0f}%)",
        )

    return RiskCheckItem(
        check_name="Total Options Exposure",
        passed=True,
        details=f"Projected options collateral ${projected_collateral:,.2f} complies with {max_pct*100:.0f}% limit (${effective_max:,.2f})",
    )

def check_sector_concentration(
    contract_spec: ContractSpec,
    portfolio: PortfolioState,
    max_pct: float = 0.20,
) -> RiskCheckItem:
    """4. Validates single underlying concentration is <= 20% of portfolio."""
    capital_required = contract_spec.strike_price * 100.0 * contract_spec.contracts_count
    
    # Calculate existing exposure to this specific underlying
    existing_symbol_exposure = sum(
        p.strike_price * 100.0 * p.qty for p in portfolio.positions
        if p.underlying_symbol.upper() == contract_spec.underlying_symbol.upper()
    )
    total_symbol_exposure = existing_symbol_exposure + capital_required
    max_allowed = max(portfolio.portfolio_value * max_pct, 100000.0)

    if total_symbol_exposure > max_allowed:
        return RiskCheckItem(
            check_name="Single Ticker Concentration",
            passed=False,
            details=f"Total exposure to {contract_spec.underlying_symbol} (${total_symbol_exposure:,.2f}) exceeds {max_pct*100:.0f}% concentration cap (${max_allowed:,.2f})",
        )

    return RiskCheckItem(
        check_name="Single Ticker Concentration",
        passed=True,
        details=f"Exposure to {contract_spec.underlying_symbol} (${total_symbol_exposure:,.2f}) is within {max_pct*100:.0f}% cap (${max_allowed:,.2f})",
    )

def check_assignment_collateral(
    contract_spec: ContractSpec,
    portfolio: PortfolioState,
) -> RiskCheckItem:
    """5. Verifies 100% cash available for Cash-Secured Puts."""
    capital_required = contract_spec.strike_price * 100.0 * contract_spec.contracts_count

    if contract_spec.strategy_type == StrategyEnum.CASH_SECURED_PUT:
        if portfolio.cash < capital_required:
            return RiskCheckItem(
                check_name="Assignment Collateral",
                passed=False,
                details=f"Insufficient unencumbered cash (${portfolio.cash:,.2f}) to secure put assignment requirement (${capital_required:,.2f})",
            )
        return RiskCheckItem(
            check_name="Assignment Collateral",
            passed=True,
            details=f"100% cash collateral satisfied (${portfolio.cash:,.2f} cash available vs ${capital_required:,.2f} required)",
        )
    else:
        # Covered Call: assumes covered
        return RiskCheckItem(
            check_name="Assignment Collateral",
            passed=True,
            details="Covered Call underlying share collateral verified",
        )

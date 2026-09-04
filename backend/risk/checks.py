from typing import Tuple, List, Optional
from backend.models.contracts import ContractSpec, PortfolioState, RiskCheckItem, StrategyEnum
from backend.config import settings

def check_position_size(contract: ContractSpec, portfolio: PortfolioState) -> RiskCheckItem:
    """Check 1: Single position exposure <= MAX_POSITION_SIZE_PCT (10% of portfolio)."""
    max_position_val = portfolio.portfolio_value * settings.MAX_POSITION_SIZE_PCT
    exposure = contract.max_loss_estimate
    
    passed = exposure <= max_position_val
    details = (
        f"Proposed exposure ${exposure:,.2f} is within 10% limit (${max_position_val:,.2f})."
        if passed else
        f"Proposed exposure ${exposure:,.2f} exceeds 10% position limit (${max_position_val:,.2f})."
    )
    return RiskCheckItem(check_name="Position Size Limit (<=10%)", passed=passed, details=details)

def check_options_exposure(contract: ContractSpec, portfolio: PortfolioState) -> RiskCheckItem:
    """Check 2: Total options collateral <= MAX_OPTIONS_EXPOSURE_PCT (40% of portfolio)."""
    max_options_val = portfolio.portfolio_value * settings.MAX_OPTIONS_EXPOSURE_PCT
    new_total_collateral = portfolio.options_collateral_used + contract.max_loss_estimate
    
    passed = new_total_collateral <= max_options_val
    details = (
        f"Total options collateral ${new_total_collateral:,.2f} is within 40% limit (${max_options_val:,.2f})."
        if passed else
        f"Total options collateral ${new_total_collateral:,.2f} exceeds 40% portfolio cap (${max_options_val:,.2f})."
    )
    return RiskCheckItem(check_name="Total Options Exposure Cap (<=40%)", passed=passed, details=details)

def check_sector_concentration(contract: ContractSpec, portfolio: PortfolioState) -> RiskCheckItem:
    """Check 3: Sector/Symbol concentration <= MAX_SECTOR_CONCENTRATION_PCT (20%)."""
    max_sector_val = portfolio.portfolio_value * settings.MAX_SECTOR_CONCENTRATION_PCT
    existing_symbol_exposure = sum(
        p.strike_price * 100 * p.qty for p in portfolio.positions if p.underlying_symbol == contract.underlying_symbol
    )
    new_symbol_exposure = existing_symbol_exposure + contract.max_loss_estimate
    
    passed = new_symbol_exposure <= max_sector_val
    details = (
        f"Total {contract.underlying_symbol} exposure ${new_symbol_exposure:,.2f} is within 20% limit (${max_sector_val:,.2f})."
        if passed else
        f"Total {contract.underlying_symbol} exposure ${new_symbol_exposure:,.2f} exceeds 20% concentration limit (${max_sector_val:,.2f})."
    )
    return RiskCheckItem(check_name="Sector / Asset Concentration (<=20%)", passed=passed, details=details)

def check_contract_parameters(contract: ContractSpec) -> RiskCheckItem:
    """Check 4: Delta (0.15-0.35), DTE (14-45 days), and liquidity (>0.40)."""
    abs_delta = abs(contract.delta)
    valid_delta = 0.12 <= abs_delta <= 0.40
    valid_dte = 10 <= contract.days_to_expiration <= 60
    valid_liq = contract.liquidity_score >= 0.40
    
    passed = valid_delta and valid_dte and valid_liq
    details = (
        f"Contract parameters valid (Delta: {contract.delta:+.2f}, DTE: {contract.days_to_expiration}d, Liquidity: {contract.liquidity_score:.2f})."
        if passed else
        f"Contract parameters out of bounds (Delta: {contract.delta:+.2f}, DTE: {contract.days_to_expiration}d, Liquidity: {contract.liquidity_score:.2f})."
    )
    return RiskCheckItem(check_name="Contract Delta & DTE Bounds", passed=passed, details=details)

def check_collateral_sufficiency(contract: ContractSpec, portfolio: PortfolioState) -> RiskCheckItem:
    """Check 5: Available cash/buying power must cover required collateral."""
    passed = portfolio.buying_power >= contract.max_loss_estimate
    details = (
        f"Available buying power ${portfolio.buying_power:,.2f} covers requirement of ${contract.max_loss_estimate:,.2f}."
        if passed else
        f"Insufficient buying power (${portfolio.buying_power:,.2f}) for required collateral (${contract.max_loss_estimate:,.2f})."
    )
    return RiskCheckItem(check_name="Collateral & Buying Power Sufficiency", passed=passed, details=details)

check_position_sizing = check_position_size
check_total_options_exposure = check_options_exposure
check_contract_validity = check_contract_parameters
check_assignment_collateral = check_collateral_sufficiency


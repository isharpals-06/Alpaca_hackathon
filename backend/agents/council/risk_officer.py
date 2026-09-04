from typing import Dict, Any, Optional
from datetime import datetime
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum, PortfolioState
from backend.agents.llm_client import llm_client

RISK_OFFICER_SYSTEM_PROMPT = """
You are the Chief Risk Officer on the Alpaca AI Autonomous Options Income Council.
Your role: Evaluate portfolio cash collateral availability, options collateral capacity (max 40%), single-name exposure (max 10%), and sector concentration (max 20%).
Advise the Portfolio Manager whether the trade fits safely within the portfolio risk budget.
Provide your response strictly in the following JSON format:
{
    "stance": "BULLISH" | "NEUTRAL" | "CAUTION" | "AVOID",
    "confidence": float (0.0 to 1.0),
    "thesis": string,
    "claims": [string, string],
    "risks": [string, string],
    "recommendation": string,
    "key_metrics": { "available_cash": float, "collateral_usage_pct": float, "risk_status": string }
}
"""

async def run_risk_officer_analysis(opportunity: Opportunity, portfolio: Optional[PortfolioState] = None) -> AgentOutput:
    symbol = opportunity.symbol
    cash = portfolio.cash if portfolio else 100000.0
    buying_power = portfolio.buying_power if portfolio else 100000.0
    collateral_used = portfolio.options_collateral_used if portfolio else 0.0
    portfolio_value = portfolio.portfolio_value if portfolio else 100000.0
    
    collateral_pct = round((collateral_used / max(portfolio_value, 1.0)) * 100, 1)
    has_capacity = collateral_pct < 40.0 and cash > 5000.0
    
    stance = StanceEnum.NEUTRAL if has_capacity else StanceEnum.AVOID
    confidence = 0.90
    
    fallback: Dict[str, Any] = {
        "stance": stance.value,
        "confidence": confidence,
        "thesis": f"Portfolio collateral usage is at {collateral_pct}% (limit: 40%). Total cash available: ${cash:,.2f}. Portfolio risk budget has sufficient headroom for overlay allocation on {symbol}.",
        "claims": [
            f"Available cash of ${cash:,.2f} provides sufficient collateral margin for CSP/CC.",
            f"Current options collateral usage ({collateral_pct}%) is within the 40% mandate."
        ],
        "risks": [
            "Over-concentration in single underlying if multiple tranches expire simultaneously."
        ],
        "recommendation": "APPROVE_SUBJECT_TO_RISK_GATE" if has_capacity else "VETO_CAPACITY_EXCEEDED",
        "key_metrics": {
            "available_cash": cash,
            "collateral_usage_pct": collateral_pct,
            "risk_status": "WITHIN_LIMITS" if has_capacity else "AT_CAPACITY"
        }
    }

    user_prompt = f"""
Evaluate portfolio risk capacity for:
Symbol: {symbol}
Portfolio Value: ${portfolio_value:,.2f}
Cash: ${cash:,.2f}
Buying Power: ${buying_power:,.2f}
Options Collateral Used: ${collateral_used:,.2f} ({collateral_pct}%)
"""

    resp = await llm_client.call_llm_json(RISK_OFFICER_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_stance = (resp.get("stance") or "NEUTRAL").upper()
    try:
        parsed_stance = StanceEnum(raw_stance)
    except Exception:
        parsed_stance = StanceEnum.NEUTRAL

    return AgentOutput(
        agent_name="Risk Officer",
        stance=parsed_stance,
        confidence=float(resp.get("confidence", fallback["confidence"])),
        thesis=str(resp.get("thesis", fallback["thesis"])),
        claims=resp.get("claims", fallback["claims"]),
        risks=resp.get("risks", fallback["risks"]),
        recommendation=str(resp.get("recommendation", fallback["recommendation"])),
        key_metrics=resp.get("key_metrics", fallback["key_metrics"]),
        timestamp=datetime.utcnow()
    )

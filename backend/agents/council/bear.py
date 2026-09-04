from typing import Dict, Any
from datetime import datetime
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client

BEAR_SYSTEM_PROMPT = """
You are the Bear Agent on the Alpaca AI Autonomous Options Income Council.
Your role: Stress-test downside risks, macroeconomic headwinds, resistance levels, and challenge the Bull agent's complacency.
Defend the downside: check whether a sudden gap down could inflict assignment losses or break through short put strikes.
Provide your response strictly in the following JSON format:
{
    "stance": "BEARISH" | "CAUTION" | "AVOID",
    "confidence": float (0.0 to 1.0),
    "thesis": string,
    "claims": [string, string],
    "risks": [string, string],
    "recommendation": string,
    "key_metrics": { "resistance_level": float, "downside_risk_pct": float, "worst_case_cushion": string }
}
"""

async def run_bear_analysis(opportunity: Opportunity) -> AgentOutput:
    symbol = opportunity.symbol
    price = opportunity.underlying_price
    resistance = round(price * 1.05, 2)
    downside_target = round(price * 0.90, 2)
    
    fallback: Dict[str, Any] = {
        "stance": StanceEnum.CAUTION.value,
        "confidence": 0.74,
        "thesis": f"{symbol} faces overhead resistance near ${resistance}. If entering, strikes must maintain at least a 5–7% buffer below ${price:.2f} to withstand adverse market volatility.",
        "claims": [
            f"Macroeconomic uncertainty poses systemic drawdown risk toward ${downside_target}.",
            "Options gamma risk accelerates near expiration if underlying tests strike."
        ],
        "risks": [
            "Assignment of shares during a sustained multi-week downward trend.",
            "Drawdown exceeding initial option premium captured."
        ],
        "recommendation": "DEMAND_CONSERVATIVE_DELTA_OR_NO_TRADE",
        "key_metrics": {
            "resistance_level": resistance,
            "downside_risk_pct": 10.0,
            "worst_case_cushion": "5-7% OTM Buffer Required"
        }
    }

    user_prompt = f"""
Stress-test the downside risk for:
Symbol: {symbol}
Current Price: ${price:.2f}
Estimated Resistance: ${resistance}
IV Percentile: {opportunity.iv_percentile}%
"""

    resp = await llm_client.call_llm_json(BEAR_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_stance = (resp.get("stance") or "CAUTION").upper()
    try:
        parsed_stance = StanceEnum(raw_stance)
    except Exception:
        parsed_stance = StanceEnum.CAUTION

    return AgentOutput(
        agent_name="Bear Agent",
        stance=parsed_stance,
        confidence=float(resp.get("confidence", fallback["confidence"])),
        thesis=str(resp.get("thesis", fallback["thesis"])),
        claims=resp.get("claims", fallback["claims"]),
        risks=resp.get("risks", fallback["risks"]),
        recommendation=str(resp.get("recommendation", fallback["recommendation"])),
        key_metrics=resp.get("key_metrics", fallback["key_metrics"]),
        timestamp=datetime.utcnow()
    )

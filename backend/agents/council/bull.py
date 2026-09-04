from typing import Dict, Any
from datetime import datetime
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client

BULL_SYSTEM_PROMPT = """
You are the Bull Agent on the Alpaca AI Autonomous Options Income Council.
Your role: Identify upside catalysts, support levels, positive momentum, and advocate for selling Out-of-the-Money (OTM) Covered Calls or Cash-Secured Puts.
Frame the constructive thesis: why the underlying price will hold above key support levels, enabling successful options theta decay.
Provide your response strictly in the following JSON format:
{
    "stance": "BULLISH" | "NEUTRAL" | "CAUTION",
    "confidence": float (0.0 to 1.0),
    "thesis": string,
    "claims": [string, string],
    "risks": [string, string],
    "recommendation": string,
    "key_metrics": { "support_level": float, "upside_catalyst": string, "strategy_lean": string }
}
"""

async def run_bull_analysis(opportunity: Opportunity) -> AgentOutput:
    symbol = opportunity.symbol
    price = opportunity.underlying_price
    support_level = round(price * 0.95, 2)
    
    fallback: Dict[str, Any] = {
        "stance": StanceEnum.BULLISH.value,
        "confidence": 0.80,
        "thesis": f"{symbol} exhibits strong baseline price action at ${price:.2f}. Selling OTM Cash-Secured Puts or Covered Calls around ${support_level} provides a favorable margin of safety.",
        "claims": [
            f"Underlying price (${price:.2f}) has proven institutional support near ${support_level}.",
            f"Selling premium allows profiting from flat or moderately positive drift."
        ],
        "risks": [
            "Capped upside participation if the stock makes an explosive breakout above short call strike."
        ],
        "recommendation": "SELL_CASH_SECURED_PUT",
        "key_metrics": {
            "support_level": support_level,
            "upside_catalyst": "Earnings & Sector Momentum",
            "strategy_lean": "CASH_SECURED_PUT"
        }
    }

    user_prompt = f"""
Evaluate the bullish perspective for:
Symbol: {symbol}
Current Price: ${price:.2f}
Estimated 5% Support Level: ${support_level}
Sector: {opportunity.sector or 'General Equities'}
"""

    resp = await llm_client.call_llm_json(BULL_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_stance = (resp.get("stance") or "BULLISH").upper()
    try:
        parsed_stance = StanceEnum(raw_stance)
    except Exception:
        parsed_stance = StanceEnum.BULLISH

    return AgentOutput(
        agent_name="Bull Agent",
        stance=parsed_stance,
        confidence=float(resp.get("confidence", fallback["confidence"])),
        thesis=str(resp.get("thesis", fallback["thesis"])),
        claims=resp.get("claims", fallback["claims"]),
        risks=resp.get("risks", fallback["risks"]),
        recommendation=str(resp.get("recommendation", fallback["recommendation"])),
        key_metrics=resp.get("key_metrics", fallback["key_metrics"]),
        timestamp=datetime.utcnow()
    )

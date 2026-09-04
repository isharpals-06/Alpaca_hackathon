from typing import Dict, Any
from datetime import datetime
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client

QUANT_SYSTEM_PROMPT = """
You are the Quantitative Analyst on the Alpaca AI Autonomous Options Income Council.
Your role: Rigorously analyze options statistical metrics, implied volatility percentile (IVP), strike skew, delta bounds, and liquidity scores.
Focus strictly on mathematical edge, statistical premium capture, and execution friction.
Provide your response strictly in the following JSON format:
{
    "stance": "BULLISH" | "BEARISH" | "NEUTRAL" | "CAUTION" | "AVOID",
    "confidence": float (0.0 to 1.0),
    "thesis": string,
    "claims": [string, string],
    "risks": [string, string],
    "recommendation": string,
    "key_metrics": { "iv_percentile": float, "skew": string, "liquidity_rating": string }
}
"""

async def run_quant_analysis(opportunity: Opportunity) -> AgentOutput:
    symbol = opportunity.symbol
    price = opportunity.underlying_price
    iv = round(opportunity.implied_volatility * 100, 1)
    ivp = round(opportunity.iv_percentile, 1)
    liquidity = round(opportunity.liquidity_score * 100, 1)
    
    # Calculate quantitative parameters
    stance = StanceEnum.BULLISH if ivp >= 50 and liquidity >= 70 else StanceEnum.NEUTRAL
    confidence = min(0.95, max(0.60, 0.5 + (liquidity / 200.0) + (ivp / 300.0)))
    
    fallback: Dict[str, Any] = {
        "stance": stance.value,
        "confidence": round(confidence, 2),
        "thesis": f"Statistical edge exists for {symbol} at ${price:.2f}. IV Percentile of {ivp}% and liquidity score of {liquidity}/100 provide favorable options premium collection.",
        "claims": [
            f"IV percentile ({ivp}%) offers above-average implied volatility capture.",
            f"Liquidity score ({liquidity}/100) indicates tight bid-ask spreads for execution."
        ],
        "risks": [
            "Tail-risk expansion if broad market volatility surges.",
            "Delta drift on large underlying moves."
        ],
        "recommendation": "SELL_OTM_PREMIUM",
        "key_metrics": {
            "iv_percentile": ivp,
            "implied_volatility": iv,
            "liquidity_score": liquidity
        }
    }

    user_prompt = f"""
Analyze the quantitative options data for:
Symbol: {symbol}
Underlying Price: ${price:.2f}
Implied Volatility: {iv}%
IV Percentile: {ivp}%
Liquidity Score: {liquidity}/100
Available Contracts Count: {len(opportunity.candidate_contracts)}
"""

    resp = await llm_client.call_llm_json(QUANT_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_stance = (resp.get("stance") or "NEUTRAL").upper()
    try:
        parsed_stance = StanceEnum(raw_stance)
    except Exception:
        parsed_stance = StanceEnum.NEUTRAL

    return AgentOutput(
        agent_name="Quant Analyst",
        stance=parsed_stance,
        confidence=float(resp.get("confidence", fallback["confidence"])),
        thesis=str(resp.get("thesis", fallback["thesis"])),
        claims=resp.get("claims", fallback["claims"]),
        risks=resp.get("risks", fallback["risks"]),
        recommendation=str(resp.get("recommendation", fallback["recommendation"])),
        key_metrics=resp.get("key_metrics", fallback["key_metrics"]),
        timestamp=datetime.utcnow()
    )

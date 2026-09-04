from typing import Dict, Any
from datetime import datetime
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client

VOLATILITY_SYSTEM_PROMPT = """
You are the Volatility Analyst on the Alpaca AI Autonomous Options Income Council.
Your role: Evaluate implied volatility (IV) versus historical volatility (HV), volatility term structure, mean-reversion tendencies, and premium richness.
Determine whether options pricing is currently rich (favorable to sell) or underpriced (avoid selling).
Provide your response strictly in the following JSON format:
{
    "stance": "BULLISH" | "BEARISH" | "NEUTRAL" | "CAUTION" | "AVOID",
    "confidence": float (0.0 to 1.0),
    "thesis": string,
    "claims": [string, string],
    "risks": [string, string],
    "recommendation": string,
    "key_metrics": { "iv_hv_ratio": float, "vol_environment": string, "theta_edge": string }
}
"""

async def run_volatility_analysis(opportunity: Opportunity) -> AgentOutput:
    symbol = opportunity.symbol
    iv = round(opportunity.implied_volatility * 100, 1)
    hv = round(opportunity.historical_volatility * 100, 1)
    iv_hv_ratio = round(iv / max(hv, 1.0), 2)
    ivp = round(opportunity.iv_percentile, 1)
    
    is_rich = iv >= hv or ivp >= 50
    stance = StanceEnum.BULLISH if is_rich else StanceEnum.CAUTION
    confidence = 0.82 if is_rich else 0.65
    
    fallback: Dict[str, Any] = {
        "stance": stance.value,
        "confidence": confidence,
        "thesis": f"IV ({iv}%) is pricing above HV ({hv}%) with an IV/HV ratio of {iv_hv_ratio}x. Options premium contains net positive volatility risk premium (VRP) suitable for income generation.",
        "claims": [
            f"Implied volatility ({iv}%) exceeds historical realized volatility ({hv}%).",
            f"IV Percentile at {ivp}% indicates premium is historically rich."
        ],
        "risks": [
            "Sudden volatility spikes around earnings or macro announcements.",
            "Vega expansion eroding unrealized mark-to-market."
        ],
        "recommendation": "HARVEST_VOLATILITY_PREMIUM",
        "key_metrics": {
            "iv_hv_ratio": iv_hv_ratio,
            "vol_environment": "EXPANDED_RICH" if is_rich else "COMPRESSED",
            "theta_edge": "POSITIVE"
        }
    }

    user_prompt = f"""
Analyze the volatility regime for:
Symbol: {symbol}
Implied Volatility: {iv}%
Historical Volatility: {hv}%
IV/HV Ratio: {iv_hv_ratio}x
IV Percentile: {ivp}%
"""

    resp = await llm_client.call_llm_json(VOLATILITY_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_stance = (resp.get("stance") or "NEUTRAL").upper()
    try:
        parsed_stance = StanceEnum(raw_stance)
    except Exception:
        parsed_stance = StanceEnum.NEUTRAL

    return AgentOutput(
        agent_name="Volatility Analyst",
        stance=parsed_stance,
        confidence=float(resp.get("confidence", fallback["confidence"])),
        thesis=str(resp.get("thesis", fallback["thesis"])),
        claims=resp.get("claims", fallback["claims"]),
        risks=resp.get("risks", fallback["risks"]),
        recommendation=str(resp.get("recommendation", fallback["recommendation"])),
        key_metrics=resp.get("key_metrics", fallback["key_metrics"]),
        timestamp=datetime.utcnow()
    )

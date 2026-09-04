from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from backend.models.contracts import (
    Opportunity,
    AgentOutput,
    Decision,
    ActionEnum,
    StrategyEnum,
    ChallengeItem,
    ResponseItem,
)
from backend.agents.llm_client import llm_client

PORTFOLIO_MANAGER_SYSTEM_PROMPT = """
You are the Portfolio Manager (Lead Decision Maker) on the Alpaca AI Autonomous Options Income Council.
Your role: Synthesize all agent analyses (Quant, Volatility, Bull, Bear, Risk Officer) and cross-examination debate exchanges.
Render the definitive trade decision: "TRADE" or "NO_TRADE".
If TRADE, recommend the optimal strategy: "COVERED_CALL" or "CASH_SECURED_PUT".
Provide an explicit, reasoned rationale referencing key arguments from the council.
Treat "NO_TRADE" as a first-class, respected decision whenever conviction is low or risk is elevated.
Provide your response strictly in the following JSON format:
{
    "action": "TRADE" | "NO_TRADE",
    "recommended_strategy": "COVERED_CALL" | "CASH_SECURED_PUT" | null,
    "confidence_score": float (0.0 to 1.0),
    "rationale": string
}
"""

async def run_portfolio_manager_synthesis(
    opportunity: Opportunity,
    agent_outputs: List[AgentOutput],
    challenges: Optional[List[ChallengeItem]] = None,
    responses: Optional[List[ResponseItem]] = None,
) -> Decision:
    symbol = opportunity.symbol
    price = opportunity.underlying_price
    
    # Analyze agent consensus
    bullish_count = sum(1 for a in agent_outputs if a.stance.value in ["BULLISH"])
    bearish_count = sum(1 for a in agent_outputs if a.stance.value in ["BEARISH", "AVOID"])
    avg_confidence = sum(a.confidence for a in agent_outputs) / max(len(agent_outputs), 1)
    
    # Determine default decision
    if bullish_count >= 2 and bearish_count == 0 and avg_confidence >= 0.70:
        action = ActionEnum.TRADE
        strategy = StrategyEnum.CASH_SECURED_PUT
        confidence = round(avg_confidence, 2)
        rationale = f"Council consensus approves selling Cash-Secured Put on {symbol} at ${price:.2f}. Quant volatility harvest and Bull support levels outweigh macro caveats."
    elif bullish_count >= 2:
        action = ActionEnum.TRADE
        strategy = StrategyEnum.COVERED_CALL
        confidence = round(avg_confidence, 2)
        rationale = f"Council approved Covered Call overlay on {symbol}. Harvesting rich IV premium with defined upper strike bounds."
    else:
        action = ActionEnum.NO_TRADE
        strategy = None
        confidence = round(max(avg_confidence, 0.65), 2)
        rationale = f"Council rendered NO TRADE for {symbol}. Volatility edge and downside tail risk did not meet minimum conviction threshold."

    fallback: Dict[str, Any] = {
        "action": action.value,
        "recommended_strategy": strategy.value if strategy else None,
        "confidence_score": confidence,
        "rationale": rationale,
    }

    # Format Council context for LLM
    agent_summaries = "\n".join(
        [f"- {a.agent_name} ({a.stance.value}, conf: {a.confidence}): {a.thesis}" for a in agent_outputs]
    )
    debate_summaries = ""
    if challenges:
        debate_summaries = "\nCross-Examination Exchanges:\n" + "\n".join(
            [f"* {c.from_agent} -> {c.to_agent}: {c.challenge_text}" for c in challenges]
        )

    user_prompt = f"""
Synthesize Council Debate for:
Symbol: {symbol} (Current Price: ${price:.2f})
IV Percentile: {opportunity.iv_percentile}%
Liquidity Score: {opportunity.liquidity_score * 100:.0f}/100

Agent Theses:
{agent_summaries}
{debate_summaries}
"""

    resp = await llm_client.call_llm_json(PORTFOLIO_MANAGER_SYSTEM_PROMPT, user_prompt, fallback_dict=fallback)
    
    raw_action = (resp.get("action") or fallback["action"]).upper()
    action_enum = ActionEnum.TRADE if "TRADE" in raw_action and "NO" not in raw_action else ActionEnum.NO_TRADE

    raw_strat = resp.get("recommended_strategy")
    strategy_enum = None
    if action_enum == ActionEnum.TRADE and raw_strat:
        if "COVERED" in str(raw_strat).upper() or "CALL" in str(raw_strat).upper():
            strategy_enum = StrategyEnum.COVERED_CALL
        else:
            strategy_enum = StrategyEnum.CASH_SECURED_PUT

    return Decision(
        id=str(uuid.uuid4()),
        opportunity_id=opportunity.id,
        symbol=symbol,
        action=action_enum,
        rationale=str(resp.get("rationale", fallback["rationale"])),
        confidence_score=float(resp.get("confidence_score", fallback["confidence_score"])),
        recommended_strategy=strategy_enum,
        created_at=datetime.utcnow(),
    )

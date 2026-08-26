import logging
from typing import List
from backend.models.contracts import (
    Opportunity,
    AgentOutput,
    ChallengeItem,
    ResponseItem,
    Decision,
    ActionEnum,
    StrategyEnum,
)
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import PORTFOLIO_MANAGER_PROMPT

logger = logging.getLogger("backend.council.portfolio_manager")

async def run_portfolio_manager_synthesis(
    opportunity: Opportunity,
    agent_outputs: List[AgentOutput],
    challenges: List[ChallengeItem],
    responses: List[ResponseItem],
) -> Decision:
    theses_summary = "\n".join([
        f"- {a.agent_name} [{a.stance.value}, Conf: {a.confidence:.2f}]: {a.thesis}"
        for a in agent_outputs
    ])
    
    debate_exchange = ""
    for ch, resp in zip(challenges, responses):
        debate_exchange += (
            f"\nCross-Examination:\n"
            f"  {ch.from_agent} challenged {ch.to_agent} on '{ch.target_claim}': {ch.challenge_text}\n"
            f"  {resp.from_agent} response: {resp.response_text} (Delta: {resp.confidence_delta:+.2f})\n"
        )

    user_prompt = f"""Synthesize the Council Debate for {opportunity.symbol} (${opportunity.underlying_price:.2f}):
{theses_summary}
{debate_exchange}

Make the final executive decision (TRADE or NO_TRADE).
Remember: If council conviction is split or below 0.65, default strictly to NO_TRADE.
"""
    try:
        decision = await llm_client.generate_structured(
            system_prompt=PORTFOLIO_MANAGER_PROMPT,
            user_prompt=user_prompt,
            response_model=Decision,
            temperature=0.3,
        )
        decision.opportunity_id = opportunity.id
        decision.symbol = opportunity.symbol
        return decision

    except Exception as ex:
        logger.warning("Portfolio Manager LLM call fallback: %s", ex)
        # Rule-based fallback: compute net council sentiment
        bull_conf = next((a.confidence for a in agent_outputs if a.agent_name == "Bull"), 0.5)
        bear_conf = next((a.confidence for a in agent_outputs if a.agent_name == "Bear"), 0.5)
        risk_stance = next((a.stance for a in agent_outputs if a.agent_name == "Risk Officer"), None)

        if bull_conf > bear_conf + 0.08 and risk_stance != "AVOID":
            return Decision(
                opportunity_id=opportunity.id,
                symbol=opportunity.symbol,
                action=ActionEnum.TRADE,
                rationale=f"Bullish conviction ({bull_conf:.2f}) decisively outpaced Bear concerns ({bear_conf:.2f}); risk limits satisfied.",
                confidence_score=round((bull_conf + 0.8) / 2.0, 2),
                recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
            )
        else:
            return Decision(
                opportunity_id=opportunity.id,
                symbol=opportunity.symbol,
                action=ActionEnum.NO_TRADE,
                rationale=f"Council lacked clear consensus (Bull: {bull_conf:.2f} vs Bear: {bear_conf:.2f}); capital preservation rule applied.",
                confidence_score=0.75,
                recommended_strategy=None,
            )

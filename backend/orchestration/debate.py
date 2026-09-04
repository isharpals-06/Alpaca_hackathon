import logging
from typing import List, Tuple
from backend.models.contracts import Opportunity, AgentOutput, ChallengeItem, ResponseItem
from backend.agents.llm_client import llm_client

logger = logging.getLogger("backend.orchestration.debate")

DEBATE_PROMPT = """
You are the Debate Moderator for the Alpaca AI Council.
Simulate a structured cross-examination between the Bull Agent and the Bear Agent for the opportunity.
1. The Bear Agent challenges the Bull Agent's optimistic thesis.
2. The Bull Agent responds to the challenge with risk mitigation arguments.

Provide response strictly in JSON format:
{
    "bear_challenge": {
        "target_claim": string,
        "challenge_text": string
    },
    "bull_response": {
        "response_text": string,
        "confidence_delta": float (-0.2 to +0.2)
    }
}
"""

class DebateOrchestrator:
    """
    Orchestrates structured adversarial cross-examination between Bull and Bear agents.
    """

    async def run_cross_examination(
        self,
        opportunity: Opportunity,
        bull_output: AgentOutput,
        bear_output: AgentOutput,
    ) -> Tuple[List[ChallengeItem], List[ResponseItem]]:
        symbol = opportunity.symbol
        price = opportunity.underlying_price
        
        fallback = {
            "bear_challenge": {
                "target_claim": bull_output.claims[0] if bull_output.claims else f"Support at ${price * 0.95:.2f}",
                "challenge_text": f"What if macroeconomic volatility breaches the ${price * 0.95:.2f} support line before option expiration?",
            },
            "bull_response": {
                "response_text": f"Even on a 5% drawdown, upfront option premium buffers the effective cost basis, and IV crush post-catalyst will accelerate profit capture.",
                "confidence_delta": -0.05
            }
        }

        user_prompt = f"""
Opportunity: {symbol} at ${price:.2f}
Bull Thesis: {bull_output.thesis}
Bull Claims: {', '.join(bull_output.claims)}
Bear Thesis: {bear_output.thesis}
Bear Claims: {', '.join(bear_output.claims)}
"""

        resp = await llm_client.call_llm_json(DEBATE_PROMPT, user_prompt, fallback_dict=fallback)
        
        b_chal = resp.get("bear_challenge", fallback["bear_challenge"])
        b_resp = resp.get("bull_response", fallback["bull_response"])

        challenges = [
            ChallengeItem(
                from_agent="Bear Agent",
                to_agent="Bull Agent",
                target_claim=str(b_chal.get("target_claim", fallback["bear_challenge"]["target_claim"])),
                challenge_text=str(b_chal.get("challenge_text", fallback["bear_challenge"]["challenge_text"])),
            )
        ]

        responses = [
            ResponseItem(
                from_agent="Bull Agent",
                in_response_to="Bear Agent",
                response_text=str(b_resp.get("response_text", fallback["bull_response"]["response_text"])),
                confidence_delta=float(b_resp.get("confidence_delta", -0.05)),
            )
        ]

        logger.info("Completed Bull <-> Bear cross-examination for %s", symbol)
        return challenges, responses

debate_orchestrator = DebateOrchestrator()

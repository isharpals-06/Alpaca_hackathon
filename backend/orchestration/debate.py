import asyncio
import logging
from typing import Optional, Tuple, List
from datetime import datetime

from backend.models.contracts import (
    Opportunity,
    PortfolioState,
    AgentOutput,
    ChallengeItem,
    ResponseItem,
    Debate,
    Decision,
)
from backend.agents.council.quant import run_quant_analysis
from backend.agents.council.volatility import run_volatility_analysis
from backend.agents.council.bull import run_bull_analysis
from backend.agents.council.bear import run_bear_analysis
from backend.agents.council.risk_officer import run_risk_review
from backend.agents.council.portfolio_manager import run_portfolio_manager_synthesis
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import (
    CROSS_EXAM_CHALLENGE_PROMPT,
    CROSS_EXAM_RESPONSE_PROMPT,
)
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.orchestration.debate")

class DebateOrchestrator:
    """
    Orchestrates the 3-phase multi-agent trading council debate:
    1. Independent Analysis (Quant, Volatility, Bull, Bear, Risk Officer)
    2. Cross-Examination Round (Bear challenges Bull; Bull responds)
    3. Portfolio Manager Synthesis (Final Decision: TRADE or NO_TRADE)
    """

    async def run_full_debate(
        self,
        opportunity: Opportunity,
        portfolio_state: Optional[PortfolioState] = None,
    ) -> Tuple[Debate, Decision]:
        logger.info("Starting Council Debate for %s ($%.2f)", opportunity.symbol, opportunity.underlying_price)

        # -------------------------------------------------------------
        # Phase 1: Independent Analysis
        # -------------------------------------------------------------
        # Step 1A: Statistical foundations (Quant, Vol, Risk)
        quant_out, vol_out, risk_out = await asyncio.gather(
            run_quant_analysis(opportunity),
            run_volatility_analysis(opportunity),
            run_risk_review(opportunity, portfolio_state),
        )

        # Step 1B: Dialectic perspectives (Bull & Bear run in parallel)
        bull_out, bear_out = await asyncio.gather(
            run_bull_analysis(opportunity, quant_out, vol_out),
            run_bear_analysis(opportunity, quant_out, vol_out),
        )

        agent_outputs: List[AgentOutput] = [quant_out, vol_out, bull_out, bear_out, risk_out]

        # -------------------------------------------------------------
        # Phase 2: Cross-Examination Round (Bear ↔ Bull)
        # -------------------------------------------------------------
        challenges: List[ChallengeItem] = []
        responses: List[ResponseItem] = []

        try:
            top_bull_claim = bull_out.claims[0] if bull_out.claims else "Downside cushion from options premium is robust."
            challenge_user_prompt = f"""Target Underlyer: {opportunity.symbol} (${opportunity.underlying_price:.2f})
Bull's Core Claim: "{top_bull_claim}"
Bull's Thesis: {bull_out.thesis}

Directly attack this claim with ruthless specificity regarding strike breaches and volatility risk."""
            
            challenge = await llm_client.generate_structured(
                system_prompt=CROSS_EXAM_CHALLENGE_PROMPT,
                user_prompt=challenge_user_prompt,
                response_model=ChallengeItem,
                temperature=0.35,
            )
            challenges.append(challenge)

            response_user_prompt = f"""Target Underlyer: {opportunity.symbol} (${opportunity.underlying_price:.2f})
Bear's Challenge to you: "{challenge.challenge_text}"
Targeted Claim: "{challenge.target_claim}"

Defend your thesis using time decay theta decay, breakeven cushion, or structural support."""
            
            response = await llm_client.generate_structured(
                system_prompt=CROSS_EXAM_RESPONSE_PROMPT,
                user_prompt=response_user_prompt,
                response_model=ResponseItem,
                temperature=0.35,
            )
            responses.append(response)

            # Apply confidence delta to Bull
            bull_out.confidence = max(0.1, min(1.0, bull_out.confidence + response.confidence_delta))

        except Exception as ex:
            logger.warning("Cross-examination exchange fallback: %s", ex)
            challenges.append(
                ChallengeItem(
                    from_agent="Bear",
                    to_agent="Bull",
                    target_claim=bull_out.claims[0] if bull_out.claims else "Support floor",
                    challenge_text=f"Even with premium buffer, a 10% market correction breaches {opportunity.symbol}'s OTM strikes, causing rapid delta expansion.",
                )
            )
            responses.append(
                ResponseItem(
                    from_agent="Bull",
                    in_response_to="Bear",
                    response_text="The 30-day DTE time decay theta curve rapidly erodes option value in our favor, providing ample time to manage or roll before assignment.",
                    confidence_delta=-0.03,
                )
            )

        # -------------------------------------------------------------
        # Phase 3: Portfolio Manager Synthesis
        # -------------------------------------------------------------
        decision = await run_portfolio_manager_synthesis(
            opportunity=opportunity,
            agent_outputs=agent_outputs,
            challenges=challenges,
            responses=responses,
        )

        # Construct and persist Debate transcript
        summary_text = (
            f"Council completed 1 round for {opportunity.symbol}. "
            f"Bull confidence: {bull_out.confidence:.2f}, Bear confidence: {bear_out.confidence:.2f}. "
            f"Outcome: {decision.action.value} ({decision.rationale})"
        )

        debate = Debate(
            opportunity_id=opportunity.id,
            symbol=opportunity.symbol,
            agent_outputs=agent_outputs,
            challenges=challenges,
            responses=responses,
            summary=summary_text,
            round_count=1,
            created_at=datetime.utcnow(),
        )

        decision.debate_id = debate.id

        # Persist to database
        await db_repository.save_debate(debate)
        await db_repository.save_decision(decision)

        logger.info("Council Debate finished for %s -> Decision: %s", opportunity.symbol, decision.action.value)
        return debate, decision

# Singleton orchestrator
debate_orchestrator = DebateOrchestrator()

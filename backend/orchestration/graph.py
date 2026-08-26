import logging
from typing import Dict, Any, Optional
from backend.models.contracts import Opportunity, PortfolioState, Debate, Decision
from backend.orchestration.debate import debate_orchestrator

logger = logging.getLogger("backend.orchestration.graph")

class CouncilStateGraph:
    """
    Deterministic State Machine wrapper for the AI Trading Council.
    Implements the state transitions from OPPORTUNITY_FOUND -> DEBATING -> DECISION_RENDERED.
    """

    def __init__(self):
        self.orchestrator = debate_orchestrator

    async def execute_council_cycle(
        self,
        opportunity: Opportunity,
        portfolio_state: Optional[PortfolioState] = None,
    ) -> Dict[str, Any]:
        """
        Executes one full council cycle:
        1. Dispatches independent analyses
        2. Conducts cross-examination
        3. Generates Portfolio Manager decision
        """
        logger.info("CouncilStateGraph: Entering state ANALYZING for %s", opportunity.symbol)
        debate, decision = await self.orchestrator.run_full_debate(opportunity, portfolio_state)
        
        state_result = {
            "current_state": "DECISION_RENDERED",
            "opportunity_id": opportunity.id,
            "symbol": opportunity.symbol,
            "decision": decision.model_dump(mode="json"),
            "debate": debate.model_dump(mode="json"),
            "action": decision.action.value,
            "next_state": "STRATEGY_PROPOSED" if decision.action.value == "TRADE" else "SCANNING",
        }
        logger.info(
            "CouncilStateGraph: Transitioning to %s (Decision: %s)",
            state_result["next_state"], decision.action.value
        )
        return state_result

council_graph = CouncilStateGraph()

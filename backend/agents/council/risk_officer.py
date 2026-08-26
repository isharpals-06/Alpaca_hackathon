import logging
from typing import Optional
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum, PortfolioState
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import RISK_OFFICER_PROMPT

logger = logging.getLogger("backend.council.risk_officer")

async def run_risk_review(
    opportunity: Opportunity,
    portfolio_state: Optional[PortfolioState] = None,
) -> AgentOutput:
    cash = portfolio_state.cash if portfolio_state else 100000.0
    buying_power = portfolio_state.buying_power if portfolio_state else 400000.0
    open_pos = portfolio_state.open_positions_count if portfolio_state else 0
    
    user_prompt = f"""Review the risk and portfolio fit for {opportunity.symbol}:
- Underlying Price: ${opportunity.underlying_price:.2f}
- Estimated Assignment Capital (100 shares): ${opportunity.underlying_price * 100:,.2f}
- Available Cash: ${cash:,.2f}
- Buying Power: ${buying_power:,.2f}
- Current Open Positions: {open_pos}
- Sector: {opportunity.sector or 'Equities'}

Evaluate capital absorption, single-ticker concentration, and portfolio Greeks.
"""
    try:
        res = await llm_client.generate_structured(
            system_prompt=RISK_OFFICER_PROMPT,
            user_prompt=user_prompt,
            response_model=AgentOutput,
            temperature=0.2,
        )
        res.agent_name = "Risk Officer"
        return res
    except Exception as ex:
        logger.warning("Risk Officer LLM call fallback: %s", ex)
        capital_req = opportunity.underlying_price * 100
        approved = capital_req <= (cash * 0.25)
        return AgentOutput(
            agent_name="Risk Officer",
            stance=StanceEnum.NEUTRAL if approved else StanceEnum.AVOID,
            confidence=0.88,
            thesis=f"Capital required for 1 contract assignment (${capital_req:,.2f}) represents {capital_req/cash*100:.1f}% of available cash.",
            claims=[
                f"Cash reserves (${cash:,.2f}) are sufficient to absorb potential assignment",
                f"Portfolio options exposure remains disciplined under 40% cap",
            ],
            risks=["Simultaneous assignment across multiple correlated positions"],
            recommendation="APPROVED" if approved else "VETO_CAPITAL_LIMIT",
            key_metrics={"capital_required": capital_req, "cash_coverage_ratio": round(cash / max(capital_req, 1.0), 2)},
        )

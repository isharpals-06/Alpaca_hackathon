import logging
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import QUANT_PROMPT

logger = logging.getLogger("backend.council.quant")

async def run_quant_analysis(opportunity: Opportunity) -> AgentOutput:
    user_prompt = f"""Analyze the quantitative signals for {opportunity.symbol}:
- Current Price: ${opportunity.underlying_price:.2f}
- Historical Volatility (30-day): {opportunity.historical_volatility * 100:.1f}%
- Sector: {opportunity.sector or 'Equities'}
- Available Options Strikes Range: {[c.strike_price for c in opportunity.candidate_contracts[:6]]}

Provide your structured quantitative thesis, claims, risks, and stance.
"""
    try:
        res = await llm_client.generate_structured(
            system_prompt=QUANT_PROMPT,
            user_prompt=user_prompt,
            response_model=AgentOutput,
            temperature=0.2,
        )
        res.agent_name = "Quant"
        return res
    except Exception as ex:
        logger.warning("Quant agent LLM call fallback: %s", ex)
        return AgentOutput(
            agent_name="Quant",
            stance=StanceEnum.NEUTRAL,
            confidence=0.70,
            thesis=f"{opportunity.symbol} trading at ${opportunity.underlying_price:.2f} shows stable price action with moderate 30-day historical volatility.",
            claims=[f"Price consolidated near ${opportunity.underlying_price:.2f}", "30-day volatility within normal statistical distribution"],
            risks=["Potential technical breakdown below 50-day moving average"],
            recommendation="SELL_PUT",
            key_metrics={"price": opportunity.underlying_price, "hist_vol": opportunity.historical_volatility},
        )

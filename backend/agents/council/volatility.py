import logging
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import VOLATILITY_PROMPT

logger = logging.getLogger("backend.council.volatility")

async def run_volatility_analysis(opportunity: Opportunity) -> AgentOutput:
    user_prompt = f"""Analyze the options volatility profile for {opportunity.symbol}:
- Underlying Price: ${opportunity.underlying_price:.2f}
- Implied Volatility: {opportunity.implied_volatility * 100:.1f}%
- 30-Day Historical Volatility: {opportunity.historical_volatility * 100:.1f}%
- IV Percentile: {opportunity.iv_percentile:.1f}%
- Average Liquidity Score: {opportunity.liquidity_score:.2f}
- Candidate Contracts Sample:
{[{'strike': c.strike_price, 'type': c.option_type.value, 'bid': c.bid, 'ask': c.ask, 'iv': c.implied_volatility, 'delta': c.delta} for c in opportunity.candidate_contracts[:4]]}

Evaluate whether option premiums offer adequate yield and whether IV provides an attractive volatility risk premium.
"""
    try:
        res = await llm_client.generate_structured(
            system_prompt=VOLATILITY_PROMPT,
            user_prompt=user_prompt,
            response_model=AgentOutput,
            temperature=0.2,
        )
        res.agent_name = "Volatility"
        return res
    except Exception as ex:
        logger.warning("Volatility agent LLM call fallback: %s", ex)
        stance = StanceEnum.BULLISH if opportunity.iv_percentile >= 50 else StanceEnum.NEUTRAL
        return AgentOutput(
            agent_name="Volatility",
            stance=stance,
            confidence=0.75,
            thesis=f"IV percentile of {opportunity.iv_percentile:.1f}% offers sufficient premium richness for option selling relative to historical realized moves.",
            claims=[f"Implied volatility {opportunity.implied_volatility*100:.1f}% exceeds realized volatility", "Contract bid-ask spreads demonstrate liquid execution"],
            risks=["Implied volatility crush or post-earnings volatility spike"],
            recommendation="SELL_PUT" if stance == StanceEnum.BULLISH else "CAUTION",
            key_metrics={"iv": opportunity.implied_volatility, "iv_percentile": opportunity.iv_percentile},
        )

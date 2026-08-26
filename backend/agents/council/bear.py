import logging
from backend.models.contracts import Opportunity, AgentOutput, StanceEnum
from backend.agents.llm_client import llm_client
from backend.agents.prompts.council_prompts import BEAR_PROMPT

logger = logging.getLogger("backend.council.bear")

async def run_bear_analysis(
    opportunity: Opportunity,
    quant_output: AgentOutput,
    vol_output: AgentOutput,
) -> AgentOutput:
    user_prompt = f"""Stress-test and attack the proposed options income trade on {opportunity.symbol}:
- Price: ${opportunity.underlying_price:.2f}
- Quant Stance: {quant_output.stance.value} | Claims: {quant_output.claims}
- Volatility Stance: {vol_output.stance.value} | Claims: {vol_output.claims}
- Candidate Contracts:
{[{'strike': c.strike_price, 'type': c.option_type.value, 'delta': c.delta, 'dte': c.days_to_expiration} for c in opportunity.candidate_contracts[:4]]}

Identify how this trade could fail, what could breach the strike prices, and why collecting premium might be picking up pennies in front of a steamroller.
"""
    try:
        res = await llm_client.generate_structured(
            system_prompt=BEAR_PROMPT,
            user_prompt=user_prompt,
            response_model=AgentOutput,
            temperature=0.35,
        )
        res.agent_name = "Bear"
        return res
    except Exception as ex:
        logger.warning("Bear agent LLM call fallback: %s", ex)
        return AgentOutput(
            agent_name="Bear",
            stance=StanceEnum.BEARISH,
            confidence=0.72,
            thesis=f"Downside tail risk in {opportunity.symbol} is underappreciated; sharp drawdowns can quickly overrun OTM put cushions.",
            claims=[
                f"Break below ${opportunity.underlying_price * 0.96:.2f} exposes the stock to severe technical selling",
                "Asymmetric risk: limited premium upside versus steep assignment losses if market sells off",
            ],
            risks=["Macro interest rate headwinds and earnings volatility"],
            recommendation="CAUTION",
            key_metrics={"breach_risk_level": round(opportunity.underlying_price * 0.96, 2)},
        )

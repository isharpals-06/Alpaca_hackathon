import pytest
import asyncio
from datetime import datetime
from backend.models.contracts import (
    ActionEnum,
    StrategyEnum,
    OptionTypeEnum,
    Opportunity,
    CandidateContract,
    AgentOutput,
    StanceEnum,
    Debate,
    Decision,
    ContractSpec,
    RiskAssessment,
    Order,
    Position,
)
from backend.db.supabase_client import SupabaseRepository

def test_models_instantiation_and_validation():
    # 1. CandidateContract
    contract = CandidateContract(
        symbol="SPY260918P00540000",
        underlying_symbol="SPY",
        option_type=OptionTypeEnum.PUT,
        strike_price=540.0,
        expiration_date="2026-09-18",
        days_to_expiration=30,
        bid=4.20,
        ask=4.30,
        mid_price=4.25,
        open_interest=1500,
        volume=600,
        implied_volatility=0.22,
        delta=-0.25,
        liquidity_score=0.92,
    )
    assert contract.strike_price == 540.0
    assert contract.delta == -0.25

    # 2. Opportunity
    opp = Opportunity(
        symbol="SPY",
        underlying_price=560.0,
        implied_volatility=0.22,
        iv_percentile=60.0,
        liquidity_score=0.92,
        candidate_contracts=[contract],
    )
    assert opp.symbol == "SPY"
    assert len(opp.candidate_contracts) == 1

    # 3. AgentOutput
    agent_out = AgentOutput(
        agent_name="Quant",
        stance=StanceEnum.BULLISH,
        confidence=0.85,
        thesis="Momentum remains positive above 50-day moving average.",
        claims=["RSI at 54 is neutral-bullish", "Support at $550"],
        risks=["Macro CPI print next week"],
        recommendation="SELL_PUT",
    )
    assert agent_out.confidence == 0.85

    # 4. Decision
    decision = Decision(
        opportunity_id=opp.id,
        symbol="SPY",
        action=ActionEnum.TRADE,
        rationale="Strong risk-reward on 30-day 0.25 delta put.",
        confidence_score=0.88,
        recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
    )
    assert decision.action == ActionEnum.TRADE
    assert decision.recommended_strategy == StrategyEnum.CASH_SECURED_PUT

@pytest.mark.asyncio
async def test_supabase_in_memory_repository():
    repo = SupabaseRepository()
    
    # 1. Opportunity save & get
    opp = Opportunity(
        symbol="AAPL",
        underlying_price=225.0,
        implied_volatility=0.25,
        iv_percentile=55.0,
        liquidity_score=0.88,
    )
    saved_opp = await repo.save_opportunity(opp)
    assert saved_opp.id == opp.id
    
    fetched_opp = await repo.get_opportunity(opp.id)
    assert fetched_opp is not None
    assert fetched_opp.symbol == "AAPL"

    # 2. Decision save & list
    decision = Decision(
        opportunity_id=opp.id,
        symbol="AAPL",
        action=ActionEnum.TRADE,
        rationale="Favorable IV percentile for put selling",
        confidence_score=0.80,
        recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
    )
    await repo.save_decision(decision)
    decisions = await repo.list_decisions()
    assert len(decisions) >= 1
    assert any(d.id == decision.id for d in decisions)

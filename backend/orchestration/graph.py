import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from backend.models.contracts import (
    Opportunity,
    AgentOutput,
    Debate,
    Decision,
    ActionEnum,
    StrategyEnum,
    ContractSpec,
    RiskAssessment,
    Order,
    Position,
    PortfolioState,
    OptionTypeEnum,
    OrderStatusEnum,
)
from backend.scanner.options_scanner import options_scanner
from backend.agents.council.quant import run_quant_analysis
from backend.agents.council.volatility import run_volatility_analysis
from backend.agents.council.bull import run_bull_analysis
from backend.agents.council.bear import run_bear_analysis
from backend.agents.council.risk_officer import run_risk_officer_analysis
from backend.agents.council.portfolio_manager import run_portfolio_manager_synthesis
from backend.orchestration.debate import debate_orchestrator
from backend.strategy.covered_call import covered_call_strategy
from backend.strategy.cash_secured_put import cash_secured_put_strategy
from backend.risk.engine import risk_engine
from backend.execution.mcp_bridge import mcp_bridge
from backend.execution.alpaca_client import alpaca_client
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.orchestration.graph")

class TradingWorkflow:
    """
    End-to-End Multi-Agent Trading & Risk State Machine.
    Orchestrates the entire lifecycle:
    Scan -> 5-Agent Council Dispatch -> Bull/Bear Cross-Examination ->
    Portfolio Manager Synthesis -> Strategy Selection -> Deterministic Risk Gate ->
    Alpaca Paper Execution -> Supabase Persistence.
    """

    async def execute_cycle(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        target_symbol = (symbol or "SPY").upper()
        logger.info(">>> Starting Autonomous Pipeline Cycle for %s", target_symbol)

        # 1. Scanner Node: Get or generate Opportunity
        opportunity = await options_scanner.scan_symbol(target_symbol)
        if not opportunity:
            raise ValueError(f"Scanner could not generate Opportunity for {target_symbol}")
        
        await db_repository.save_opportunity(opportunity)

        # 2. Portfolio Context Node
        account = await alpaca_client.get_account()
        positions_list = await db_repository.list_positions()
        portfolio_state = PortfolioState(
            cash=account.get("cash", 100000.0),
            buying_power=account.get("buying_power", 100000.0),
            portfolio_value=account.get("portfolio_value", 100000.0),
            options_collateral_used=sum(p.strike_price * 100 * p.qty for p in positions_list),
            positions=positions_list,
        )

        # 3. Parallel Agent Dispatch Node (Concurrently run 5 analysis agents)
        quant_task = run_quant_analysis(opportunity)
        vol_task = run_volatility_analysis(opportunity)
        bull_task = run_bull_analysis(opportunity)
        bear_task = run_bear_analysis(opportunity)
        risk_task = run_risk_officer_analysis(opportunity, portfolio_state)

        quant_out, vol_out, bull_out, bear_out, risk_out = await asyncio.gather(
            quant_task, vol_task, bull_task, bear_task, risk_task
        )
        agent_outputs: List[AgentOutput] = [quant_out, vol_out, bull_out, bear_out, risk_out]

        # 4. Debate Node: Bull <-> Bear Cross-Examination
        challenges, responses = await debate_orchestrator.run_cross_examination(
            opportunity, bull_out, bear_out
        )

        # Create & Persist Debate Transcript
        debate = Debate(
            id=str(uuid.uuid4()),
            opportunity_id=opportunity.id,
            symbol=target_symbol,
            agent_outputs=agent_outputs,
            challenges=challenges,
            responses=responses,
            round_count=1,
            summary=f"Cross-examination completed between {bull_out.agent_name} and {bear_out.agent_name}.",
            created_at=datetime.utcnow(),
        )
        await db_repository.save_debate(debate)

        # 5. Portfolio Manager Synthesis Node
        decision: Decision = await run_portfolio_manager_synthesis(
            opportunity, agent_outputs, challenges, responses
        )

        contract_spec: Optional[ContractSpec] = None
        risk_assessment: Optional[RiskAssessment] = None
        order: Optional[Order] = None
        position: Optional[Position] = None

        # 6. Strategy & Risk Gate Nodes (If TRADE approved by PM)
        if decision.action == ActionEnum.TRADE and decision.recommended_strategy:
            if decision.recommended_strategy == StrategyEnum.COVERED_CALL:
                contract_spec = covered_call_strategy.construct_proposal(opportunity)
            else:
                contract_spec = cash_secured_put_strategy.construct_proposal(opportunity)

            if contract_spec:
                # 7. Deterministic Risk Gate Node (Strict Gatekeeper)
                risk_assessment = risk_engine.validate_trade(contract_spec, portfolio_state)
                
                if not risk_assessment.approved:
                    # Risk Gate VETO overrides PM approval into NO_TRADE
                    decision.action = ActionEnum.NO_TRADE
                    decision.rationale = f"RISK VETO: {risk_assessment.veto_reason} (Original PM Thesis: {decision.rationale})"
                    logger.warning(">>> Trade VETOED by Risk Gate for %s", target_symbol)
                else:
                    # 8. Alpaca Paper Execution Node
                    logger.info(">>> Submitting Approved Paper Order for %s", contract_spec.symbol)
                    order = await mcp_bridge.execute_contract(contract_spec, decision_id=decision.id)
                    await db_repository.save_order(order)

                    # Create Open Position Record
                    entry_prem = round(contract_spec.premium_estimate / (100.0 * contract_spec.contracts_count), 2)
                    position = Position(
                        id=str(uuid.uuid4()),
                        symbol=contract_spec.symbol,
                        underlying_symbol=target_symbol,
                        strategy=contract_spec.strategy_type,
                        option_type=contract_spec.option_type,
                        strike_price=contract_spec.strike_price,
                        expiration_date=contract_spec.expiration_date,
                        days_to_expiration=contract_spec.days_to_expiration,
                        qty=contract_spec.contracts_count,
                        entry_premium=entry_prem,
                        current_premium=entry_prem,
                        unrealized_pnl=0.0,
                        realized_pnl=0.0,
                        recommendation=ActionEnum.HOLD,
                        recommendation_reason="Position healthy, capturing theta decay.",
                        opened_at=datetime.utcnow(),
                    )
                    await db_repository.save_position(position)

        # 9. Persist Decision
        await db_repository.save_decision(decision)
        logger.info(">>> Cycle finished. Decision: %s for %s", decision.action.value, target_symbol)

        return {
            "opportunity": opportunity,
            "debate": debate,
            "decision": decision,
            "contract_spec": contract_spec,
            "risk_assessment": risk_assessment,
            "order": order,
            "position": position,
        }

trading_workflow = TradingWorkflow()

async def run_full_pipeline_cycle(symbol: Optional[str] = None) -> Dict[str, Any]:
    return await trading_workflow.execute_cycle(symbol)

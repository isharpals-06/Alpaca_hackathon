from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime

from backend.models.contracts import ActionEnum
from backend.scanner.options_scanner import options_scanner
from backend.orchestration.debate import debate_orchestrator
from backend.strategy.engine import strategy_engine
from backend.risk.engine import risk_engine
from backend.execution.alpaca_client import alpaca_execution
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.post("/scan")
async def trigger_scan(symbol: Optional[str] = None):
    """Triggers an on-demand market & options chain scan."""
    if symbol:
        opp = await options_scanner.scan_symbol(symbol.upper())
        if opp:
            await db_repository.save_opportunity(opp)
            return {"message": f"Scan completed for {symbol}", "opportunities": [opp.model_dump(mode="json")]}
        raise HTTPException(status_code=400, detail=f"Failed to scan symbol {symbol}")
    
    opps = await options_scanner.scan_universe()
    return {"message": f"Universe scan completed ({len(opps)} opportunities)", "opportunities": [o.model_dump(mode="json") for o in opps]}

@router.post("/run-cycle")
async def trigger_full_cycle(
    symbol: str = Query(default="SPY", description="Ticker symbol to run through full pipeline"),
    simulate_risk_veto: bool = Query(default=False, description="Simulate a risk gate veto for demo presentations"),
):
    """
    Executes one complete end-to-end trading cycle:
    SCAN -> COUNCIL DEBATE -> PM DECISION -> STRATEGY SELECTION -> RISK GATE -> ALPACA EXECUTION.
    """
    symbol = symbol.upper()
    
    # 1. Fetch live Account/Portfolio State
    portfolio_state = await alpaca_execution.get_account_state()

    # 2. Options Intelligence Scan
    opportunity = await options_scanner.scan_symbol(symbol)
    if not opportunity:
        raise HTTPException(status_code=400, detail=f"Unable to generate opportunity for {symbol}")
    await db_repository.save_opportunity(opportunity)

    # 3. AI Trading Council Debate & Synthesis
    debate, decision = await debate_orchestrator.run_full_debate(opportunity, portfolio_state)

    contract_spec = None
    risk_assessment = None
    order = None
    position = None

    # 4. If Decision is TRADE -> Run Strategy Engine & Risk Gate
    if decision.action == ActionEnum.TRADE:
        contract_spec = strategy_engine.build_contract_spec(opportunity, decision, portfolio_state)
        
        if contract_spec:
            # 5. Deterministic Risk Gate Review
            risk_assessment = risk_engine.evaluate_trade(
                contract_spec=contract_spec,
                portfolio_state=portfolio_state,
                simulate_veto=simulate_risk_veto,
            )

            # 6. Safe Alpaca Paper Execution (Only if APPROVED)
            if risk_assessment.approved:
                order, position = await alpaca_execution.submit_option_order(
                    contract_spec=contract_spec,
                    risk_assessment=risk_assessment,
                    decision_id=decision.id,
                )

    return {
        "status": "COMPLETED",
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "action_taken": decision.action.value,
        "opportunity": opportunity.model_dump(mode="json"),
        "debate": debate.model_dump(mode="json"),
        "decision": decision.model_dump(mode="json"),
        "contract_spec": contract_spec.model_dump(mode="json") if contract_spec else None,
        "risk_assessment": risk_assessment.model_dump(mode="json") if risk_assessment else None,
        "order": order.model_dump(mode="json") if order else None,
        "position": position.model_dump(mode="json") if position else None,
    }

@router.get("/status")
async def get_pipeline_status():
    """Returns overview stats of the active trading pipeline."""
    portfolio = await alpaca_execution.get_account_state()
    opps = await db_repository.list_opportunities(limit=10)
    decisions = await db_repository.list_decisions(limit=10)
    positions = await db_repository.list_positions()
    orders = await db_repository.list_orders(limit=10)

    return {
        "service": "alpaca-ai-trading-pipeline",
        "portfolio": {
            "cash": portfolio.cash,
            "buying_power": portfolio.buying_power,
            "portfolio_value": portfolio.portfolio_value,
            "options_collateral_used": portfolio.options_collateral_used,
        },
        "metrics": {
            "opportunities_scanned": len(opps),
            "decisions_rendered": len(decisions),
            "open_positions": len(positions),
            "orders_submitted": len(orders),
        },
    }

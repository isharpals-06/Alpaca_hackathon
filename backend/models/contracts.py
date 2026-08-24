from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ActionEnum(str, Enum):
    TRADE = "TRADE"
    NO_TRADE = "NO_TRADE"
    HOLD = "HOLD"
    CLOSE = "CLOSE"
    ROLL = "ROLL"

class StrategyEnum(str, Enum):
    COVERED_CALL = "COVERED_CALL"
    CASH_SECURED_PUT = "CASH_SECURED_PUT"

class Opportunity(BaseModel):
    id: str
    symbol: str
    underlying_price: float
    implied_volatility: float
    iv_percentile: float
    liquidity_score: float
    scanned_at: datetime = Field(default_factory=datetime.utcnow)

class AgentOutput(BaseModel):
    agent_name: str
    stance: str
    confidence: float
    thesis: str
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Debate(BaseModel):
    id: str
    opportunity_id: str
    agent_outputs: List[AgentOutput]
    cross_examination: List[Dict[str, str]]
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Decision(BaseModel):
    id: str
    opportunity_id: str
    action: ActionEnum
    rationale: str
    confidence_score: float
    recommended_strategy: Optional[StrategyEnum] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContractSpec(BaseModel):
    symbol: str
    underlying_symbol: str
    option_type: str  # call / put
    strike_price: float
    expiration_date: str
    premium: float
    delta: float
    contracts_count: int

class RiskAssessment(BaseModel):
    approved: bool
    rejection_reasons: List[str] = Field(default_factory=list)
    portfolio_exposure_pct: float
    max_loss_potential: float
    delta_risk_check: bool
    collateral_verified: bool

class Order(BaseModel):
    id: str
    decision_id: str
    alpaca_order_id: Optional[str] = None
    status: str
    symbol: str
    side: str
    qty: int
    filled_avg_price: Optional[float] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class Position(BaseModel):
    id: str
    symbol: str
    strategy: StrategyEnum
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    days_to_expiration: int
    recommendation: ActionEnum = ActionEnum.HOLD
    opened_at: datetime = Field(default_factory=datetime.utcnow)

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ActionEnum(str, Enum):
    TRADE = "TRADE"
    NO_TRADE = "NO_TRADE"
    HOLD = "HOLD"
    CLOSE = "CLOSE"
    ROLL = "ROLL"

class StrategyEnum(str, Enum):
    COVERED_CALL = "COVERED_CALL"
    CASH_SECURED_PUT = "CASH_SECURED_PUT"

class OptionTypeEnum(str, Enum):
    CALL = "call"
    PUT = "put"

class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class StanceEnum(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    CAUTION = "CAUTION"
    AVOID = "AVOID"

class CandidateContract(BaseModel):
    model_config = ConfigDict(extra="ignore")
    symbol: str
    underlying_symbol: str
    option_type: OptionTypeEnum
    strike_price: float
    expiration_date: str
    days_to_expiration: int
    bid: float
    ask: float
    mid_price: float
    open_interest: int
    volume: int
    implied_volatility: float
    delta: Optional[float] = None
    liquidity_score: float = 0.0

class Opportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    underlying_price: float
    historical_volatility: float = 0.0
    implied_volatility: float = 0.0
    iv_percentile: float = 50.0
    liquidity_score: float = 0.0
    sector: Optional[str] = None
    candidate_contracts: List[CandidateContract] = Field(default_factory=list)
    scanned_at: datetime = Field(default_factory=datetime.utcnow)

class AgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    agent_name: str
    stance: StanceEnum
    confidence: float = Field(ge=0.0, le=1.0)
    thesis: str
    claims: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendation: str
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChallengeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    from_agent: str
    to_agent: str
    target_claim: str
    challenge_text: str

class ResponseItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    from_agent: str
    in_response_to: str
    response_text: str
    confidence_delta: float = 0.0

class Debate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_id: str
    symbol: str
    agent_outputs: List[AgentOutput] = Field(default_factory=list)
    challenges: List[ChallengeItem] = Field(default_factory=list)
    responses: List[ResponseItem] = Field(default_factory=list)
    summary: str = ""
    round_count: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Decision(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_id: str
    symbol: str
    action: ActionEnum
    rationale: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommended_strategy: Optional[StrategyEnum] = None
    debate_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContractSpec(BaseModel):
    model_config = ConfigDict(extra="ignore")
    symbol: str
    underlying_symbol: str
    strategy_type: StrategyEnum
    option_type: OptionTypeEnum
    strike_price: float
    expiration_date: str
    days_to_expiration: int
    delta: float
    premium_estimate: float
    contracts_count: int = 1
    max_loss_estimate: float = 0.0
    liquidity_score: float = 0.0

class RiskCheckItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    check_name: str
    passed: bool
    details: str

class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approved: bool
    checks_run: List[str] = Field(default_factory=list)
    checks_passed: List[str] = Field(default_factory=list)
    checks_failed: List[str] = Field(default_factory=list)
    veto_reason: Optional[str] = None
    portfolio_exposure_pct: float = 0.0
    max_loss_potential: float = 0.0
    detailed_checks: List[RiskCheckItem] = Field(default_factory=list)
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    contract_symbol: str
    underlying_symbol: str
    strategy: StrategyEnum
    alpaca_order_id: Optional[str] = None
    status: OrderStatusEnum = OrderStatusEnum.PENDING
    side: str
    qty: int = 1
    limit_price: Optional[float] = None
    filled_avg_price: Optional[float] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None

class Position(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    underlying_symbol: str
    strategy: StrategyEnum
    option_type: OptionTypeEnum
    strike_price: float
    expiration_date: str
    qty: int = 1
    entry_premium: float
    current_premium: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    days_to_expiration: int
    recommendation: ActionEnum = ActionEnum.HOLD
    recommendation_reason: str = "Position healthy, monitoring decay."
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)

class PortfolioState(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cash: float
    buying_power: float
    portfolio_value: float
    options_collateral_used: float = 0.0
    open_positions_count: int = 0
    positions: List[Position] = Field(default_factory=list)
    as_of: datetime = Field(default_factory=datetime.utcnow)

class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    total_realized_pnl: float = 0.0
    total_unrealized_pnl: float = 0.0
    win_rate_pct: float = 0.0
    total_trades_count: int = 0
    winning_trades_count: int = 0
    average_premium_captured_pct: float = 0.0
    as_of: datetime = Field(default_factory=datetime.utcnow)

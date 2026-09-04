from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict, Any, Union
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
    bid: Optional[float] = 0.0
    ask: Optional[float] = 0.0
    mid_price: Optional[float] = 0.0
    open_interest: Optional[int] = 0
    volume: Optional[int] = 0
    implied_volatility: Optional[float] = 0.0
    delta: Optional[float] = None
    liquidity_score: Optional[float] = 0.0

    @model_validator(mode="before")
    @classmethod
    def handle_nulls(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for k in ["bid", "ask", "mid_price", "open_interest", "volume", "implied_volatility", "liquidity_score"]:
                if data.get(k) is None:
                    data[k] = 0
        return data

class Opportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    underlying_price: float
    historical_volatility: Optional[float] = 0.0
    implied_volatility: Optional[float] = 0.0
    iv_percentile: Optional[float] = 50.0
    liquidity_score: Optional[float] = 0.0
    sector: Optional[str] = "Equities"
    candidate_contracts: List[CandidateContract] = Field(default_factory=list)
    scanned_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def handle_nulls(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("historical_volatility") is None:
                data["historical_volatility"] = 0.0
            if data.get("implied_volatility") is None:
                data["implied_volatility"] = 0.0
            if data.get("iv_percentile") is None:
                data["iv_percentile"] = 50.0
            if data.get("liquidity_score") is None:
                data["liquidity_score"] = 0.0
            if data.get("candidate_contracts") is None:
                data["candidate_contracts"] = []
        return data

class AgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    agent_name: str
    stance: StanceEnum = StanceEnum.NEUTRAL
    confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    thesis: str = ""
    claims: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendation: str = ""
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def handle_nulls(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("claims") is None:
                data["claims"] = []
            if data.get("risks") is None:
                data["risks"] = []
            if data.get("key_metrics") is None:
                data["key_metrics"] = {}
        return data

class ChallengeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    from_agent: str
    to_agent: str
    target_claim: str = ""
    challenge_text: str = ""
    severity: str = "MEDIUM"

class ResponseItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    from_agent: str
    in_response_to: str
    response_text: str = ""
    concession: bool = False
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
    action: ActionEnum = ActionEnum.NO_TRADE
    rationale: str = ""
    confidence_score: float = Field(default=0.70, ge=0.0, le=1.0)
    recommended_strategy: Optional[StrategyEnum] = None
    debate_id: Optional[str] = None
    order_spec: Optional[str] = None
    premium: Optional[float] = None
    status: Optional[str] = None
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
    delta: float = 0.0
    premium_estimate: float = 0.0
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
    contract_symbol: str = ""
    underlying_symbol: str = ""
    strategy: StrategyEnum = StrategyEnum.CASH_SECURED_PUT
    alpaca_order_id: Optional[str] = None
    status: OrderStatusEnum = OrderStatusEnum.PENDING
    side: str = "sell_to_open"
    qty: int = 1
    limit_price: Optional[float] = None
    filled_avg_price: Optional[float] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "symbol" in data and not data.get("contract_symbol"):
                data["contract_symbol"] = data["symbol"]
        return data

class Position(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    underlying_symbol: str = ""
    strategy: StrategyEnum = StrategyEnum.CASH_SECURED_PUT
    option_type: OptionTypeEnum = OptionTypeEnum.PUT
    strike_price: float = 0.0
    expiration_date: str = ""
    qty: int = 1
    entry_premium: float = 0.0
    current_premium: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    days_to_expiration: int = 30
    recommendation: ActionEnum = ActionEnum.HOLD
    recommendation_reason: str = "Position healthy, monitoring decay."
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "entry_price" in data and not data.get("entry_premium"):
                data["entry_premium"] = float(data["entry_price"] or 0.0)
            if "current_price" in data and not data.get("current_premium"):
                data["current_premium"] = float(data["current_price"] or 0.0)
            if not data.get("underlying_symbol") and data.get("symbol"):
                sym = str(data["symbol"])
                data["underlying_symbol"] = sym[:4].rstrip("0123456789")
        return data

class PortfolioState(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cash: float = 100000.0
    buying_power: float = 100000.0
    portfolio_value: float = 100000.0
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

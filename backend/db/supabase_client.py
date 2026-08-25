import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from backend.config import settings
from backend.models.contracts import (
    Opportunity,
    Debate,
    Decision,
    Order,
    Position,
    RiskAssessment,
)

logger = logging.getLogger("backend.db")

class SupabaseRepository:
    """
    Repository for persisting and querying trading pipeline entities.
    Connects to Supabase PostgREST API when configured, or transparently
    falls back to an in-memory datastore during local/offline testing.
    """

    def __init__(self):
        self.url = settings.SUPABASE_URL.rstrip("/") if settings.SUPABASE_URL else ""
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.is_configured = bool(self.url and self.service_key and "supabase.co" in self.url)
        
        # In-memory storage fallback
        self._mem_opportunities: Dict[str, Dict[str, Any]] = {}
        self._mem_debates: Dict[str, Dict[str, Any]] = {}
        self._mem_decisions: Dict[str, Dict[str, Any]] = {}
        self._mem_orders: Dict[str, Dict[str, Any]] = {}
        self._mem_positions: Dict[str, Dict[str, Any]] = {}
        self._mem_risk: Dict[str, Dict[str, Any]] = {}

        if self.is_configured:
            logger.info("Supabase configured: %s", self.url)
        else:
            logger.info("Supabase not fully configured; operating in resilient in-memory mode.")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    # ==========================================
    # Opportunity Operations
    # ==========================================
    async def save_opportunity(self, opp: Opportunity) -> Opportunity:
        data = opp.model_dump(mode="json")
        self._mem_opportunities[opp.id] = data

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"{self.url}/rest/v1/opportunities",
                        headers=self._get_headers(),
                        json={
                            "id": opp.id,
                            "symbol": opp.symbol,
                            "underlying_price": opp.underlying_price,
                            "implied_volatility": opp.implied_volatility,
                            "iv_percentile": opp.iv_percentile,
                            "liquidity_score": opp.liquidity_score,
                            "scanned_at": opp.scanned_at.isoformat(),
                        },
                    )
                    if resp.is_success:
                        logger.debug("Persisted opportunity %s to Supabase", opp.id)
            except Exception as ex:
                logger.warning("Supabase save_opportunity fallback to memory: %s", ex)

        return opp

    async def get_opportunity(self, id: str) -> Optional[Opportunity]:
        if id in self._mem_opportunities:
            return Opportunity(**self._mem_opportunities[id])

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{self.url}/rest/v1/opportunities?id=eq.{id}",
                        headers=self._get_headers(),
                    )
                    if resp.is_success and resp.json():
                        return Opportunity(**resp.json()[0])
            except Exception as ex:
                logger.warning("Supabase get_opportunity error: %s", ex)

        return None

    async def list_opportunities(self, limit: int = 50) -> List[Opportunity]:
        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{self.url}/rest/v1/opportunities?order=scanned_at.desc&limit={limit}",
                        headers=self._get_headers(),
                    )
                    if resp.is_success and resp.json():
                        return [Opportunity(**item) for item in resp.json()]
            except Exception as ex:
                logger.warning("Supabase list_opportunities error: %s", ex)

        # In-memory fallback
        sorted_opps = sorted(
            self._mem_opportunities.values(),
            key=lambda x: x.get("scanned_at", ""),
            reverse=True,
        )
        return [Opportunity(**item) for item in sorted_opps[:limit]]

    # ==========================================
    # Debate Operations
    # ==========================================
    async def save_debate(self, debate: Debate) -> Debate:
        data = debate.model_dump(mode="json")
        self._mem_debates[debate.id] = data

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.url}/rest/v1/debates",
                        headers=self._get_headers(),
                        json={
                            "id": debate.id,
                            "opportunity_id": debate.opportunity_id,
                            "agent_outputs": [a.model_dump(mode="json") for a in debate.agent_outputs],
                            "cross_examination": [c.model_dump(mode="json") for c in debate.challenges],
                            "summary": debate.summary,
                            "created_at": debate.created_at.isoformat(),
                        },
                    )
            except Exception as ex:
                logger.warning("Supabase save_debate fallback to memory: %s", ex)

        return debate

    async def get_debate(self, id: str) -> Optional[Debate]:
        if id in self._mem_debates:
            return Debate(**self._mem_debates[id])

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{self.url}/rest/v1/debates?id=eq.{id}",
                        headers=self._get_headers(),
                    )
                    if resp.is_success and resp.json():
                        return Debate(**resp.json()[0])
            except Exception as ex:
                logger.warning("Supabase get_debate error: %s", ex)

        return None

    # ==========================================
    # Decision Operations
    # ==========================================
    async def save_decision(self, decision: Decision) -> Decision:
        data = decision.model_dump(mode="json")
        self._mem_decisions[decision.id] = data

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.url}/rest/v1/decisions",
                        headers=self._get_headers(),
                        json={
                            "id": decision.id,
                            "opportunity_id": decision.opportunity_id,
                            "action": decision.action.value,
                            "rationale": decision.rationale,
                            "confidence_score": decision.confidence_score,
                            "recommended_strategy": decision.recommended_strategy.value if decision.recommended_strategy else None,
                            "created_at": decision.created_at.isoformat(),
                        },
                    )
            except Exception as ex:
                logger.warning("Supabase save_decision fallback to memory: %s", ex)

        return decision

    async def list_decisions(self, limit: int = 50) -> List[Decision]:
        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{self.url}/rest/v1/decisions?order=created_at.desc&limit={limit}",
                        headers=self._get_headers(),
                    )
                    if resp.is_success and resp.json():
                        return [Decision(**item) for item in resp.json()]
            except Exception as ex:
                logger.warning("Supabase list_decisions error: %s", ex)

        sorted_decisions = sorted(
            self._mem_decisions.values(),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )
        return [Decision(**item) for item in sorted_decisions[:limit]]

    # ==========================================
    # Order Operations
    # ==========================================
    async def save_order(self, order: Order) -> Order:
        data = order.model_dump(mode="json")
        self._mem_orders[order.id] = data

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.url}/rest/v1/orders",
                        headers=self._get_headers(),
                        json={
                            "id": order.id,
                            "decision_id": order.decision_id,
                            "alpaca_order_id": order.alpaca_order_id,
                            "status": order.status.value,
                            "symbol": order.contract_symbol,
                            "side": order.side,
                            "qty": order.qty,
                            "filled_avg_price": order.filled_avg_price,
                            "submitted_at": order.submitted_at.isoformat(),
                        },
                    )
            except Exception as ex:
                logger.warning("Supabase save_order fallback to memory: %s", ex)

        return order

    async def list_orders(self, limit: int = 50) -> List[Order]:
        sorted_orders = sorted(
            self._mem_orders.values(),
            key=lambda x: x.get("submitted_at", ""),
            reverse=True,
        )
        return [Order(**item) for item in sorted_orders[:limit]]

    # ==========================================
    # Position Operations
    # ==========================================
    async def save_position(self, position: Position) -> Position:
        data = position.model_dump(mode="json")
        self._mem_positions[position.id] = data

        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.url}/rest/v1/positions",
                        headers=self._get_headers(),
                        json={
                            "id": position.id,
                            "symbol": position.symbol,
                            "strategy": position.strategy.value,
                            "entry_price": position.entry_premium,
                            "current_price": position.current_premium,
                            "unrealized_pnl": position.unrealized_pnl,
                            "realized_pnl": position.realized_pnl,
                            "days_to_expiration": position.days_to_expiration,
                            "recommendation": position.recommendation.value,
                            "opened_at": position.opened_at.isoformat(),
                        },
                    )
            except Exception as ex:
                logger.warning("Supabase save_position fallback to memory: %s", ex)

        return position

    async def list_positions(self) -> List[Position]:
        return [Position(**item) for item in self._mem_positions.values()]

    async def update_position(self, id: str, updates: Dict[str, Any]) -> Optional[Position]:
        if id in self._mem_positions:
            self._mem_positions[id].update(updates)
            self._mem_positions[id]["last_checked_at"] = datetime.utcnow().isoformat()
            return Position(**self._mem_positions[id])
        return None

# Singleton instance
db_repository = SupabaseRepository()

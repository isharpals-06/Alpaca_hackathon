import logging
from typing import Optional
from backend.models.contracts import ContractSpec, Order
from backend.execution.alpaca_client import alpaca_client

logger = logging.getLogger("backend.execution.mcp")

class AlpacaMCPBridge:
    """
    Alpaca MCP Integration Bridge.
    Maps agent council approved ContractSpec objects into Alpaca execution operations.
    """

    async def execute_contract(
        self,
        contract: ContractSpec,
        decision_id: Optional[str] = None,
    ) -> Order:
        logger.info("Routing contract execution through Alpaca Paper Bridge for %s", contract.symbol)
        order = await alpaca_client.submit_option_order(contract, decision_id=decision_id)
        return order

mcp_bridge = AlpacaMCPBridge()

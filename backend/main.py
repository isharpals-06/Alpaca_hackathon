import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    health,
    opportunities,
    debates,
    decisions,
    positions,
    portfolio,
    trades,
    pipeline,
    performance,
)
from backend.monitoring.position_monitor import position_monitor

logger = logging.getLogger("backend.main")

async def background_position_worker():
    """Background loop that evaluates open positions every 60 seconds."""
    logger.info("Started continuous position monitoring background worker.")
    while True:
        try:
            await asyncio.sleep(60)
            evaluated = await position_monitor.evaluate_positions()
            if evaluated:
                logger.info("Evaluated %d active positions in background loop.", len(evaluated))
        except asyncio.CancelledError:
            logger.info("Background position worker shutting down.")
            break
        except Exception as ex:
            logger.warning("Background position monitor encountered error: %s", ex)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch background position monitoring task
    worker_task = asyncio.create_task(background_position_worker())
    yield
    # Shutdown: Cancel background worker
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Alpaca AI Trading Engine",
    description="Autonomous AI Agent Council for Options Income Overlay & Risk-Governed Paper Trading",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(performance.router, prefix="/performance", tags=["Performance"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
app.include_router(debates.router, prefix="/debates", tags=["Debates"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
app.include_router(positions.router, prefix="/positions", tags=["Positions"])
app.include_router(trades.router, prefix="/trades", tags=["Trades"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline Execution & Scanner"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

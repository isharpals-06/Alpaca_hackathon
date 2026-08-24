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
)

app = FastAPI(
    title="Alpaca AI Trading Engine",
    description="Autonomous AI Agent Council for Options Income Overlay & Risk-Governed Paper Trading",
    version="1.0.0"
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
app.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
app.include_router(debates.router, prefix="/debates", tags=["Debates"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
app.include_router(positions.router, prefix="/positions", tags=["Positions"])
app.include_router(trades.router, prefix="/trades", tags=["Trades"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline Execution & Scanner"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

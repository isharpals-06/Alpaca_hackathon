# 🏛️ ThetaCouncil AI — Autonomous Options Income Overlay & Risk-Governed Trading Engine

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Alpaca API](https://img.shields.io/badge/Alpaca-Paper%20Trading-yellow.svg)](https://alpaca.markets)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Multi--LLM-purple.svg)](https://openrouter.ai/)
[![Tests Passing](https://img.shields.io/badge/Tests-20%2F20%20Passing%20(100%25)-brightgreen.svg)]()

> **ThetaCouncil AI** is an autonomous options trading platform that combines an adversarial 6-Agent AI Debate Council with a deterministic, code-governed 5-stage Risk Gate to execute options income overlay strategies (**The Wheel**: Cash-Secured Puts & Covered Calls) with real-time Alpaca paper trading.

---

## 🌟 Key Architectural Innovations

1. **Adversarial AI Trading Council (Cognitive Layer)**:
   - Six specialized LLM agents (**Quant**, **Volatility**, **Bull**, **Bear**, **Risk Officer**, **Portfolio Manager**) independently analyze live options chains, cross-examine opposing theses in Phase 2, and synthesize high-conviction decisions.
   - **Capital Preservation First**: If council confidence is < 65% or risks dominate, the system strictly renders `NO_TRADE` (a first-class outcome).
2. **Deterministic Risk Gate (Safety Layer)**:
   - A non-LLM, code-governed Python gatekeeper with unilateral veto power. Enforces 5 sequential checks (Contract Validity, 10% Position Size Cap, 40% Options Exposure Cap, 20% Sector Concentration Cap, 100% Cash/Share Collateral) before any order reaches Alpaca.
3. **Continuous Position Monitoring & Wheel Lifecycle**:
   - Evaluates open contracts against 50% profit-target capture, time decay (DTE <= 3), and delta drift (> 0.45) to surface real-time `HOLD`, `CLOSE`, or `ROLL` recommendations.
   - Automatically loops freed capital upon put expiration back into put scanning, or transitions assigned shares to Covered Call writing.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Cognitive Layer (6-Agent AI Council)
        MKT[Live Market & Options Data] --> SCAN[Options Scanner Universe]
        SCAN --> AGENTS[5 Analytical Agents:<br>Quant, Volatility, Bull, Bear, Risk Officer]
        AGENTS --> XEXAM[Phase 2: Bear vs Bull Cross-Examination]
        XEXAM --> PM[Phase 3: Portfolio Manager Synthesis]
        PM -->|Consensus >= 65%| DEC[TRADE Decision]
        PM -->|Low Conviction / Split| NT[NO_TRADE: Capital Preservation]
    end

    subgraph Deterministic Safety Layer (Risk Gate)
        DEC --> RG{5 Sequential Code Checks:<br>1. Contract Validity<br>2. Position Sizing <= 10%<br>3. Total Options Exposure <= 40%<br>4. Concentration <= 20%<br>5. 100% Collateral}
        RG -->|All Passed| APPR[Risk APPROVED]
        RG -->|Any Failed| VETO[RISK VETO -> Order Aborted]
    end

    subgraph Execution & Lifecycle (Alpaca + Wheel)
        APPR --> ALP[Alpaca Paper Trading API]
        ALP --> POS[Open Position Created]
        POS --> MON[3-Rule Position Monitor:<br>1. Profit Target >= 50% -> CLOSE<br>2. Expiry <= 3 DTE -> EXPIRE/ROLL<br>3. Delta > 0.45 -> ROLL]
        MON --> WHEEL[Wheel Loop-Back:<br>CSP Expiry -> Sell Puts<br>CSP Assignment -> Sell Covered Calls]
    end

    subgraph Frontend Dashboard
        POS -.-> UI[React Dashboard: http://localhost:3000]
        DEC -.-> UI
        RG -.-> UI
    end
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Alpaca Paper Trading Account (API Key + Secret)
- OpenRouter API Key

### 1. Clone & Configure Environment
```bash
git clone https://github.com/isharpals-06/Alpaca_hackathon.git
cd Alpaca_hackathon

# Copy example environment file
cp .env.example .env
```

Edit `.env` and provide your keys:
```env
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_LLM_MODEL=deepseek/deepseek-chat
```

---

### 2. Start the Application

#### Option A: Local Run (Fastest)

**Terminal 1 (Backend):**
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

Open **`http://localhost:3000`** in your browser.

#### Option B: Docker Compose
```bash
docker-compose up --build
```

---

## 🧪 Master Test Suite

Run the unified test harness covering all 20 unit, integration, risk, and API test cases across the system:

```bash
python tests/run_all_tests.py
```

Output:
```text
======================================================================
 MASTER TEST RUNNER SUMMARY: Ran 20 tests in 82.26s
 Status: ALL PASSED (100% SUCCESS)
======================================================================
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health check |
| `GET` | `/portfolio` | Live paper account cash, buying power, and portfolio value |
| `GET` | `/opportunities` | List active scanned options opportunities |
| `POST` | `/opportunities/scan` | Trigger on-demand options chain universe scan |
| `POST` | `/debates/run?symbol=SPY` | Run 6-agent debate and cross-examination on a ticker |
| `GET` | `/decisions` | List portfolio manager decisions and transcripts |
| `POST` | `/pipeline/run-cycle?symbol=SPY` | Run full automated cycle (Scan ➔ Debate ➔ Risk ➔ Execution) |
| `GET` | `/positions` | List open options contracts with real-time `HOLD/CLOSE/ROLL` recommendations |
| `POST` | `/positions/tick-all` | Trigger position monitor tick across all open positions |
| `POST` | `/positions/{id}/close` | Close an open position and realize P&L |
| `GET` | `/performance` | Aggregated realized/unrealized P&L and win rate |
| `GET` | `/performance/history` | Historical equity curve data points for frontend charts |

---

## 🎬 Live Presentation & Demo Script

When presenting to judges:
1. **Show Real Portfolio**: Top stats show live Alpaca paper account cash ($100k) and buying power ($400k).
2. **Click "Run Auto Cycle (SPY)"**: Watch the 6 agents debate live, cross-examine claims, pass the 5-check Risk Gate, and submit a paper order to Alpaca.
3. **Click "Simulate Risk Veto"**: Demonstrate the non-LLM Risk Gate vetoing an unsafe trade live on stage.
4. **Click "Tick Monitor"**: Demonstrate automated 50% profit-target capture and time-decay rules updating open positions.

---

## 👥 The Quant Council Team
* **Person 1 (AI & Trading Core Lead)**: Options Intelligence Scanner, Multi-Agent LangGraph Debate Orchestration, Strategy Engine, Deterministic Risk Gate, and Alpaca Paper Execution.
* **Person 2 (Platform & Frontend Lead)**: React UI Dashboard, Live AI Debate Arena, Risk Gate Visualizer, and Video Presentation.

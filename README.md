# Alpaca AI — Autonomous Options Income & Portfolio Overlay Engine

Autonomous AI Agent Council for options income overlay strategies (Covered Calls & Cash-Secured Puts) with risk governance and automated paper execution on Alpaca.

## Architecture

- **Frontend**: React + Vite + TailwindCSS + Supabase Realtime
- **Backend**: FastAPI + LangGraph Multi-Agent Debate Council
- **Database**: Supabase (PostgreSQL + Realtime)
- **Execution**: Alpaca Paper Trading API & MCP Bridge

## Repository Structure

```
├── backend/
│   ├── api/            # FastAPI endpoints
│   ├── agents/         # AI Council agents & prompts
│   ├── orchestration/  # LangGraph debate & workflow
│   ├── strategy/       # Options strategy builders
│   ├── risk/           # Risk validation engine & gates
│   ├── execution/      # Alpaca execution client & MCP bridge
│   ├── monitoring/     # Position monitoring & performance
│   ├── models/         # Pydantic data contracts
│   ├── config.py       # Configuration loader
│   ├── main.py         # Application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/ # UI components (parchment theme, debate transcript)
│   │   ├── hooks/      # Realtime & data hooks
│   │   ├── pages/      # View pages
│   │   ├── types/      # TypeScript interfaces
│   │   ├── utils/      # API client & helpers
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── supabase/
│   ├── migrations/     # Database schemas
│   └── seed.sql        # Demo seed data
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Fill in your Alpaca paper keys, Supabase credentials, and LLM API key
```

### 2. Backend Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate

pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

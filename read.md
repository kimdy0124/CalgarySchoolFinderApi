# Calgary School Finder API (MVP)

FastAPI + Postgres(PostGIS) backend for a Calgary school finder.
It supports distance-based nearby search, filters (district/program/grade), and school detail lookup.

## Features (MVP)
- Health check: `GET /health`
- Nearby schools (PostGIS): `GET /schools/nearby`
- School detail: `GET /schools/{school_id}`
- District list: `GET /districts`
- Program list: `GET /programs`
- API docs (Swagger): `/docs`

## Tech Stack
- FastAPI (Python)
- PostgreSQL + PostGIS
- SQLAlchemy (for DB connection) + raw SQL (for PostGIS functions)
- Docker (recommended for DB)

## Requirements
- Python 3.10+ (recommended)
- Docker Desktop (recommended) OR local Postgres + PostGIS

---

## Quick Start

### 1 Create venv and install deps
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlalchemy psycopg2-binary requests


###Roadmap

CSV ingest pipeline for real CBE/CCSD school lists

Address → geocode → nearby (single endpoint)

Program catalog + richer filtering

Catchment / transportation logic (phase 2+)
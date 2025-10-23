# QoraTrader Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-22

## Active Technologies
- Python 3.11+ (for trading engine and backtesting) and TypeScript/JavaScript (for web UI) + FastAPI, pandas, numpy, TA-Lib, Docker, Docker Compose, miniQMT API, PostgreSQL, InfluxDB (or TimescaleDB) (002-add-user-stories-spec)
- Python 3.11+ (for trading engine and backtesting) and TypeScript/JavaScript (for web UI) + FastAPI, pandas, numpy, TA-Lib, Docker, Docker Compose, miniQMT API, PostgreSQL, TimescaleDB (002-add-user-stories-spec)
- Hybrid - PostgreSQL for transactional data (orders, trades, accounts), Time-series DB (TimescaleDB) for market data (002-add-user-stories-spec)

## Project Structure
```
backend/
frontend/
tests/
```

## Commands
cd src; pytest; ruff check .

## Code Style
Python 3.11+ (for trading engine and backtesting) and TypeScript/JavaScript (for web UI): Follow standard conventions

## Recent Changes
- 002-add-user-stories-spec: Added Python 3.11+ (for trading engine and backtesting) and TypeScript/JavaScript (for web UI) + FastAPI, pandas, numpy, TA-Lib, Docker, Docker Compose, miniQMT API, PostgreSQL, TimescaleDB
- 002-add-user-stories-spec: Added Python 3.11+ (for trading engine and backtesting) and TypeScript/JavaScript (for web UI) + FastAPI, pandas, numpy, TA-Lib, Docker, Docker Compose, miniQMT API, PostgreSQL, InfluxDB (or TimescaleDB)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

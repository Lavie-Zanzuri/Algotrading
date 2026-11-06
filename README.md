# Agent Trader – Multi-Agent Algorithmic Trading System

A Python algorithmic trading system powered by **4 collaborating AI agents** built with **CrewAI**. The agents analyze the market, assess risk, read the news and execute trades through **Alpaca's paper trading API**, so no real money is involved.

The system starts with $100,000 in virtual cash and trades PLTR, NFLX and PLTK, with the goal of maximizing portfolio value.

## Architecture

| Agent | Role |
|---|---|
| **Market Analyst** | Analyzes price data and market trends |
| **Risk Manager** | Evaluates position size and risk/reward before each trade |
| **News Analyzer** | Considers recent news and sentiment about each company |
| **Trade Executor** | Makes the final buy/sell/hold decision and executes it |

### Custom agent tools
- `CalculateProfitLossTool`: profit/loss for a position
- `CalculatePositionSizeTool`: how much to buy based on available capital and risk
- `CalculateRiskRewardTool`: risk/reward ratio of a potential trade

## Engineering highlights

- **Test-Driven Development:** the Portfolio Manager was built test-first. The project has 100+ pytest tests.
- **Mocked paid APIs:** development and tests run against mocks, so they make no real API calls.
- **Custom rate limiter:** per-second, per-hour and per-day limits on paid services, with graceful handling when a limit is hit.
- **Caching layer:** repeated API calls with the same input are served from cache.
- **Structured logging:** every decision and the current portfolio value are logged.

## Tech stack

Python · CrewAI · Alpaca API · OpenAI API · pytest · pandas

## Project structure

```
src/
  agent_trader.py           # Main entry point
  alpaca_client.py          # Alpaca API wrapper (with mock support)
  trading_crew.py           # The 4-agent CrewAI crew
  market_analyst_agent.py
  custom_tools.py           # Custom agent tools
  trading_algorithm.py
  portfolio_manager.py      # Built with TDD
  stock_data_collector.py
  rate_limiter.py
  cache.py
tests/                      # pytest test suite
```

## Getting started

```bash
git clone https://github.com/Lavie-Zanzuri/Algotrading.git
cd Algotrading
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (it is ignored by git):

```
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
OPENAI_API_KEY=your_key
```

Run the tests:

```bash
pytest
```

Run the trader (press Ctrl+C to stop):

```bash
python -m src.agent_trader
```

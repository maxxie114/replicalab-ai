"""Finance and trading planning scenario templates."""

from __future__ import annotations

import random
from typing import Any

from replicalab.config import MAX_ROUNDS


def build_finance_trading_template(rng: random.Random) -> dict[str, Any]:
    cases = [
        {
            "domain_id": "finance_trading",
            "paper_title": "Planning an offline mean-reversion backtest for SPY and QQQ",
            "paper_hypothesis": "A simple mean-reversion design can be evaluated fairly without live execution.",
            "paper_method": "Run an offline daily-bar backtest with transaction costs, slippage assumptions, and fixed entry rules.",
            "paper_key_finding": "The plan is accepted only if risk limits and evaluation hygiene remain explicit.",
            "task_summary": "Design a mean-reversion backtest workflow for SPY and QQQ under capital, drawdown, and deadline limits.",
            "success_criteria": [
                "Use only offline historical data with explicit slippage assumptions.",
                "Keep position sizing inside the stated capital and drawdown rules.",
                "Separate strategy design from final evaluation.",
            ],
            "reference_summary": "A valid plan keeps the workflow offline, constrains drawdown, and documents slippage assumptions.",
            "required_elements": [
                "offline historical data only",
                "transaction cost assumption",
                "drawdown guardrail",
                "final evaluation split",
            ],
            "flexible_elements": [
                "lookback window",
                "entry threshold",
                "report visualization format",
            ],
            "target_metric": "risk_adjusted_return",
            "target_value": "positive Sharpe with drawdown inside the guardrail",
            "constraints": [
                {
                    "key": "max_capital",
                    "label": "Maximum simulated capital",
                    "quantity": 50000,
                    "unit": "usd",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The simulation must stay within the stated capital cap.",
                },
                {
                    "key": "max_drawdown",
                    "label": "Maximum allowed drawdown",
                    "quantity": 8,
                    "unit": "percent",
                    "comparator": "<=",
                    "hard": True,
                    "details": "Any accepted plan must respect the drawdown guardrail.",
                },
                {
                    "key": "live_execution",
                    "label": "Execution mode",
                    "quantity": None,
                    "unit": None,
                    "comparator": "=",
                    "hard": True,
                    "details": "Only offline or backtest planning is allowed. No live trading.",
                },
            ],
            "resources": [
                {
                    "key": "historical_bars",
                    "label": "Historical daily bar dataset",
                    "quantity": 1,
                    "unit": "dataset",
                    "available": True,
                    "category": "data",
                    "details": "Contains adjusted SPY and QQQ bars with metadata.",
                },
                {
                    "key": "backtest_engine",
                    "label": "Backtest engine",
                    "quantity": 1,
                    "unit": "engine",
                    "available": True,
                    "category": "tool",
                    "details": "Supports offline simulation with transaction costs and slippage.",
                },
                {
                    "key": "risk_reviewer",
                    "label": "Risk reviewer",
                    "quantity": 1,
                    "unit": "reviewer",
                    "available": True,
                    "category": "personnel",
                    "details": "Reviews risk assumptions and evaluation hygiene.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "daily bars",
                    "alternative": "hourly bars aggregated to daily decisions",
                    "condition": "Use if the daily dataset is delayed or incomplete.",
                    "tradeoff": "The plan must justify any slippage-model change.",
                },
                {
                    "original": "risk reviewer",
                    "alternative": "pre-committed risk checklist",
                    "condition": "Use if the reviewer is unavailable.",
                    "tradeoff": "The plan must include explicit drawdown checks.",
                },
            ],
            "budget_total": 950.0,
            "staff_count": 1,
            "time_limit_days": 3,
            "max_rounds": MAX_ROUNDS,
        },
        {
            "domain_id": "finance_trading",
            "paper_title": "Planning an offline momentum backtest for liquid futures",
            "paper_hypothesis": "A disciplined momentum design can be evaluated offline with strict liquidity and cost assumptions.",
            "paper_method": "Run a futures momentum backtest with predefined roll logic, cost model, and walk-forward evaluation.",
            "paper_key_finding": "The plan is accepted only if walk-forward evaluation and liquidity constraints are explicit.",
            "task_summary": "Design an offline momentum futures backtest under liquidity, slippage, and review constraints.",
            "success_criteria": [
                "Use only offline walk-forward evaluation.",
                "Model roll handling and transaction costs explicitly.",
                "Keep liquidity and concentration rules visible in the final plan.",
            ],
            "reference_summary": "A valid plan models roll logic, transaction costs, and walk-forward evaluation with liquidity limits.",
            "required_elements": [
                "walk-forward evaluation",
                "roll logic",
                "transaction cost assumption",
                "liquidity limit",
            ],
            "flexible_elements": [
                "lookback horizon",
                "rebalance frequency",
                "reporting template",
            ],
            "target_metric": "risk_adjusted_return",
            "target_value": "positive out-of-sample Sharpe with liquidity-compliant trades",
            "constraints": [
                {
                    "key": "max_markets",
                    "label": "Maximum simultaneous markets",
                    "quantity": 4,
                    "unit": "markets",
                    "comparator": "<=",
                    "hard": False,
                    "details": "Keep the design narrow enough to review in one session.",
                },
                {
                    "key": "max_drawdown",
                    "label": "Maximum allowed drawdown",
                    "quantity": 10,
                    "unit": "percent",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The plan must remain inside the drawdown guardrail.",
                },
                {
                    "key": "live_execution",
                    "label": "Execution mode",
                    "quantity": None,
                    "unit": None,
                    "comparator": "=",
                    "hard": True,
                    "details": "Only offline design and backtesting are allowed.",
                },
            ],
            "resources": [
                {
                    "key": "futures_dataset",
                    "label": "Historical futures dataset",
                    "quantity": 1,
                    "unit": "dataset",
                    "available": True,
                    "category": "data",
                    "details": "Includes roll metadata and contract-level liquidity fields.",
                },
                {
                    "key": "backtest_engine",
                    "label": "Walk-forward backtest engine",
                    "quantity": 1,
                    "unit": "engine",
                    "available": True,
                    "category": "tool",
                    "details": "Supports walk-forward slicing and execution-cost modeling.",
                },
                {
                    "key": "risk_reviewer",
                    "label": "Risk reviewer",
                    "quantity": 1,
                    "unit": "reviewer",
                    "available": True,
                    "category": "personnel",
                    "details": "Checks liquidity and concentration assumptions.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "contract-level backtest",
                    "alternative": "continuous-series backtest with explicit caveat",
                    "condition": "Use if contract roll metadata is incomplete.",
                    "tradeoff": "The plan must document the fidelity loss clearly.",
                }
            ],
            "budget_total": 1100.0,
            "staff_count": 1,
            "time_limit_days": 4,
            "max_rounds": MAX_ROUNDS,
        },
    ]
    return rng.choice(cases)

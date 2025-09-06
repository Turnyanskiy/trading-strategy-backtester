"""Entry point for package."""

import random

from .backtester import Backtester
from .data_handler import DataHandler
from .execution_handler import ExecutionHandler
from .portfolio import Portfolio
from .strategies import SimpleMomentumStrategy

# TODO: Create command line tool which uses Hydra to take a config.

random.seed(0)

stocks = [
    "AAPL",
    "MSFT",
    "GOOG",
    "META",
    "AMZN",
    "TSLA",
    "NVDA",
    "AMD",
    "PLTR",
    "INTC",
    "AVGO",
    "NFLX",
]

print(stocks)
data = DataHandler(stocks, "2024-01-01", "2024-06-01", "1d")
strategy = SimpleMomentumStrategy(stocks)
portfolio = Portfolio()
execution_handler = ExecutionHandler()
backtester = Backtester(data, strategy, portfolio, execution_handler)

backtester.run()

history = portfolio.get_position_history()
for k, v in history.items():
    print(k)
    print(v)

print(portfolio.summary())

"""Entry point for package."""

from .backtester import Backtester
from .data_handler import DataHandler
from .execution_handler import ExecutionHandler
from .portfolio import Portfolio
from .strategies import RandomStrategy

# TODO: Create command line tool which uses Hydra to take a config.
data = DataHandler("AAPL", "2024-01-01", "2024-06-01")
strategy = RandomStrategy()
portfolio = Portfolio()
execution_handler = ExecutionHandler()
backtester = Backtester(data, strategy, portfolio, execution_handler)

backtester.run()

history = portfolio.get_position_history()
print(history["portfolio"])
print(history["AAPL"])

print(portfolio.summary())

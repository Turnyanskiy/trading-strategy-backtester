""""""
from .execution_handler import ExecutionHandler
from .data_handler import DataHandler
from .strategies import RandomStrategy
from .backtester import Backtester
from .portfolio import Portfolio

# TODO: Create command line tool which uses Hydra to take a config.
data = DataHandler("AAPL", "2024-01-01", "2024-06-01")
strategy = RandomStrategy()
portfolio = Portfolio()
execution_handler = ExecutionHandler()
backtester = Backtester(data, strategy, portfolio, execution_handler)

backtester.run()

print(portfolio.get_position_history())

"""Backtester class to simulate capital, positions and portfolio value."""
from .strategies import Strategy
from .data_handler import DataHandler
from .portfolio import Portfolio
from .execution_handler import ExecutionHandler
from collections import deque
from typing import Deque
from .events import Event, FillEvent, MarketEvent, OrderEvent, SignalEvent



class Backtester:

    def __init__(self, data_handler: DataHandler, strategy: Strategy, portfolio: Portfolio, execution_handler: ExecutionHandler) -> None:
        """"""
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution_handler = execution_handler

        self.event_queue: Deque[Event] = deque()

        self.data_handler.event_queue = self.event_queue
        self.strategy.event_queue = self.event_queue
        self.portfolio.event_queue = self.event_queue
        self.execution_handler.event_queue = self.event_queue
            

    def run(self) -> None:
        """"""
        for _ in self.data_handler:

            while self.event_queue:
                event = self.event_queue.popleft()
                
                match event:
                    case MarketEvent():
                        self.strategy.generate_signal(event)
                        self.execution_handler.on_market_event(event)
                        self.portfolio.on_market_event(event)
                    case SignalEvent():
                        self.portfolio.on_signal_event(event)
                    case OrderEvent():
                        self.execution_handler.execute_order(event)
                    case FillEvent():
                        self.portfolio.on_fill_event(event)
                    case _:
                        raise ValueError(f"Unkown event type: {event.type}")



"""Backtester module.

This module contains the Backtester class, which simulates the trading process by
coordinating the data handler, strategy, portfolio, and execution_handler.
"""

from collections import deque
from typing import Deque

from .data_handler import DataHandler
from .events import Event, FillEvent, MarketEvent, OrderEvent, SignalEvent
from .execution_handler import ExecutionHandler
from .portfolio import Portfolio
from .strategies import Strategy


class Backtester:
    """Backtester to manage events.

    Coordinates the data handler, strategy, portfolio, and execution_handler by
    processing events from a shared queue during simulation.
    """

    def __init__(
        self,
        data_handler: DataHandler,
        strategy: Strategy,
        portfolio: Portfolio,
        execution_handler: ExecutionHandler,
    ) -> None:
        """Initialize the backtester.

        Args:
            data_handler (DataHandler): Component responsible for providing market data
                and generating MarketEvents.
            strategy (Strategy): Trading strategy that handles MarketEvents and
                generates SignalEvents.
            portfolio (Portfolio): Component tracking positions, cash, and portfolio
                value. Handles SignalEvents and FillEvents and generates OrderEvents.
            execution_handler (ExecutionHandler): Simulates the market execution of
                orders, handles OrderEvents and produces FillEvents.
        """
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
        """Run the backtest.

        Iterates over the data handler, generating market events, and processes all
        events in the queue according to their type until no more events remain.

        Raises:
            ValueError: If an unknown event type is encountered.
        """
        for _ in self.data_handler:
            while self.event_queue:
                event = self.event_queue.popleft()

                match event:
                    case MarketEvent():
                        self.strategy.on_market_event(event)
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

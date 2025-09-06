"""Strategy module.

This module defines the base class for trading strategies.
"""

from typing import Deque

from ..events import Event, MarketEvent


class Strategy:
    """Base class for trading strategies.

    Strategies must inherit from this class and implement the generate_signal method.
    """

    def __init__(self, tickers: str | list[str]):
        """Initialize the strategy.

        Args:
            tickers (str | list[str]): Ticker(s) symbol to use strategy on.
        """
        self.event_queue: Deque[Event] | None = None
        self.tickers: set[str] = set(tickers)

    def on_market_event(self, event: MarketEvent) -> None:
        """Filter market events by ticker symbol.

        Args:
            event (MarketEvent): Latest market event with pricing information.

        Raises:
            RuntimeError: If the event queue has not been set.
        """
        if self.event_queue is None:
            raise RuntimeError("RandomStrategy: event_queue not set")

        if event.symbol in self.tickers:
            self.generate_signal(event)

    def generate_signal(self, event: MarketEvent) -> None:
        """Generate trading signals from market data.

        Trading signal stregth are in the range [-1, 1].

        Args:
            event (MarketEvent): Latest market event with pricing information.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError

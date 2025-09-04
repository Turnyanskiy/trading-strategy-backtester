"""Strategy module.

This module defines the base class for trading strategies.
"""

from typing import Deque

from ..events import Event, MarketEvent


class Strategy:
    """Base class for trading strategies.

    Strategies must inherit from this class and implement the generate_signal method.
    """

    def __init__(self):
        """Initialize the strategy."""
        self.event_queue: Deque[Event] | None = None

    def generate_signal(self, event: MarketEvent) -> None:
        """Generate trading signals from market data.

        Trading signal stregth are in the range [-1, 1].

        Args:
            event (MarketEvent): Latest market event with pricing information.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError

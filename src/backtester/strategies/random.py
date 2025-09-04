"""Random trading strategy module.

This module defines a simple strategy that generates random buy/sell signals for
demonstration or testing purposes.
"""

import random

from ..events import MarketEvent, SignalEvent
from .base import Strategy


class RandomStrategy(Strategy):
    """Strategy that generates random trading signals.

    Produces SignalEvent with random strengths in the range [-1, 1] whenever a
    MarketEvent is received.
    """

    def generate_signal(self, event: MarketEvent) -> None:
        """Generate a random trading signal in the range [-1, 1].

        Args:
            event (MarketEvent): Market event containing symbol and price data.

        Raises:
            RuntimeError: If the event queue has not been set.
        """
        if self.event_queue is None:
            raise RuntimeError("RandomStrategy: event_queue not set")
        self.event_queue.append(SignalEvent(event.symbol, random.uniform(-1, 1)))

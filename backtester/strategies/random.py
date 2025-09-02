""""""
from .base import Strategy
from ..events import MarketEvent, SignalEvent
import random

class RandomStrategy(Strategy):
    """"""

    def generate_signal(self, event: MarketEvent) -> None:
        """"""
        if self.event_queue is None:
            raise RuntimeError("RandomStrategy: event_queue not set")
        self.event_queue.append(SignalEvent(event.symbol, random.uniform(-1, 1)))

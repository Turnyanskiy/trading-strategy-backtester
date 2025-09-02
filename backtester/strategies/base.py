""""""
from ..events import Event, MarketEvent
from typing import Deque

class Strategy:
    """"""

    def __init__(self):
        self.event_queue: Deque[Event] | None = None

    def generate_signal(self, event: MarketEvent) -> None:
        """"""
        raise NotImplementedError



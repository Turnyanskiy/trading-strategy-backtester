""""""
from collections import deque
from typing import Deque
from .events import Event, MarketEvent, OrderEvent, FillEvent

class ExecutionHandler:
    """"""

    def __init__(self):
        """"""
        self.event_queue: Deque[Event] | None = None

        self.market_history: Deque[MarketEvent] = deque(maxlen=10)
        self.pending: list[FillEvent] = [] 
    
    def on_market_event(self, event: MarketEvent) -> None:
        """"""
        self.market_history.append(event)
        
        if self.pending:
            if self.event_queue is None:
                raise RuntimeError("ExecutionHandler: event_queue is not set")

            fill_event = self.pending.pop()
            fill_event.fill_cost = fill_event.quantity * event.open
            self.event_queue.append(fill_event)

    # TODO: Simulate slippage (with more accuracy) & fees
    def execute_order(self, event: OrderEvent) -> None:
        """"""
        if self.event_queue is None:
            raise RuntimeError("ExecutionHandler: event_queue is not set")

        self.pending.append(FillEvent(event.symbol, event.quantity, event.quantity * self.market_history[-1].open, 0))



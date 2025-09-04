"""Execution handler module.

This module contains the ExecutionHandler class, which simulates market order execution
by handling OrderEvents and appending FillEvents to the event queue created using
recent market data.
"""

from collections import deque
from typing import Deque

from .events import Event, FillEvent, MarketEvent, OrderEvent


class ExecutionHandler:
    """Simulate order execution.

    The execution handler listens for OrderEvents and converts them into FillEvents
    using recent market prices. FillEvents are append to the event queue.
    """

    def __init__(self):
        """Initialize the execution handler."""
        self.event_queue: Deque[Event] | None = None

        self.market_history: Deque[MarketEvent] = deque(maxlen=10)
        self.pending: list[FillEvent] = []

    # TODO: Allow the creation of several FillEvents for different tickers.
    def on_market_event(self, event: MarketEvent) -> None:
        """Handle a market event.

        Adds the event to market history and, if pending orders exist,
        converts them into a FillEvents.

        Args:
            event (MarketEvent): Latest market event with pricing information.

        Raises:
            RuntimeError: If the event queue is not set.
        """
        self.market_history.append(event)

        if self.pending:
            if self.event_queue is None:
                raise RuntimeError("ExecutionHandler: event_queue is not set")

            fill_event = self.pending.pop()
            fill_event.fill_cost = fill_event.quantity * event.open
            self.event_queue.append(fill_event)

    # TODO: Simulate slippage & fees
    def execute_order(self, event: OrderEvent) -> None:
        """Queue a new fill event for execution.

        Converts an OrderEvent into a pending FillEvent that will be processed
        on the next MarketEvent.

        Args:
            event (OrderEvent): Order event to be executed.

        Raises:
            RuntimeError: If the event queue is not set.
        """
        if self.event_queue is None:
            raise RuntimeError("ExecutionHandler: event_queue is not set")

        self.pending.append(
            FillEvent(
                event.symbol,
                event.quantity,
                event.quantity * self.market_history[-1].open,
                0,
            )
        )

"""Event system module.

This module defines the types and event dataclasses used to communicate between
components of the backtester.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

import pandas as pd


class EventType(Enum):
    """Enumeration of event types."""

    MARKET = auto()
    SIGNAL = auto()
    ORDER = auto()
    FILL = auto()


class OrderType(Enum):
    """Enumeration of order types."""

    MARKET = auto()
    LIMIT = auto()
    STOP = auto()


@dataclass(slots=True)
class Event:
    """Base class for all events.

    Attributes:
        type (EventType): The type of the event (set by subclasses).
        symbol (str): The ticker symbol the event refers to.
    """

    type: EventType = field(init=False)
    symbol: str


@dataclass(slots=True)
class MarketEvent(Event):
    """Event triggered on receipt of new market data.

    Attributes:
        datetime (pd.DatetimeIndex): Timestamp of the market data.
        open (float): Opening price of period.
        close (float): Closing price of period.
    """

    type: EventType = field(init=False, default=EventType.MARKET)
    datetime: pd.DatetimeIndex
    open: float
    close: float


@dataclass(slots=True)
class SignalEvent(Event):
    """Event triggered to indicate a trading signal.

    Attributes:
        strength (float): Signal strength in range [-1, 1] (positive = buy, negative =
            sell/short).
    """

    type: EventType = field(init=False, default=EventType.SIGNAL)
    strength: float


@dataclass(slots=True)
class OrderEvent(Event):
    """Event triggered on an order execution.

    Attributes:
        order_type (OrderType): Type of order (market, limit, stop).
        quantity (int): Number of units to trade.
    """

    type: EventType = field(init=False, default=EventType.ORDER)
    order_type: OrderType
    quantity: int


@dataclass(slots=True)
class FillEvent(Event):
    """Event triggered on a completed order fill.

    Attributes:
        quantity (int): Number of units filled.
        fill_cost (float): Cost of the filled trade.
        commission (float): Commission paid for the fill.
    """

    type: EventType = field(init=False, default=EventType.FILL)
    quantity: int
    fill_cost: float
    commission: float

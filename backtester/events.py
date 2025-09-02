""""""
from enum import Enum, auto
from dataclasses import dataclass, field
import pandas as pd


class EventType(Enum):
    MARKET = auto()
    SIGNAL = auto()
    ORDER = auto()
    FILL = auto()


class OrderType(Enum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()


@dataclass(slots=True)
class Event:
    type: EventType = field(init=False)
    symbol: str


@dataclass(slots=True)
class MarketEvent(Event):
    type: EventType = field(init=False, default=EventType.MARKET)
    datetime: pd.DatetimeIndex
    open: float
    close: float


@dataclass(slots=True)
class SignalEvent(Event):
    type: EventType = field(init=False, default=EventType.SIGNAL)
    strength: float


@dataclass(slots=True)
class OrderEvent(Event):
    type: EventType = field(init=False, default=EventType.ORDER)
    order_type: OrderType 
    quantity: int


@dataclass(slots=True)
class FillEvent(Event):
    type: EventType = field(init=False, default=EventType.FILL)
    quantity: int
    fill_cost: float
    commission: float

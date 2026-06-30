"""Core domain models for the customer lifecycle engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Customer events the engine reasons about."""

    SIGNUP = "signup"
    ACTIVATION = "activation"  # completed the key onboarding / "aha" action
    LOGIN = "login"
    FEATURE_USE = "feature_use"
    PAYMENT = "payment"
    SUPPORT_TICKET = "support_ticket"
    CANCELLATION = "cancellation"


class LifecycleStage(str, Enum):
    """Where a customer sits in their lifecycle."""

    NEW = "new"
    ONBOARDING = "onboarding"
    ACTIVATED = "activated"
    ENGAGED = "engaged"
    AT_RISK = "at_risk"
    CHURNED = "churned"


@dataclass(frozen=True)
class Event:
    """A single timestamped customer event."""

    type: EventType
    at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Customer:
    """A customer and their event history."""

    id: str
    name: str
    email: str
    signed_up_at: datetime
    plan: str = "free"
    events: list[Event] = field(default_factory=list)

    def events_of(self, *types: EventType) -> list[Event]:
        wanted = set(types)
        return [e for e in self.events if e.type in wanted]

    def has_event(self, type: EventType) -> bool:
        return any(e.type == type for e in self.events)

    def last_event_at(self) -> datetime | None:
        return max((e.at for e in self.events), default=None)

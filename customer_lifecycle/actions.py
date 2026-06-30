"""Lifecycle actions and pluggable dispatch.

The engine produces :class:`ActionRequest` objects; a :class:`ActionDispatcher`
decides what actually happens to them. The default :class:`LoggingDispatcher`
just records them, which keeps demos and tests side-effect free. In production
you'd subclass ``ActionDispatcher`` to send email (e.g. customer.io / Resend),
open a CRM task, or post to Slack.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    SEND_ONBOARDING = "send_onboarding_sequence"
    SEND_ACTIVATION_NUDGE = "send_activation_nudge"
    SEND_ENGAGEMENT_TIP = "send_engagement_tip"
    REQUEST_REVIEW = "request_review"
    SEND_REENGAGEMENT = "send_reengagement"
    FLAG_FOR_CSM = "flag_for_csm"
    WINBACK = "winback"


@dataclass(frozen=True)
class ActionRequest:
    type: ActionType
    customer_id: str
    channel: str = "email"
    reason: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


class ActionDispatcher:
    """Base class — override :meth:`dispatch` to wire up a real channel."""

    def dispatch(self, action: ActionRequest) -> None:  # pragma: no cover
        raise NotImplementedError


class LoggingDispatcher(ActionDispatcher):
    """Records dispatched actions in memory. Safe default for demos/tests."""

    def __init__(self) -> None:
        self.dispatched: list[ActionRequest] = []

    def dispatch(self, action: ActionRequest) -> None:
        self.dispatched.append(action)

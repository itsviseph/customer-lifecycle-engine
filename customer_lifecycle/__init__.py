"""customer_lifecycle — a small, explainable customer-lifecycle automation engine.

Ingest customer events -> score health & churn risk -> classify lifecycle stage
-> fire the right lifecycle actions (onboarding, re-engagement, CSM hand-off,
win-back), with optional LLM-personalised copy.
"""
from __future__ import annotations

from .actions import (
    ActionDispatcher,
    ActionRequest,
    ActionType,
    LoggingDispatcher,
)
from .engine import EngineResult, LifecycleEngine
from .health import HealthScore, compute_health
from .models import Customer, Event, EventType, LifecycleStage
from .personalize import MessageProvider, TemplateProvider, personalize
from .rules import LifecycleRule, default_rules, evaluate
from .stages import determine_stage

__all__ = [
    "ActionDispatcher",
    "ActionRequest",
    "ActionType",
    "LoggingDispatcher",
    "EngineResult",
    "LifecycleEngine",
    "HealthScore",
    "compute_health",
    "Customer",
    "Event",
    "EventType",
    "LifecycleStage",
    "MessageProvider",
    "TemplateProvider",
    "personalize",
    "LifecycleRule",
    "default_rules",
    "evaluate",
    "determine_stage",
]

__version__ = "0.1.0"

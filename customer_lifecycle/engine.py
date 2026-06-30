"""The orchestrator: ingest a customer, score, stage, decide, and dispatch."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .actions import ActionDispatcher, ActionRequest, LoggingDispatcher
from .health import HealthScore, compute_health
from .models import Customer, LifecycleStage
from .rules import LifecycleRule, evaluate
from .stages import determine_stage


@dataclass
class EngineResult:
    customer_id: str
    health: HealthScore
    stage: LifecycleStage
    actions: list[ActionRequest]


class LifecycleEngine:
    """Runs the full pipeline for one or many customers.

    >>> from datetime import datetime
    >>> engine = LifecycleEngine()
    >>> result = engine.process(customer, now=datetime(2026, 6, 1))  # doctest: +SKIP
    """

    def __init__(
        self,
        dispatcher: ActionDispatcher | None = None,
        rules: list[LifecycleRule] | None = None,
    ) -> None:
        self.dispatcher = dispatcher or LoggingDispatcher()
        self.rules = rules

    def process(self, customer: Customer, now: datetime | None = None) -> EngineResult:
        now = now or datetime.now()
        health = compute_health(customer, now)
        stage = determine_stage(customer, health, now)
        actions = evaluate(customer, health, stage, self.rules)
        for action in actions:
            self.dispatcher.dispatch(action)
        return EngineResult(customer.id, health, stage, actions)

    def run_batch(
        self, customers: list[Customer], now: datetime | None = None
    ) -> list[EngineResult]:
        return [self.process(c, now) for c in customers]

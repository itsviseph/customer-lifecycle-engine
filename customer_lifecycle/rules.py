"""Declarative lifecycle rules: (stage + health) -> actions.

Rules are plain data so they are easy to read, test, and extend. Swap in your
own ruleset by passing a list of :class:`LifecycleRule` to the engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .actions import ActionRequest, ActionType
from .health import HealthScore
from .models import Customer, LifecycleStage

Condition = Callable[[Customer, HealthScore, LifecycleStage], bool]

HIGH_CHURN_RISK = 0.7


@dataclass(frozen=True)
class LifecycleRule:
    name: str
    when: Condition
    action_type: ActionType
    channel: str = "email"
    reason: str = ""

    def applies(
        self, customer: Customer, health: HealthScore, stage: LifecycleStage
    ) -> bool:
        return self.when(customer, health, stage)


def default_rules() -> list[LifecycleRule]:
    """A sensible starter ruleset covering the whole lifecycle."""
    return [
        LifecycleRule(
            "onboard-new",
            lambda c, h, s: s == LifecycleStage.NEW,
            ActionType.SEND_ONBOARDING,
            reason="welcome new signup",
        ),
        LifecycleRule(
            "nudge-stalled-onboarding",
            lambda c, h, s: s == LifecycleStage.ONBOARDING,
            ActionType.SEND_ACTIVATION_NUDGE,
            reason="signed up but not activated",
        ),
        LifecycleRule(
            "tip-activated",
            lambda c, h, s: s == LifecycleStage.ACTIVATED,
            ActionType.SEND_ENGAGEMENT_TIP,
            reason="drive deeper adoption",
        ),
        LifecycleRule(
            "review-engaged",
            lambda c, h, s: s == LifecycleStage.ENGAGED,
            ActionType.REQUEST_REVIEW,
            reason="happy customer — ask for a review",
        ),
        LifecycleRule(
            "reengage-at-risk",
            lambda c, h, s: s == LifecycleStage.AT_RISK,
            ActionType.SEND_REENGAGEMENT,
            reason="health is dropping",
        ),
        LifecycleRule(
            "csm-high-risk",
            lambda c, h, s: s == LifecycleStage.AT_RISK and h.churn_risk >= HIGH_CHURN_RISK,
            ActionType.FLAG_FOR_CSM,
            channel="internal",
            reason="high churn risk — needs a human",
        ),
        LifecycleRule(
            "winback-churned",
            lambda c, h, s: s == LifecycleStage.CHURNED,
            ActionType.WINBACK,
            reason="win-back campaign",
        ),
    ]


def evaluate(
    customer: Customer,
    health: HealthScore,
    stage: LifecycleStage,
    rules: list[LifecycleRule] | None = None,
) -> list[ActionRequest]:
    """Return every action whose rule fires for this customer."""
    rules = default_rules() if rules is None else rules
    return [
        ActionRequest(
            type=rule.action_type,
            customer_id=customer.id,
            channel=rule.channel,
            reason=rule.reason,
        )
        for rule in rules
        if rule.applies(customer, health, stage)
    ]

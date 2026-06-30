"""Map a customer + health score onto a lifecycle stage."""
from __future__ import annotations

from datetime import datetime, timedelta

from .health import HealthScore
from .models import Customer, EventType, LifecycleStage

ONBOARDING_GRACE_DAYS = 7
CHURN_INACTIVE_DAYS = 60
ENGAGED_SCORE = 70
AT_RISK_SCORE = 40


def determine_stage(
    customer: Customer, health: HealthScore, now: datetime
) -> LifecycleStage:
    """Return the lifecycle stage for ``customer`` as of ``now``."""
    if customer.has_event(EventType.CANCELLATION):
        return LifecycleStage.CHURNED

    last = customer.last_event_at()
    if last is not None and (now - last) > timedelta(days=CHURN_INACTIVE_DAYS):
        return LifecycleStage.CHURNED

    activated = customer.has_event(EventType.ACTIVATION)
    age_days = (now - customer.signed_up_at).total_seconds() / 86_400.0

    if not activated:
        # Fresh signups get a grace window before we treat onboarding as stalled.
        if age_days <= ONBOARDING_GRACE_DAYS:
            return LifecycleStage.NEW
        return LifecycleStage.ONBOARDING

    # Activated customers are graded by health.
    if health.score >= ENGAGED_SCORE:
        return LifecycleStage.ENGAGED
    if health.score < AT_RISK_SCORE:
        return LifecycleStage.AT_RISK
    return LifecycleStage.ACTIVATED

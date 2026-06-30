"""Customer health scoring and churn-risk estimation.

The score is a transparent, rule-based signal (0-100) derived from a customer's
event history. Every contribution is recorded in ``reasons`` so the output is
explainable — important when a CSM or a customer asks "why?".
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import Customer, EventType

# Tunable knobs (kept here so they are easy to find and test).
ACTIVITY_WINDOW_DAYS = 30
INACTIVE_AT_RISK_DAYS = 14
SUPPORT_TICKET_FRICTION_THRESHOLD = 3


@dataclass(frozen=True)
class HealthScore:
    score: int  # 0-100
    churn_risk: float  # 0.0 (healthy) - 1.0 (almost certainly churning)
    reasons: list[str]


def _days_between(then: datetime | None, now: datetime) -> float | None:
    if then is None:
        return None
    return (now - then).total_seconds() / 86_400.0


def compute_health(customer: Customer, now: datetime) -> HealthScore:
    """Compute an explainable health score for ``customer`` as of ``now``."""
    if customer.has_event(EventType.CANCELLATION):
        return HealthScore(score=0, churn_risk=1.0, reasons=["customer has cancelled"])

    reasons: list[str] = []
    score = 50  # neutral baseline

    # --- Activation ---------------------------------------------------------
    if customer.has_event(EventType.ACTIVATION):
        score += 15
        reasons.append("activated (+15)")
    else:
        score -= 10
        reasons.append("not activated (-10)")

    # --- Recent engagement --------------------------------------------------
    window_start = now - timedelta(days=ACTIVITY_WINDOW_DAYS)
    recent = [
        e
        for e in customer.events
        if e.type in (EventType.LOGIN, EventType.FEATURE_USE) and e.at >= window_start
    ]
    eng_points = min(len(recent) * 3, 25)
    score += eng_points
    reasons.append(
        f"{len(recent)} engagement events in {ACTIVITY_WINDOW_DAYS}d (+{eng_points})"
    )

    # --- Recency ------------------------------------------------------------
    days_since = _days_between(customer.last_event_at(), now)
    if days_since is None:
        score -= 15
        reasons.append("no activity recorded (-15)")
    elif days_since > INACTIVE_AT_RISK_DAYS:
        penalty = min(int(days_since - INACTIVE_AT_RISK_DAYS) * 2, 30)
        score -= penalty
        reasons.append(f"inactive {days_since:.0f}d (-{penalty})")
    else:
        score += 10
        reasons.append(f"active recently ({days_since:.0f}d ago) (+10)")

    # --- Monetisation -------------------------------------------------------
    if customer.has_event(EventType.PAYMENT):
        score += 10
        reasons.append("paying customer (+10)")

    # --- Friction -----------------------------------------------------------
    tickets = len(customer.events_of(EventType.SUPPORT_TICKET))
    if tickets >= SUPPORT_TICKET_FRICTION_THRESHOLD:
        score -= 8
        reasons.append(f"{tickets} support tickets (-8)")

    score = max(0, min(100, score))
    churn_risk = round(1.0 - score / 100.0, 2)
    return HealthScore(score=score, churn_risk=churn_risk, reasons=reasons)

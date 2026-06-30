from datetime import datetime, timedelta

from customer_lifecycle import (
    Customer,
    Event,
    EventType,
    LifecycleStage,
    compute_health,
    determine_stage,
)

NOW = datetime(2026, 6, 1, 12, 0, 0)


def ev(type: EventType, days_ago: float) -> Event:
    return Event(type=type, at=NOW - timedelta(days=days_ago))


def cust(signup_days_ago: float, events) -> Customer:
    return Customer(
        id="c",
        name="N",
        email="e@e.com",
        signed_up_at=NOW - timedelta(days=signup_days_ago),
        events=events,
    )


def stage_of(c: Customer) -> LifecycleStage:
    return determine_stage(c, compute_health(c, NOW), NOW)


def test_fresh_signup_is_new():
    assert stage_of(cust(2, [ev(EventType.SIGNUP, 2)])) == LifecycleStage.NEW


def test_unactivated_past_grace_is_onboarding():
    c = cust(20, [ev(EventType.SIGNUP, 20), ev(EventType.LOGIN, 18)])
    assert stage_of(c) == LifecycleStage.ONBOARDING


def test_cancellation_is_churned():
    c = cust(30, [ev(EventType.SIGNUP, 30), ev(EventType.CANCELLATION, 1)])
    assert stage_of(c) == LifecycleStage.CHURNED


def test_long_inactivity_is_churned():
    c = cust(
        120,
        [ev(EventType.SIGNUP, 120), ev(EventType.ACTIVATION, 119), ev(EventType.LOGIN, 90)],
    )
    assert stage_of(c) == LifecycleStage.CHURNED


def test_active_paying_customer_is_engaged():
    events = [ev(EventType.SIGNUP, 60), ev(EventType.ACTIVATION, 58), ev(EventType.PAYMENT, 55)]
    events += [ev(EventType.LOGIN, d) for d in (1, 3, 5, 7)]
    events += [ev(EventType.FEATURE_USE, d) for d in (1, 2)]
    assert stage_of(cust(60, events)) == LifecycleStage.ENGAGED


def test_activated_but_unhealthy_is_at_risk():
    c = cust(50, [ev(EventType.SIGNUP, 50), ev(EventType.ACTIVATION, 48), ev(EventType.LOGIN, 32)])
    assert stage_of(c) == LifecycleStage.AT_RISK


def test_activated_moderate_health_is_activated():
    c = cust(30, [ev(EventType.SIGNUP, 30), ev(EventType.ACTIVATION, 28), ev(EventType.LOGIN, 18)])
    assert stage_of(c) == LifecycleStage.ACTIVATED

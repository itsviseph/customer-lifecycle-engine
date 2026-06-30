from datetime import datetime, timedelta

from customer_lifecycle import Customer, Event, EventType, compute_health

NOW = datetime(2026, 6, 1, 12, 0, 0)


def ev(type: EventType, days_ago: float) -> Event:
    return Event(type=type, at=NOW - timedelta(days=days_ago))


def make(signup_days_ago: float = 30, events=None) -> Customer:
    return Customer(
        id="c1",
        name="Test",
        email="t@example.com",
        signed_up_at=NOW - timedelta(days=signup_days_ago),
        events=events or [],
    )


def test_cancelled_customer_is_zero_health():
    c = make(events=[ev(EventType.SIGNUP, 40), ev(EventType.CANCELLATION, 1)])
    h = compute_health(c, NOW)
    assert h.score == 0
    assert h.churn_risk == 1.0


def test_engaged_paying_customer_scores_high():
    events = [
        ev(EventType.SIGNUP, 60),
        ev(EventType.ACTIVATION, 58),
        ev(EventType.PAYMENT, 55),
    ]
    events += [ev(EventType.LOGIN, d) for d in (1, 3, 5, 7, 10)]
    events += [ev(EventType.FEATURE_USE, d) for d in (1, 2, 4)]
    h = compute_health(make(60, events), NOW)
    assert h.score >= 70
    assert h.churn_risk <= 0.3


def test_inactive_unactivated_customer_scores_low():
    c = make(40, [ev(EventType.SIGNUP, 40), ev(EventType.LOGIN, 35)])
    h = compute_health(c, NOW)
    assert h.score < 40
    assert h.churn_risk > 0.6


def test_engagement_increases_score():
    base = make(events=[ev(EventType.SIGNUP, 20), ev(EventType.ACTIVATION, 19)])
    busy_events = [ev(EventType.SIGNUP, 20), ev(EventType.ACTIVATION, 19)]
    busy_events += [ev(EventType.FEATURE_USE, d) for d in (1, 2, 3, 4, 5)]
    busy = make(events=busy_events)
    assert compute_health(busy, NOW).score > compute_health(base, NOW).score


def test_score_is_bounded():
    h = compute_health(make(1, [ev(EventType.SIGNUP, 1)]), NOW)
    assert 0 <= h.score <= 100
    assert 0.0 <= h.churn_risk <= 1.0


def test_reasons_are_populated():
    h = compute_health(make(10, [ev(EventType.SIGNUP, 10), ev(EventType.ACTIVATION, 9)]), NOW)
    assert h.reasons
    assert all(isinstance(r, str) for r in h.reasons)

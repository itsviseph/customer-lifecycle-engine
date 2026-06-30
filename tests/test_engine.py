from datetime import datetime, timedelta

from customer_lifecycle import (
    ActionType,
    Customer,
    Event,
    EventType,
    LifecycleEngine,
    LifecycleStage,
    LoggingDispatcher,
)

NOW = datetime(2026, 6, 1)


def ev(type: EventType, days_ago: float) -> Event:
    return Event(type=type, at=NOW - timedelta(days=days_ago))


def test_process_returns_result_and_dispatches():
    c = Customer(
        id="c",
        name="N",
        email="e@e.com",
        signed_up_at=NOW - timedelta(days=2),
        events=[ev(EventType.SIGNUP, 2)],
    )
    dispatcher = LoggingDispatcher()
    engine = LifecycleEngine(dispatcher=dispatcher)

    result = engine.process(c, now=NOW)

    assert result.stage == LifecycleStage.NEW
    assert result.actions
    assert dispatcher.dispatched == result.actions
    assert ActionType.SEND_ONBOARDING in {a.type for a in result.actions}


def test_run_batch_processes_all_customers():
    c1 = Customer(
        id="a",
        name="A",
        email="a@e.com",
        signed_up_at=NOW - timedelta(days=2),
        events=[ev(EventType.SIGNUP, 2)],
    )
    c2 = Customer(
        id="b",
        name="B",
        email="b@e.com",
        signed_up_at=NOW - timedelta(days=90),
        events=[ev(EventType.SIGNUP, 90), ev(EventType.CANCELLATION, 1)],
    )

    results = LifecycleEngine().run_batch([c1, c2], now=NOW)

    assert len(results) == 2
    assert results[0].stage == LifecycleStage.NEW
    assert results[1].stage == LifecycleStage.CHURNED


def test_custom_dispatcher_receives_actions():
    seen = []

    class CapturingDispatcher(LoggingDispatcher):
        def dispatch(self, action):
            seen.append(action.type)
            super().dispatch(action)

    c = Customer(
        id="c",
        name="N",
        email="e@e.com",
        signed_up_at=NOW - timedelta(days=2),
        events=[ev(EventType.SIGNUP, 2)],
    )
    LifecycleEngine(dispatcher=CapturingDispatcher()).process(c, now=NOW)
    assert ActionType.SEND_ONBOARDING in seen

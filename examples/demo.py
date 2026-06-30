"""Runnable demo. From the repo root:  python examples/demo.py"""
from __future__ import annotations

from datetime import datetime, timedelta

from customer_lifecycle import (
    Customer,
    Event,
    EventType,
    LifecycleEngine,
    LoggingDispatcher,
    personalize,
)

NOW = datetime(2026, 6, 1)


def ev(type: EventType, days_ago: float) -> Event:
    return Event(type=type, at=NOW - timedelta(days=days_ago))


def sample_customers() -> list[Customer]:
    return [
        Customer("c1", "Asha", "asha@acme.com", NOW - timedelta(days=2), "trial",
                 [ev(EventType.SIGNUP, 2)]),
        Customer("c2", "Ben", "ben@beta.io", NOW - timedelta(days=20), "trial",
                 [ev(EventType.SIGNUP, 20), ev(EventType.LOGIN, 18)]),
        Customer("c3", "Cara", "cara@corp.com", NOW - timedelta(days=90), "pro",
                 [ev(EventType.SIGNUP, 90), ev(EventType.ACTIVATION, 88), ev(EventType.PAYMENT, 85)]
                 + [ev(EventType.LOGIN, d) for d in (1, 3, 5, 7)]
                 + [ev(EventType.FEATURE_USE, d) for d in (1, 2)]),
        Customer("c4", "Dev", "dev@delta.dev", NOW - timedelta(days=50), "pro",
                 [ev(EventType.SIGNUP, 50), ev(EventType.ACTIVATION, 48), ev(EventType.LOGIN, 32)]
                 + [ev(EventType.SUPPORT_TICKET, d) for d in (30, 25, 20)]),
        Customer("c5", "Eli", "eli@echo.co", NOW - timedelta(days=120), "free",
                 [ev(EventType.SIGNUP, 120), ev(EventType.ACTIVATION, 118), ev(EventType.CANCELLATION, 5)]),
    ]


def main() -> None:
    engine = LifecycleEngine(dispatcher=LoggingDispatcher())
    print("Customer lifecycle run (as of %s)\n%s" % (NOW.date(), "=" * 60))
    for customer in sample_customers():
        result = engine.process(customer, now=NOW)
        print(
            f"\n{customer.name} ({customer.id})  ·  stage={result.stage.value}  "
            f"health={result.health.score}/100  churn_risk={result.health.churn_risk}"
        )
        for action in result.actions:
            print(f"   -> {action.type.value} [{action.channel}] — {action.reason}")
            print(f"      preview: {personalize(action, customer)}")


if __name__ == "__main__":
    main()

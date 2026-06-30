from datetime import datetime

from customer_lifecycle import (
    ActionType,
    Customer,
    HealthScore,
    LifecycleStage,
    evaluate,
)

C = Customer(id="c", name="N", email="e@e.com", signed_up_at=datetime(2026, 1, 1))


def health(score: int) -> HealthScore:
    return HealthScore(score=score, churn_risk=round(1 - score / 100, 2), reasons=[])


def types(actions):
    return {a.type for a in actions}


def test_new_triggers_onboarding():
    assert ActionType.SEND_ONBOARDING in types(
        evaluate(C, health(50), LifecycleStage.NEW)
    )


def test_engaged_triggers_review_request():
    assert ActionType.REQUEST_REVIEW in types(
        evaluate(C, health(85), LifecycleStage.ENGAGED)
    )


def test_at_risk_low_churn_reengages_without_csm():
    acts = types(evaluate(C, health(45), LifecycleStage.AT_RISK))  # churn 0.55 < 0.7
    assert ActionType.SEND_REENGAGEMENT in acts
    assert ActionType.FLAG_FOR_CSM not in acts


def test_at_risk_high_churn_flags_csm():
    acts = types(evaluate(C, health(20), LifecycleStage.AT_RISK))  # churn 0.8 >= 0.7
    assert ActionType.FLAG_FOR_CSM in acts
    assert ActionType.SEND_REENGAGEMENT in acts


def test_churned_triggers_winback():
    assert ActionType.WINBACK in types(evaluate(C, health(0), LifecycleStage.CHURNED))


def test_empty_ruleset_yields_no_actions():
    assert evaluate(C, health(50), LifecycleStage.NEW, rules=[]) == []


def test_actions_carry_customer_id():
    acts = evaluate(C, health(50), LifecycleStage.NEW)
    assert acts and all(a.customer_id == "c" for a in acts)

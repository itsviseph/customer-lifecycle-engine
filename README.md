# customer-lifecycle-engine

A small, **explainable customer-lifecycle automation engine** in pure Python.

Feed it a customer's event history and it will:

1. **Score health & churn risk** (0–100 / 0.0–1.0) — every point is explained, so a CSM or a customer can always ask *"why?"*
2. **Classify the lifecycle stage** — `new → onboarding → activated → engaged → at_risk → churned`
3. **Decide the right lifecycle action** via a declarative rule set — onboarding sequence, activation nudge, engagement tip, review request, re-engagement, **CSM hand-off for high-risk accounts**, win-back
4. **Personalise the copy** — offline templates by default, or drop in an LLM (Claude / OpenAI) provider in production without touching the engine

No runtime dependencies. Fully unit-tested.

> Built as a focused demonstration of customer-success / lifecycle engineering: turning raw product signals into the right, timely, personalised touch — automatically.

## Quickstart

```bash
git clone https://github.com/itsviseph/customer-lifecycle-engine.git
cd customer-lifecycle-engine
python examples/demo.py
```

Example output:

```
Cara (c3)  ·  stage=engaged  health=100/100  churn_risk=0.0
   -> request_review [email] — happy customer — ask for a review
      preview: Hi Cara, so glad it's working for you! Would you share a quick review?

Dev (c4)  ·  stage=at_risk  health=35/100  churn_risk=0.65
   -> send_reengagement [email] — health is dropping
      preview: Hi Dev, we miss you — here's what's new since you last logged in.
```

## Usage

```python
from datetime import datetime, timedelta
from customer_lifecycle import Customer, Event, EventType, LifecycleEngine

now = datetime(2026, 6, 1)
customer = Customer(
    id="c1", name="Asha", email="asha@acme.com",
    signed_up_at=now - timedelta(days=2),
    events=[Event(EventType.SIGNUP, now - timedelta(days=2))],
)

result = LifecycleEngine().process(customer, now=now)
print(result.stage, result.health.score, [a.type.value for a in result.actions])
# LifecycleStage.NEW 35 ['send_onboarding_sequence']
```

### Plugging in real channels and an LLM

The defaults are side-effect free. In production you subclass two things:

```python
from customer_lifecycle import ActionDispatcher, LifecycleEngine, personalize

class EmailDispatcher(ActionDispatcher):
    def dispatch(self, action):
        # send via your ESP / CRM (customer.io, Resend, Salesforce, ...)
        ...

class ClaudeProvider:                      # satisfies the MessageProvider protocol
    def generate(self, system, prompt):
        # call Claude / OpenAI and return the message
        ...

engine = LifecycleEngine(dispatcher=EmailDispatcher())
# personalize(action, customer, provider=ClaudeProvider())  ->  LLM-written copy
```

## Design

| Module | Responsibility |
|---|---|
| `models.py` | `Customer`, `Event`, and the `EventType` / `LifecycleStage` enums |
| `health.py` | transparent, weighted health & churn-risk scoring |
| `stages.py` | maps a customer + health onto a lifecycle stage |
| `rules.py` | declarative `(stage, health) -> action` rules (bring your own) |
| `actions.py` | action requests + a pluggable dispatcher |
| `personalize.py` | offline templates by default; LLM provider in prod |
| `engine.py` | orchestrates ingest → score → stage → rules → dispatch |

The scoring weights and stage thresholds are deliberately simple constants at the top of each module, so they're easy to read, tune, and test.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Covers health scoring, stage transitions (including churn and at-risk edges), rule firing (incl. the high-churn CSM escalation), personalisation, and the end-to-end engine.

## License

MIT

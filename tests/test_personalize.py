from datetime import datetime

from customer_lifecycle import (
    ActionRequest,
    ActionType,
    Customer,
    TemplateProvider,
    personalize,
)

C = Customer(id="c7", name="Asha", email="a@e.com", signed_up_at=datetime(2026, 1, 1))


def test_template_provider_personalises_with_name():
    a = ActionRequest(type=ActionType.SEND_ONBOARDING, customer_id="c7")
    assert "Asha" in personalize(a, C)


def test_every_action_type_has_copy():
    for action_type in ActionType:
        a = ActionRequest(type=action_type, customer_id="c7")
        msg = personalize(a, C)
        assert isinstance(msg, str) and msg.strip()


def test_template_provider_used_directly():
    a = ActionRequest(type=ActionType.WINBACK, customer_id="c7")
    assert "Asha" in TemplateProvider().message_for(a, C)


def test_custom_llm_provider_is_used():
    class FakeLLM:
        def __init__(self):
            self.calls: list[tuple[str, str]] = []

        def generate(self, system: str, prompt: str) -> str:
            self.calls.append((system, prompt))
            return "LLM-generated copy"

    llm = FakeLLM()
    a = ActionRequest(
        type=ActionType.SEND_REENGAGEMENT, customer_id="c7", reason="health dropping"
    )
    msg = personalize(a, C, provider=llm)
    assert msg == "LLM-generated copy"
    assert llm.calls
    assert "Asha" in llm.calls[0][1]  # the customer name made it into the prompt

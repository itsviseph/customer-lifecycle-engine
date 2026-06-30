"""Turn an action into customer-facing copy.

By default this uses an offline, deterministic :class:`TemplateProvider` so the
demo and tests run with no API keys. The :class:`MessageProvider` protocol lets
you drop in an LLM (Claude / OpenAI) in production to personalise copy per
customer — the engine code never changes.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from .actions import ActionRequest
from .models import Customer


@runtime_checkable
class MessageProvider(Protocol):
    """Anything that can turn a (system, prompt) pair into a message."""

    def generate(self, system: str, prompt: str) -> str:  # pragma: no cover
        ...


class TemplateProvider:
    """Deterministic offline copy. Good enough for previews, tests, and fallbacks."""

    TEMPLATES: dict[str, str] = {
        "send_onboarding_sequence": "Welcome aboard, {name}! Here's how to get your first win in 5 minutes.",
        "send_activation_nudge": "Hi {name} — you're one step from real value. Finish setup and we'll help you get there.",
        "send_engagement_tip": "Hi {name}, here's a tip most teams miss to get more out of the product.",
        "request_review": "Hi {name}, so glad it's working for you! Would you share a quick review?",
        "send_reengagement": "Hi {name}, we miss you — here's what's new since you last logged in.",
        "winback": "Hi {name}, we'd love you back — here's something to make giving us another look worth it.",
        "flag_for_csm": "[internal] {name} ({id}) is high churn-risk — reach out personally this week.",
    }

    def message_for(self, action: ActionRequest, customer: Customer) -> str:
        template = self.TEMPLATES.get(action.type.value, "Hi {name}, just checking in.")
        return template.format(name=customer.name, id=customer.id)


def personalize(
    action: ActionRequest,
    customer: Customer,
    provider: MessageProvider | None = None,
) -> str:
    """Return a message for ``action``.

    Falls back to the offline template provider when no LLM provider is given.
    """
    if provider is None:
        return TemplateProvider().message_for(action, customer)

    system = "You write concise, warm B2B SaaS lifecycle messages. One short paragraph, no fluff."
    prompt = (
        f"Write a '{action.type.value}' message for {customer.name} "
        f"(plan: {customer.plan}). Reason: {action.reason or 'n/a'}."
    )
    return provider.generate(system, prompt)

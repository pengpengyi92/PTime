from ptime.greetings.models import GreetingTemplate
from ptime.models import text


def render(template: GreetingTemplate, values: dict[str, str] | None = None) -> str:
    if not template.active:
        raise ValueError("Cannot render inactive greeting")
    values = values or {}
    if set(values) != set(template.personalization_slots):
        raise ValueError("Supply exactly the declared personalization slots")
    for name, value in values.items():
        text(value, name)
    result = template.message.format_map(values)
    text(result, "rendered greeting")
    return result

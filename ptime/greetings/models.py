from dataclasses import dataclass
from string import Formatter

from ptime.festivals.models import ASYNC_CHANNELS, STYLES, flags, strings
from ptime.models import text


@dataclass(frozen=True)
class GreetingTemplate:
    id: str
    festival_id: str
    style: str
    locale: str
    audience: str
    channel: str
    message: str
    personalization_slots: tuple[str, ...] = ()
    active: bool = True

    def __post_init__(self):
        for name in ("id", "festival_id", "audience", "message"):
            text(getattr(self, name), name)
        if self.style not in STYLES or self.locale not in {"en", "zh-CN"}:
            raise ValueError("Invalid greeting style/locale")
        if self.channel not in ASYNC_CHANNELS | {"any_async"}:
            raise ValueError("Greeting template needs an asynchronous channel")
        flags(self, "active")
        slots = strings(self.personalization_slots, "personalization_slots")
        fields = []
        for _, field, spec, conversion in Formatter().parse(self.message):
            if field is not None:
                if not field.isidentifier() or spec or conversion:
                    raise ValueError("Only named plain-text personalization slots are supported")
                fields.append(field)
        if set(fields) != set(slots):
            raise ValueError("Template slots and declared personalization slots disagree")
        object.__setattr__(self, "personalization_slots", slots)

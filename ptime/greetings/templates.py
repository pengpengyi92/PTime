from pathlib import Path

import yaml

from ptime.core.config import default_resource, read_document
from ptime.greetings.models import GreetingTemplate


def load_templates(config_dir: Path | None = None):
    result = []
    for style in ("general", "professional", "reconnect"):
        doc = (read_document(config_dir / "greetings" / f"{style}.yaml") if config_dir is not None
               else yaml.safe_load(default_resource(f"greetings/{style}.yaml").read_text(encoding="utf-8")))
        if not isinstance(doc, dict) or set(doc) != {"templates"} or not isinstance(doc["templates"], list):
            raise ValueError("Greeting configuration requires a templates list")
        for row in doc["templates"]:
            template = GreetingTemplate(**row)
            if template.style != style:
                raise ValueError("Greeting style/file mismatch")
            result.append(template)
    if len({item.id for item in result}) != len(result):
        raise ValueError("Duplicate greeting template ID")
    return result


def select_templates(templates, festival_id, style, locale, audience="general", channel=None):
    return sorted((t for t in templates if t.active and t.festival_id == festival_id and t.style == style
                   and t.locale == locale and t.audience in {audience, "general"}
                   and (channel is None or t.channel in {channel, "any_async"})),
                  key=lambda t: (t.audience != audience, t.channel != channel, t.id))

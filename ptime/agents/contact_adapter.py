"""Global Contact Adapter Agent coordinates explicit sources and explainable ranking."""

from datetime import datetime

from ptime.adapters.base import ContactSource
from ptime.core.config import Settings, load_settings
from ptime.core.recommender import recommend
from ptime.models import TimeRecommendation


class GlobalContactAdapterAgent:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()

    def run(self, source: ContactSource, instant: datetime) -> list[TimeRecommendation]:
        return recommend(source.get_contacts(), instant, self.settings)

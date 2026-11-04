"""Austauschbare Datenquelle. Neue Quellen (offizielle Garmin-API, Health Connect, ...)
implementieren dieses Protokoll, der Rest der App bleibt unverändert."""
from datetime import date
from typing import Protocol

from ..models import Activity, DailyMetrics


class DataSource(Protocol):
    name: str

    def fetch_daily(self, start: date, end: date) -> list[DailyMetrics]: ...

    def fetch_activities(self, start: date, end: date) -> list[Activity]: ...

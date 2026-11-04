"""Garmin-Connect-Cloud über die inoffizielle Bibliothek `garminconnect`.

Der Server loggt sich NIE mit Passwort ein, sondern nutzt nur gespeicherte Tokens
(einmalig erzeugt mit `python -m app.garmin_login`). Das vermeidet Login-Schleifen
und damit die Rate-Limits (HTTP 429) von Garmin.
"""
import logging
from datetime import date, datetime, timedelta, timezone

from garminconnect import Garmin

from .. import config
from ..models import Activity, DailyMetrics

log = logging.getLogger(__name__)


def _dig(obj, *path):
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _int(v):
    try:
        return None if v is None else int(round(float(v)))
    except (TypeError, ValueError):
        return None


class GarminCloudSource:
    name = "garmin"

    def __init__(self) -> None:
        self._client: Garmin | None = None

    def _api(self) -> Garmin:
        if self._client is None:
            client = Garmin()
            client.login(config.TOKENSTORE)  # nur Tokens, kein Passwort
            self._client = client
        return self._client

    def fetch_daily(self, start: date, end: date) -> list[DailyMetrics]:
        api = self._api()
        out = []
        d = start
        while d <= end:
            iso = d.isoformat()
            m = DailyMetrics(date=d)
            try:
                s = api.get_stats(iso) or {}
                m.steps = _int(s.get("totalSteps"))
                m.distance_m = s.get("totalDistanceMeters")
                m.resting_hr = _int(s.get("restingHeartRate"))
                m.avg_hr = _int(s.get("averageHeartRate"))
                m.stress_avg = _int(s.get("averageStressLevel"))
                m.body_battery_high = _int(s.get("bodyBatteryHighestValue"))
                m.body_battery_low = _int(s.get("bodyBatteryLowestValue"))
                m.active_kcal = _int(s.get("activeKilocalories"))
                m.total_kcal = _int(s.get("totalKilocalories"))
            except Exception as e:  # einzelne Metriken dürfen fehlen
                log.warning("stats %s: %s", iso, e)
            try:
                sl = api.get_sleep_data(iso) or {}
                m.sleep_seconds = _int(_dig(sl, "dailySleepDTO", "sleepTimeSeconds"))
                m.sleep_score = _int(_dig(sl, "dailySleepDTO", "sleepScores", "overall", "value"))
            except Exception as e:
                log.warning("sleep %s: %s", iso, e)
            try:
                m.hrv_ms = _int(_dig(api.get_hrv_data(iso) or {}, "hrvSummary", "lastNightAvg"))
            except Exception as e:
                log.warning("hrv %s: %s", iso, e)
            try:
                grams = _dig(api.get_body_composition(iso) or {}, "totalAverage", "weight")
                m.weight_kg = round(float(grams) / 1000, 1) if grams else None
            except Exception as e:
                log.warning("weight %s: %s", iso, e)
            out.append(m)
            d += timedelta(days=1)
        return out

    def fetch_activities(self, start: date, end: date) -> list[Activity]:
        out = []
        for a in self._api().get_activities_by_date(start.isoformat(), end.isoformat()) or []:
            dist = a.get("distance")
            dur = a.get("duration")
            start_gmt = a.get("startTimeGMT")
            out.append(
                Activity(
                    source_id=str(a.get("activityId")),
                    type=_dig(a, "activityType", "typeKey"),
                    name=a.get("activityName"),
                    start_time=datetime.fromisoformat(start_gmt.replace(" ", "T")).replace(tzinfo=timezone.utc) if start_gmt else None,
                    duration_s=dur,
                    distance_m=dist,
                    avg_hr=_int(a.get("averageHR")),
                    max_hr=_int(a.get("maxHR")),
                    calories=_int(a.get("calories")),
                    elevation_gain_m=a.get("elevationGain"),
                    avg_pace_s_per_km=round(dur / (dist / 1000), 1) if dist and dur else None,
                )
            )
        return out

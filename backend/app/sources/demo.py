"""Deterministische Fake-Daten, damit die App ohne Garmin-Konto lauffähig ist."""
import random
from datetime import date, datetime, timedelta, timezone

from ..models import Activity, DailyMetrics


class DemoSource:
    name = "demo"

    def fetch_daily(self, start: date, end: date) -> list[DailyMetrics]:
        out = []
        d = start
        while d <= end:
            r = random.Random(d.toordinal())
            steps = r.randint(3500, 15000)
            out.append(
                DailyMetrics(
                    date=d,
                    steps=steps,
                    distance_m=steps * 0.75,
                    resting_hr=r.randint(48, 60),
                    avg_hr=r.randint(62, 78),
                    sleep_seconds=r.randint(5 * 3600, 9 * 3600),
                    sleep_score=r.randint(55, 92),
                    hrv_ms=r.randint(38, 85),
                    stress_avg=r.randint(18, 48),
                    body_battery_high=r.randint(70, 100),
                    body_battery_low=r.randint(5, 35),
                    active_kcal=r.randint(300, 1100),
                    total_kcal=r.randint(2200, 3200),
                    weight_kg=round(78 + r.uniform(-0.6, 0.6), 1),
                )
            )
            d += timedelta(days=1)
        return out

    def fetch_activities(self, start: date, end: date) -> list[Activity]:
        out = []
        d = start
        kinds = [("running", "Lauf", 5000, 5.6), ("cycling", "Radfahrt", 25000, 7.5), ("strength_training", "Krafttraining", 0, 0)]
        while d <= end:
            r = random.Random(d.toordinal() * 7)
            if r.random() < 0.55:
                typ, label, base, speed = r.choice(kinds)
                dist = base * r.uniform(0.7, 1.6) if base else 0
                dur = (dist / speed) if dist else r.randint(2400, 4200)
                out.append(
                    Activity(
                        source_id=f"demo-{d.isoformat()}",
                        type=typ,
                        name=f"{label} am {d.strftime('%d.%m.')}",
                        start_time=datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=r.randint(6, 19)),
                        duration_s=round(dur, 1),
                        distance_m=round(dist, 1) or None,
                        avg_hr=r.randint(125, 160),
                        max_hr=r.randint(165, 190),
                        calories=int(dur / 60 * r.uniform(8, 12)),
                        elevation_gain_m=round(r.uniform(5, 250), 1) if dist else None,
                        avg_pace_s_per_km=round(dur / (dist / 1000), 1) if dist else None,
                    )
                )
            d += timedelta(days=1)
        return out

from datetime import date as Date, datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DailyMetrics(SQLModel, table=True):
    date: Date = Field(primary_key=True)
    steps: int | None = None
    distance_m: float | None = None
    resting_hr: int | None = None
    avg_hr: int | None = None
    sleep_seconds: int | None = None
    sleep_score: int | None = None
    hrv_ms: int | None = None
    stress_avg: int | None = None
    body_battery_high: int | None = None
    body_battery_low: int | None = None
    active_kcal: int | None = None
    total_kcal: int | None = None
    weight_kg: float | None = None


class Activity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_id: str = Field(unique=True, index=True)
    type: str | None = None
    name: str | None = None
    start_time: datetime | None = Field(default=None, index=True)
    duration_s: float | None = None
    distance_m: float | None = None
    avg_hr: int | None = None
    max_hr: int | None = None
    calories: int | None = None
    elevation_gain_m: float | None = None
    avg_pace_s_per_km: float | None = None


class Food(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    brand: str | None = None
    kcal_100g: float
    protein_100g: float = 0
    carbs_100g: float = 0
    fat_100g: float = 0
    barcode: str | None = Field(default=None, index=True)


class FoodLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: Date = Field(index=True)
    meal: str
    food_id: int = Field(foreign_key="food.id")
    grams: float


class NutritionGoal(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    kcal_target: int = 2200
    protein_g: int = 130
    carbs_g: int = 250
    fat_g: int = 70


class SyncRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    status: str = "running"  # running | ok | error
    message: str | None = None
    days: int = 14
    source: str = "demo"

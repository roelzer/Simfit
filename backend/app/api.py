from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlmodel import Session, col, select

from . import config
from .db import get_session
from .models import Activity, DailyMetrics, Food, FoodLog, NutritionGoal, SyncRun
from .sync import new_run, run_sync

router = APIRouter(prefix="/api")
Meal = Literal["breakfast", "lunch", "dinner", "snack"]


# ---------- System / Sync ----------
@router.get("/health")
def health():
    return {"status": "ok", "source": config.SOURCE}


class SyncRequest(BaseModel):
    days: int = 14


@router.post("/sync", response_model=SyncRun)
def start_sync(bg: BackgroundTasks, body: SyncRequest | None = None, s: Session = Depends(get_session)):
    days = max(1, min((body.days if body else 14), 365))
    running = s.exec(select(SyncRun).where(SyncRun.status == "running")).first()
    if running:
        return running
    run = new_run(s, days)
    bg.add_task(run_sync, run.id)
    return run


@router.get("/sync/status", response_model=SyncRun | None)
def sync_status(s: Session = Depends(get_session)):
    return s.exec(select(SyncRun).order_by(col(SyncRun.id).desc())).first()


# ---------- Garmin-Daten ----------
@router.get("/daily", response_model=list[DailyMetrics])
def daily(
    from_: date = Query(alias="from", default_factory=lambda: date.today() - timedelta(days=29)),
    to: date = Query(default_factory=date.today),
    s: Session = Depends(get_session),
):
    q = select(DailyMetrics).where(DailyMetrics.date >= from_, DailyMetrics.date <= to).order_by(DailyMetrics.date)
    return s.exec(q).all()


@router.get("/activities", response_model=list[Activity])
def activities(
    from_: date | None = Query(alias="from", default=None),
    to: date | None = None,
    limit: int = Query(50, ge=1, le=500),
    s: Session = Depends(get_session),
):
    q = select(Activity)
    if from_:
        q = q.where(Activity.start_time >= datetime.combine(from_, datetime.min.time(), tzinfo=timezone.utc))
    if to:
        q = q.where(Activity.start_time < datetime.combine(to + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc))
    return s.exec(q.order_by(col(Activity.start_time).desc()).limit(limit)).all()


@router.get("/activities/{activity_id}", response_model=Activity)
def activity(activity_id: int, s: Session = Depends(get_session)):
    a = s.get(Activity, activity_id)
    if not a:
        raise HTTPException(404, "Aktivität nicht gefunden")
    return a


# ---------- Ernährung ----------
class FoodIn(BaseModel):
    name: str
    brand: str | None = None
    kcal_100g: float
    protein_100g: float = 0
    carbs_100g: float = 0
    fat_100g: float = 0
    barcode: str | None = None


@router.get("/foods", response_model=list[Food])
def foods(q: str = "", s: Session = Depends(get_session)):
    stmt = select(Food)
    if q:
        stmt = stmt.where(col(Food.name).ilike(f"%{q}%"))
    return s.exec(stmt.order_by(Food.name).limit(50)).all()


@router.post("/foods", response_model=Food, status_code=201)
def create_food(body: FoodIn, s: Session = Depends(get_session)):
    food = Food(**body.model_dump())
    s.add(food)
    s.commit()
    s.refresh(food)
    return food


class Macros(BaseModel):
    kcal: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0


class FoodLogEntry(BaseModel):
    id: int
    date: date
    meal: str
    food: Food
    grams: float
    kcal: float
    protein: float
    carbs: float
    fat: float


def _entry(log: FoodLog, food: Food) -> FoodLogEntry:
    f = log.grams / 100
    return FoodLogEntry(
        id=log.id, date=log.date, meal=log.meal, food=food, grams=log.grams,
        kcal=round(food.kcal_100g * f, 1), protein=round(food.protein_100g * f, 1),
        carbs=round(food.carbs_100g * f, 1), fat=round(food.fat_100g * f, 1),
    )


def _entries(s: Session, day: date) -> list[FoodLogEntry]:
    rows = s.exec(select(FoodLog, Food).join(Food, Food.id == FoodLog.food_id).where(FoodLog.date == day).order_by(FoodLog.id)).all()
    return [_entry(log, food) for log, food in rows]


class FoodLogIn(BaseModel):
    date: date
    meal: Meal
    food_id: int
    grams: float


@router.get("/food-log", response_model=list[FoodLogEntry])
def food_log(date: date, s: Session = Depends(get_session)):
    return _entries(s, date)


@router.post("/food-log", response_model=FoodLogEntry, status_code=201)
def add_food_log(body: FoodLogIn, s: Session = Depends(get_session)):
    food = s.get(Food, body.food_id)
    if not food:
        raise HTTPException(404, "Lebensmittel nicht gefunden")
    if body.grams <= 0:
        raise HTTPException(422, "Menge muss größer als 0 sein")
    log = FoodLog(**body.model_dump())
    s.add(log)
    s.commit()
    s.refresh(log)
    return _entry(log, food)


@router.delete("/food-log/{entry_id}", status_code=204)
def delete_food_log(entry_id: int, s: Session = Depends(get_session)):
    log = s.get(FoodLog, entry_id)
    if not log:
        raise HTTPException(404, "Eintrag nicht gefunden")
    s.delete(log)
    s.commit()
    return Response(status_code=204)


class Goal(BaseModel):
    kcal_target: int
    protein_g: int
    carbs_g: int
    fat_g: int


class NutritionDay(BaseModel):
    date: date
    eaten: Macros
    burned_kcal: int | None
    goal: Goal
    balance_kcal: float


@router.get("/nutrition/goal", response_model=Goal)
def get_goal(s: Session = Depends(get_session)):
    return s.get(NutritionGoal, 1) or NutritionGoal()


@router.put("/nutrition/goal", response_model=Goal)
def put_goal(body: Goal, s: Session = Depends(get_session)):
    goal = s.merge(NutritionGoal(id=1, **body.model_dump()))
    s.commit()
    return goal


@router.get("/nutrition/day", response_model=NutritionDay)
def nutrition_day(date: date, s: Session = Depends(get_session)):
    entries = _entries(s, date)
    eaten = Macros(
        kcal=round(sum(e.kcal for e in entries), 1), protein=round(sum(e.protein for e in entries), 1),
        carbs=round(sum(e.carbs for e in entries), 1), fat=round(sum(e.fat for e in entries), 1),
    )
    goal = s.get(NutritionGoal, 1) or NutritionGoal()
    daily = s.get(DailyMetrics, date)
    burned = daily.total_kcal if daily else None
    # Bilanz: Aufnahme minus Verbrauch (Garmin), ohne Garmin-Wert minus Zielwert
    balance = eaten.kcal - (burned if burned is not None else goal.kcal_target)
    return NutritionDay(date=date, eaten=eaten, burned_kcal=burned, goal=Goal(**goal.model_dump(exclude={"id"})), balance_kcal=round(balance, 1))

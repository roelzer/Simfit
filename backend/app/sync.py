from datetime import date, timedelta

from sqlmodel import Session, select

from . import config
from .db import engine
from .models import Activity, DailyMetrics, SyncRun, utcnow
from .sources import get_source


def run_sync(run_id: int) -> None:
    """Läuft im Hintergrund mit eigener Session; schreibt das Ergebnis in SyncRun."""
    with Session(engine) as s:
        run = s.get(SyncRun, run_id)
        try:
            source = get_source()
            end = date.today()
            start = end - timedelta(days=run.days - 1)
            for m in source.fetch_daily(start, end):
                s.merge(m)
            for a in source.fetch_activities(start, end):
                existing = s.exec(select(Activity).where(Activity.source_id == a.source_id)).first()
                if existing:
                    for k, v in a.model_dump(exclude={"id"}).items():
                        setattr(existing, k, v)
                else:
                    s.add(a)
            run.status, run.message = "ok", None
        except Exception as e:
            s.rollback()
            run = s.get(SyncRun, run_id)
            run.status, run.message = "error", f"{type(e).__name__}: {e}"
        run.finished_at = utcnow()
        s.add(run)
        s.commit()


def new_run(s: Session, days: int) -> SyncRun:
    run = SyncRun(days=days, source=config.SOURCE)
    s.add(run)
    s.commit()
    s.refresh(run)
    return run

import os
import tempfile
from datetime import date

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["SIMFIT_SOURCE"] = "demo"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_flow():
    with TestClient(app) as c:
        assert c.get("/api/health").json() == {"status": "ok", "source": "demo"}
        assert c.get("/api/sync/status").json() is None

        run = c.post("/api/sync", json={"days": 7}).json()
        assert run["id"]
        st = c.get("/api/sync/status").json()  # Background-Task läuft im TestClient synchron
        assert st["status"] == "ok", st

        daily = c.get("/api/daily").json()
        assert len(daily) == 7 and daily[0]["date"] < daily[-1]["date"]
        acts = c.get("/api/activities").json()
        assert acts and c.get(f"/api/activities/{acts[0]['id']}").status_code == 200
        assert c.get("/api/activities/99999").status_code == 404

        # erneuter Sync darf nicht duplizieren
        c.post("/api/sync", json={"days": 7})
        assert len(c.get("/api/activities").json()) == len(acts)

        today = date.today().isoformat()
        food = c.get("/api/foods", params={"q": "hafer"}).json()[0]
        e = c.post("/api/food-log", json={"date": today, "meal": "breakfast", "food_id": food["id"], "grams": 100}).json()
        assert e["kcal"] == food["kcal_100g"]
        day = c.get("/api/nutrition/day", params={"date": today}).json()
        assert day["eaten"]["kcal"] == e["kcal"] and day["burned_kcal"] is not None
        assert c.delete(f"/api/food-log/{e['id']}").status_code == 204
        assert c.get("/api/food-log", params={"date": today}).json() == []

        goal = c.put("/api/nutrition/goal", json={"kcal_target": 1800, "protein_g": 140, "carbs_g": 180, "fat_g": 60}).json()
        assert goal["kcal_target"] == 1800
        assert c.post("/api/foods", json={"name": "Test", "kcal_100g": 100}).status_code == 201

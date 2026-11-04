import os
from pathlib import Path

SOURCE = os.getenv("SIMFIT_SOURCE", "demo").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./simfit.db")
TOKENSTORE = str(Path(os.getenv("GARMIN_TOKENSTORE", "~/.simfit/garmin")).expanduser())
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

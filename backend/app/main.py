from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from . import config
from .api import router
from .db import engine, init_db
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as s:
        seed(s)
    yield


app = FastAPI(title="Simfit API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

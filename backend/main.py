import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import *

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend starting... Lifespan initiated.")
    app.state.model = None
    app.state.scaler = None
    app.state.pro_coords = None

    yield

    logger.info("Application shutting down...")
    app.state.model = None
    app.state.scaler = None
    app.state.pro_coords = None


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(pro_stats.router, prefix="/api/pro-stats", tags=["Pro Stats"])
app.include_router(transform.router, prefix="/api/transform", tags=["Transform"])


@app.get("/")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}


handler = Mangum(app, lifespan="on")

import logging
from contextlib import asynccontextmanager
from typing import Iterator, Tuple
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from pathlib import Path
from mangum import Mangum

from routers import *

logger = logging.getLogger("uvicorn.error")

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend starting... Lifespan initiated.")

    try:
        logger.info("Loading model...")
        app.state.model = joblib.load(BASE_DIR / "assets/umap-model.joblib")
        logger.info("Model loaded successfully.")

        logger.info("Loading scaler...")
        app.state.scaler = joblib.load(BASE_DIR / "assets/scaler.joblib")
        logger.info("Scaler loaded successfully.")

        logger.info("Loading pro coords...")
        pro_coords_zip_obj: Iterator[Tuple[str, np.ndarray]] = joblib.load(
            BASE_DIR / "assets/umap-coords.joblib"
        )
        pro_coords_dict = {
            player_name: coord.tolist() for player_name, coord in pro_coords_zip_obj
        }
        app.state.pro_coords = pro_coords_dict
        logger.info("Pro coords object loaded successfully.")
    except Exception as e:
        logger.error(
            f"CRITICAL STARTUP FAILURE: Error during loading: {e}", exc_info=True
        )
        raise  # Immediately abort startup

    logger.info("Startup complete.")
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


@app.get("/api/data")
def get_data():
    return {
        "id": 123,
        "name": "Sample Data",
        "description": "This data came from your Python backend.",
    }


handler = Mangum(app, lifespan="on")

import logging
from contextlib import asynccontextmanager
import io
from typing import Iterator, Tuple
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np

from config import get_settings
from routers import *

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend starting... Lifespan initiated.")

    settings = get_settings()
    s3_client = None

    try:
        logger.info("Initialising S3 client...")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        logger.info("S3 client initialised successfully.")

        logger.info("Loading model...")
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=settings.UMAP_MODEL_KEY
        )
        model_data = response["Body"].read()
        app.state.model = joblib.load(io.BytesIO(model_data))
        logger.info("Model loaded successfully.")

        logger.info("Loading scaler...")
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=settings.SCALER_KEY
        )
        scaler_data = response["Body"].read()
        app.state.scaler = joblib.load(io.BytesIO(scaler_data))
        logger.info("Scaler loaded successfully.")

        logger.info("Loading pro coords...")
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=settings.UMAP_COORDS_KEY
        )
        pro_coords_data = response["Body"].read()
        pro_coords_zip_obj: Iterator[Tuple[str, np.ndarray]] = joblib.load(
            io.BytesIO(pro_coords_data)
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
    finally:
        if s3_client:
            logger.info("S3 client operations complete. Closing client.")
            s3_client.close()

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

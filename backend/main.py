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


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Backend starting...")

    settings = get_settings()

    try:
        print("Initialising S3 client...")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        print("S3 client initialised successfully.")
    except Exception as e:
        print(f"Error initialising S3 client: {e}")

    try:
        print("Loading model...")
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=settings.UMAP_MODEL_KEY
        )
        model_data = response["Body"].read()
        app.state.model = joblib.load(io.BytesIO(model_data))
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        app.state.model = None

    try:
        print("Loading scaler...")
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=settings.SCALER_KEY
        )
        scaler_data = response["Body"].read()
        app.state.scaler = joblib.load(io.BytesIO(scaler_data))
        print("Scaler loaded successfully.")
    except Exception as e:
        print(f"Error loading scaler : {e}")
        app.state.scaler = None

    try:
        print(f"Loading pro coords...")
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
        print("Pro coords object loaded successfully.")
    except Exception as e:
        print(f"Error loading pro coords: {e}")
        app.state.pro_coords = None

    s3_client.close()
    yield

    print("Application shutting down...")
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

from contextlib import asynccontextmanager
import io
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib

from config import get_settings
from routers import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Backend starting...")

    settings = get_settings()
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    UMAP_MODEL_KEY = settings.UMAP_MODEL_KEY

    print("Loading model...")

    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=UMAP_MODEL_KEY)
        model_data = response["Body"].read()
        app.state.model = joblib.load(io.BytesIO(model_data))
        print("Model loaded successfully.")

    except Exception as e:
        print(f"Error loading model: {e}")
        app.state.model = None

    yield

    print("Application shutting down...")
    app.state.model = None


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

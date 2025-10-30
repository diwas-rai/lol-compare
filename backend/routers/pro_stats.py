from fastapi import APIRouter, HTTPException, Depends
import io
import boto3
import joblib
import numpy as np
from typing import Annotated
from config import Settings, get_settings

router = APIRouter()

ConfigDeps = Annotated[Settings, Depends(get_settings)]


@router.get("/coords")
async def get_pro_player_stats(settings: ConfigDeps):
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    UMAP_COORDS_KEY = settings.UMAP_COORDS_KEY

    if not S3_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME is not set")

    s3_client = boto3.client("s3")

    print(f"Accessing files from bucket: {S3_BUCKET_NAME}...")

    try:
        print(f"Loading {UMAP_COORDS_KEY}...")

        umap_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=UMAP_COORDS_KEY)

        with io.BytesIO(umap_obj["Body"].read()) as umap_buffer:
            umap_coords = joblib.load(umap_buffer)

        print("UMAP coords object loaded successfully.")

        coordinates_list = {pn: c.tolist() for pn, c in umap_coords}

        return coordinates_list

    except Exception as e:
        print(f"Error loading {UMAP_COORDS_KEY}: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading coordinates: {e}")

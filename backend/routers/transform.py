from fastapi import APIRouter, HTTPException, Request
from sklearn.preprocessing import StandardScaler
from umap import UMAP
from schemas import UserStats
import pandas as pd


router = APIRouter()


@router.post("/")
async def transform_user_stats(user_stats: UserStats, request: Request):
    umap_model: UMAP = request.app.state.model
    if umap_model is None:
        raise HTTPException(status_code=500, detail="Model is not found.")

    scaler: StandardScaler = request.app.state.scaler
    if scaler is None:
        raise HTTPException(status_code=500, detail="Scaler is not found.")

    features_list = user_stats.model_dump(by_alias=True)

    features_df = pd.DataFrame([features_list])
    try:
        user_stats_scaled = scaler.transform(features_df)
        transformed_user_stats = umap_model.transform(user_stats_scaled)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"user_coordinates": transformed_user_stats.tolist()}

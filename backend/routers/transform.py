from fastapi import APIRouter, HTTPException, Request, Depends
from dependencies import get_ml_models_cache
from schemas import UserStats
import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from umap import UMAP
    from sklearn.preprocessing import StandardScaler
    from pandas import DataFrame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", dependencies=[Depends(get_ml_models_cache)])
async def transform_user_stats(user_stats: UserStats, request: Request):
    scaler: "StandardScaler" = request.app.state.scaler
    model: "UMAP" = request.app.state.model

    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model initialisation failed.")

    try:
        features_list = user_stats.model_dump(by_alias=True)

        import pandas as pd

        features_df = pd.DataFrame([features_list])

        user_stats_scaled = scaler.transform(features_df)
        transformed_user_stats = model.transform(user_stats_scaled)

    except Exception as e:
        print(f"Error during transformation: {e}")
        raise HTTPException(status_code=500, detail=f"Error in transformation: {e}")

    return {"user_coordinates": transformed_user_stats.tolist()}

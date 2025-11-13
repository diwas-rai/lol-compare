import threading
import logging
from fastapi import Request, HTTPException
from typing import Iterator, Tuple, TYPE_CHECKING
from pathlib import Path

coords_load_lock = threading.Lock()
model_and_scaler_load_lock = threading.Lock()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = Path.joinpath(BASE_DIR / "assets")
logger.info(BASE_DIR)

if TYPE_CHECKING:
    import numpy as np


def _load_coords_from_disk(app_state):
    try:
        import joblib
        import numpy as np

        COORDS_PATH = Path.joinpath(ASSETS_DIR / "umap-coords.joblib")
        if not Path.exists(COORDS_PATH):
            raise FileNotFoundError(f"Coords file not found at {COORDS_PATH}")

        logger.info(f"Loading pro_coords from {COORDS_PATH}...")
        pro_coords_zip_obj: Iterator[Tuple[str, np.ndarray]] = joblib.load(COORDS_PATH)
        pro_coords_dict = {
            player_name: coord.tolist() for player_name, coord in pro_coords_zip_obj
        }
        app_state.pro_coords = pro_coords_dict
        logger.info("Pro coords loaded and cached in app.state.")

    except Exception as e:
        logger.error(f"FATAL: Failed to load pro_coords: {e}", exc_info=True)
        app_state.pro_coords = "FAILED"
        raise RuntimeError(f"Failed to load pro_coords: {e}")


def get_coords_cache(request: Request):
    if request.app.state.pro_coords is None:
        with coords_load_lock:
            if request.app.state.pro_coords is None:
                logger.info("Cold instance: Triggering lazy-load of pro_coords...")
                _load_coords_from_disk(request.app.state)

    if request.app.state.pro_coords == "FAILED":
        raise HTTPException(
            status_code=503, detail="Pro coords cache is in a failed state."
        )

    return


def _load_ml_models_from_disk(app_state):
    try:
        logger.info("Loading scaler and model")
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.preprocessing import StandardScaler
        from umap import UMAP

        SCALER_PATH = Path.joinpath(ASSETS_DIR / "scaler.joblib")
        MODEL_PATH = Path.joinpath(ASSETS_DIR / "umap-model.joblib")

        logger.info(f"Loading scaler from {SCALER_PATH}...")
        app_state.scaler = joblib.load(SCALER_PATH)

        logger.info(f"Loading model from {MODEL_PATH}...")
        app_state.model = joblib.load(MODEL_PATH)
        logger.info("Scaler and model loaded and cached in app.state.")

    except Exception as e:
        logger.error(f"FATAL: Failed to load model or scaler: {e}", exc_info=True)
        app_state.model = "FAILED"
        app_state.scaler = "FAILED"
        raise RuntimeError(f"Failed to load model or scaler: {e}")


def get_ml_models_cache(request: Request):
    if request.app.state.model is None:
        with model_and_scaler_load_lock:
            if request.app.state.model is None:
                logger.info(
                    "Cold instance: Triggering lazy-load of model and scaler..."
                )
                _load_ml_models_from_disk(request.app.state)

    if request.app.state.model == "FAILED":
        raise HTTPException(
            status_code=503, detail="ML model cache is in a failed state."
        )
    if request.app.state.scaler == "FAILED":
        raise HTTPException(
            status_code=503, detail="Scaler cache is in a failed state."
        )

    return

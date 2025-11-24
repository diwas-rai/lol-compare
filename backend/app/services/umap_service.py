import joblib
import logging
from pathlib import Path
import pandas as pd
from functools import lru_cache

logger = logging.getLogger(__name__)


class UMAPService:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.assets_path = self.project_root / "assets"

        logger.info(f"Loading ML assets from: {self.assets_path}")

        try:
            self.scaler = self._load_asset("scaler.joblib")
            self.model = self._load_asset("umap-model.joblib")
        except FileNotFoundError:
            logger.critical(f"Assets not found in {self.assets_path}")
            raise

    def _load_asset(self, filename: str):
        return joblib.load(self.assets_path / filename)

    def transform_stats(self, stats_dict: dict) -> list:
        if not self.model or not self.scaler:
            raise RuntimeError("ML Models not initialized")

        try:
            features_df = pd.DataFrame([stats_dict])
            if hasattr(self.scaler, "feature_names_in_"):
                features_df = features_df.reindex(
                    columns=self.scaler.feature_names_in_, fill_value=0
                )

            user_stats_scaled = self.scaler.transform(features_df)
            transformed_user_stats = self.model.transform(user_stats_scaled)

            return transformed_user_stats.flatten().tolist()
        except Exception as e:
            logger.error(f"Error during ML transformation: {e}")
            raise ValueError(f"Failed to transform user stats: {e}")


@lru_cache()
def get_umap_service() -> UMAPService:
    return UMAPService()

from functools import lru_cache
from pathlib import Path
import logging

import joblib

logger = logging.getLogger(__name__)


class CoordsService:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.assets_path = self.project_root / "assets"

        logger.info(f"Loading coords from: {self.assets_path}")

        try:
            coords = self._load_asset("umap-coords.joblib")
            pro_coords_dict = {
                player_name: coord.tolist() for player_name, coord in coords
            }
            self.coords = pro_coords_dict
        except FileNotFoundError:
            logger.critical(f"Assets not found in {self.assets_path}")
            raise

    def _load_asset(self, filename: str):
        return joblib.load(self.assets_path / filename)


@lru_cache()
def get_coords_service() -> CoordsService:
    return CoordsService()

from typing import Annotated
from fastapi import APIRouter, Depends
from app.services.umap_service import UMAPService, get_umap_service

router = APIRouter()

UMAPServiceDeps = Annotated[UMAPService, Depends(get_umap_service)]


@router.get("")
def warmup(umap_service: UMAPServiceDeps):
    _ = umap_service.scaler
    _ = umap_service.model
    return {"model_loadeds": "true"}

from typing import Annotated
from fastapi import APIRouter, Request, Depends
from app.services.coords_service import CoordsService, get_coords_service

router = APIRouter()


CoordsServiceDeps = Annotated[CoordsService, Depends(get_coords_service)]


@router.get("/coords")
async def get_pro_player_stats(request: Request, coords_service: CoordsServiceDeps):
    return coords_service.coords

from fastapi import APIRouter, Request, Depends
from dependencies import get_coords_cache

router = APIRouter()


@router.get("/coords", dependencies=[Depends(get_coords_cache)])
async def get_pro_player_stats(request: Request):
    return request.app.state.pro_coords

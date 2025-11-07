from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/coords")
async def get_pro_player_stats(request: Request):
    return request.app.state.pro_coords

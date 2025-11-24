from fastapi import APIRouter, Depends, HTTPException
import httpx
from typing import Annotated, AsyncGenerator

# Note: We use relative imports now that everything is in the 'app' package
from app.config import get_settings, Settings
from app.services.riot_service import RiotService
from app.services.umap_service import UMAPService, get_umap_service

router = APIRouter()


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


HTTPClientDeps = Annotated[httpx.AsyncClient, Depends(get_http_client)]
SettingsDeps = Annotated[Settings, Depends(get_settings)]
UMAPServiceDeps = Annotated[UMAPService, Depends(get_umap_service)]


@router.get("/")
async def analyse_user(
    gameName: str,
    tagLine: str,
    settings: SettingsDeps,
    client: HTTPClientDeps,
    umap_service: UMAPServiceDeps,
):
    riot_service = RiotService(settings=settings, client=client)

    try:
        average_stats = await riot_service.get_player_averages(gameName, tagLine)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching Riot data: {str(e)}"
        )

    if not average_stats:
        raise HTTPException(status_code=404, detail="No match data found to analyze.")

    try:
        coordinates = umap_service.transform_stats(average_stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing ML model: {str(e)}"
        )

    return {gameName: coordinates}

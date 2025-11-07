from fastapi import APIRouter, Depends, HTTPException
import requests
from typing import Annotated
from config import get_settings, Settings

router = APIRouter()


ConfigDeps = Annotated[Settings, Depends(get_settings)]


@router.get("/")
async def get_matches(gameName: str, tagLine: str, settings: ConfigDeps):
    try:
        player_details_response = requests.get(
            f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName.strip()}/{tagLine.strip()}",
            headers={"X-Riot-Token": settings.RIOT_API_KEY},
        )
        player_details = player_details_response.json()

        puuid = player_details.get("puuid")
        if not puuid:
            raise HTTPException(status_code=404, detail="Player not found")

        match_list_response = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid.strip()}/ids?type=ranked&start=0&count=20",
            headers={"X-Riot-Token": settings.RIOT_API_KEY},
        )

        return match_list_response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

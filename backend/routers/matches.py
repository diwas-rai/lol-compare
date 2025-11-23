from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
import httpx
from typing import Annotated, AsyncGenerator
from config import get_settings, Settings
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)


ConfigDeps = Annotated[Settings, Depends(get_settings)]


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


HTTPClientDeps = Annotated[httpx.AsyncClient, Depends(get_http_client)]


async def _fetch_match_data(url: str, headers: dict, client: HTTPClientDeps):
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@router.get("/stats/")
async def get_match_stats(
    gameName: str, tagLine: str, settings: ConfigDeps, client: HTTPClientDeps
):
    puuid = await _get_puuid(gameName, tagLine, settings, client)
    match_list = await _get_matches(puuid, settings, client)

    if not match_list:
        return {}

    headers = {"X-Riot-Token": settings.RIOT_API_KEY}
    tasks = []

    for match_id in match_list:
        match_summary_url = (
            f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
        )
        match_timeline_url = (
            f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
        )
        tasks.append(_fetch_match_data(match_summary_url, headers, client))
        tasks.append(_fetch_match_data(match_timeline_url, headers, client))

    all_match_data = await asyncio.gather(*tasks, return_exceptions=True)

    processed_stats_list = []
    for i in range(0, len(all_match_data), 2):
        match_id = match_list[i // 2]
        match_summary = all_match_data[i]
        match_timeline = all_match_data[i + 1]

        if isinstance(match_summary, Exception):
            logger.warning(
                f"Failed to fetch match data for {match_id}: {match_summary}"
            )
            raise HTTPException(status_code=500, detail="Internal server error.")
        if isinstance(match_timeline, Exception):
            logger.warning(
                f"Failed to fetch timeline data for {match_id}: {match_timeline}"
            )
            raise HTTPException(status_code=500, detail="Internal server error.")

        try:
            match_stats = _get_stats_from_match_endpoint(match_summary, puuid)
            timeline_stats = _get_stats_from_match_timeline(match_timeline, puuid)
            processed_stats_list.append({**match_stats, **timeline_stats})
        except Exception as e:
            logger.error(f"Failed to process data for match {match_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")

    df = pd.DataFrame(processed_stats_list)
    average = df.mean(numeric_only=True)

    return average


async def _get_puuid(
    gameName: str, tagLine: str, settings: ConfigDeps, client: HTTPClientDeps
) -> str:
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName.strip()}/{tagLine.strip()}"
    headers = {"X-Riot-Token": settings.RIOT_API_KEY}

    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        player_details = response.json()
        puuid = player_details.get("puuid")
        if not puuid:
            logger.error(f"PUUID not found in response for {gameName}#{tagLine}")
            raise HTTPException(status_code=404, detail="PUUID not found")
        return puuid
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Player not found.")
        logger.error(f"Riot API error fetching PUUID: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Error fetching player details from Riot API.",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching PUUID: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


async def _get_matches(puuid: str, settings: ConfigDeps, client: HTTPClientDeps):
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=5"
    headers = {"X-Riot-Token": settings.RIOT_API_KEY}
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Riot API error fetching match list: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Error fetching match list from Riot API.",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching match list: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


def _find_player_index(participants, puuid):
    for index, player in enumerate(participants):
        if player.get("puuid") == puuid:
            return index
    return -1


def _get_stats_from_match_endpoint(match_data, puuid):
    d = match_data
    index = _find_player_index(d["info"]["participants"], puuid)

    if index == -1:
        logger.error(f"Could not find player {puuid} in match {d['info']['gameId']}")
        raise ValueError(f"Player PUUID not found in match participants.")

    game_duration = d["info"]["gameDuration"] / 60
    player_stats = d["info"]["participants"][index]

    res = {
        "kills": player_stats["kills"],
        "deaths": player_stats["deaths"],
        "assists": player_stats["assists"],
        "dpm": player_stats["challenges"]["damagePerMinute"],
        "damageshare": player_stats["challenges"]["teamDamagePercentage"],
        "damagetakenperminute": player_stats["totalDamageTaken"] / game_duration,
        "wpm": player_stats["wardsPlaced"] / game_duration,
        "wcpm": player_stats["wardsKilled"] / game_duration,
        "vspm": player_stats["visionScore"] / game_duration,
        "earned_gpm": player_stats["goldEarned"] / game_duration,
        "cspm": (
            player_stats["totalMinionsKilled"] + player_stats["neutralMinionsKilled"]
        )
        / game_duration,
    }

    return res


def _find_participant_id(participants, puuid):
    for participant in participants:
        if participant.get("puuid") == puuid:
            return participant.get("participantId")
    return None


def _get_stats_from_match_timeline(match_timeline_data, puuid):
    d = match_timeline_data
    frames = d["info"]["frames"]
    player_participant_id = _find_participant_id(
        match_timeline_data["info"]["participants"], puuid
    )

    if player_participant_id is None:
        logger.error(f"Could not find participantId for {puuid} in match timeline.")
        raise ValueError("Player PUUID not found in match timeline participants.")

    if player_participant_id + 5 <= 10:
        opp_participant_id = player_participant_id + 5
    else:
        opp_participant_id = player_participant_id - 5

    stats = {
        "player": {"kills": 0, "assists": 0, "deaths": 0},
        "opp": {"kills": 0, "assists": 0, "deaths": 0},
        "player_at": {t: {} for t in [10, 15, 20, 25]},
        "opp_at": {t: {} for t in [10, 15, 20, 25]},
    }

    for i, frame in enumerate(frames):
        for event in frame["events"]:
            if event["type"] == "CHAMPION_KILL":
                if event["killerId"] == player_participant_id:
                    stats["player"]["kills"] += 1
                elif player_participant_id in event.get("assistingParticipantIds", []):
                    stats["player"]["assists"] += 1
                elif event["victimId"] == player_participant_id:
                    stats["player"]["deaths"] += 1

                if event["killerId"] == opp_participant_id:
                    stats["opp"]["kills"] += 1
                elif opp_participant_id in event.get("assistingParticipantIds", []):
                    stats["opp"]["assists"] += 1
                elif event["victimId"] == opp_participant_id:
                    stats["opp"]["deaths"] += 1

        if i in stats["player_at"]:
            stats["player_at"][i] = stats["player"].copy()
            stats["opp_at"][i] = stats["opp"].copy()

    res = {}
    timestamps = [10, 15, 20, 25]

    for time in timestamps:
        if time < len(frames):
            frame = d["info"]["frames"][time]
            player_frame = frame["participantFrames"][str(player_participant_id)]
            opp_frame = frame["participantFrames"][str(opp_participant_id)]

            player_cs = (
                player_frame["minionsKilled"] + player_frame["jungleMinionsKilled"]
            )
            opp_cs = opp_frame["minionsKilled"] + opp_frame["jungleMinionsKilled"]

            res["goldat" + str(time)] = player_frame["totalGold"]
            res["xpat" + str(time)] = player_frame["xp"]
            res["csat" + str(time)] = player_cs

            res["golddiffat" + str(time)] = (
                player_frame["totalGold"] - opp_frame["totalGold"]
            )

            res["xpdiffat" + str(time)] = player_frame["xp"] - opp_frame["xp"]
            res["csdiffat" + str(time)] = player_cs - opp_cs

            res["killsat" + str(time)] = stats["player_at"][time]["kills"]
            res["assistsat" + str(time)] = stats["player_at"][time]["assists"]
            res["deathsat" + str(time)] = stats["player_at"][time]["deaths"]

            res["opp_goldat" + str(time)] = opp_frame["totalGold"]
            res["opp_xpat" + str(time)] = opp_frame["xp"]
            res["opp_csat" + str(time)] = opp_cs
            res["opp_killsat" + str(time)] = stats["opp_at"][time]["kills"]
            res["opp_assistsat" + str(time)] = stats["opp_at"][time]["assists"]
            res["opp_deathsat" + str(time)] = stats["opp_at"][time]["deaths"]
        else:
            for key_prefix in [
                "gold",
                "xp",
                "cs",
                "golddiff",
                "xpdiff",
                "csdiff",
                "kills",
                "assists",
                "deaths",
                "opp_kills",
                "opp_assists",
                "opp_deaths",
                "opp_gold",
            ]:
                res[f"{key_prefix}at{time}"] = None

    return res

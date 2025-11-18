from fastapi import APIRouter, Depends, HTTPException
import requests
from typing import Annotated
from config import get_settings, Settings

router = APIRouter()


ConfigDeps = Annotated[Settings, Depends(get_settings)]


async def _get_matches(puuid: str, settings: ConfigDeps):
    try:
        match_list_response = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid.strip()}/ids?type=ranked&start=0&count=5",
            headers={"X-Riot-Token": settings.RIOT_API_KEY},
        )

        return match_list_response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


async def _get_puuid(gameName, tagLine, settings):
    player_details_response = requests.get(
        f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName.strip()}/{tagLine.strip()}",
        headers={"X-Riot-Token": settings.RIOT_API_KEY},
    )
    player_details = player_details_response.json()

    puuid = player_details.get("puuid")
    if not puuid:
        raise HTTPException(status_code=404, detail="Player not found")

    return {"puuid": puuid}


@router.get("/stats")
async def get_match_stats(gameName: str, tagLine: str, settings: ConfigDeps):
    puuid_response = await _get_puuid(gameName, tagLine, settings)
    puuid: str = puuid_response["puuid"]
    match_list = await _get_matches(puuid, settings)

    res = []
    res2 = []

    for i, match_id in enumerate(match_list):
        match_data_response = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}",
            headers={"X-Riot-Token": settings.RIOT_API_KEY},
        )

        if match_data_response.status_code == 200:
            match_data = match_data_response.json()
        else:
            raise HTTPException(
                status_code=match_data_response.status_code,
                detail="Error fetching match data",
            )

        t = _get_stats_from_match_endpoint(match_data, puuid)
        res.append(t)

        match_timeline_response = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline",
            headers={"X-Riot-Token": settings.RIOT_API_KEY},
        )

        if match_timeline_response.status_code == 200:
            match_timeline_data = match_timeline_response.json()
        else:
            raise HTTPException(
                status_code=match_timeline_response.status_code,
                detail="Error fetching match timeline data",
            )

        t2 = _get_stats_from_match_timeline(match_timeline_data, puuid)
        res2.append(t2)
    r = [{**a, **b} for a, b in zip(res, res2)]
    r2 = {i: t for i, t in enumerate(r)}

    return r2


def _find_player_index(participants, puuid):
    for index, player in enumerate(participants):
        if player.get("puuid") == puuid:
            return index
    return -1


def _get_stats_from_match_endpoint(match_data, puuid):
    d = match_data
    index = _find_player_index(d["info"]["participants"], puuid)

    if index == -1:
        raise HTTPException(status_code=500, detail="Internal server error")

    game_duration = d["info"]["gameDuration"] / 60

    res = {
        "kills": d["info"]["participants"][index]["kills"],
        "deaths": d["info"]["participants"][index]["deaths"],
        "assists": d["info"]["participants"][index]["assists"],
        "dpm": d["info"]["participants"][index]["challenges"]["damagePerMinute"],
        "damageshare": d["info"]["participants"][index]["challenges"][
            "teamDamagePercentage"
        ],
        "damagetakenperminute": d["info"]["participants"][index]["totalDamageTaken"]
        / game_duration,
        "wpm": d["info"]["participants"][index]["wardsPlaced"] / game_duration,
        "wcpm": d["info"]["participants"][index]["wardsKilled"] / game_duration,
        "vspm": d["info"]["participants"][index]["visionScore"] / game_duration,
        "earned_gpm": d["info"]["participants"][index]["goldEarned"] / game_duration,
        "cspm": (
            d["info"]["participants"][index]["totalMinionsKilled"]
            + d["info"]["participants"][index]["neutralMinionsKilled"]
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
    if player_participant_id + 5 <= 10:
        opp_participant_id = player_participant_id + 5
    else:
        opp_participant_id = player_participant_id - 5

    stats = {
        "player": {"kills": 0, "assists": 0, "deaths": 0},
        "opp": {"kills": 0, "assists": 0, "deaths": 0},
        "player_at": {
            10: {"kills": 0, "assists": 0, "deaths": 0},
            15: {"kills": 0, "assists": 0, "deaths": 0},
            20: {"kills": 0, "assists": 0, "deaths": 0},
            25: {"kills": 0, "assists": 0, "deaths": 0},
        },
        "opp_at": {
            10: {"kills": 0, "assists": 0, "deaths": 0},
            15: {"kills": 0, "assists": 0, "deaths": 0},
            20: {"kills": 0, "assists": 0, "deaths": 0},
            25: {"kills": 0, "assists": 0, "deaths": 0},
        },
    }

    for i, frame in enumerate(frames):
        for event in frame["events"]:
            if event["type"] == "CHAMPION_KILL":
                if event["killerId"] == player_participant_id:
                    stats["player"]["kills"] += 1
                elif (
                    "assistingParticipantIds" in event
                    and player_participant_id in event["assistingParticipantIds"]
                ):
                    stats["player"]["assists"] += 1
                elif event["victimId"] == player_participant_id:
                    stats["player"]["deaths"] += 1

                if event["killerId"] == opp_participant_id:
                    stats["opp"]["kills"] += 1
                elif (
                    "assistingParticipantIds" in event
                    and opp_participant_id in event["assistingParticipantIds"]
                ):
                    stats["opp"]["assists"] += 1
                elif event["victimId"] == opp_participant_id:
                    stats["opp"]["deaths"] += 1

        if i in stats["player_at"]:
            stats["player_at"][i]["kills"] = stats["player"]["kills"]
            stats["player_at"][i]["assists"] = stats["player"]["assists"]
            stats["player_at"][i]["deaths"] = stats["player"]["deaths"]

            stats["opp_at"][i]["kills"] = stats["opp"]["kills"]
            stats["opp_at"][i]["assists"] = stats["opp"]["assists"]
            stats["opp_at"][i]["deaths"] = stats["opp"]["deaths"]

    res = {
        "gold_at_10": {},
        "xp_at_10": {},
        "cs_at_10": {},
        "gold_diff_at_10": {},
        "xp_diff_at_10": {},
        "cs_diff_at_10": {},
        "kills_at_10": {},
        "assists_at_10": {},
        "deaths_at_10": {},
        "opp_kills_at_10": {},
        "opp_assists_at_10": {},
        "opp_deaths_at_10": {},
        "gold_at_15": {},
        "xp_at_15": {},
        "cs_at_15": {},
        "gold_diff_at_15": {},
        "xp_diff_at_15": {},
        "cs_diff_at_15": {},
        "kills_at_15": {},
        "assists_at_15": {},
        "deaths_at_15": {},
        "opp_kills_at_15": {},
        "opp_assists_at_15": {},
        "opp_deaths_at_15": {},
        "gold_at_20": {},
        "xp_at_20": {},
        "cs_at_20": {},
        "gold_diff_at_20": {},
        "xp_diff_at_20": {},
        "cs_diff_at_20": {},
        "kills_at_20": {},
        "assists_at_20": {},
        "deaths_at_20": {},
        "opp_kills_at_20": {},
        "opp_assists_at_20": {},
        "opp_deaths_at_20": {},
        "gold_at_25": {},
        "xp_at_25": {},
        "cs_at_25": {},
        "gold_diff_at_25": {},
        "xp_diff_at_25": {},
        "cs_diff_at_25": {},
        "kills_at_25": {},
        "assists_at_25": {},
        "deaths_at_25": {},
        "opp_kills_at_25": {},
        "opp_assists_at_25": {},
        "opp_deaths_at_25": {},
    }

    for time in [10, 15, 20, 25]:
        if time < len(frames):
            frame = d["info"]["frames"][time]
            player_frame = frame["participantFrames"][str(player_participant_id)]
            opp_frame = frame["participantFrames"][str(opp_participant_id)]

            res["gold_at_" + str(time)] = player_frame["totalGold"]
            res["xp_at_" + str(time)] = player_frame["xp"]
            res["cs_at_" + str(time)] = (
                player_frame["minionsKilled"] + player_frame["jungleMinionsKilled"]
            )

            res["gold_diff_at_" + str(time)] = (
                player_frame["totalGold"] - opp_frame["totalGold"]
            )
            res["xp_diff_at_" + str(time)] = player_frame["xp"] - opp_frame["xp"]
            res["cs_diff_at_" + str(time)] = (
                player_frame["minionsKilled"] + player_frame["jungleMinionsKilled"]
            ) - (opp_frame["minionsKilled"] + opp_frame["jungleMinionsKilled"])

            res["kills_at_" + str(time)] = stats["player_at"][time]["kills"]
            res["assists_at_" + str(time)] = stats["player_at"][time]["assists"]
            res["deaths_at_" + str(time)] = stats["player_at"][time]["deaths"]

            res["opp_kills_at_" + str(time)] = stats["opp_at"][time]["kills"]
            res["opp_assists_at_" + str(time)] = stats["opp_at"][time]["assists"]
            res["opp_deaths_at_" + str(time)] = stats["opp_at"][time]["deaths"]

    return res

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sklearn.preprocessing import StandardScaler
from umap import UMAP
from config import Settings, get_settings
import pandas as pd
from pydantic import BaseModel


class UserStats(BaseModel):
    kills: float
    deaths: float
    assists: float
    dpm: float
    damageshare: float
    damagetakenperminute: float
    wpm: float
    wcpm: float
    vspm: float
    earned_gpm: float
    cspm: float
    goldat10: float
    xpat10: float
    csat10: float
    opp_goldat10: float
    opp_xpat10: float
    opp_csat10: float
    golddiffat10: float
    xpdiffat10: float
    csdiffat10: float
    killsat10: float
    assistsat10: float
    deathsat10: float
    opp_killsat10: float
    opp_assistsat10: float
    opp_deathsat10: float
    goldat15: float
    xpat15: float
    csat15: float
    opp_goldat15: float
    opp_xpat15: float
    opp_csat15: float
    golddiffat15: float
    xpdiffat15: float
    csdiffat15: float
    killsat15: float
    assistsat15: float
    deathsat15: float
    opp_killsat15: float
    opp_assistsat15: float
    opp_deathsat15: float
    goldat20: float
    xpat20: float
    csat20: float
    opp_goldat20: float
    opp_xpat20: float
    opp_csat20: float
    golddiffat20: float
    xpdiffat20: float
    csdiffat20: float
    killsat20: float
    assistsat20: float
    deathsat20: float
    opp_killsat20: float
    opp_assistsat20: float
    opp_deathsat20: float
    goldat25: float
    xpat25: float
    csat25: float
    opp_goldat25: float
    opp_xpat25: float
    opp_csat25: float
    golddiffat25: float
    xpdiffat25: float
    csdiffat25: float
    killsat25: float
    assistsat25: float
    deathsat25: float
    opp_killsat25: float
    opp_assistsat25: float
    opp_deathsat25: float


router = APIRouter()

ConfigDeps = Annotated[Settings, Depends(get_settings)]


@router.post("/")
async def transform_user_stats(user_stats: UserStats, request: Request):
    umap_model: UMAP = request.app.state.model
    if umap_model == None:
        raise HTTPException(status_code=500, detail="Model is not found.")

    scaler: StandardScaler = request.app.state.scaler
    if scaler == None:
        raise HTTPException(status_code=500, detail="Scaler is not found.")

    features_list = {
        "kills": user_stats.kills,
        "deaths": user_stats.deaths,
        "assists": user_stats.assists,
        "dpm": user_stats.dpm,
        "damageshare": user_stats.damageshare,
        "damagetakenperminute": user_stats.damagetakenperminute,
        "wpm": user_stats.wpm,
        "wcpm": user_stats.wcpm,
        "vspm": user_stats.vspm,
        "earned gpm": user_stats.earned_gpm,
        "cspm": user_stats.cspm,
        "goldat10": user_stats.goldat10,
        "xpat10": user_stats.xpat10,
        "csat10": user_stats.csat10,
        "opp_goldat10": user_stats.opp_goldat10,
        "opp_xpat10": user_stats.opp_xpat10,
        "opp_csat10": user_stats.opp_csat10,
        "golddiffat10": user_stats.golddiffat10,
        "xpdiffat10": user_stats.xpdiffat10,
        "csdiffat10": user_stats.csdiffat10,
        "killsat10": user_stats.killsat10,
        "assistsat10": user_stats.assistsat10,
        "deathsat10": user_stats.deathsat10,
        "opp_killsat10": user_stats.opp_killsat10,
        "opp_assistsat10": user_stats.opp_assistsat10,
        "opp_deathsat10": user_stats.opp_deathsat10,
        "goldat15": user_stats.goldat15,
        "xpat15": user_stats.xpat15,
        "csat15": user_stats.csat15,
        "opp_goldat15": user_stats.opp_goldat15,
        "opp_xpat15": user_stats.opp_xpat15,
        "opp_csat15": user_stats.opp_csat15,
        "golddiffat15": user_stats.golddiffat15,
        "xpdiffat15": user_stats.xpdiffat15,
        "csdiffat15": user_stats.csdiffat15,
        "killsat15": user_stats.killsat15,
        "assistsat15": user_stats.assistsat15,
        "deathsat15": user_stats.deathsat15,
        "opp_killsat15": user_stats.opp_killsat15,
        "opp_assistsat15": user_stats.opp_assistsat15,
        "opp_deathsat15": user_stats.opp_deathsat15,
        "goldat20": user_stats.goldat20,
        "xpat20": user_stats.xpat20,
        "csat20": user_stats.csat20,
        "opp_goldat20": user_stats.opp_goldat20,
        "opp_xpat20": user_stats.opp_xpat20,
        "opp_csat20": user_stats.opp_csat20,
        "golddiffat20": user_stats.golddiffat20,
        "xpdiffat20": user_stats.xpdiffat20,
        "csdiffat20": user_stats.csdiffat20,
        "killsat20": user_stats.killsat20,
        "assistsat20": user_stats.assistsat20,
        "deathsat20": user_stats.deathsat20,
        "opp_killsat20": user_stats.opp_killsat20,
        "opp_assistsat20": user_stats.opp_assistsat20,
        "opp_deathsat20": user_stats.opp_deathsat20,
        "goldat25": user_stats.goldat25,
        "xpat25": user_stats.xpat25,
        "csat25": user_stats.csat25,
        "opp_goldat25": user_stats.opp_goldat25,
        "opp_xpat25": user_stats.opp_xpat25,
        "opp_csat25": user_stats.opp_csat25,
        "golddiffat25": user_stats.golddiffat25,
        "xpdiffat25": user_stats.xpdiffat25,
        "csdiffat25": user_stats.csdiffat25,
        "killsat25": user_stats.killsat25,
        "assistsat25": user_stats.assistsat25,
        "deathsat25": user_stats.deathsat25,
        "opp_killsat25": user_stats.opp_killsat25,
        "opp_assistsat25": user_stats.opp_assistsat25,
        "opp_deathsat25": user_stats.opp_deathsat25,
    }

    features_df = pd.DataFrame([features_list])
    try:
        user_stats_scaled = scaler.transform(features_df)
        transformed_user_stats = umap_model.transform(user_stats_scaled)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"user_coordinates": transformed_user_stats.tolist()}

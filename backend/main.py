from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}


@app.get("/api/data")
def get_data():
    return {
        "id": 123,
        "name": "Sample Data",
        "description": "This data came from your Python backend.",
    }


@app.get("/api/matches")
async def get_matches(gameName: str, tagLine: str):
    try:
        player_details = requests.get(
            f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName.strip()}/{tagLine.strip()}",
            headers={"X-Riot-Token": RIOT_API_KEY},
        ).json()

        ranked_match_list = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{player_details['puuid'].strip()}/ids?type=ranked&start=0&count=20",
            headers={"X-Riot-Token": RIOT_API_KEY},
        ).json()

        return ranked_match_list
    except Exception as e:
        return e

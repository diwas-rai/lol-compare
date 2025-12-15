import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routers import pro_stats, analyse, warmup

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


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

app.include_router(pro_stats.router, prefix="/api/pro-stats", tags=["Pro Stats"])
app.include_router(analyse.router, prefix="/api/analyse", tags=["Analyse"])
app.include_router(warmup.router, prefix="/api/warmup", tags=["Warmup"])


@app.get("/")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}


handler = Mangum(app, lifespan="on")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller import router

app = FastAPI(title="reportgenerator Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

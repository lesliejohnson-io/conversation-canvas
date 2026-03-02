from fastapi import FastAPI
from .db import init_db
from .api.sessions import router as sessions_router
from .api.read import router as read_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Paloma Session Canvas MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.include_router(sessions_router)
app.include_router(read_router)

@app.get("/health")
def health() -> dict:
    return {"ok": True}


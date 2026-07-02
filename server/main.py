"""Future Abdullah (2050) — FastAPI backend."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from server.personality import get_response, get_timeline, get_welcome_message
from server.sessions import store

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(
    title="Future Abdullah API",
    description="Dynamic chat backend for Abdullah.exe (2050 Edition)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = None
    topic: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    topics: list[str]
    stats: dict
    counter_delta: dict
    engine: str


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "persona": "Future Abdullah 2050"}


@app.get("/api/timeline")
async def timeline() -> list[dict[str, str]]:
    return get_timeline()


@app.get("/api/welcome")
async def welcome(session_id: str | None = None) -> dict:
    session = store.get(session_id)
    return {
        "message": get_welcome_message(),
        "session_id": session.id,
        "stats": session.to_stats(),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session = store.get(body.session_id)
    store.add_message(session, "user", message)

    result = await get_response(session, message, body.topic)
    store.add_message(session, "assistant", result["reply"])

    return ChatResponse(
        reply=result["reply"],
        session_id=session.id,
        topics=result["topics"],
        stats=result["stats"],
        counter_delta=result["counter_delta"],
        engine=result["engine"],
    )


@app.get("/api/stats/{session_id}")
async def stats(session_id: str) -> dict:
    session = store.get_existing(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_stats()


# Static files — must be last
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")

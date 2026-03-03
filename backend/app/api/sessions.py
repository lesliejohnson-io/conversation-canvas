import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlmodel import Session as DBSession

from ..db import engine
from ..models import Session, Sentence
from ..services.otter_ingest import parse_txt_to_sentences

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("/ingest")
async def ingest_otter(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Expected a .txt file export")

    raw = await file.read()
    try:
        txt = raw.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode file as UTF-8 text")

    ingest = parse_txt_to_sentences(txt)

    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    with DBSession(engine) as db:
        db.add(Session(id=session_id, source_filename=file.filename, created_at=now))
        for idx, item in enumerate(ingest.sentences):
            db.add(
                Sentence(
                    session_id=session_id,
                    sentence_index=idx,
                    speaker=item.speaker,
                    sentence_text=item.sentence_text,
                )
            )
        db.commit()

    return {
        "session": {"id": session_id, "source_filename": file.filename, "created_at": now.isoformat() + "Z"},
        "stats": {"sentences_ingested": len(ingest.sentences)},
    }
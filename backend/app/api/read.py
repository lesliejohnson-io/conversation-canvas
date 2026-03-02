from fastapi import APIRouter
from sqlmodel import Session as DBSession, select

from ..models import Sentence, Phrase
from ..services.phrase_seed import seed_phrases_from_sentences

from ..db import engine
from ..models import Sentence

router = APIRouter(prefix="/api", tags=["read"])

@router.get("/sessions/{session_id}/sentences")
def list_sentences(session_id: str) -> dict:
    with DBSession(engine) as db:
        rows = db.exec(
            select(Sentence)
            .where(Sentence.session_id == session_id)
            .order_by(Sentence.sentence_index.asc())
        ).all()



    return {
        "session_id": session_id,
        "sentences": [
            {
                "sentence_index": r.sentence_index,
                "speaker": r.speaker,
                "sentence_text": r.sentence_text,
            }
            for r in rows
        ],
    }

@router.post("/sessions/{session_id}/seed_phrases")
def seed_phrases(session_id: str) -> dict:
    stats = seed_phrases_from_sentences(session_id)
    return {"session_id": session_id, "stats": stats}

_COMMITMENT_ORDER = [
    "i will",
    "i'm going to",
    "i want",
    "i'd be",
    "i'd have",
]

def _commitment_score(text: str) -> int:
    t = text.strip().lower()
    for i, prefix in enumerate(_COMMITMENT_ORDER):
        if t.startswith(prefix):
            return len(_COMMITMENT_ORDER) - i
    return 0

@router.get("/sessions/{session_id}/phrases")
def list_phrases(session_id: str) -> dict:
    with DBSession(engine) as db:
        rows = db.exec(
            select(Phrase)
            .where(Phrase.session_id == session_id)
        ).all()

    # sort per V1: recurrence desc, commitment desc, classification_conf desc, then id asc
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            -r.recurrence_count,
            -_commitment_score(r.phrase_text),
            -(r.classification_confidence or 0.0),
            r.id or 0,
        ),
    )

    return {
        "session_id": session_id,
        "phrases": [
            {
                "id": r.id,
                "phrase_text": r.phrase_text,
                "phrase_norm": r.phrase_norm,
                "source_sentence_index": r.source_sentence_index,
                "extraction_confidence": r.extraction_confidence,
                "classification_confidence": r.classification_confidence,
                "quadrant_model": r.quadrant_model,
                "quadrant_final": r.quadrant_final,
                "recurrence_count": r.recurrence_count,
            }
            for r in rows_sorted
        ],
    }
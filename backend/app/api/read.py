from fastapi import APIRouter
from sqlmodel import Session as DBSession, select
from fastapi import HTTPException
from pydantic import BaseModel
from ..models import Sentence, Phrase
from ..services.phrase_seed import seed_phrases_from_sentences
from ..db import engine
from ..models import Sentence
import math
from collections import defaultdict
from ..models import Phrase

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
            -(r.recurrence_count or 1),
            -(r.extraction_confidence or 0.0),
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

from typing import Optional, Literal

Quadrant = Literal[
    "resourceful_past",
    "preferred_future",
    "troubled_past",
    "dreaded_future",
]

class PhraseQuadrantUpdate(BaseModel):
    quadrant_final: Optional[Quadrant] = None

@router.patch("/phrases/{phrase_id}")
def update_phrase_quadrant(phrase_id: int, payload: PhraseQuadrantUpdate) -> dict:
    with DBSession(engine) as db:
        phrase = db.get(Phrase, phrase_id)
        if not phrase:
            raise HTTPException(status_code=404, detail="Phrase not found")

        # IMPORTANT: only update quadrant_final
        phrase.quadrant_final = payload.quadrant_final
        db.add(phrase)
        db.commit()
        db.refresh(phrase)

        return {
            "id": phrase.id,
            "phrase_text": phrase.phrase_text,
            "quadrant_model": phrase.quadrant_model,
            "quadrant_final": phrase.quadrant_final,
        }

@router.get("/sessions/{session_id}/quadrant_map")
def quadrant_map(session_id: str) -> dict:
    """
    V1 quadrant map:
    - Include phrases where quadrant_final is not null
    - Ring determined by recurrence_count (higher = closer to center)
    - Within each quadrant + ring: evenly spaced on that ring
    """
    with DBSession(engine) as db:
        rows = db.exec(
            select(Phrase)
            .where(Phrase.session_id == session_id)
            .where((Phrase.quadrant_final != None) | (Phrase.quadrant_model != None))  # noqa: E711
            .order_by(Phrase.recurrence_count.desc(), Phrase.id.asc())
        ).all()

    # Group: quadrant -> recurrence_count -> list[Phrase]
    grouped = defaultdict(lambda: defaultdict(list))
    for p in rows:
        effective_quadrant = p.quadrant_final or p.quadrant_model
        if not effective_quadrant:
            continue
        grouped[effective_quadrant][int(p.recurrence_count or 1)].append(p)
    # Determine ring order per quadrant (highest recurrence closest to center)
    # We'll map each recurrence_count to a ring_index: 0=center-most, increasing outward
    nodes = []
    for quadrant, by_recur in grouped.items():
        recurrence_levels = sorted(by_recur.keys(), reverse=True)  # high -> low
        recur_to_ring = {recur: ring_idx for ring_idx, recur in enumerate(recurrence_levels)}

        for recur in recurrence_levels:
            items = by_recur[recur]
            ring_index = recur_to_ring[recur]

            # Radius: ring_index 0 is closest to center
            # Keep it simple + deterministic
            radius = 0.20 + (ring_index * 0.22)  # 0.20, 0.42, 0.64, ...

            n = len(items)
            for i, p in enumerate(items):
                angle = (2 * math.pi * i) / max(n, 1)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                nodes.append(
                    {
                        "phrase_id": p.id,
                        "phrase_text": p.phrase_text,
                        "quadrant_final": effective_quadrant,
                        "recurrence_count": p.recurrence_count,
                        "ring_index": ring_index,
                        "x": round(x, 4),
                        "y": round(y, 4),
                    }
                )

    return {"session_id": session_id, "nodes": nodes}
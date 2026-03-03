from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session as DBSession, select
from typing import Optional, Literal
import math
from collections import defaultdict

from ..db import engine
from ..models import Sentence, Phrase
from ..services.phrase_seed import seed_phrases_from_sentences

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

    # Rank (C): recurrence desc, extraction_confidence desc, id asc
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
    Dialogic Map V1 (Round 2+):
    - Include phrases where quadrant_final is set OR quadrant_model is set
    - Quadrant for placement = quadrant_final if present else quadrant_model
    - Ring = 5 recency buckets from source_sentence_index
      * 0 = most recent (closest to center)
      * 4 = oldest (farthest)
    - Numbering = sequential in conversation order (by source_sentence_index, id)
    - Label = first 4 meaningful words (strip common fillers)
    - Dot size = deterministic importance_score
    - Opacity = coach override => 1.0 else scaled from classification_confidence
    - Within each quadrant + ring: evenly spaced on that ring
    """
    with DBSession(engine) as db:
        rows = db.exec(
            select(Phrase)
            .where(Phrase.session_id == session_id)
            .where((Phrase.quadrant_final != None) | (Phrase.quadrant_model != None))  # noqa: E711
            .order_by(Phrase.source_sentence_index.asc(), Phrase.id.asc())
        ).all()

        sentence_idxs = db.exec(
            select(Sentence.sentence_index)
            .where(Sentence.session_id == session_id)
        ).all()
        total_sentences = len(sentence_idxs)

    def recency_bucket(source_idx: int, total: int) -> int:
        # 5 buckets: 0 (most recent) ... 4 (oldest)
        if total <= 1:
            return 0
        frac = source_idx / max(total - 1, 1)  # 0..1
        bucket = int(frac * 5)  # 0..5
        if bucket >= 5:
            bucket = 4
        # invert: most recent => 0
        return 4 - bucket

    # B) Strip common fillers, then take first 4 words
    _FILLER_PREFIXES = [
        "i think",
        "i mean",
        "i feel like",
        "you know",
        "so",
        "yeah",
        "well",
        "like",
    ]

    def short_label(text: str) -> str:
        t = (text or "").strip().lower()

        for prefix in _FILLER_PREFIXES:
            if t.startswith(prefix + " "):
                t = t[len(prefix):].strip()
                break

        words = t.split()
        return " ".join(words[:4])

    def importance_score(p: Phrase) -> int:
        score = 0

        # Strongest deterministic signal: coach override
        if p.quadrant_final:
            score += 2

        # Intent / high-signal prefixes (deterministic)
        t = (p.phrase_text or "").strip().lower()
        triggers = [
            "i want",
            "i will",
            "i'm going",
            "im going",
            "i can't",
            "i cant",
            "i'm afraid",
            "im afraid",
            "what if",
        ]
        if any(t.startswith(tr) for tr in triggers):
            score += 1

        # Supportive signal: repetition
        if (p.recurrence_count or 1) > 1:
            score += 1

        return min(score, 3)

    # Group: quadrant -> recency_bucket -> list[Phrase]
    grouped = defaultdict(lambda: defaultdict(list))
    for p in rows:
        quadrant = p.quadrant_final or p.quadrant_model
        if not quadrant:
            continue
        b = recency_bucket(int(p.source_sentence_index or 0), total_sentences)
        grouped[quadrant][b].append(p)

    nodes = []

    # Numbering should follow conversation order, not quadrant grouping.
    # So we compute the sequential numbers from the sorted 'rows' list.
    phrase_id_to_number = {}
    seq = 1
    for p in rows:
        quadrant = p.quadrant_final or p.quadrant_model
        if not quadrant:
            continue
        phrase_id_to_number[p.id] = seq
        seq += 1

    for quadrant, by_bucket in grouped.items():
        bucket_levels = sorted(by_bucket.keys())  # 0..4 (not all may exist)

        for b in bucket_levels:
            items = by_bucket[b]
            ring_index = b

            # Radius: ring_index 0 is closest to center
            radius = 0.18 + (ring_index * 0.16)  # 0.18, 0.34, 0.50, 0.66, 0.82

            n = len(items)
            for i, p in enumerate(items):
                angle = (2 * math.pi * i) / max(n, 1)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                imp = importance_score(p)
                dot_radius = 6 + (imp * 2)  # 6..12

                if p.quadrant_final:
                    opacity = 1.0
                else:
                    opacity = max(0.7, min(1.0, float(p.classification_confidence or 0.7)))

                nodes.append(
                    {
                        "phrase_id": p.id,
                        "number": phrase_id_to_number.get(p.id),
                        "label": short_label(p.phrase_text),
                        "phrase_text": p.phrase_text,  # full phrase for side panel / tooltip
                        "quadrant": quadrant,
                        "ring_index": ring_index,
                        "dot_radius": dot_radius,
                        "opacity": round(opacity, 2),
                        "recurrence_count": p.recurrence_count,
                        "source_sentence_index": p.source_sentence_index,
                        "x": round(x, 4),
                        "y": round(y, 4),
                    }
                )

    return {"session_id": session_id, "nodes": nodes}
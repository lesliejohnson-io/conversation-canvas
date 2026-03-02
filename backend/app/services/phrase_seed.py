from datetime import datetime
from sqlmodel import Session as DBSession, select

from ..db import engine
from ..models import Sentence, Phrase
from .phrase_norm import normalize_phrase
from .invariants import enforce_phrase_invariants

def seed_phrases_from_sentences(session_id: str) -> dict:
    """
    TEMP scaffolding: 1 phrase per sentence (phrase_text = sentence_text)
    - collapses duplicates by phrase_norm
    - increments recurrence_count
    - sets placeholder confidences so ranking/list endpoints work
    - quadrant_model/quadrant_final remain null in this step
    """
    with DBSession(engine) as db:
        sentences = db.exec(
            select(Sentence)
            .where(Sentence.session_id == session_id)
            .order_by(Sentence.sentence_index.asc())
        ).all()

        created = 0
        collapsed = 0

        for s in sentences:
            phrase_text = s.sentence_text.strip()
            if not phrase_text:
                continue

            norm = normalize_phrase(phrase_text)

            existing = db.exec(
                select(Phrase)
                .where(Phrase.session_id == session_id)
                .where(Phrase.phrase_norm == norm)
            ).first()

            if existing:
                existing.recurrence_count += 1
                existing.updated_at = datetime.utcnow()
                collapsed += 1
            else:
                obj = Phrase(
                    session_id=session_id,
                    phrase_text=phrase_text,
                    phrase_norm=norm,
                    source_sentence_index=s.sentence_index,
                    extraction_confidence=0.99,
                    classification_confidence=0.0,
                    quadrant_model=None,
                    quadrant_final=None,
                    recurrence_count=1,
                    updated_at=datetime.utcnow(),
                )
                enforce_phrase_invariants(obj)
                db.add(obj)
                db.add(
                    Phrase(
                        session_id=session_id,
                        phrase_text=phrase_text,
                        phrase_norm=norm,
                        source_sentence_index=s.sentence_index,
                        extraction_confidence=0.99,
                        classification_confidence=0.0,
                        quadrant_model=None,
                        quadrant_final=None,
                        recurrence_count=1,
                        updated_at=datetime.utcnow(),
                    )
                )
                created += 1

        db.commit()

    return {"phrases_created": created, "phrases_collapsed": collapsed}
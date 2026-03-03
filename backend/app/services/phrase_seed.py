from datetime import datetime
from sqlmodel import Session as DBSession, select

from ..db import engine
from ..models import Sentence, Phrase
from .phrase_norm import normalize_phrase
from .invariants import enforce_phrase_invariants
from .doq_rules import sentence_to_phrases


def seed_phrases_from_sentences(session_id: str) -> dict:
    """
    Deterministic V1 extraction + classification (no LLM).
    Rules:
    - Extract candidates from each sentence with extraction_confidence >= 0.6
    - Classify candidates; if classification_confidence < 0.7 => quadrant_model must be null
    - Keep up to 2 phrases per sentence ONLY if they classify into different quadrants (both non-null)
    - Preserve recurrence collapse exactly: collapse by phrase_norm, increment recurrence_count
    - Preserve traceability: keep source_sentence_index from the originating sentence
    """
    with DBSession(engine) as db:
        sentences = db.exec(
            select(Sentence)
            .where(Sentence.session_id == session_id)
            .where(Sentence.speaker == "Client")
            .order_by(Sentence.sentence_index.asc())
        ).all()

        created = 0
        collapsed = 0

        for s in sentences:
            sentence_text = (s.sentence_text or "").strip()
            if not sentence_text:
                continue

            candidates = sentence_to_phrases(sentence_text)
            if not candidates:
                continue

            for cand in candidates:
                phrase_text = cand.phrase_text.strip()
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

                    # Deterministic model outputs can be refreshed on recurrence collapse
                    existing.extraction_confidence = float(cand.extraction_confidence)
                    existing.classification_confidence = float(cand.classification_confidence)
                    existing.quadrant_model = cand.quadrant_model  # already null if <0.7

                    collapsed += 1
                else:
                    obj = Phrase(
                        session_id=session_id,
                        phrase_text=phrase_text,
                        phrase_norm=norm,
                        source_sentence_index=s.sentence_index,
                        extraction_confidence=float(cand.extraction_confidence),
                        classification_confidence=float(cand.classification_confidence),
                        quadrant_model=cand.quadrant_model,  # already null if <0.7
                        quadrant_final=None,
                        recurrence_count=1,
                        updated_at=datetime.utcnow(),
                    )
                    enforce_phrase_invariants(obj)
                    db.add(obj)
                    created += 1

        db.commit()

    return {"phrases_created": created, "phrases_collapsed": collapsed}
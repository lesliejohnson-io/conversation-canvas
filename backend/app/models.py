from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Index


class Session(SQLModel, table=True):
    id: str = Field(primary_key=True)
    source_filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Sentence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    sentence_index: int = Field(index=True)
    speaker: str
    sentence_text: str


class Phrase(SQLModel, table=True):
    __table_args__ = (
        Index("idx_phrases_session_norm", "session_id", "phrase_norm"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)

    phrase_text: str
    phrase_norm: str

    source_sentence_index: int

    extraction_confidence: float
    classification_confidence: float

    quadrant_model: Optional[str] = Field(default=None, nullable=True)
    quadrant_final: Optional[str] = Field(default=None, nullable=True)

    recurrence_count: int = Field(default=1)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
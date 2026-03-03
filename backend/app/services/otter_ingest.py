import re
from dataclasses import dataclass
from typing import List, Optional

SPEAKER2_HEADER_RE = re.compile(r"^\s*Speaker\s+2\s*$", re.IGNORECASE)
SPEAKER_HEADER_RE = re.compile(r"^\s*Speaker\s+\d+\s*$", re.IGNORECASE)

# Inline labeled line: "Client: blah"
LABELED_INLINE_RE = re.compile(r"^\s*(Coach|Client)\s*:\s*(.+)\s*$", re.IGNORECASE)

# Block header: "Client (00:07):" or "Coach (0:07):"
LABELED_BLOCK_HEADER_RE = re.compile(
    r"^\s*(Coach|Client)\s*\(\s*\d{1,2}:\d{2}\s*\)\s*:\s*$",
    re.IGNORECASE,
)

SENTENCE_SPLIT_RE = re.compile(r"[.?!]+")


def _normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class IngestSentence:
    speaker: str
    sentence_text: str


@dataclass
class IngestResult:
    sentences: List[IngestSentence]


def _split_into_sentences(text: str) -> List[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text)]
    out: List[str] = []
    for p in parts:
        p = _normalize_whitespace(p)
        if len(p) >= 3:
            out.append(p)
    return out


def parse_txt_to_sentences(txt: str) -> IngestResult:
    """
    Supports three input formats:

    1) Labeled BLOCK transcript:
       Coach (00:03):
       <one or more lines of text>
       Client (00:07):
       <...>

    2) Labeled INLINE transcript:
       Coach: ...
       Client: ...

    3) Otter fallback:
       Speaker 2 blocks only (legacy)
    """
    lines = txt.splitlines()

    # --- 1) BLOCK labeled transcript ---
    block_sentences: List[IngestSentence] = []
    current_speaker: Optional[str] = None
    buffer: List[str] = []
    saw_block = False

    def flush_block():
        nonlocal buffer
        if current_speaker and buffer:
            chunk = _normalize_whitespace(" ".join(buffer))
            if chunk:
                for sent in _split_into_sentences(chunk):
                    block_sentences.append(
                        IngestSentence(speaker=current_speaker, sentence_text=sent)
                    )
        buffer = []

    for line in lines:
        m = LABELED_BLOCK_HEADER_RE.match(line)
        if m:
            saw_block = True
            flush_block()
            current_speaker = m.group(1).capitalize()  # Coach / Client
            continue

        if current_speaker:
            stripped = line.strip()
            if stripped:
                buffer.append(stripped)

    flush_block()

    if saw_block and block_sentences:
        return IngestResult(sentences=block_sentences)

    # --- 2) INLINE labeled transcript ---
    inline_sentences: List[IngestSentence] = []
    labeled_found = False
    for line in lines:
        m = LABELED_INLINE_RE.match(line)
        if not m:
            continue
        labeled_found = True
        speaker = m.group(1).capitalize()
        content = m.group(2)
        for sent in _split_into_sentences(content):
            inline_sentences.append(IngestSentence(speaker=speaker, sentence_text=sent))

    if labeled_found and inline_sentences:
        return IngestResult(sentences=inline_sentences)

    # --- 3) Otter Speaker 2 fallback ---
    speaker2_chunks: List[str] = []
    collecting = False
    buffer = []

    def flush_otter():
        nonlocal buffer
        if buffer:
            chunk = _normalize_whitespace(" ".join(buffer))
            if chunk:
                speaker2_chunks.append(chunk)
        buffer = []

    for line in lines:
        if SPEAKER2_HEADER_RE.match(line):
            flush_otter()
            collecting = True
            continue

        if SPEAKER_HEADER_RE.match(line):
            flush_otter()
            collecting = False
            continue

        if collecting:
            stripped = line.strip()
            if stripped:
                buffer.append(stripped)

    flush_otter()

    out: List[IngestSentence] = []
    for chunk in speaker2_chunks:
        for sent in _split_into_sentences(chunk):
            out.append(IngestSentence(speaker="Client", sentence_text=sent))

    return IngestResult(sentences=out)
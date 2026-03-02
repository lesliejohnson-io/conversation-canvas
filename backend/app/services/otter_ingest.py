import re
from dataclasses import dataclass
from typing import List, Tuple

SPEAKER2_HEADER_RE = re.compile(r"^\s*Speaker\s+2\s*$", re.IGNORECASE)
SPEAKER_HEADER_RE = re.compile(r"^\s*Speaker\s+\d+\s*$", re.IGNORECASE)

SENTENCE_SPLIT_RE = re.compile(r"[.?!]+")

def _normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

@dataclass
class IngestResult:
    sentences: List[str]

def parse_otter_txt_to_speaker2_sentences(txt: str) -> IngestResult:
    """
    V1 Otter ingest:
    - Consider only Speaker 2 blocks
    - Collect contiguous lines until the next Speaker header
    - Split into sentences by simple punctuation regex on .?!
    - Return cleaned, non-empty sentence strings
    """
    lines = txt.splitlines()

    speaker2_chunks: List[str] = []
    collecting = False
    buffer: List[str] = []

    def flush_buffer():
        nonlocal buffer
        if buffer:
            chunk = _normalize_whitespace(" ".join(buffer))
            if chunk:
                speaker2_chunks.append(chunk)
        buffer = []

    for line in lines:
        if SPEAKER2_HEADER_RE.match(line):
            # starting Speaker 2 block
            flush_buffer()
            collecting = True
            continue

        # any speaker header ends current collection
        if SPEAKER_HEADER_RE.match(line):
            flush_buffer()
            collecting = False
            continue

        if collecting:
            stripped = line.strip()
            if stripped:
                buffer.append(stripped)

    flush_buffer()

    # Split chunks into sentences
    sentences: List[str] = []
    for chunk in speaker2_chunks:
        parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(chunk)]
        for p in parts:
            p = _normalize_whitespace(p)
            if len(p) >= 3:
                sentences.append(p)

    return IngestResult(sentences=sentences)
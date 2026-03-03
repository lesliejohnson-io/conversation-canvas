import re
from dataclasses import dataclass
from typing import Optional, List, Tuple

QUADRANTS = (
    "resourceful_past",
    "preferred_future",
    "troubled_past",
    "dreaded_future",
)

FILLER_RE = re.compile(
    r"\b(?:you know|kind of|sort of|like|maybe|actually|basically|literally)\b",
    re.I,
)


@dataclass(frozen=True)
class PhraseCandidate:
    phrase_text: str
    extraction_confidence: float
    quadrant_model: Optional[str]
    classification_confidence: float


def _clean(text: str) -> str:
    t = text.strip()
    t = FILLER_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _token_count(text: str) -> int:
    return len([tok for tok in re.split(r"\s+", text.strip()) if tok])


def extract_candidates(sentence: str) -> List[Tuple[str, float]]:
    s = sentence.strip()
    if not s:
        return []

    low = s.lower()

    patterns = [
        r"\b(i\s+will\s+.+)",
        r"\b(i'?m\s+going\s+to\s+.+)",
        r"\b(i\s+plan\s+to\s+.+)",
        r"\b(i\s+want\s+to\s+.+)",
        r"\b(i\s+need\s+to\s+.+)",
        r"\b(i'?d\s+like\s+to\s+.+)",
        r"\b(i\s+can'?t\s+.+)",
        r"\b(i\s+struggle\s+to\s+.+)",
        r"\b(it'?s\s+hard\s+to\s+.+)",
        r"\b(i'?m\s+afraid\s+.+)",
        r"\b(i\s+worry\s+.+)",
        r"\b(what\s+if\s+.+)",
        r"\b(i\s+managed\s+to\s+.+)",
        r"\b(i\s+was\s+able\s+to\s+.+)",
        r"\b(i'?ve\s+been\s+able\s+to\s+.+)",
        r"\b(i\s+can\s+.+)",
        r"\b(i'?ve\s+.+)",
        r"\b(i\s+have\s+.+)",
    ]

    cands: List[Tuple[str, float]] = []

    for pat in patterns:
        m = re.search(pat, low, flags=re.I)
        if not m:
            continue

        start, end = m.span(1)
        raw_phrase = s[start:end]
        phrase = _clean(raw_phrase)

        if not phrase:
            continue

        conf = 0.45

        if re.match(
            r"^(i\s+will|i'?m\s+going\s+to|i\s+want\s+to|i\s+need\s+to|i'?d\s+like\s+to|i\s+can'?t|i'?m\s+afraid|what\s+if)\b",
            phrase,
            re.I,
        ):
            conf += 0.25

        if re.search(
            r"\b(goal|organize|finish|start|build|apply|hire|prioritize|focus|decide|choose|commit)\b",
            phrase,
            re.I,
        ):
            conf += 0.10

        if re.search(
            r"\b(overwhelmed|stressed|anxious|worried|struggling|stuck|tired|frustrated)\b",
            phrase,
            re.I,
        ):
            conf += 0.10

        n = _token_count(phrase)
        if n < 3 or n > 14:
            conf -= 0.15

        if len(phrase) < len(raw_phrase.strip()) * 0.75:
            conf -= 0.20

        conf = max(0.0, min(1.0, conf))
        cands.append((phrase, conf))

    seen = set()
    uniq: List[Tuple[str, float]] = []
    for p, c in cands:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append((p, c))

    uniq.sort(key=lambda x: x[1], reverse=True)
    return uniq


def classify_doq(phrase: str) -> Tuple[Optional[str], float]:
    p = phrase.strip()
    low = p.lower()
    conf = 0.50

    scores = {q: 0.0 for q in QUADRANTS}

    if re.match(
        r"^(i\s+want|i\s+will|i'?m\s+going\s+to|i\s+plan\s+to|i\s+need\s+to|i'?d\s+like\s+to)\b",
        low,
    ):
        scores["preferred_future"] += 0.45
        conf += 0.30

    if re.match(
        r"^(i\s+managed\s+to|i\s+was\s+able\s+to|i'?ve\s+been\s+able\s+to|i\s+can\b|i'?ve\b|i\s+have\b)",
        low,
    ):
        scores["resourceful_past"] += 0.35
        conf += 0.15

    if re.match(
        r"^(i\s+can'?t|i\s+don'?t|i\s+struggle|it'?s\s+hard|i\s+feel\s+overwhelmed)",
        low,
    ):
        scores["troubled_past"] += 0.45
        conf += 0.30

    if re.match(r"^(i'?m\s+afraid|i\s+worry|what\s+if)", low):
        scores["dreaded_future"] += 0.45
        conf += 0.30

    if re.search(r"\b(managed|handled|figured out|learned|improved|succeeded)\b", low):
        scores["resourceful_past"] += 0.15
        conf += 0.10

    if re.search(r"\b(overwhelmed|stuck|struggling|hard|frustrated|tired)\b", low):
        scores["troubled_past"] += 0.15
        conf += 0.10

    if re.search(r"\b(lose|fail|never|ruin|mess up|end up)\b", low):
        scores["dreaded_future"] += 0.15
        conf += 0.10

    strong = [q for q, sc in scores.items() if sc >= 0.45]
    if len(strong) >= 2:
        conf -= 0.10

    conf = max(0.0, min(1.0, conf))
    best_q = max(scores.items(), key=lambda kv: kv[1])[0]
    best_score = scores[best_q]

    if best_score < 0.30:
        return (None, 0.0)

    if conf < 0.70:
        return (None, conf)

    return (best_q, conf)


def sentence_to_phrases(sentence: str) -> List[PhraseCandidate]:
    extracted = extract_candidates(sentence)
    extracted = [(p, c) for (p, c) in extracted if c >= 0.60]

    cands: List[PhraseCandidate] = []
    for p, econf in extracted:
        q, cconf = classify_doq(p)
        cands.append(
            PhraseCandidate(
                phrase_text=p,
                extraction_confidence=econf,
                quadrant_model=q,
                classification_confidence=cconf,
            )
        )

    if not cands:
        return []

    cands.sort(key=lambda x: x.extraction_confidence, reverse=True)
    top = cands[:2]

    if len(top) == 1:
        return top

    a, b = top[0], top[1]

    if (
        a.quadrant_model
        and b.quadrant_model
        and a.quadrant_model != b.quadrant_model
    ):
        return [a, b]

    return [a]
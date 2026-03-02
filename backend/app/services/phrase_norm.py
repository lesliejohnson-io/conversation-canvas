import re

_MINOR_PUNCT_RE = re.compile(r"""[,\;:"'()\[\]\{\}]""")
_END_PUNCT_RE = re.compile(r"""[.?!]+""")
_WS_RE = re.compile(r"\s+")

def normalize_phrase(text: str) -> str:
    """
    V1 recurrence normalization:
    - lowercase
    - strip minor punctuation ,;:"'()[]{} 
    - remove .?! (sentence split already did it, but keep safe)
    - trim
    - collapse whitespace
    """
    s = text.lower()
    s = _MINOR_PUNCT_RE.sub("", s)
    s = _END_PUNCT_RE.sub("", s)
    s = s.strip()
    s = _WS_RE.sub(" ", s)
    return s
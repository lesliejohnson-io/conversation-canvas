def enforce_phrase_invariants(phrase) -> None:
    """
    V1 invariants:
    - If classification_confidence < 0.7, quadrant_model MUST be null
    """
    if (phrase.classification_confidence or 0.0) < 0.7:
        phrase.quadrant_model = None
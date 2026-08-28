from __future__ import annotations

import json
import re
from typing import Callable, Any, Dict, Iterable, Tuple, Type, TypeAlias


def exact_match(pred: str, gold: str) -> float:
    return 1.0 if pred.strip() == gold.strip() else 0.0


def regex_match(pred: str, pattern: str) -> float:
    try:
        return 1.0 if re.fullmatch(pattern, pred) else 0.0
    except re.error:
        return 0.0


def json_valid(pred: str, _gold: str | None = None) -> float:
    try:
        json.loads(pred)
        return 1.0
    except Exception:
        return 0.0


REGISTRY: dict[str, Callable[[str, str], float]] = {
    "exact": exact_match,
    "regex": regex_match,
    "json": json_valid,
}


 
def make_json_schema_metric(schema: Dict[str, Any]) -> Callable[[str, str], float]:
    required = schema.get("required", [])
    props = schema.get("properties", {})

    def _validate_types(obj: Dict[str, Any]) -> bool:
        # mypy: annotate the allowed ClassInfo for isinstance
        ClassInfo: TypeAlias = type | tuple[type, ...]
        type_map: Dict[str, ClassInfo] = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "object": dict,
            "array": list,
        }
        for key, rule in props.items():
            if key not in obj:
                continue
            expected_type = rule.get("type")
            if expected_type:
                pytype: ClassInfo | None = type_map.get(expected_type)
                if pytype is not None and not isinstance(obj[key], pytype):
                    return False
        return True

    def metric(pred: str, _gold: str) -> float:
        try:
            obj = json.loads(pred)
        except Exception:
            return 0.0
        # required keys present
        if any(k not in obj for k in required):
            return 0.0
        # basic type checks
        if not _validate_types(obj):
            return 0.0
        return 1.0

    metric.__name__ = "json_schema"
    return metric


def _tokens(text: str) -> list[str]:
    return text.lower().split()


def jaccard(pred: str, gold: str) -> float:
    a = set(_tokens(pred))
    b = set(_tokens(gold))
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _char_ngrams(s: str, n: int = 3) -> Iterable[str]:
    s = s.lower()
    return [s[i : i + n] for i in range(max(0, len(s) - n + 1))] or []


def char_ngram_similarity(pred: str, gold: str, n: int = 3) -> float:
    # Handle empties explicitly: both empty -> 1.0; one empty -> 0.0
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0

    a = set(_char_ngrams(pred, n))
    b = set(_char_ngrams(gold, n))

    # If both strings are shorter than n, fall back to char-set Jaccard
    if not a and not b:
        ac = set(pred.lower())
        bc = set(gold.lower())
        return len(ac & bc) / len(ac | bc) if (ac or bc) else 1.0

    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


REGISTRY.update({
    "jaccard": jaccard,
    "char_ngram": lambda p, g: char_ngram_similarity(p, g, 3),
})

# --- Semantic-ish metrics (offline, no external deps) ---
STOPWORDS: set[str] = {
    "the","a","an","of","and","or","to","in","on","for","with","by","is","are","be","as","at","this","that","it"
}

def _filtered_tokens(text: str) -> list[str]:
    return [t for t in _tokens(text) if t and t not in STOPWORDS]


def token_f1(pred: str, gold: str) -> float:
    p = set(_filtered_tokens(pred))
    g = set(_filtered_tokens(gold))
    if not p and not g:
        return 1.0
    overlap = len(p & g)
    precision = overlap / len(p) if p else 0.0
    recall = overlap / len(g) if g else 0.0
    return (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0


def _freq(tokens: Iterable[str]) -> Dict[str, float]:
    d: Dict[str, float] = {}
    for t in tokens:
        d[t] = d.get(t, 0.0) + 1.0
    return d


def semantic_cosine(pred: str, gold: str) -> float:
    tp = _filtered_tokens(pred)
    tg = _filtered_tokens(gold)
    fp = _freq(tp)
    fg = _freq(tg)
    keys = set(fp) | set(fg)
    dot = sum(fp.get(k, 0.0) * fg.get(k, 0.0) for k in keys)
    norm_p = sum(v * v for v in fp.values()) ** 0.5
    norm_g = sum(v * v for v in fg.values()) ** 0.5
    if norm_p == 0 or norm_g == 0:
        return 0.0 if (tp or tg) else 1.0
    val = dot / (norm_p * norm_g)
    # Clamp to [0,1] for simplicity
    return max(0.0, min(1.0, val))


REGISTRY.update({
    "token_f1": token_f1,
    "semantic_cosine": semantic_cosine,
})

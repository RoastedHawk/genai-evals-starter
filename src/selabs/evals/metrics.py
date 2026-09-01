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

# --- Safety / Trust metrics ---

def citation_presence(pred: str, _gold: str) -> float:
    """Require a simple citation marker. Returns 1.0 if 'source:' or an http/https link is present."""
    p = pred.lower()
    return 1.0 if ("source:" in p or "http://" in p or "https://" in p) else 0.0


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")


def pii_safe(pred: str, _gold: str) -> float:
    """Return 1.0 when no obvious PII (email/phone) is detected; 0.0 otherwise."""
    if EMAIL_RE.search(pred) or PHONE_RE.search(pred):
        return 0.0
    return 1.0


REGISTRY.update({
    "citation_presence": citation_presence,
    "pii_safe": pii_safe,
})

# --- BLEU and ROUGE-L (offline baselines) ---

def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(max(0, len(tokens) - n + 1))]


def bleu(pred: str, gold: str, max_n: int = 4) -> float:
    """Compute a simple BLEU score (up to 4-gram) with brevity penalty.
    Offline and dependency-free; tokens split on whitespace.
    """
    p_toks = _tokens(pred)
    g_toks = _tokens(gold)
    if not p_toks and not g_toks:
        return 1.0
    if not p_toks or not g_toks:
        return 0.0

    precisions: list[float] = []
    for n in range(1, max_n + 1):
        p_ngr = _ngrams(p_toks, n)
        g_ngr = _ngrams(g_toks, n)
        if not p_ngr or not g_ngr:
            precisions.append(0.0)
            continue
        g_counts: dict[tuple[str, ...], int] = {}
        for ng in g_ngr:
            g_counts[ng] = g_counts.get(ng, 0) + 1
        match = 0
        used: dict[tuple[str, ...], int] = {}
        for ng in p_ngr:
            c = g_counts.get(ng, 0)
            if c > used.get(ng, 0):
                match += 1
                used[ng] = used.get(ng, 0) + 1
        precisions.append(match / len(p_ngr))

    # geometric mean of precisions (avoid log(0))
    import math

    eps = 1e-9
    log_sum = sum(math.log(p + eps) for p in precisions) / max_n
    geo = math.exp(log_sum)

    # brevity penalty
    bp = 1.0 if len(p_toks) > len(g_toks) else math.exp(1 - len(g_toks) / max(1, len(p_toks)))
    score = bp * geo
    return max(0.0, min(1.0, score))


def rouge_l(pred: str, gold: str) -> float:
    """Compute ROUGE-L (LCS-based F1) offline.
    Returns value in [0,1].
    """
    p = _tokens(pred)
    g = _tokens(gold)
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    # LCS length
    m, n = len(p), len(g)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if p[i] == g[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
    lcs = dp[m][n]
    if lcs == 0:
        return 0.0
    prec = lcs / m
    rec = lcs / n
    f1 = (2 * prec * rec) / (prec + rec)
    return max(0.0, min(1.0, f1))

REGISTRY.update({
    "bleu": bleu,
    "rouge_l": rouge_l,
})

# --- Contract correctness metric ---

def contract_check(pred: str, gold: str) -> float:
    """Validate a JSON contract with schema and simple field checks.

    gold: JSON string specifying a spec like:
      {
        "schema": {"required": [...], "properties": {"field": {"type": "string"}, ...}},
        "checks": [
          {"field": "action", "equals": "transfer"},
          {"field": "currency", "in": ["USD","EUR"]},
          {"field": "amount", "gte": 0}
        ]
      }
    Returns 1.0 if pred parses as JSON, satisfies the schema and all checks; else 0.0.
    """
    try:
        spec = json.loads(gold) if gold else {}
    except Exception:
        return 0.0

    schema = spec.get("schema")
    checks = spec.get("checks", [])

    # Parse prediction JSON
    try:
        obj = json.loads(pred)
    except Exception:
        return 0.0

    # Schema validation using existing helper
    if isinstance(schema, dict):
        schema_metric = make_json_schema_metric(schema)
        if schema_metric(pred, "") != 1.0:  # type: ignore[arg-type]
            return 0.0

    # Simple checks
    for chk in checks:
        field = chk.get("field")
        if not field:
            return 0.0
        val = obj.get(field)
        if "equals" in chk and val != chk["equals"]:
            return 0.0
        if "regex" in chk:
            try:
                if not isinstance(val, str) or not re.fullmatch(chk["regex"], val):
                    return 0.0
            except re.error:
                return 0.0
        if "in" in chk:
            options = chk["in"]
            if not isinstance(options, list) or val not in options:
                return 0.0
        if "gte" in chk:
            try:
                if not (isinstance(val, (int, float)) and val >= float(chk["gte"])):
                    return 0.0
            except Exception:
                return 0.0
        if "lte" in chk:
            try:
                if not (isinstance(val, (int, float)) and val <= float(chk["lte"])):
                    return 0.0
            except Exception:
                return 0.0
    return 1.0

REGISTRY.update({
    "contract_check": contract_check,
})

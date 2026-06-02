import difflib
import hashlib

#dymiourgia ngrams gia jaccard
def build_ngrams(tokens: list, n: int = 5) -> set:
    if len(tokens) < n:
        return set(tuple(tokens))
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}

#jaccard similarity me vasi ta ngrams pou exoume dimiourghsei apo ta tokens
def jaccard_similarity(ngrams_a: set, ngrams_b: set) -> float:
    if not ngrams_a and not ngrams_b:
        return 1.0
    if not ngrams_a or not ngrams_b:
        return 0.0
    intersection = len(ngrams_a & ngrams_b)
    union = len(ngrams_a | ngrams_b)
    return intersection / union if union > 0 else 0.0

#lcs similarity me vasi to difflib, periorismeno se 2000 tokens gia na apofygoume megala arxeia pou mporei na epireasoun tin apodosi
def lcs_similarity(tokens_a: list, tokens_b: list) -> float:
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    MAX_TOKENS = 2000
    a = tokens_a[:MAX_TOKENS]
    b = tokens_b[:MAX_TOKENS]
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return matcher.ratio()

#rolling hash gia winnowing, xrisimopoioume MD5 hash kai periorizoume se 32 bits gia na apofygoume megalous arithmous
def _rolling_hashes(tokens: list, k: int) -> list:
    if len(tokens) < k:
        joined = " ".join(tokens)
        h = int(hashlib.md5(joined.encode()).hexdigest(), 16) & 0xFFFFFFFF
        return [h]
    hashes = []
    for i in range(len(tokens) - k + 1):
        gram = " ".join(tokens[i:i + k])
        h = int(hashlib.md5(gram.encode()).hexdigest(), 16) & 0xFFFFFFFF
        hashes.append(h)
    return hashes

#winnowing algorithm gia na paroume ta fingerprints apo ta rolling hashes, periorizoume se 4 hashes gia na apofygoume perissotera fingerprints
def _winnow(hashes: list, window: int) -> set:
    if not hashes:
        return set()
    fingerprints = set()
    if len(hashes) < window:
        fingerprints.add(min(hashes))
        return fingerprints
    for i in range(len(hashes) - window + 1):
        w = hashes[i:i + window]
        fingerprints.add(min(w))
    return fingerprints

#winnowing similarity me vasi ta fingerprints
def winnowing_similarity(tokens_a: list, tokens_b: list, k: int = 5, window: int = 4) -> float:
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    fp_a = _winnow(_rolling_hashes(tokens_a, k), window)
    fp_b = _winnow(_rolling_hashes(tokens_b, k), window)
    if not fp_a and not fp_b:
        return 1.0
    if not fp_a or not fp_b:
        return 0.0
    intersection = len(fp_a & fp_b)
    denominator = min(len(fp_a), len(fp_b))
    return intersection / denominator if denominator > 0 else 0.0

#barh ton diaforetikon metrics gia na paroume ena combined score
_WEIGHTS = {"jaccard": 0.35, "lcs": 0.40, "winnowing": 0.25}


def combined_score(jaccard: float, lcs: float, winnowing: float) -> float:
    return (
        _WEIGHTS["jaccard"] * jaccard
        + _WEIGHTS["lcs"] * lcs
        + _WEIGHTS["winnowing"] * winnowing
    )

#diaheirisi riskou me vasu to combined score
RISK_HIGH = 0.70
RISK_MEDIUM = 0.40


def risk_label(score: float) -> str:
    if score >= RISK_HIGH:
        return "High"
    elif score >= RISK_MEDIUM:
        return "Medium"
    return "Low"

"""Lightweight rule-based NLP interpretation layer for emotion analysis."""
import re
from typing import Dict, List


SLANG = {
    "lol": "laughing / amused",
    "lmao": "laughing strongly",
    "omg": "strong surprise",
    "idk": "uncertainty",
    "tbh": "honest emphasis",
    "bruh": "disbelief / frustration",
    "wtf": "strong shock / anger",
    "damn": "strong emphasis",
    "yep": "agreement",
    "nope": "rejection",
}

NEGATIONS = {"not", "never", "no", "nothing", "nobody", "nowhere", "hardly", "barely", "isn't", "wasn't", "don't", "doesn't", "didn't", "can't", "couldn't", "won't", "wouldn't"}
INTENSIFIERS = {"very", "really", "so", "extremely", "incredibly", "absolutely", "totally", "completely", "super", "too", "highly"}


def _has_any(text: str, words: set) -> bool:
    tokens = re.findall(r"\b[\w']+\b", text.lower())
    return bool(set(tokens) & words)


def analyze_text(text: str) -> Dict:
    lower = text.lower().strip()
    tokens = re.findall(r"\b[\w']+\b", lower)
    slang_hits = sorted({t for t in tokens if t in SLANG})
    negation_hits = sorted({t for t in tokens if t in NEGATIONS})
    intensity_hits = sorted({t for t in tokens if t in INTENSIFIERS})
    exclamation_count = text.count("!")
    question_count = text.count("?")
    all_caps_words = re.findall(r"\b[A-Z]{3,}\b", text)

    sarcasm_markers = [
        r"\byeah right\b", r"\bsure\b.*\b(yeah|okay|great)\b",
        r"\bthanks a lot\b", r"\bwhat a (great|wonderful|perfect)\b",
        r"\bas if\b", r"\bperfect\b.*[.!]$",
    ]
    sarcasm = any(re.search(pattern, lower, re.I) for pattern in sarcasm_markers)

    ambiguity = []
    if negation_hits:
        ambiguity.append("Negation")
    if slang_hits:
        ambiguity.append("Slang")
    if sarcasm:
        ambiguity.append("Sarcasm")
    if question_count:
        ambiguity.append("Pragmatic")
    if len(tokens) > 0 and ("it" in tokens or "this" in tokens or "that" in tokens or "they" in tokens):
        ambiguity.append("Referential")
    if len(intensity_hits) >= 2 or exclamation_count >= 2 or all_caps_words:
        ambiguity.append("Intensity / emphasis")
    if "but" in tokens or "although" in tokens or "though" in tokens:
        ambiguity.append("Semantic contrast")
    if "not" in tokens and any(w in tokens for w in {"happy", "good", "love", "like", "excited"}):
        ambiguity.append("Scope / negation")

    # A short, explainable interpretation for the UI.
    cues: List[str] = []
    if negation_hits:
        cues.append(f"negation: {', '.join(negation_hits)}")
    if slang_hits:
        cues.append("slang: " + ", ".join(slang_hits))
    if intensity_hits or exclamation_count or all_caps_words:
        cues.append("emphasis detected")
    if sarcasm:
        cues.append("possible sarcasm")
    if question_count:
        cues.append("question/context dependence")

    return {
        "ambiguity_types": list(dict.fromkeys(ambiguity)),
        "ambiguity_level": "High" if len(ambiguity) >= 3 else "Moderate" if ambiguity else "Low",
        "sarcasm": sarcasm,
        "negation": bool(negation_hits),
        "slang": bool(slang_hits),
        "intensity": bool(intensity_hits or exclamation_count or all_caps_words),
        "context_dependent": bool(question_count or any(w in tokens for w in {"it", "this", "that", "they"})),
        "cues": cues,
        "details": {
            "slang_terms": slang_hits,
            "negation_terms": negation_hits,
            "intensity_terms": intensity_hits,
            "exclamation_marks": exclamation_count,
            "question_marks": question_count,
            "emphasized_words": all_caps_words,
        },
    }

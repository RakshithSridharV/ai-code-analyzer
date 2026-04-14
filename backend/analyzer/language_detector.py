"""
Language detector using a weighted scoring approach.

Each language gets points based on keyword/pattern matches.
The language with the highest score wins. This avoids the
fragile first-match-wins problem of the previous implementation.
"""

import re


def detect_language(code: str) -> str:
    code = code.strip()
    if not code:
        return "unknown"

    scores = {
        "python": 0,
        "javascript": 0,
        "java": 0,
        "c": 0,
        "cpp_unsupported": 0,
    }

    # ── Python signals ──────────────────────────────────
    if re.search(r"\bdef\s+\w+\s*\(", code):
        scores["python"] += 3
    if "import " in code or "from " in code:
        scores["python"] += 1
    if "print(" in code:
        scores["python"] += 1
    if "self." in code or "self," in code:
        scores["python"] += 2
    if re.search(r":\s*$", code, re.MULTILINE):
        scores["python"] += 2  # colon-terminated blocks

    # ── JavaScript signals ──────────────────────────────
    if re.search(r"\bfunction\s+\w+\s*\(", code):
        scores["javascript"] += 3
    if "=>" in code:
        scores["javascript"] += 2
    if "console.log" in code:
        scores["javascript"] += 2
    if re.search(r"\b(let|const|var)\s+", code):
        scores["javascript"] += 2

    # ── Java signals ────────────────────────────────────
    if re.search(r"\bpublic\s+class\b", code):
        scores["java"] += 5  # very strong Java indicator
    if re.search(r"\b(public|private|protected)\s+(static\s+)?(void|int|String|boolean|double|float)\s+", code):
        scores["java"] += 3
    if "System.out" in code:
        scores["java"] += 2
    if re.search(r"\bclass\s+\w+", code) and "def " not in code:
        scores["java"] += 2  # class without def → likely Java, not Python

    # ── C++ (unsupported) signals ───────────────────────
    cpp_keywords = ["std::", "cout", "cin", "vector<", "map<", "#include <iostream>"]
    for kw in cpp_keywords:
        if kw in code:
            scores["cpp_unsupported"] += 3

    # ── C signals ───────────────────────────────────────
    if re.search(r"\b(int|void|char|float|double)\s+\w+\s*\(", code):
        scores["c"] += 3
    if "#include" in code and "iostream" not in code:
        scores["c"] += 2
    if "printf(" in code or "scanf(" in code:
        scores["c"] += 2
    if "malloc(" in code or "free(" in code:
        scores["c"] += 2

    # ── Pick the winner ─────────────────────────────────
    best_lang = max(scores, key=lambda k: scores[k])
    best_score = scores[best_lang]

    if best_score == 0:
        return "unknown"

    # C++ trumps C when both have scores (superset)
    if scores["cpp_unsupported"] > 0 and scores["c"] > 0:
        if scores["cpp_unsupported"] >= scores["c"]:
            return "cpp_unsupported"

    return best_lang
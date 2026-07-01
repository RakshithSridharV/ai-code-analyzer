"""
Language detector using a weighted scoring approach.

Each language gets points based on keyword/pattern matches.
The language with the highest score wins. This avoids the
fragile first-match-wins problem of the previous implementation.

Supported languages: python, javascript, java, c, cpp
"""

import re


def detect_language(code: str) -> str:
    code = code.strip()
    if not code:
        return "unknown"

    scores = {
        "python":     0,
        "javascript": 0,
        "java":       0,
        "cpp":        0,
        "c":          0,
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
    if "=>" in code and ">>=" not in code:
        scores["javascript"] += 2
    if "console.log" in code:
        scores["javascript"] += 2
    if re.search(r"\b(let|const|var)\s+", code):
        scores["javascript"] += 2
    if ".forEach(" in code or ".map(" in code or ".filter(" in code:
        scores["javascript"] += 2

    # ── Java signals ────────────────────────────────────
    if re.search(r"\bpublic\s+class\b", code):
        scores["java"] += 5   # very strong Java indicator
    if re.search(r"\b(public|private|protected)\s+(static\s+)?(void|int|String|boolean|double|float|long)\s+", code):
        scores["java"] += 3
    if "System.out" in code:
        scores["java"] += 2
    if re.search(r"\bclass\s+\w+", code) and "def " not in code and "::" not in code:
        scores["java"] += 2   # class without def or :: → likely Java
    if "ArrayList" in code or "HashMap" in code or "Scanner" in code:
        scores["java"] += 3

    # ── C++ signals (must come before C) ──────────────
    cpp_strong = ["std::", "cout", "cin", "endl",
                  "vector<", "map<", "set<", "unordered_map",
                  "string ", "template<", "auto ", "nullptr",
                  "#include <iostream>", "#include <vector>",
                  "#include <string>", "#include <algorithm>",
                  "push_back(", "emplace_back(", ".size()",
                  "pair<", "tuple<", "make_pair(", "sort("]
    for kw in cpp_strong:
        if kw in code:
            scores["cpp"] += 3

    # range-based for and lambdas are unambiguously C++
    if re.search(r"\bfor\s*\(\s*(auto|const\s+auto)", code):
        scores["cpp"] += 4
    if re.search(r"\[\s*[&=]?\s*\]\s*\(", code):   # lambda [&](
        scores["cpp"] += 4
    if "::" in code:
        scores["cpp"] += 1

    # ── C signals ───────────────────────────────────────
    if re.search(r"\b(int|void|char|float|double)\s+\w+\s*\(", code):
        scores["c"] += 2
    if "#include" in code and "iostream" not in code and "vector" not in code:
        scores["c"] += 2
    if "printf(" in code or "scanf(" in code:
        scores["c"] += 3
    if "malloc(" in code or "free(" in code:
        scores["c"] += 2
    if "struct " in code and "::" not in code:
        scores["c"] += 1

    # ── Pick the winner ─────────────────────────────────
    best_lang  = max(scores, key=lambda k: scores[k])
    best_score = scores[best_lang]

    if best_score == 0:
        return "unknown"

    # C++ always beats C when it has any signal  (superset)
    if scores["cpp"] > 0 and scores["cpp"] >= scores["c"]:
        return "cpp"

    return best_lang
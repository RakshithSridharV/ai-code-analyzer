"""
challenges.py
─────────────
Hardcoded challenge bank + submission grading logic for Challenge Mode.

Big-O ordering used for complexity comparison
(index 0 = best, higher index = worse):
  O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2^n), O(n!)
"""

import threading
import traceback
from typing import Any

# ── Big-O ordering ─────────────────────────────────────────────────────────────
_COMPLEXITY_RANK = {
    "O(1)":       0,
    "O(log n)":   1,
    "O(log N)":   1,
    "O(n)":       2,
    "O(N)":       2,
    "O(n log n)": 3,
    "O(N log N)": 3,
    "O(n²)":      4,
    "O(n^2)":     4,
    "O(N^2)":     4,
    "O(N²)":      4,
    "O(n³)":      5,
    "O(n^3)":     5,
    "O(N^3)":     5,
    "O(2^n)":     6,
    "O(2^N)":     6,
    "O(n!)":      7,
    "O(N!)":      7,
    "Unknown":    99,
}


def _rank(complexity: str) -> int:
    """Return the numeric rank of a complexity string (lower = faster)."""
    return _COMPLEXITY_RANK.get(complexity.strip(), 99)


def complexity_achieved(achieved: str, target: str) -> bool:
    """Return True if *achieved* is at least as good as *target*."""
    return _rank(achieved) <= _rank(target)


# ── Challenge bank ─────────────────────────────────────────────────────────────
CHALLENGES: list[dict] = [
    {
        "id": 1,
        "title": "Find Duplicates",
        "description": (
            "Write a function find_duplicates(arr) that returns a list of "
            "all duplicate values in arr."
        ),
        "example_input": "[1, 2, 3, 2, 4, 3]",
        "example_output": "[2, 3]",
        "target_complexity": "O(n)",
        "hint": "Think about which data structure gives O(1) membership checks.",
        "test_cases": [
            {"input": [1, 2, 3, 2, 4, 3], "expected_contains": [2, 3]},
            {"input": [1, 2, 3],            "expected_contains": []},
            {"input": [1, 1, 1],            "expected_contains": [1]},
        ],
        "starter_code": (
            "def find_duplicates(arr):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 2,
        "title": "Binary Search",
        "description": (
            "Write binary_search(arr, target) that returns the index of target "
            "in sorted arr, or -1 if not found."
        ),
        "example_input": "arr=[1,3,5,7,9], target=5",
        "example_output": "2",
        "target_complexity": "O(log n)",
        "hint": "Halve the search space each iteration using lo and hi pointers.",
        "test_cases": [
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 5},  "expected": 2},
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 1},  "expected": 0},
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 10}, "expected": -1},
        ],
        "starter_code": (
            "def binary_search(arr, target):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 3,
        "title": "Two Sum",
        "description": (
            "Write two_sum(arr, target) that returns indices of two numbers "
            "that add to target."
        ),
        "example_input": "arr=[2,7,11,15], target=9",
        "example_output": "[0, 1]",
        "target_complexity": "O(n)",
        "hint": "Use a dict to store complements as you iterate.",
        "test_cases": [
            {"input": {"arr": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"arr": [3, 2, 4],       "target": 6}, "expected": [1, 2]},
        ],
        "starter_code": (
            "def two_sum(arr, target):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 4,
        "title": "Count Word Frequency",
        "description": (
            "Write word_frequency(text) that returns a dict of each word's count."
        ),
        "example_input": "'hello world hello'",
        "example_output": "{'hello': 2, 'world': 1}",
        "target_complexity": "O(n)",
        "hint": "One pass through the words is enough.",
        "test_cases": [
            {
                "input": "hello world hello",
                "expected": {"hello": 2, "world": 1},
            },
        ],
        "starter_code": (
            "def word_frequency(text):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 5,
        "title": "Flatten Nested List",
        "description": (
            "Write flatten(lst) that returns a flat list from a nested list "
            "(one level deep)."
        ),
        "example_input": "[[1,2],[3,4],[5]]",
        "example_output": "[1, 2, 3, 4, 5]",
        "target_complexity": "O(n)",
        "hint": "Use a list comprehension or extend in one pass.",
        "test_cases": [
            {"input": [[1, 2], [3, 4], [5]], "expected": [1, 2, 3, 4, 5]},
        ],
        "starter_code": (
            "def flatten(lst):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 6,
        "title": "Check Anagram",
        "description": (
            "Write is_anagram(s1, s2) that returns True if s1 and s2 are anagrams."
        ),
        "example_input": "s1='listen', s2='silent'",
        "example_output": "True",
        "target_complexity": "O(n)",
        "hint": "Counting character frequencies is O(n). Sorting is O(n log n).",
        "test_cases": [
            {"input": {"s1": "listen", "s2": "silent"}, "expected": True},
            {"input": {"s1": "hello",  "s2": "world"},  "expected": False},
        ],
        "starter_code": (
            "def is_anagram(s1, s2):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 7,
        "title": "First Non-Repeating Character",
        "description": (
            "Write first_unique(s) that returns the first non-repeating "
            "character in s."
        ),
        "example_input": "'leetcode'",
        "example_output": "'l'",
        "target_complexity": "O(n)",
        "hint": "Two passes: one to count, one to find first with count 1.",
        "test_cases": [
            {"input": "leetcode", "expected": "l"},
            {"input": "aabb",     "expected": None},
        ],
        "starter_code": (
            "def first_unique(s):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 8,
        "title": "Maximum Subarray Sum",
        "description": (
            "Write max_subarray(arr) that returns the largest sum of any "
            "contiguous subarray (Kadane's algorithm)."
        ),
        "example_input": "[-2,1,-3,4,-1,2,1,-5,4]",
        "example_output": "6",
        "target_complexity": "O(n)",
        "hint": "Track current sum and global max in a single pass.",
        "test_cases": [
            {"input": [-2, 1, -3, 4, -1, 2, 1, -5, 4], "expected": 6},
            {"input": [1],                               "expected": 1},
        ],
        "starter_code": (
            "def max_subarray(arr):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 9,
        "title": "Group Anagrams",
        "description": (
            "Write group_anagrams(words) that groups anagrams together."
        ),
        "example_input": "['eat','tea','tan','ate','nat','bat']",
        "example_output": "[['eat','tea','ate'],['tan','nat'],['bat']]",
        "target_complexity": "O(n log n)",
        "hint": "Sort each word as a key. Sorting one word is O(k log k).",
        "test_cases": [
            {
                "input": ["eat", "tea", "tan", "ate", "nat", "bat"],
                "expected_groups": 3,
            },
        ],
        "starter_code": (
            "def group_anagrams(words):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
    {
        "id": 10,
        "title": "Longest Consecutive Sequence",
        "description": (
            "Write longest_consecutive(arr) that finds the length of the "
            "longest consecutive sequence."
        ),
        "example_input": "[100,4,200,1,3,2]",
        "example_output": "4",
        "target_complexity": "O(n)",
        "hint": (
            "Convert to set first. A number starts a sequence only if "
            "num-1 is not in the set."
        ),
        "test_cases": [
            {"input": [100, 4, 200, 1, 3, 2],          "expected": 4},
            {"input": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1],  "expected": 9},
        ],
        "starter_code": (
            "def longest_consecutive(arr):\n"
            "    # Write your solution here\n"
            "    pass"
        ),
    },
]

# Quick lookup by id
_CHALLENGE_MAP: dict[int, dict] = {c["id"]: c for c in CHALLENGES}


def get_all_challenges() -> list[dict]:
    """Return all challenges without test_cases (safe for public API)."""
    safe_keys = {
        "id", "title", "description", "example_input",
        "example_output", "target_complexity", "hint", "starter_code",
    }
    return [{k: v for k, v in c.items() if k in safe_keys} for c in CHALLENGES]


def get_challenge(challenge_id: int) -> dict | None:
    """Return a full challenge dict (including test_cases) or None."""
    return _CHALLENGE_MAP.get(challenge_id)


# ── Safe test runner ────────────────────────────────────────────────────────────

def _run_with_timeout(fn, timeout: float = 2.0) -> tuple[Any, str | None]:
    """
    Run *fn()* in a daemon thread with a *timeout* second limit.
    Returns (result, error_message).  result is None on error/timeout.
    """
    result_holder: list[Any]  = [None]
    error_holder:  list[str]  = [None]

    def target():
        try:
            result_holder[0] = fn()
        except Exception:
            error_holder[0] = traceback.format_exc()

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None, "Execution timed out (2 s limit)."
    return result_holder[0], error_holder[0]


def _exec_user_code(code: str) -> dict:
    """
    Execute *code* in a sandboxed namespace.
    Returns the namespace dict on success, raises on syntax/runtime error.
    """
    namespace: dict = {}
    exec(compile(code, "<challenge>", "exec"), namespace)  # noqa: S102
    return namespace


def _run_test_cases(challenge: dict, code: str) -> tuple[int, int, list[str]]:
    """
    Execute each test case against the submitted code.
    Returns (passed, total, error_messages).
    """
    test_cases = challenge.get("test_cases", [])
    total   = len(test_cases)
    passed  = 0
    errors: list[str] = []

    # Compile once
    try:
        compiled = compile(code, "<challenge>", "exec")
    except SyntaxError as e:
        return 0, total, [f"SyntaxError: {e}"]

    cid = challenge["id"]

    for idx, tc in enumerate(test_cases, 1):
        inp = tc.get("input")

        def run_case(compiled=compiled, inp=inp, tc=tc, cid=cid):
            ns: dict = {}
            exec(compiled, ns)  # noqa: S102

            # ── Per-challenge dispatch ─────────────────────────────────────────
            if cid == 1:                           # find_duplicates(arr)
                result = ns["find_duplicates"](list(inp))
                expected_contains = set(tc.get("expected_contains", []))
                return set(result) == expected_contains

            elif cid == 2:                         # binary_search(arr, target)
                result = ns["binary_search"](list(inp["arr"]), inp["target"])
                return result == tc["expected"]

            elif cid == 3:                         # two_sum(arr, target)
                result = ns["two_sum"](list(inp["arr"]), inp["target"])
                return sorted(result) == sorted(tc["expected"])

            elif cid == 4:                         # word_frequency(text)
                result = ns["word_frequency"](inp)
                return result == tc["expected"]

            elif cid == 5:                         # flatten(lst)
                result = ns["flatten"]([list(x) for x in inp])
                return result == tc["expected"]

            elif cid == 6:                         # is_anagram(s1, s2)
                result = ns["is_anagram"](inp["s1"], inp["s2"])
                return result == tc["expected"]

            elif cid == 7:                         # first_unique(s)
                result = ns["first_unique"](inp)
                return result == tc["expected"]

            elif cid == 8:                         # max_subarray(arr)
                result = ns["max_subarray"](list(inp))
                return result == tc["expected"]

            elif cid == 9:                         # group_anagrams(words)
                result = ns["group_anagrams"](list(inp))
                return len(result) == tc["expected_groups"]

            elif cid == 10:                        # longest_consecutive(arr)
                result = ns["longest_consecutive"](list(inp))
                return result == tc["expected"]

            return False

        outcome, err = _run_with_timeout(run_case, timeout=2.0)

        if err:
            errors.append(f"Test {idx}: {err.strip().splitlines()[-1]}")
        elif outcome is True:
            passed += 1
        else:
            errors.append(f"Test {idx}: wrong answer.")

    return passed, total, errors


# ── Public grading API ─────────────────────────────────────────────────────────

def grade_submission(challenge_id: int, code: str, achieved_complexity: str) -> dict:
    """
    Grade a submission.  *achieved_complexity* comes from InferenceEngine.

    Returns a result dict with:
      tests_passed, tests_total, achieved_complexity, target_complexity,
      complexity_achieved, overall_grade, feedback, errors
    """
    challenge = get_challenge(challenge_id)
    if challenge is None:
        raise ValueError(f"Challenge {challenge_id} not found.")

    target = challenge["target_complexity"]
    passed, total, errors = _run_test_cases(challenge, code)

    comp_ok = complexity_achieved(achieved_complexity, target)
    all_pass = (passed == total and total > 0)

    if all_pass and comp_ok:
        grade = "PASS"
        feedback = (
            f"Excellent! All {total} tests passed and you achieved "
            f"{achieved_complexity}, meeting the {target} target."
        )
    elif all_pass and not comp_ok:
        grade = "PARTIAL"
        feedback = (
            f"Your solution is correct but can be more efficient. "
            f"You achieved {achieved_complexity} — target is {target}. "
            f"Hint: {challenge['hint']}"
        )
    else:
        grade = "FAIL"
        detail = f"  {errors[0]}" if errors else ""
        feedback = (
            f"{passed}/{total} tests passed.{detail} "
            "Review your logic and try again."
        )

    return {
        "tests_passed":        passed,
        "tests_total":         total,
        "achieved_complexity": achieved_complexity,
        "target_complexity":   target,
        "complexity_achieved": comp_ok,
        "overall_grade":       grade,
        "feedback":            feedback,
        "errors":              errors,
    }

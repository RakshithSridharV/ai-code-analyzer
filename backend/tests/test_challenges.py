"""
tests/test_challenges.py
─────────────────────────
Pytest suite for the Challenge Mode backend.

Tests cover:
  1. get_all_challenges() — correct count, no test_cases leaked
  2. get_challenge()      — found / not found
  3. complexity_achieved()
  4. grade_submission()   — PASS / PARTIAL / FAIL paths for each challenge
"""

import sys
import os

# Make sure we can import from the backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from challenges import (
    CHALLENGES,
    get_all_challenges,
    get_challenge,
    complexity_achieved,
    grade_submission,
)


# ── 1. Challenge catalogue ─────────────────────────────────────────────────────

class TestCatalogue:
    def test_ten_challenges(self):
        assert len(CHALLENGES) == 10

    def test_public_list_hides_test_cases(self):
        public = get_all_challenges()
        assert len(public) == 10
        for ch in public:
            assert "test_cases" not in ch

    def test_public_list_has_required_fields(self):
        required = {"id", "title", "description", "target_complexity",
                    "hint", "starter_code"}
        for ch in get_all_challenges():
            assert required <= set(ch.keys()), f"Challenge {ch['id']} missing fields"

    def test_get_challenge_found(self):
        ch = get_challenge(1)
        assert ch is not None
        assert ch["id"] == 1
        assert "test_cases" in ch

    def test_get_challenge_not_found(self):
        assert get_challenge(999) is None


# ── 2. Complexity comparison ───────────────────────────────────────────────────

class TestComplexityAchieved:
    @pytest.mark.parametrize("achieved,target,expected", [
        ("O(n)",      "O(n)",      True),   # exact match
        ("O(1)",      "O(n)",      True),   # better than target
        ("O(log n)",  "O(n)",      True),   # better than target
        ("O(n²)",     "O(n)",      False),  # worse than target
        ("O(n)",      "O(log n)",  False),  # worse than target
        ("O(n log n)","O(n log n)",True),   # exact
        ("Unknown",   "O(n)",      False),  # unknown treated as worst
    ])
    def test_complexity_ordering(self, achieved, target, expected):
        assert complexity_achieved(achieved, target) is expected


# ── 3. grade_submission — helper solutions ─────────────────────────────────────

# Correct, efficient solutions for each challenge
SOLUTIONS = {
    1: """
def find_duplicates(arr):
    seen = set()
    dups = []
    for x in arr:
        if x in seen and x not in dups:
            dups.append(x)
        seen.add(x)
    return dups
""",
    2: """
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
""",
    3: """
def two_sum(arr, target):
    seen = {}
    for i, v in enumerate(arr):
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
""",
    4: """
def word_frequency(text):
    freq = {}
    for w in text.split():
        freq[w] = freq.get(w, 0) + 1
    return freq
""",
    5: """
def flatten(lst):
    return [item for sub in lst for item in sub]
""",
    6: """
def is_anagram(s1, s2):
    from collections import Counter
    return Counter(s1) == Counter(s2)
""",
    7: """
def first_unique(s):
    from collections import Counter
    counts = Counter(s)
    for c in s:
        if counts[c] == 1:
            return c
    return None
""",
    8: """
def max_subarray(arr):
    best = cur = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
""",
    9: """
def group_anagrams(words):
    from collections import defaultdict
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)
    return list(groups.values())
""",
    10: """
def longest_consecutive(arr):
    s = set(arr)
    best = 0
    for n in s:
        if n - 1 not in s:
            length = 1
            while n + length in s:
                length += 1
            best = max(best, length)
    return best
""",
}

# Brute-force / wrong solutions
WRONG_SOLUTIONS = {
    1: "def find_duplicates(arr):\n    return []",
    2: "def binary_search(arr, target):\n    return -1",
    3: "def two_sum(arr, target):\n    return [0, 0]",
    4: "def word_frequency(text):\n    return {}",
    5: "def flatten(lst):\n    return []",
    6: "def is_anagram(s1, s2):\n    return False",
    7: "def first_unique(s):\n    return None",
    8: "def max_subarray(arr):\n    return 0",
    9: "def group_anagrams(words):\n    return [words]",
    10: "def longest_consecutive(arr):\n    return 0",
}


class TestGradeSubmission:

    @pytest.mark.parametrize("cid", list(SOLUTIONS.keys()))
    def test_correct_solution_passes_tests(self, cid):
        """A correct solution must pass all test cases."""
        result = grade_submission(cid, SOLUTIONS[cid], "O(n)")
        assert result["tests_passed"] == result["tests_total"], (
            f"Challenge {cid}: {result['errors']}"
        )

    @pytest.mark.parametrize("cid", list(WRONG_SOLUTIONS.keys()))
    def test_wrong_solution_fails(self, cid):
        """An obviously wrong solution must fail at least one test."""
        result = grade_submission(cid, WRONG_SOLUTIONS[cid], "O(n)")
        assert result["overall_grade"] == "FAIL"
        assert result["tests_passed"] < result["tests_total"]

    def test_pass_grade_when_all_tests_and_complexity_met(self):
        result = grade_submission(1, SOLUTIONS[1], "O(n)")
        assert result["overall_grade"] == "PASS"
        assert result["complexity_achieved"] is True

    def test_partial_grade_when_tests_pass_but_complexity_missed(self):
        result = grade_submission(1, SOLUTIONS[1], "O(n²)")
        assert result["overall_grade"] == "PARTIAL"
        assert result["complexity_achieved"] is False
        assert "hint" in result["feedback"].lower() or "efficient" in result["feedback"].lower()

    def test_fail_grade_message(self):
        result = grade_submission(1, WRONG_SOLUTIONS[1], "O(n)")
        assert result["overall_grade"] == "FAIL"
        assert "passed" in result["feedback"].lower()

    def test_invalid_challenge_raises(self):
        with pytest.raises(ValueError, match="not found"):
            grade_submission(999, "pass", "O(n)")

    def test_syntax_error_returns_fail(self):
        bad_code = "def find_duplicates(arr):\n    !!!"
        result = grade_submission(1, bad_code, "Unknown")
        assert result["overall_grade"] == "FAIL"
        assert result["tests_passed"] == 0

    def test_result_has_all_required_keys(self):
        result = grade_submission(1, SOLUTIONS[1], "O(n)")
        required = {
            "tests_passed", "tests_total", "achieved_complexity",
            "target_complexity", "complexity_achieved",
            "overall_grade", "feedback", "errors",
        }
        assert required <= set(result.keys())

    def test_binary_search_correct(self):
        result = grade_submission(2, SOLUTIONS[2], "O(log n)")
        assert result["overall_grade"] == "PASS"

    def test_group_anagrams_correct(self):
        result = grade_submission(9, SOLUTIONS[9], "O(n log n)")
        assert result["tests_passed"] == result["tests_total"]

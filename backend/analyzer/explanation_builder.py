"""
explanation_builder.py
──────────────────────
Builds a plain-English explanation of time complexity from the InferenceEngine
reasoning dict, filling templates with actual variable names and line numbers.

Replaces:  explanations.py

Uses ONLY Python's built-in ast module (no third-party analysis libraries).

Author: AI Code Analyzer
"""

import ast


class ExplanationBuilder:
    """
    Reads the InferenceEngine reasoning dict and fills in complexity templates
    using the actual loop variable names, collections, and line numbers found
    in the AST so the explanation is precise and code-specific.
    """

    def __init__(
        self,
        inference_result: dict,
        source_code: str,
        function_name: str,
    ) -> None:
        self.result = inference_result
        self.source_code = source_code
        # Friendly display name for the subject of the explanation
        self.fn = function_name.strip() if function_name.strip() else "This code"
        self.reasoning = inference_result.get("reasoning", {})
        self.time_c = inference_result.get("time", "O(1)")

    # ── Public API ────────────────────────────────────────────────────────────

    def build(self) -> str:
        """
        Return a single plain-English sentence (or short paragraph) explaining
        the detected time complexity.
        """
        time_c = self.time_c
        rec = self.reasoning.get("recursion", {})
        loops = self.reasoning.get("loops", [])

        # ── Memoized exponential / near-exponential ────────────────────────
        if rec.get("is_memoized"):
            dec_name = rec.get("decorator_name") or "lru_cache"
            explanation = (
                f"{self.fn} looks like O(2^n) but the @{dec_name} decorator "
                f"caches results, making it effectively O(n)."
            )
            if rec.get("is_tail"):
                explanation += (
                    " Note: this is tail-recursive — the recursive call is the"
                    " last operation. Python does not optimize tail calls, so"
                    " this still uses O(n) stack space."
                )
            return explanation

        # ── O(1) — constant time ───────────────────────────────────────────
        if time_c == "O(1)":
            return (
                f"{self.fn} runs in constant time — no loops or recursive calls"
                " that depend on the input size."
            )

        # ── O(log n) — halving loop or single-call divide-and-conquer ─────
        if time_c == "O(log n)":
            outer = self.reasoning.get("outer_loop", {})
            loop_var = outer.get("var") or "the loop variable"
            # Detect whether it halves via multiplication/division
            op_word = "multiplied or divided"
            for lp in loops:
                if lp.get("complexity") == "O(log n)":
                    op_word = "multiplied or floor-divided"
                    break
            return (
                f"{self.fn} is O(log n) because the {loop_var} variable is"
                f" {op_word} each iteration (the search/work space halves each"
                " step), so for n=1000 this takes at most 10 iterations."
            )

        # ── O(n) — single linear loop or linear recursion ─────────────────
        if time_c == "O(n)":
            if rec.get("is_recursive") and not loops:
                tail_note = (
                    " Note: this is tail-recursive — Python does not optimize"
                    " tail calls, so this still uses O(n) stack space."
                    if rec.get("is_tail") else ""
                )
                return (
                    f"{self.fn} is O(n) because it calls itself once per step,"
                    f" doing O(1) work each time — the recursion depth is n."
                    + tail_note
                )
            outer = self.reasoning.get("outer_loop", {})
            col = outer.get("collection") or "the input"
            line = outer.get("line", "?")
            return (
                f"{self.fn} is O(n) because it loops over {col} once"
                f" (line {line}), doing O(1) work per element."
            )

        # ── O(n log n) — divide-and-conquer or log-n inner op ─────────────
        if time_c == "O(n log n)":
            if rec.get("is_recursive"):
                return (
                    f"{self.fn} is O(n log n) — it uses a divide-and-conquer"
                    " strategy, splitting the problem in half each time"
                    " (log n levels) and doing O(n) work at each level."
                )
            outer = self.reasoning.get("outer_loop", {})
            col = outer.get("collection") or "the input"
            return (
                f"{self.fn} is O(n log n) — it has an outer O(n) loop over"
                f" {col} with an inner operation that halves the space each time."
            )

        # ── O(n²) — doubly nested loops ────────────────────────────────────
        if time_c == "O(n^2)":
            outer = self.reasoning.get("outer_loop", {})
            inner = self.reasoning.get("inner_loop", {})
            outer_var  = outer.get("var") or "the outer variable"
            outer_col  = outer.get("collection") or "the input"
            outer_line = outer.get("line", "?")
            inner_var  = inner.get("var") or "the inner variable"
            inner_col  = inner.get("collection") or "the same collection"
            inner_line = inner.get("line", "?")
            return (
                f"{self.fn} is O(n\u00b2) because {outer_var} loops over"
                f" {outer_col} (line {outer_line}) and inside it {inner_var}"
                f" loops over {inner_col} (line {inner_line}), so for input"
                " size n you perform n\u00d7n = n\u00b2 operations."
            )

        # ── O(2^n) — binary recursion without memoization ─────────────────
        if time_c == "O(2^n)":
            call_count = rec.get("call_count", 2)
            explanation = (
                f"{self.fn} is O(2^n) because it calls itself {call_count} times"
                " recursively with no memoization."
                " For n=20 this means over 1 million calls."
            )
            if rec.get("is_tail"):
                explanation += (
                    " Note: this is tail-recursive — the recursive call is the"
                    " last operation. Python does not optimize tail calls, so"
                    " this still uses O(n) stack space."
                )
            return explanation

        # ── Fallback for O(n^3) and anything else ─────────────────────────
        return (
            f"{self.fn} has {time_c} time complexity based on its"
            " loop and recursion structure."
        )

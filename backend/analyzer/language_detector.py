def detect_language(code: str) -> str:
    """
    Improved language detection with ordered heuristics.
    Most-specific patterns checked first to reduce false positives.
    """
    code = code.strip()

    # ---- Java (must check BEFORE C/C++ since Java has "int " too) ----
    if "public class " in code or "import java." in code or "System.out." in code:
        return "java"

    # ---- C++ specific (before generic C) ----
    if "cout" in code or "cin" in code or "std::" in code:
        return "cpp"
    if "#include" in code and ("iostream" in code or "vector" in code or "string" in code):
        return "cpp"

    # ---- JavaScript ----
    if "function " in code or "const " in code or "let " in code:
        return "javascript"
    if "=>" in code or "console.log" in code or "var " in code:
        return "javascript"

    # ---- Python (check def + indentation patterns) ----
    if "def " in code or "import " in code or "print(" in code:
        return "python"
    # Python-specific keywords
    if "elif " in code or "self." in code or "lambda " in code:
        return "python"

    # ---- C (generic check last) ----
    if "#include" in code:
        return "c"
    if ("int " in code or "void " in code) and ("{" in code):
        return "c"

    return "unknown"
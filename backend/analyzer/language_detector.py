def detect_language(code: str) -> str:
    code = code.strip()

    # Java
    if "class " in code:
        return "java"

    # JavaScript
    if "function " in code or "=>" in code:
        return "javascript"

    # C / C++
    if "cout" in code or "cin" in code or "std::" in code:
        return "cpp"
    if "int " in code or "void " in code:
        return "c"

    # Python
    if "def " in code:
        return "python"

    return "unknown"
"""
C++ code analyzer — regex-based.

pycparser cannot parse C++ (templates, namespaces, classes, etc.)
so we use robust regex heuristics to detect loops, recursion,
and infer complexity.
"""
import re


def analyze_cpp_code(code):
    """
    Analyze C++ code using regex-based heuristics.
    Returns: (time_complexity, space_complexity, is_recursive, loops, recursive_calls)
    """

    # ---- STRIP COMMENTS & STRINGS ----
    clean = re.sub(r'//.*', '', code)                   # single-line comments
    clean = re.sub(r'/\*[\s\S]*?\*/', '', clean)        # multi-line comments
    clean = re.sub(r'"(?:[^"\\]|\\.)*"', '""', clean)   # string literals
    clean = re.sub(r"'(?:[^'\\]|\\.)*'", "''", clean)   # char literals

    # ---- FUNCTION DETECTION ----
    # Match C++ function definitions:  type name(params) {
    func_pattern = re.compile(
        r'(?:(?:static|inline|virtual|const|constexpr|unsigned|signed|long|short|explicit)\s+)*'
        r'(?:\w[\w:<>*&\s]*?)\s+'     # return type (handles templates, namespaces)
        r'(\w+)\s*'                    # function name (capture group 1)
        r'\([^)]*\)\s*'               # parameter list
        r'(?:const\s*)?'              # optional trailing const
        r'(?:override\s*)?'           # optional override
        r'\{',                         # opening brace
        re.MULTILINE
    )

    functions = func_pattern.findall(clean)
    # Filter out common C++ keywords that might match
    skip_names = {
        'main', 'if', 'while', 'for', 'switch', 'return', 'else',
        'int', 'void', 'char', 'float', 'double', 'bool', 'string',
        'auto', 'class', 'struct', 'namespace', 'using', 'template',
        'include', 'define', 'cout', 'cin', 'endl', 'std', 'sizeof',
        'new', 'delete', 'try', 'catch', 'throw', 'public', 'private',
        'protected', 'enum', 'typedef', 'typename'
    }
    func_names = [f for f in functions if f not in skip_names]

    # ---- LOOP DETECTION ----
    loop_pattern = re.compile(r'\b(for|while|do)\s*[\({]')
    loop_matches = list(loop_pattern.finditer(clean))
    loops = len(loop_matches)

    # Estimate nesting depth by checking if loops appear inside other loops
    # Strategy: for each loop, count how many other loops' ranges contain it
    max_loop_depth = 0
    if loops > 0:
        # Find each loop's approximate range by matching braces from its position
        loop_ranges = []
        for m in loop_matches:
            start = m.start()
            # Find the opening brace of this loop's body
            brace_pos = clean.find('{', start)
            if brace_pos == -1:
                continue
            # Match closing brace
            depth = 0
            end = brace_pos
            for i in range(brace_pos, len(clean)):
                if clean[i] == '{':
                    depth += 1
                elif clean[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            loop_ranges.append((start, end))

        # For each loop, count how many other loops contain it
        for start, end in loop_ranges:
            nesting = sum(1 for s, e in loop_ranges if s <= start and e >= end)
            max_loop_depth = max(max_loop_depth, nesting)

    # ---- RECURSION DETECTION ----
    recursion = False
    recursive_calls = 0

    for fname in func_names:
        # Find all calls to this function inside the code body
        call_pattern = re.compile(
            r'(?<!\w)' + re.escape(fname) + r'\s*\(',
            re.MULTILINE
        )
        calls = list(call_pattern.finditer(clean))
        # First match is the definition; additional matches are recursive calls
        if len(calls) > 1:
            recursion = True
            recursive_calls = len(calls) - 1  # subtract definition

    # ---- DATA STRUCTURE DETECTION ----
    has_data_structures = bool(re.search(
        r'\b(vector|map|unordered_map|set|unordered_set|list|deque|stack|queue|'
        r'priority_queue|array|new\s+\w+\[|malloc|calloc)\b',
        clean
    ))

    # ---- COMPLEXITY INFERENCE ----
    if recursion:
        time_c = "O(2^n)" if recursive_calls >= 2 else "O(n)"
        space_c = "O(1) + recursion stack"
    elif max_loop_depth >= 3:
        time_c = f"O(n^{max_loop_depth})"
        space_c = "O(1)"
    elif max_loop_depth == 2:
        time_c = "O(n^2)"
        space_c = "O(1)"
    elif max_loop_depth == 1:
        time_c = "O(n)"
        space_c = "O(1)"
    else:
        time_c = "O(1)"
        space_c = "O(1)"

    # Add data structure memory overhead
    if has_data_structures:
        if "recursion stack" in space_c:
            space_c = "O(n) + recursion stack"
        else:
            space_c = "O(n)"

    return time_c, space_c, recursion, loops, recursive_calls
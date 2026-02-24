from pyjsparser import parse

def analyze_js_code(code):
    loops = 0
    recursion = False
    recursive_calls = 0
    current_func = None

    try:
        ast = parse(code)
    except Exception:
        return "Unknown", "Unknown", False, 0

    def walk(node):
        nonlocal loops, recursion, recursive_calls, current_func

        if isinstance(node, dict):
            node_type = node.get("type")

            if node_type == "FunctionDeclaration":
                current_func = node["id"]["name"]

            if node_type in ("ForStatement", "WhileStatement", "DoWhileStatement"):
                loops += 1

            if node_type == "CallExpression":
                callee = node.get("callee")
                if (
                    callee
                    and callee.get("type") == "Identifier"
                    and callee.get("name") == current_func
                ):
                    recursion = True
                    recursive_calls += 1

            for value in node.values():
                walk(value)

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(ast)

    # ---- COMPLEXITY INFERENCE ----
    if recursion and recursive_calls > 1:
        return "O(2^n)", "O(n)", True, loops
    elif recursion:
        return "O(n)", "O(n)", True, loops
    elif loops > 1:
        return "O(n^2)", "O(1)", False, loops
    elif loops == 1:
        return "O(n)", "O(1)", False, loops
    else:
        return "O(1)", "O(1)", False, loops
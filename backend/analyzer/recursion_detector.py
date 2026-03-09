import ast


class RecursionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_names = set()
        self.recursive_functions = set()
        self.recursive_call_counts = {}  # func_name -> count

    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        call_count = 0

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == node.name:
                        self.recursive_functions.add(node.name)
                        call_count += 1

        if call_count > 0:
            self.recursive_call_counts[node.name] = call_count

        self.generic_visit(node)


def detect_recursion(tree):
    """Returns True if any function in the code is recursive."""
    visitor = RecursionVisitor()
    visitor.visit(tree)
    return bool(visitor.recursive_functions)


def count_recursive_calls(tree):
    """
    Returns the max number of recursive self-calls in any single function.
    - 1 call  → linear recursion  (factorial)   → O(n)
    - 2+ calls → branching recursion (fibonacci) → O(2^n)
    """
    visitor = RecursionVisitor()
    visitor.visit(tree)

    if not visitor.recursive_call_counts:
        return 0

    return max(visitor.recursive_call_counts.values())

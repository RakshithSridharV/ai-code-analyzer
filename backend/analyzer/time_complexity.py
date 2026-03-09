import ast

class LoopVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0
        self.loop_count = 0

    def visit_For(self, node):
        self.loop_count += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.visit_For(node)

# Time complexity is estimated based on loop nesting depth using AST traversal

def estimate_time_complexity(tree):
    visitor = LoopVisitor()
    visitor.visit(tree)

    # No loops
    if visitor.loop_count == 0:
        return "O(1)"

    # Only one loop
    if visitor.max_depth == 1:
        return "O(n)"

    # Nested loops
    return f"O(n^{visitor.max_depth})"

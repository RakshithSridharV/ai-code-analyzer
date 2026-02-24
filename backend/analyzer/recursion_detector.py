import ast

class RecursionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_names = set()
        self.recursive_functions = set()

    def visit_FunctionDef(self, node):
        # Store function name
        self.function_names.add(node.name)

        # Visit function body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == node.name:
                        self.recursive_functions.add(node.name)

        self.generic_visit(node)


def detect_recursion(tree):
    visitor = RecursionVisitor()
    visitor.visit(tree)

    if visitor.recursive_functions:
        return True
    return False

# Detects recursive function calls using AST traversal


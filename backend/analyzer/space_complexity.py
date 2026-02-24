import ast

class SpaceVisitor(ast.NodeVisitor):
    def __init__(self):
        self.uses_list = False
        self.uses_dict = False
        self.uses_set = False

    def visit_List(self, node):
        self.uses_list = True
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.uses_dict = True
        self.generic_visit(node)

    def visit_Set(self, node):
        self.uses_set = True
        self.generic_visit(node)


def estimate_space_complexity(code, is_recursive=False):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Unknown"

    visitor = SpaceVisitor()
    visitor.visit(tree)

    # Base space complexity
    if visitor.uses_list or visitor.uses_dict or visitor.uses_set:
        space = "O(n)"
    else:
        space = "O(1)"

    # Add recursion stack consideration
    if is_recursive:
        space += " + recursion stack"

    return space
# Estimates space complexity based on data structure usage and recursion stack


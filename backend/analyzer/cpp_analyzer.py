from pycparser import CParser, c_ast

def analyze_c_code(code):
    parser = CParser()
    tree = parser.parse(code)

    loops = 0
    recursion = False
    functions = {}

    class Visitor(c_ast.NodeVisitor):
        def visit_FuncDef(self, node):
            functions[node.decl.name] = node
            self.generic_visit(node)

        def visit_For(self, node):
            nonlocal loops
            loops += 1
            self.generic_visit(node)

        def visit_While(self, node):
            nonlocal loops
            loops += 1
            self.generic_visit(node)

        def visit_FuncCall(self, node):
            nonlocal recursion
            if isinstance(node.name, c_ast.ID):
                if node.name.name in functions:
                    recursion = True
            self.generic_visit(node)

    Visitor().visit(tree)

    if recursion:
        time_c = "O(n)"
        space_c = "O(n)"
    elif loops > 1:
        time_c = "O(n^2)"
        space_c = "O(1)"
    elif loops == 1:
        time_c = "O(n)"
        space_c = "O(1)"
    else:
        time_c = "O(1)"
        space_c = "O(1)"

    return time_c, space_c, recursion
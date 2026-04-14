import ast

def parse_code(code):
    try:
        return ast.parse(code)
    except SyntaxError as e:
        return str(e)

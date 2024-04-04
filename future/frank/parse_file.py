from tree_sitter import Language, Parser

PY_LANGUAGE = Language('grammar/python.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

# Parse some code
code = b"""
def hello_world():
    print("Hello, world!")
"""
tree = parser.parse(code)

root_node = tree.root_node
print(root_node.sexp())

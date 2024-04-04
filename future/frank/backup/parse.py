from tree_sitter import Language, Parser

compiled_library_path = "/Users/sud/Desktop/code/tree-sitter-typescript/typescript/libtree_sitter_typescript.so"
TS_LANGUAGE = Language(compiled_library_path, "typescript")
parser = Parser()
parser.set_language(TS_LANGUAGE)


def parse(file):
    with open(file, "r") as js_file:
        js_code = js_file.read()

    tree = parser.parse(bytes(js_code, "utf8"))
    return tree

from tree_sitter import Language, Parser


def highlight_code(code):
    # parser = Parser()
    # parser.set_language(Language('build/my-languages.so', 'python'))
    PY_LANGUAGE = Language('grammar/python.so', 'python')
    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    tree = parser.parse(bytes(code, "utf8"))
    cursor = tree.walk()

    highlighted_code = ""

    while True:
        node = cursor.node

        if node.type == 'string':
            print('>>>')
            highlighted_code += f'<span style="color: green;">{code[node.start_byte:node.end_byte]}</span>'
        elif node.type == 'comment':
            print('>>>')
            highlighted_code += f'<span style="color: grey;">{code[node.start_byte:node.end_byte]}</span>'
        elif node.type == 'keyword':
            print('>>>')
            highlighted_code += f'<span style="color: blue;">{code[node.start_byte:node.end_byte]}</span>'
        else:
            print('>>s>')
            highlighted_code += code[node.start_byte:node.end_byte]

        if not cursor.goto_next_sibling():
            break

    return highlighted_code

# Example usage
code = """
def hello_world():
    # This is a comment
    print("Hello, world!")
"""
print(highlight_code(code))

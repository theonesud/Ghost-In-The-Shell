import os

from tree_sitter import Language, Parser


def parse_file(filepath, language):
    with open(filepath, "rb") as file:
        content = file.read()
    parser = Parser()
    parser.set_language(Language("grammar/py-js-ts-tsx-html-css-json.so", language))
    tree = parser.parse(content)
    return tree


def extract_functions(tree):
    cursor = tree.walk()
    functions = []

    def visit(node):
        if node.type == "function_definition":
            functions.append(node.text.decode("utf8"))
        for child in node.children:
            visit(child)

    visit(cursor.node)
    return functions


def extract_function_names(tree):
    cursor = tree.walk()
    function_names = []

    def visit(node):
        if node.type == "function_definition":
            for child in node.children:
                if child.type == "identifier":
                    function_names.append(child.text.decode("utf8"))
                    break
        for child in node.children:
            visit(child)

    visit(cursor.node)
    return function_names


def extract_class_names(tree):
    cursor = tree.walk()
    class_names = []

    def visit(node):
        if node.type == "class_definition":
            for child in node.children:
                if child.type == "identifier":
                    class_names.append(child.text.decode("utf8"))
                    break
        for child in node.children:
            visit(child)

    visit(cursor.node)
    return class_names


def find_calls_within_function(tree, target_function_name):
    calls = []

    def visit(node, inside_target_function=False):
        nonlocal calls

        # Check if this node represents a function definition
        if node.type == "function_definition":
            # Check if the function name matches our target function
            for child in node.children:
                if (
                    child.type == "identifier"
                    and child.text.decode("utf8") == target_function_name
                ):
                    # We are now inside the target function
                    inside_target_function = True
                    break
                elif child.type == "function_definition":
                    # Nested function, skip it
                    return

        # If we are inside the target function, look for call nodes
        if inside_target_function and node.type == "call":
            # Assuming the function or class being called is the first child (simplification)
            call_name_node = node.children[0]
            if call_name_node.type == "identifier":
                calls.append(call_name_node.text.decode("utf8"))

        # Recursively visit children
        for child in node.children:
            visit(child, inside_target_function)

    # Start traversal from the root node
    visit(tree.root_node)
    return calls


def traverse_directory(directory, language, extention):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extention):
                filepath = os.path.join(root, file)
                tree = parse_file(filepath, language)
                function_names = extract_function_names(tree)
                print(function_names)
                # functions = extract_functions(tree)
                # if functions:
                #     print(f'Found functions in {filepath}:')
                #     for function in functions:
                #         print(f'  {function}')


if __name__ == "__main__":
    directory_path = "/home/sud/code/ai/ghost/ghost"
    language = "python"
    extention = ".py"

    traverse_directory(directory_path, language, extention)

    # # Example usage:
    # # Assuming `tree` is already a Tree-sitter syntax tree you've obtained from parsing Python source code
    # target_function_name = 'my_function'
    # calls = find_calls_within_function(tree, target_function_name)
    # print(f'Calls within {target_function_name}:', calls)

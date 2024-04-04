import pathlib
from tree_sitter import Language, Parser
import requests
import json


def get_embeddings(text):
    # Placeholder function for OpenAI API call
    # Implement the OpenAI API call here
    pass


def explore_tree(node, source_code, definitions):
    # Modified function to collect function/class definitions and calls
    # Implement logic here based on your requirements
    pass


def process_file(file_path):
    with open(file_path, "r") as file:
        source_code = file.read()
    tree = parser.parse(bytes(source_code, "utf8"))
    definitions = []
    explore_tree(tree.root_node, bytes(source_code, "utf8"), definitions)
    return definitions


def main(directory_path):
    embeddings = {}
    for file_path in pathlib.Path(directory_path).rglob("*.ts"):
        definitions = process_file(file_path)
        for definition in definitions:
            # Avoid duplicate processing if needed
            if definition not in embeddings:
                embeddings[definition] = get_embeddings(definition)
    # Store the embeddings
    with open("embeddings.json", "w") as file:
        json.dump(embeddings, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main("/path/to/your/typescript/codebase")


# Read your JavaScript code into a variable
print(tree)


# def explore_tree(node, depth=0):
#     # Print node type and its start and end positions in the source code
#     print(
#         f"{' ' * depth * 2}Node type: {node.type}, Start: {node.start_point}, End: {node.end_point}"
#     )

#     # Recursively explore each child node
#     for child in node.children:
#         explore_tree(child, depth + 1)


# def explore_functions(node, depth=0):
#     if node.type == "function_declaration" or node.type == "method_definition":
#         # Print function-related information
#         print(
#             f"{' ' * depth * 2}Function: {node.type}, Start: {node.start_point}, End: {node.end_point}"
#         )

#     # Continue traversing
#     for child in node.children:
#         explore_functions(child, depth + 1)


# def explore_tree(node, source_code, depth=0):
#     indent = " " * depth * 2
#     node_text = source_code[node.start_byte : node.end_byte].decode("utf8")
#     print(
#         f"{indent}Node type: {node.type}, Start: {node.start_point}, End: {node.end_point}"
#     )
#     print(
#         f"{indent}Text: {node_text[:50]}..."
#     )  # Print the first 50 characters of the node text for brevity

#     # Recursively explore each child node
#     for child in node.children:
#         explore_tree(child, source_code, depth + 1)


# js_code_bytes = bytes(js_code, "utf8")  # Assuming js_code is your source code string
# explore_tree(tree.root_node, js_code_bytes)


# root_node = tree.root_node
# explore_functions(root_node)

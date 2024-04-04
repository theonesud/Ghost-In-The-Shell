import os
from pprint import pprint

from tree_sitter import Language, Parser

# Assuming you've already set up Tree-sitter and loaded the Python grammar
language = Language("grammar/python.so", "python")
parser = Parser()
parser.set_language(language)


def parse_file(file_path):
    with open(file_path, "rb") as file:
        return parser.parse(file.read())


def extract_definitions_and_calls(tree):
    # Limitations and Considerations:

    #     Complex Call Patterns: This simplified approach may not accurately handle more complex call patterns, such as method calls on objects or calls within nested expressions. You might need to adjust the logic for identifying the called entity in such cases.
    #     Dynamic Behavior: Static analysis can't fully capture dynamic behaviors (e.g., calls made using getattr or similar Python features), so some calls might be missed or inaccurately represented.
    #     Imports and Namespaces: The function doesn't resolve imports or handle namespaced calls. You might need additional logic to resolve the actual definitions for imported or namespaced entities.

    """
    Extracts definitions and calls from a given syntax tree.

    Args:
    - tree (Tree): The syntax tree from which to extract information.

    Returns:
    - Tuple[Dict[str, Dict], Dict[str, List[Dict]]]: A tuple containing two dictionaries,
      one for definitions and another for calls. The definitions dictionary maps names to
      their details (e.g., type, location), and the calls dictionary maps names to a list
      of details about where they are called.
    """
    definitions = {}
    calls = {}

    def visit(node, parent_type=None):
        # Handle function and class definitions
        if node.type == "function_definition" or node.type == "class_definition":
            identifier = None
            for child in node.children:
                if child.type == "identifier":
                    identifier = child.text.decode("utf8")
                    break
            if identifier:
                definitions[identifier] = {
                    "type": node.type,
                    "location": (node.start_point, node.end_point),
                }

        # Handle calls within functions/classes or at the top level
        elif node.type == "call":
            identifier = None
            # Assuming the called function or class might not always be a direct child,
            # e.g., it could be a method call or namespaced.
            # This simplification may need adjustments for complex cases.
            for child in node.children:
                if child.type == "identifier":
                    identifier = child.text.decode("utf8")
                    break
            if identifier:
                if identifier not in calls:
                    calls[identifier] = []
                calls[identifier].append(
                    {
                        "type": "call",
                        "location": (node.start_point, node.end_point),
                        "parent_type": parent_type,
                    }
                )

        # Recursively visit children, passing down the parent node type if it's a definition
        for child in node.children:
            new_parent_type = (
                node.type
                if node.type in ["function_definition", "class_definition"]
                else parent_type
            )
            visit(child, new_parent_type)

    visit(tree.root_node)
    return definitions, calls


def build_call_graph(project_directory):
    definitions = {}
    calls = {}
    for root, dirs, files in os.walk(project_directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                tree = parse_file(file_path)
                file_definitions, file_calls = extract_definitions_and_calls(tree)
                # Update definitions and calls with information from this file
                definitions.update(file_definitions)
                calls.update(file_calls)
    return definitions, calls


def link_calls(definitions, calls):
    #     Considerations and Limitations:

    #     Dynamic Features and Imports: This simplified approach does not account for Python's dynamic features (e.g., getattr, importlib) or the complexities of the import system (e.g., relative imports, aliases).
    #     Scope and Visibility: The function does not consider scope and visibility rules, which means it could incorrectly link calls to similarly named functions or classes in different modules or scopes.
    #     Enhancements: For a more accurate and comprehensive solution, you would need to enhance this approach to handle Python's import system, including resolving module paths and aliases, as well as consider the scope and visibility of names.

    # This basic implementation serves as a starting point for building a call graph. Developing a tool that accurately models the complexities of a Python codebase requires a more sophisticated analysis, potentially incorporating static analysis libraries that can resolve imports and understand Python's scoping rules.

    """
    Links calls to their definitions across files, based on name matching.

    Args:
    - definitions (Dict[str, Dict]): Dictionary of definitions with details.
    - calls (Dict[str, List[Dict]]): Dictionary of calls with details.

    Returns:
    - Dict[str, Any]: A dictionary representing the call graph, linking calls to definitions.
    """
    call_graph = {}

    # Iterate over all calls
    for call_name, call_list in calls.items():
        for call in call_list:
            # Check if the call matches a known definition
            if call_name in definitions:
                definition = definitions[call_name]

                # If the call name is found in definitions, link it
                if call_name not in call_graph:
                    call_graph[call_name] = {"definition": definition, "calls": []}
                call_graph[call_name]["calls"].append(call)
            else:
                # Handle the case where a call doesn't match any known definition
                # This could happen for various reasons (dynamic behavior, external libraries, etc.)
                if call_name not in call_graph:
                    call_graph[call_name] = {"definition": None, "calls": [call]}
                else:
                    call_graph[call_name]["calls"].append(call)

    return call_graph


# Example usage
if __name__ == "__main__":
    project_directory = "/home/sud/code/ai/ghost/ghost"
    definitions, calls = build_call_graph(project_directory)
    call_graph = link_calls(definitions, calls)
    pprint(call_graph)


# Challenges and Considerations

#     Resolving Imports: Understanding where a function or class is defined based on a call requires resolving Python imports, which can be non-trivial due to dynamic imports, conditional imports, and module re-exports.
#     Scalability: For large projects, this process can be resource-intensive. Efficient data structures and algorithms are crucial.
#     Dynamic Features: Python's dynamic features (e.g., reflection, dynamic imports) can make static analysis challenging.

# This approach provides a static analysis of your codebase. Dynamic behaviors, runtime imports, and other Pythonic features might not be fully captured. For comprehensive analysis, consider integrating with or developing tools that also consider runtime information.

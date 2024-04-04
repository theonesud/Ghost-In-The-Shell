import ast
import os
from pprint import pprint

# def parse_python_file(file_path):
#     with open(file_path, encoding="utf-8") as source:
#         return ast.parse(source.read(), filename=file_path)

# def collect_imports(file_ast):
#     imports = []
#     for node in ast.walk(file_ast):
#         if isinstance(node, ast.Import):
#             for alias in node.names:
#                 imports.append((alias.name, None))
#         elif isinstance(node, ast.ImportFrom):
#             module = node.module if node.module else ''
#             for alias in node.names:
#                 imports.append((module, alias.name))
#     return imports

# def collect_definitions(file_ast):
#     definitions = {}
#     for node in ast.walk(file_ast):
#         if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
#             definitions[node.name] = 'function'
#         elif isinstance(node, ast.ClassDef):
#             definitions[node.name] = 'class'
#     return definitions

# def build_project_symbol_table(project_directory):
#     project_imports = {}
#     project_definitions = {}

#     # Collect imports and definitions from each file
#     for root, dirs, files in os.walk(project_directory):
#         for file in files:
#             if file.endswith(".py"):
#                 file_path = os.path.join(root, file)
#                 file_ast = parse_python_file(file_path)
#                 file_imports = collect_imports(file_ast)
#                 file_definitions = collect_definitions(file_ast)
#                 project_imports[file_path] = file_imports
#                 project_definitions.update({(file_path, name): kind for name, kind in file_definitions.items()})

#     # Resolve imports here based on project_imports and project_definitions
#     # This step requires a more complex logic to accurately map imports to their definitions

#     return project_definitions


def parse_python_file(file_path):
    with open(file_path, encoding="utf-8") as source:
        return ast.parse(source.read(), filename=file_path)


def collect_imports_and_definitions(file_ast):
    imports, definitions = [], {}
    for node in ast.walk(file_ast):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(("import", alias.name, alias.asname))
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for alias in node.names:
                imports.append(("from-import", module, alias.name, alias.asname))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions[node.name] = ("function", node.lineno)
        elif isinstance(node, ast.ClassDef):
            definitions[node.name] = ("class", node.lineno)
    return imports, definitions


def build_project_symbol_table(project_directory):
    project_files = {}
    symbol_table = {}

    # Step 1: Collect imports and definitions from each file
    for root, dirs, files in os.walk(project_directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_ast = parse_python_file(file_path)
                imports, definitions = collect_imports_and_definitions(file_ast)
                project_files[file_path] = {
                    "imports": imports,
                    "definitions": definitions,
                }

    # Step 2: Build a basic symbol table with local definitions
    for file_path, content in project_files.items():
        for name, (kind, lineno) in content["definitions"].items():
            symbol_table[name] = {
                "type": kind,
                "defined_in": file_path,
                "lineno": lineno,
            }

    # Step 3: Resolve imports within the project
    # Note: This simplified version does not handle relative imports or external packages
    for file_path, content in project_files.items():
        for import_type, module, name, *asname in content["imports"]:
            asname = asname[0] if asname else name
            if import_type == "from-import":
                # Assuming all from-imports are from within the project for simplicity
                # This would need more logic to handle properly, especially with relative imports
                if name in symbol_table:
                    # Directly link the import to the symbol if available
                    symbol_table[asname] = symbol_table[name].copy()
                    symbol_table[asname]["imported_by"] = file_path
            elif import_type == "import":
                # This would require parsing the imported module to link symbols correctly
                pass

    return symbol_table


if __name__ == "__main__":
    project_directory = "/home/sud/code/ai/ghost/ghost"
    project_symbol_table = build_project_symbol_table(project_directory)
    pprint(project_symbol_table)

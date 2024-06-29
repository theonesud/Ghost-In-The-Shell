import ast
import json
import os

import requests


class CodebaseAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = {}
        self.current_class = None
        self.current_file = None

    def visit_ClassDef(self, node):
        class_name = node.name
        bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
        self.current_class = class_name
        self.classes[class_name] = {
            "bases": bases,
            "functions": [],
            "file": self.current_file,
        }
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class:
            self.classes[self.current_class]["functions"].append(node.name)
        self.generic_visit(node)


def total_influence(class_name, code_structure, direct_influences, visited=None):
    if visited is None:
        visited = set()
    if class_name in visited:
        return 0
    visited.add(class_name)
    total = direct_influences[class_name]
    for other_class, details in code_structure.items():
        if class_name in details["bases"]:
            total += total_influence(
                other_class, code_structure, direct_influences, visited.copy()
            )
    return total


def find_depth(class_name, code_structure, inheritance_depths):
    if inheritance_depths[class_name] > 0:
        return inheritance_depths[class_name]
    bases = code_structure[class_name]["bases"]
    if not bases:
        inheritance_depths[class_name] = 1
        return 1
    max_depth = max(
        (
            find_depth(base, code_structure, inheritance_depths)
            if base in inheritance_depths
            else 1
        )
        for base in bases
    )
    inheritance_depths[class_name] = max_depth + 1
    return max_depth + 1


def create_json_structure(in_dir, out_file):
    analyzer = CodebaseAnalyzer()
    for dirpath, _, filenames in os.walk(in_dir):
        for filename in filenames:
            if "test" in dirpath:
                continue
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                analyzer.current_file = file_path
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    tree = ast.parse(content)
                    analyzer.visit(tree)
    code_structure = analyzer.classes
    inheritance_depths = {class_name: 0 for class_name in code_structure.keys()}
    for c in code_structure.keys():
        find_depth(c, code_structure, inheritance_depths)
    direct_influences = {class_name: 0 for class_name in code_structure.keys()}
    for _, details in code_structure.items():
        for base in details["bases"]:
            if base in direct_influences:
                direct_influences[base] += 1
    class_weightages = {
        class_name: total_influence(class_name, code_structure, direct_influences)
        for class_name in code_structure.keys()
    }
    for class_name in code_structure.keys():
        code_structure[class_name]["inheritance_depth"] = inheritance_depths.get(
            class_name, 0
        )
        code_structure[class_name]["weightage"] = class_weightages.get(class_name, 0)
    sorted_structure = sorted(
        code_structure.items(),
        key=lambda x: (x[1]["inheritance_depth"], -x[1]["weightage"]),
    )
    with open(out_file, "w") as f:
        json.dump(dict(sorted_structure), f)


def call_model(prompt):
    balanced_chat_mode = {
        "prompt": prompt,
        "max_new_tokens": 2048,
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.85,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "num_beams": 1,
        "num_return_sequences": 1,
        "no_repeat_ngram_size": 2,
    }
    with requests.Session() as session:
        response = session.post("http://localhost:8000/", json=balanced_chat_mode)
    assert response.status_code == 200
    assert "generated_text" in response.json()
    return response.json()["generated_text"]


if __name__ == "__main__":
    repo_path = "/home/sud/code/llama_index"
    json_structure_path = "/home/sud/code/llamaindex_code_structure.json"

    create_json_structure(repo_path, json_structure_path)

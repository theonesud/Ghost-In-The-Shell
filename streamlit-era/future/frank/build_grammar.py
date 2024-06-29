from tree_sitter import Language

Language.build_library(
    # Store the library in the `build` directory
    "grammar/py-js-ts-tsx-html-css-json.so",
    # Include one or more languages
    ["parser/tree-sitter-python", "parser/tree-sitter-javascript", "parser/tree-sitter-typescript/typescript", "parser/tree-sitter-typescript/tsx", "parser/tree-sitter-html", "parser/tree-sitter-css", "parser/tree-sitter-json"],
)

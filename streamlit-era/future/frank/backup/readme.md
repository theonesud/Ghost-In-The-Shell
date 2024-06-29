git clone https://github.com/tree-sitter/tree-sitter-javascript.git
npm install -g tree-sitter-cli
cd tree-sitter-javascript
tree-sitter generate
gcc -o libtree_sitter_javascript.so -shared src/parser.c src/scanner.c -Isrc -fPIC

git clone https://github.com/tree-sitter/tree-sitter-typescript.git
cd tree-sitter-typescript/typescript

mkdir -p /Users/sud/Desktop/code/tree-sitter-typescript/node_modules
ln -s /Users/sud/Desktop/code/tree-sitter-javascript /Users/sud/Desktop/code/tree-sitter-typescript/node_modules/tree-sitter-javascript

tree-sitter generate
gcc -o libtree_sitter_typescript.so -shared src/parser.c src/scanner.c -Isrc -fPIC

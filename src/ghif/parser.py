import ast
from .tree import GitHubDirectory, GitHubFile
from .client import GitHubClient

_collected: dict[str, tuple[str, int, int]] = {}


class GitHubSourceWalker(ast.NodeVisitor):
    def __init__(self, tree: GitHubDirectory, client: GitHubClient, file_path: str):
        self.tree = tree
        self.client = client
        self.path = ""
        self.file_path = file_path
        super().__init__()

    def visit_ClassDef(self, node: ast.ClassDef):
        orig_path = self.path
        self.path = f"{self.path}{node.name}."
        for child in node.body:
            self.visit(child)
        self.path = orig_path

    def visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        if not node.end_lineno:
            raise Exception(
                f"ast.{"Async" if isinstance(node, ast.AsyncFunctionDef) else ""}FunctionDef.end_lineno is null! Investigate this!"
            )

        _collected[f"{self.path}{node.name}"] = (
            self.file_path,
            node.lineno,
            node.end_lineno,
        )

        for child in node.body:
            self.visit(child)

    visit_FunctionDef = visit_function
    visit_AsyncFunctioNDef = visit_function

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if not node.end_lineno:
            raise Exception(f"ast.AnnAssign.end_lineno is null! Investigate this!")

        if isinstance(node.target, ast.Name) and self.path:
            _collected[f"{self.path}{node.target.id}"] = (
                self.file_path,
                node.lineno,
                node.end_lineno,
            )

    def visit_Assign(self, node: ast.Assign):
        if not self.path:
            return

        for target in node.targets:
            if isinstance(target, ast.Name):
                print(self.path, "name:", target.id, node.lineno)
            elif isinstance(target, ast.Attribute):
                print(self.path, "attribute:", target.attr, node.lineno)
            elif isinstance(target, ast.Tuple):
                print(self.path, "tuple:", target.elts, node.lineno)
            else:
                raise Exception(type(target))


class GitHubSourceParser:
    def __init__(self, client: GitHubClient):
        self._client = client

    def build(self, tree: GitHubDirectory, file: GitHubFile):
        _collected.clear()
        root = ast.parse(self._client._fetch(file))
        walker = GitHubSourceWalker(tree, self._client, file.path)
        walker.visit(root)
        print(_collected)

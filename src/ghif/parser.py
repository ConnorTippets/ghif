import ast
from .tree import GitHubFile
from .client import GitHubClient

_collected: list[list[str | int]] = []


class GitHubSourceWalker(ast.NodeVisitor):
    def __init__(self, file: GitHubFile):
        self.path = ""
        self.file_path = file.path
        self.file_sha = file.sha
        super().__init__()

    def visit_ClassDef(self, node: ast.ClassDef):
        if not node.end_lineno:
            raise Exception("ast.ClassDef.end_lineno is null! Investigate this!")

        _collected.append(
            [
                f"{self.path}{node.name}",
                self.file_path,
                self.file_sha,
                node.lineno,
                node.end_lineno,
            ],
        )

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

        _collected.append(
            [
                f"{self.path}{node.name}",
                self.file_path,
                self.file_sha,
                node.lineno,
                node.end_lineno,
            ],
        )

    visit_FunctionDef = visit_function
    visit_AsyncFunctionDef = visit_function


class GitHubSourceParser:
    def __init__(self, client: GitHubClient):
        self._client = client
        _collected.clear()

    def build(self, file: GitHubFile):
        root = ast.parse(self._client._fetch(file))
        walker = GitHubSourceWalker(file)
        walker.visit(root)

    def get_collected(self):
        return _collected

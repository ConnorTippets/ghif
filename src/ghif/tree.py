from dataclasses import dataclass
from functools import cached_property
from typing import Iterator


@dataclass
class GitHubFile:
    path: str
    sha: str
    repo: str

    @cached_property
    def url(self):
        return f"https://api.github.com/repos/{self.repo}/git/blobs/{self.sha}"


@dataclass
class GitHubDirectory:
    path: str
    sha: str
    repo: str
    files: "list[GitHubFile | GitHubDirectory]"

    def find(self, path: str) -> GitHubFile | None:
        for file in self.files:
            if isinstance(file, GitHubFile) and file.path == path:
                return file
            elif isinstance(file, GitHubDirectory) and path.startswith(file.path):
                return file.find(path)

        return None

    def walk_files(self) -> Iterator[GitHubFile]:
        for file in self.files:
            if isinstance(file, GitHubFile):
                yield file
            elif isinstance(file, GitHubDirectory):
                yield from file.walk_files()

    def walk_dirs(self) -> "Iterator[GitHubDirectory]":
        yield self
        for file in self.files:
            if isinstance(file, GitHubDirectory):
                yield file
                yield from file.walk_dirs()


class GitHubTreeBuilder:
    def _build_dir(self, repo: str, path: str, tree: list, i: int):
        files = []

        while i < len(tree):
            file = tree[i]
            if not file["path"].startswith(path):
                break
            if file["type"] == "blob":
                files.append(GitHubFile(file["path"], file["sha"], repo))
                i += 1
            elif file["type"] == "tree":
                inner_files, new_i = self._build_dir(repo, file["path"], tree, i + 1)
                files.append(
                    GitHubDirectory(file["path"], file["sha"], repo, inner_files)
                )
                i = new_i
            else:
                raise Exception(f"Unknown file type! {file["type"]}")

        return files, i

    def build(self, repo: str, name: str, response: dict):
        root = GitHubDirectory(name, response["sha"], repo, [])
        tree = response["tree"]

        i = 0
        while i < len(tree):
            file = tree[i]
            if file["type"] == "blob":
                root.files.append(GitHubFile(file["path"], file["sha"], repo))
                i += 1
            elif file["type"] == "tree":
                files, new_i = self._build_dir(repo, file["path"], tree, i + 1)
                root.files.append(
                    GitHubDirectory(file["path"], file["sha"], repo, files)
                )
                i = new_i
            else:
                raise Exception(f"Unknown file type! {file["type"]}")

        return root

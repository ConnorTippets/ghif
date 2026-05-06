from dataclasses import dataclass


@dataclass
class GitHubFile:
    path: str
    sha: str
    repo: str

    @property
    def url(self):
        return f"https://api.github.com/repos/{self.repo}/git/blobs/{self.sha}"


@dataclass
class GitHubDirectory:
    path: str
    sha: str
    repo: str
    files: "list[GitHubFile | GitHubDirectory]"


class GitHubTreeBuilder:
    def _build_dir(self, repo: str, path: str, tree: list):
        files = []

        i = 0
        while i < len(tree):
            file = tree[i]
            if not file["path"].startswith(path):
                break
            if file["type"] == "blob":
                files.append(GitHubFile(file["path"], file["sha"], repo))
                i += 1
            elif file["type"] == "tree":
                inner_files, offset = self._build_dir(
                    repo, file["path"], tree[(i + 1) :]
                )
                files.append(
                    GitHubDirectory(file["path"], file["sha"], repo, inner_files)
                )
                i += offset + 1
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
                files, offset = self._build_dir(
                    repo, file["path"], response["tree"][(i + 1) :]
                )
                root.files.append(
                    GitHubDirectory(file["path"], file["sha"], repo, files)
                )
                i += offset + 1
            else:
                raise Exception(f"Unknown file type! {file["type"]}")

        return root

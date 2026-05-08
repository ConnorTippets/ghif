from .tree import GitHubTreeBuilder, GitHubDirectory, GitHubFile
from .parser import GitHubSourceParser
from .client import GitHubClient


class GitHubLoader:
    def __init__(self):
        self._client = GitHubClient()

    def load(
        self, repo_url: str, branch: str, sub_dir: str | None = None
    ) -> list[dict[str, str | int]]:
        tree = self._fetch_tree(repo_url, branch, sub_dir)
        parser = GitHubSourceParser(self._client)

        known_packages: list[str] = []
        for dir in tree.walk_dirs():
            if any(
                file.path.endswith("__init__.py")
                for file in dir.files
                if isinstance(file, GitHubFile)
            ):
                known_packages.append("" if dir == tree else dir.path)

        for file in tree.walk_files():
            if file.path.endswith(".py") and any(
                file.path.startswith(dir_path) for dir_path in known_packages
            ):
                parser.build(file)

        return parser.get_collected()

    def _fetch_tree(
        self, repo_url: str, branch: str, sub_dir: str | None = None
    ) -> GitHubDirectory:
        repo_raw = "/".join(
            repo_url.replace("\\", "/").strip("/").replace(".git", "").split("/")[-2:]
        )
        repo_api_url = f"https://api.github.com/repos/{repo_raw}"

        response = self._client._session.get(
            repo_api_url
            + f"/git/trees/{branch}{(":" + sub_dir.strip("/")) if sub_dir else ""}?recursive=1",
            headers=self._client._get_headers(),
        )
        data = response.json()

        if "documentation_url" in data:
            raise Exception(
                f"Error while fetching `{repo_raw}`: {data["status"]} {data["message"]}"
            )

        return GitHubTreeBuilder().build(repo_raw, sub_dir or "/", data)

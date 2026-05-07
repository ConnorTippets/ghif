from .tree import GitHubTreeBuilder, GitHubDirectory, GitHubFile
from .parser import GitHubSourceParser
from .client import GitHubClient

# from pprint import pprint as print


class GitHubLoader:
    def __init__(self):
        self._client = GitHubClient()

    def load(self, repo_url: str, branch: str, file: str, sub_dir: str | None = None):
        tree = self._fetch_tree(repo_url, branch, sub_dir)
        path = file.replace("\\", "/").strip("/")

        file_obj = tree.find(path)
        if not file_obj:
            raise Exception(f"Couldn't find `{file}` in repo!")

        GitHubSourceParser(self._client).build(tree, file_obj)

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

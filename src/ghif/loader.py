import requests
from .tree import GitHubTreeBuilder, GitHubDirectory, GitHubFile
import codecs
import json

# from pprint import pprint as print


class GitHubLoader:
    _api_key: str
    _session: requests.Session

    def __init__(self):
        self._api_key = ""
        self._session = requests.Session()

    def load(self, repo_url: str, branch: str, file: str, sub_dir: str | None = None):
        tree = self._fetch_tree(repo_url, branch, sub_dir)
        path = file.strip("/")

        file_obj = tree.find(path)
        if not file_obj:
            raise Exception(f"Couldn't find `{file}` in repo!")

        print(file_obj)

    def _fetch(self, file: GitHubFile) -> bytes:
        repo_api_url = f"https://api.github.com/repos/{file.repo}"
        response = self._session.get(
            repo_api_url + f"/git/blobs/{file.sha}",
            headers=self._get_headers(),
        )

        return codecs.decode(
            json.loads(response.content.decode("utf-8"))["content"].encode("utf-8"),
            "base64",
        )

    def _get_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._api_key}",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    def _fetch_tree(
        self, repo_url: str, branch: str, sub_dir: str | None = None
    ) -> GitHubDirectory:
        repo_raw = "/".join(
            repo_url.replace("\\", "/").strip("/").replace(".git", "").split("/")[-2:]
        )
        repo_api_url = f"https://api.github.com/repos/{repo_raw}"

        response = self._session.get(
            repo_api_url
            + f"/git/trees/{branch}{(":" + sub_dir.strip("/")) if sub_dir else ""}?recursive=1",
            headers=self._get_headers(),
        )
        data = response.json()

        if "documentation_url" in data:
            raise Exception(
                f"Error while fetching `{repo_raw}`: {data["status"]} {data["message"]}"
            )

        return GitHubTreeBuilder().build(repo_raw, sub_dir or "/", data)

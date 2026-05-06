import requests


class GitHubLoader:
    _api_key: str
    _session: requests.Session

    def __init__(self):
        self._api_key = ""
        self._session = requests.Session()

    def load(self, repo_url: str, branch: str, sub_dir: str | None = None):
        self._fetch_tree(repo_url, branch, sub_dir)

    def _get_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._api_key}",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    def _fetch_tree(self, repo_url: str, branch: str, sub_dir: str | None = None):
        repo_raw = (
            "/".join(repo_url.replace("\\", "/").split("/")[-2:])
            .replace(".git", "")
            .strip("/")
        )
        repo_api_url = f"https://api.github.com/repos/{repo_raw}"

        response = self._session.get(
            repo_api_url
            + f"/git/trees/{branch}{(":" + sub_dir.strip("/")) if sub_dir else ""}?recursive=1",
            headers=self._get_headers(),
        )
        print(response.json())

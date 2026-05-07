import codecs
import requests
from .tree import GitHubFile


class GitHubClient:
    _api_key: str
    _session: requests.Session

    def __init__(self):
        self._api_key = ""
        self._session = requests.Session()

    def _fetch(self, file: GitHubFile) -> bytes:
        repo_api_url = f"https://api.github.com/repos/{file.repo}"
        response = self._session.get(
            repo_api_url + f"/git/blobs/{file.sha}",
            headers=self._get_headers(),
        )

        return codecs.decode(
            response.json()["content"].encode("utf-8"),
            "base64",
        )

    def _get_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._api_key}",
            "X-GitHub-Api-Version": "2026-03-10",
        }

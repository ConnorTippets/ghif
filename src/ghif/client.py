import codecs
import requests
from .tree import GitHubFile
import httpx


class GitHubClient:
    _api_key: str
    _session: requests.Session

    def __init__(self):
        self._api_key = ""
        self._session = requests.Session()

    async def _fetch(
        self, client: httpx.AsyncClient, file: GitHubFile
    ) -> tuple[GitHubFile, bytes]:
        repo_api_url = f"https://api.github.com/repos/{file.repo}"
        response = await client.get(
            repo_api_url + f"/git/blobs/{file.sha}",
            headers=self._get_headers(),
        )

        return file, codecs.decode(
            response.json()["content"].encode("utf-8"),
            "base64",
        )

    def _get_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._api_key}",
            "X-GitHub-Api-Version": "2026-03-10",
        }

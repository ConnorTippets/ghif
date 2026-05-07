from .loader import GitHubLoader

_loader = GitHubLoader()


def config(api_key: str):
    _loader._client._api_key = api_key


def load(repo_url: str, branch: str, sub_dir: str | None = None):
    """
    Load module from github repo given a branch. Optionally supply a subdirectory if the module is not toplevel.
    """
    return _loader.load(repo_url, branch, sub_dir)

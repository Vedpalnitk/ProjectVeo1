"""Utility script for publishing the local repository to GitHub.

The script creates (or reuses) a GitHub repository and pushes the current
branch to it. It relies on a GitHub personal access token with the
``repo`` scope and uses only the Python standard library so it can run
without extra dependencies.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API returns an error response."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"GitHub API error {status}: {message}")
        self.status = status
        self.message = message


@dataclass
class RepoInfo:
    """Information about a GitHub repository returned from the API."""

    name: str
    full_name: str
    clone_url: str
    created: bool


def _api_request(token: str, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Perform a request against the GitHub API and return the parsed JSON body."""

    data: Optional[bytes] = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    url = f"{API_ROOT}{path}"
    request = Request(url, data=data, method=method.upper())
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urlopen(request) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_body = response.read().decode(charset)
    except HTTPError as exc:  # pragma: no cover - exercised in integration usage
        body = exc.read().decode("utf-8", errors="replace")
        raise GitHubAPIError(exc.code, body)

    if not raw_body:
        return {}

    return json.loads(raw_body)


def _get_authenticated_user(token: str) -> str:
    data = _api_request(token, "GET", "/user")
    login = data.get("login")
    if not login:
        raise RuntimeError("Unable to determine the authenticated GitHub user")
    return str(login)


def ensure_repository(token: str, repo: str, owner: Optional[str], private: bool) -> RepoInfo:
    payload: Dict[str, Any] = {
        "name": repo,
        "private": private,
        "auto_init": False,
    }
    path = f"/user/repos"
    if owner:
        path = f"/orgs/{owner}/repos"

    try:
        data = _api_request(token, "POST", path, payload)
    except GitHubAPIError as error:
        if error.status != 422:
            raise
        resolved_owner = owner or _get_authenticated_user(token)
        repo_data = _api_request(token, "GET", f"/repos/{resolved_owner}/{repo}")
        return RepoInfo(
            name=str(repo_data["name"]),
            full_name=str(repo_data["full_name"]),
            clone_url=str(repo_data["clone_url"]),
            created=False,
        )

    return RepoInfo(
        name=str(data["name"]),
        full_name=str(data["full_name"]),
        clone_url=str(data["clone_url"]),
        created=True,
    )


def run_git_command(args: list[str], cwd: Path) -> str:
    process = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(
            "Git command failed ({}): {}".format(
                " ".join(args), process.stderr.strip() or process.stdout.strip()
            )
        )
    return process.stdout.strip()


def get_current_branch(cwd: Path) -> str:
    branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if branch == "HEAD":
        raise RuntimeError("Cannot determine branch name from a detached HEAD state")
    return branch


def ensure_remote(remote: str, url: str, cwd: Path) -> None:
    remotes = run_git_command(["remote"], cwd).splitlines()
    if remote in remotes:
        run_git_command(["remote", "set-url", remote, url], cwd)
        return
    run_git_command(["remote", "add", remote, url], cwd)


def push_current_branch(remote: str, local_branch: str, remote_branch: str, cwd: Path) -> None:
    spec = f"{local_branch}:{remote_branch}" if local_branch != remote_branch else local_branch
    run_git_command(["push", "-u", remote, spec], cwd)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload the current repository to GitHub")
    parser.add_argument("repository", help="Name of the GitHub repository to create or update")
    parser.add_argument(
        "--token",
        help="GitHub personal access token with repo scope. Defaults to the GITHUB_TOKEN environment variable.",
    )
    parser.add_argument(
        "--owner",
        help="GitHub user or organization to own the repository. Defaults to the authenticated user.",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Name of the git remote to configure (default: origin)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Create the repository as public. Private by default.",
    )
    parser.add_argument(
        "--branch",
        help="Local branch to push. Defaults to the current checked out branch.",
    )
    parser.add_argument(
        "--remote-branch",
        help=(
            "Branch name to create or update on the remote. Defaults to the current branch for "
            "existing repositories and 'main' when a repository is created."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the repository root (default: project root)",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("A GitHub token is required via --token or the GITHUB_TOKEN environment variable")

    repo_root = args.repo_root
    if not (repo_root / ".git").exists():
        raise SystemExit(f"{repo_root} does not appear to be a git repository")

    local_branch = args.branch or get_current_branch(repo_root)
    repo_info = ensure_repository(token, args.repository, args.owner, not args.public)
    ensure_remote(args.remote, repo_info.clone_url, repo_root)
    remote_branch = args.remote_branch
    if not remote_branch:
        remote_branch = "main" if repo_info.created else local_branch
    push_current_branch(args.remote, local_branch, remote_branch, repo_root)

    print(
        f"Repository {repo_info.full_name} is up to date with branch {remote_branch} "
        f"(local: {local_branch})."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except GitHubAPIError as error:
        raise SystemExit(str(error))

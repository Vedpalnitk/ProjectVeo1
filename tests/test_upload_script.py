import subprocess
from pathlib import Path

import pytest

from scripts import upload_to_github


def test_ensure_repository_creates_repo(monkeypatch):
    captured = {}

    def fake_api(token: str, method: str, path: str, payload=None):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = payload
        return {
            "name": "demo",
            "full_name": "test/demo",
            "clone_url": "https://github.com/test/demo.git",
        }

    monkeypatch.setattr(upload_to_github, "_api_request", fake_api)
    info = upload_to_github.ensure_repository("token", "demo", None, True)

    assert info.name == "demo"
    assert info.full_name == "test/demo"
    assert info.clone_url.endswith("demo.git")
    assert info.created is True
    assert captured["method"] == "POST"
    assert captured["path"] == "/user/repos"
    assert captured["payload"]["private"] is True


def test_ensure_repository_reuses_existing(monkeypatch):
    calls = []

    def fake_api(token: str, method: str, path: str, payload=None):
        calls.append((method, path, payload))
        if method == "POST":
            raise upload_to_github.GitHubAPIError(422, "exists")
        return {
            "name": "demo",
            "full_name": "owner/demo",
            "clone_url": "https://github.com/owner/demo.git",
        }

    monkeypatch.setattr(upload_to_github, "_api_request", fake_api)
    monkeypatch.setattr(upload_to_github, "_get_authenticated_user", lambda token: "owner")

    info = upload_to_github.ensure_repository("token", "demo", None, False)

    assert info.full_name == "owner/demo"
    assert info.created is False
    assert calls[0][0] == "POST"
    assert calls[1][0] == "GET"
    assert calls[1][1] == "/repos/owner/demo"


def _make_repo_root(tmp_path: Path) -> Path:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    return repo_dir


def test_main_pushes_created_repo_to_main(monkeypatch, tmp_path: Path) -> None:
    repo_dir = _make_repo_root(tmp_path)

    monkeypatch.setattr(
        upload_to_github,
        "ensure_repository",
        lambda *args, **kwargs: upload_to_github.RepoInfo(
            name="demo",
            full_name="owner/demo",
            clone_url="https://github.com/owner/demo.git",
            created=True,
        ),
    )
    monkeypatch.setattr(upload_to_github, "ensure_remote", lambda *args, **kwargs: None)
    monkeypatch.setattr(upload_to_github, "get_current_branch", lambda cwd: "work")

    captured = {}

    def fake_push(remote: str, local_branch: str, remote_branch: str, cwd: Path) -> None:
        captured.update(
            {
                "remote": remote,
                "local_branch": local_branch,
                "remote_branch": remote_branch,
                "cwd": cwd,
            }
        )

    monkeypatch.setattr(upload_to_github, "push_current_branch", fake_push)

    exit_code = upload_to_github.main(["demo", "--token", "abc", "--repo-root", str(repo_dir)])

    assert exit_code == 0
    assert captured["remote"] == "origin"
    assert captured["local_branch"] == "work"
    assert captured["remote_branch"] == "main"
    assert captured["cwd"] == repo_dir


def test_main_pushes_existing_repo_to_current_branch(monkeypatch, tmp_path: Path) -> None:
    repo_dir = _make_repo_root(tmp_path)

    monkeypatch.setattr(
        upload_to_github,
        "ensure_repository",
        lambda *args, **kwargs: upload_to_github.RepoInfo(
            name="demo",
            full_name="owner/demo",
            clone_url="https://github.com/owner/demo.git",
            created=False,
        ),
    )
    monkeypatch.setattr(upload_to_github, "ensure_remote", lambda *args, **kwargs: None)
    monkeypatch.setattr(upload_to_github, "get_current_branch", lambda cwd: "work")

    captured = {}

    def fake_push(remote: str, local_branch: str, remote_branch: str, cwd: Path) -> None:
        captured.update(
            {
                "remote": remote,
                "local_branch": local_branch,
                "remote_branch": remote_branch,
                "cwd": cwd,
            }
        )

    monkeypatch.setattr(upload_to_github, "push_current_branch", fake_push)

    exit_code = upload_to_github.main(["demo", "--token", "abc", "--repo-root", str(repo_dir)])

    assert exit_code == 0
    assert captured["remote_branch"] == "work"
    assert captured["local_branch"] == "work"


@pytest.mark.parametrize("initial_remote", [None, "origin"])
def test_ensure_remote(tmp_path: Path, initial_remote: str) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)

    if initial_remote:
        subprocess.run(
            ["git", "remote", "add", initial_remote, "https://example.com/original.git"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )

    upload_to_github.ensure_remote("origin", "https://example.com/updated.git", repo_dir)
    remotes = subprocess.run(["git", "remote", "-v"], cwd=repo_dir, capture_output=True, text=True, check=True)

    assert "origin" in remotes.stdout
    assert "https://example.com/updated.git" in remotes.stdout

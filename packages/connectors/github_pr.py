from __future__ import annotations
import base64
import os
from typing import Optional
import requests

GITHUB_API = "https://api.github.com"

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GH_TOKEN")
        if not self.token:
            raise RuntimeError("Missing GH_TOKEN env var")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        })

    def get_default_branch(self, repo: str) -> str:
        r = self.session.get(f"{GITHUB_API}/repos/{repo}")
        r.raise_for_status()
        return r.json()["default_branch"]

    def get_ref_sha(self, repo: str, ref: str) -> str:
        r = self.session.get(f"{GITHUB_API}/repos/{repo}/git/ref/heads/{ref}")
        r.raise_for_status()
        return r.json()["object"]["sha"]

    def create_branch(self, repo: str, new_branch: str, from_branch: Optional[str] = None) -> str:
        base = from_branch or self.get_default_branch(repo)
        sha = self.get_ref_sha(repo, base)
        r = self.session.post(f"{GITHUB_API}/repos/{repo}/git/refs", json={
            "ref": f"refs/heads/{new_branch}",
            "sha": sha
        })
        r.raise_for_status()
        return new_branch

    def put_file(self, repo: str, branch: str, path: str, content: str, message: str) -> None:
        # create or update file
        url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
        b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
        r = self.session.put(url, json={
            "message": message,
            "content": b64,
            "branch": branch
        })
        r.raise_for_status()

    def open_pr(self, repo: str, branch: str, title: str, body: str) -> str:
        r = self.session.post(f"{GITHUB_API}/repos/{repo}/pulls", json={
            "title": title,
            "head": branch,
            "base": self.get_default_branch(repo),
            "body": body
        })
        r.raise_for_status()
        return r.json()["html_url"]

def open_pr(repo: str, branch: str, path: str, content: str, pr_title: str, pr_body: str) -> str:
    gh = GitHubClient()
    gh.create_branch(repo, branch)
    gh.put_file(repo, branch, path, content, f"add {path}")
    return gh.open_pr(repo, branch, pr_title, pr_body)

import os
import time
from pathlib import Path
import yaml
import pytest
from typer.testing import CliRunner

from pulsewriter_cli.main import app, get_latest_post


@pytest.fixture
def runner():
    return CliRunner()


def write_file(path: Path, content: str, mtime: float | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def test_get_latest_post_returns_newest(tmp_path: Path):
    posts = tmp_path / "_posts"
    posts.mkdir()
    now = time.time()
    a = posts / "a.md"
    b = posts / "b.md"
    c = posts / "c.md"
    write_file(a, "A", mtime=now - 300)
    write_file(b, "B", mtime=now - 100)
    write_file(c, "C", mtime=now - 200)

    latest = get_latest_post(posts)
    assert latest is not None
    assert latest.name == "b.md"


def test_last_dry_run_does_not_create_out_dir(tmp_path: Path, runner: CliRunner):
    # Create config and a single post
    posts = tmp_path / "_posts"
    posts.mkdir()
    post = posts / "post.md"
    write_file(post, "Hello world")

    cfg = {
        "posts_dir": str(posts),
        "out_dir": str(tmp_path / "out"),
        "default_platforms": ["blog", "linkedin", "x", "devto"],
    }
    (tmp_path / ".pulsewriter.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        result = runner.invoke(app, ["last", "--dry-run"])
        assert result.exit_code == 0
        assert "Would transform:" in result.stdout
        # out dir should not be created
        assert not (tmp_path / "out").exists()


def test_last_platforms_override(tmp_path: Path, runner: CliRunner):
    posts = tmp_path / "p"
    posts.mkdir()
    write_file(posts / "x.md", "content")
    cfg = {
        "posts_dir": str(posts),
        "out_dir": str(tmp_path / "out"),
        "default_platforms": ["blog", "linkedin"],
    }
    (tmp_path / ".pulsewriter.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        result = runner.invoke(app, ["last", "--dry-run", "--platforms", "x", "--platforms", "linkedin"])
        assert result.exit_code == 0
        # Ensure the platforms in output reflect override order
        assert "platforms=['x', 'linkedin']" in result.stdout.replace("\"", "'")


def test_last_errors_when_posts_dir_missing(tmp_path: Path, runner: CliRunner):
    cfg = {
        "posts_dir": str(tmp_path / "missing"),
        "out_dir": str(tmp_path / "out"),
        "default_platforms": ["blog", "linkedin"],
    }
    (tmp_path / ".pulsewriter.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        result = runner.invoke(app, ["last"]) 
        assert result.exit_code == 2
        assert "Posts directory not found" in result.stdout or "Posts directory not found" in result.stderr


def test_last_errors_when_empty_posts_dir(tmp_path: Path, runner: CliRunner):
    posts = tmp_path / "empty"
    posts.mkdir()
    cfg = {
        "posts_dir": str(posts),
        "out_dir": str(tmp_path / "out"),
        "default_platforms": ["blog", "linkedin"],
    }
    (tmp_path / ".pulsewriter.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        result = runner.invoke(app, ["last"]) 
        assert result.exit_code == 2
        msg = f"No Markdown posts found in {posts}"
        assert msg in result.stdout or msg in result.stderr

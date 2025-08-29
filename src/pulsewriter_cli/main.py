import typer
from pathlib import Path
from typing import List, Optional
import yaml
import sys
from pulsewriter_core import TransformConfig, generate, save_text, load_markdown

ALLOWED_PLATFORMS = {"blog", "linkedin", "x", "devto"}

app = typer.Typer(help="PulseWriter CLI — transform markdown into platform drafts.", no_args_is_help=True)


def _load_config() -> dict:
    """Load YAML config from CWD or user home. Returns dict with defaults applied."""
    defaults = {
        "posts_dir": "./_posts",
        "out_dir": "./out",
        "default_platforms": ["blog", "linkedin", "x", "devto"],
    }
    cfg_paths = [Path.cwd() / ".pulsewriter.yaml", Path.home() / ".pulsewriter.yaml"]
    data: dict = {}
    for p in cfg_paths:
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as fh:
                    loaded = yaml.safe_load(fh) or {}
                    if isinstance(loaded, dict):
                        data.update(loaded)
            except Exception as e:
                typer.secho(f"Failed to read config {p}: {e}", fg=typer.colors.RED, err=True)
                raise typer.Exit(code=1)
            break
    # apply defaults when missing
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data


def _normalize_path(path_value: str | Path) -> Path:
    p = Path(path_value)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


def get_latest_post(posts_dir: Path) -> Optional[Path]:
    """Return the most recently modified *.md file in posts_dir, or None if none."""
    try:
        if not posts_dir.exists():
            return None
        md_files = sorted(posts_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        return md_files[0] if md_files else None
    except Exception:
        return None


@app.command()
def transform(
    input_md: Path = typer.Argument(..., exists=True, readable=True, help="Input markdown file"),
    platforms: List[str] = typer.Option(["blog", "linkedin", "x", "devto"], help="Platforms to generate"),
    out_dir: Path = typer.Option(Path("./out"), help="Output directory"),
    tone: str = typer.Option("practical", help="Tone (meta, practical, inspiring...)"),
    persona: str = typer.Option("action-oriented", help="Persona label"),
    word_target: int = typer.Option(600, help="Target word count (hint)"),
):
    raw = load_markdown(input_md)
    cfg = TransformConfig(tone=tone, persona=persona, word_target=word_target)
    outputs = generate(raw, platforms, cfg)
    for k, v in outputs.items():
        ext = ".md" if k.endswith("_md") else ".txt"
        path = out_dir / f"{input_md.stem}.{k}{ext}"
        save_text(path, v)
        typer.echo(f"Wrote {path}")


@app.command()
def last(
    platforms: Optional[List[str]] = typer.Option(None, "--platforms", help="Platforms to generate; overrides config"),
    out_dir: Optional[Path] = typer.Option(None, "--out-dir", help="Output directory; overrides config"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be transformed without writing files"),
):
    """Transform the most recently modified Markdown file from posts_dir using config defaults."""
    try:
        cfg = _load_config()
        posts_dir = _normalize_path(cfg.get("posts_dir", "./_posts"))
        effective_out_dir = _normalize_path(out_dir) if out_dir is not None else _normalize_path(cfg.get("out_dir", "./out"))
        effective_platforms = platforms if platforms is not None else list(cfg.get("default_platforms", ["blog", "linkedin", "x", "devto"]))

        # Validate platforms for a friendlier message before core raises
        invalid = [p for p in effective_platforms if p not in ALLOWED_PLATFORMS]
        if invalid:
            allowed_str = ", ".join(sorted(ALLOWED_PLATFORMS))
            typer.secho(f"Invalid platform(s): {invalid}. Allowed: {allowed_str}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2)

        if not posts_dir.exists():
            typer.secho(
                f"Posts directory not found: {posts_dir}. Set 'posts_dir' in .pulsewriter.yaml.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=2)

        latest = get_latest_post(posts_dir)
        if latest is None:
            typer.secho(f"No Markdown posts found in {posts_dir}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2)

        if dry_run:
            typer.echo(
                f"Would transform: {latest.name} → platforms={effective_platforms} out_dir='{effective_out_dir}'"
            )
            return

        # Not dry-run: create out_dir if not exist
        try:
            effective_out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            typer.secho(f"Failed to create output dir {effective_out_dir}: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        raw = load_markdown(latest)
        outputs = generate(raw, effective_platforms, TransformConfig())
        for k, v in outputs.items():
            ext = ".md" if k.endswith("_md") else ".txt"
            path = effective_out_dir / f"{latest.stem}.{k}{ext}"
            save_text(path, v)
        typer.echo(
            f"Transformed: {latest.name} → platforms={effective_platforms} out_dir='{effective_out_dir}'"
        )
    except typer.Exit:
        raise
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

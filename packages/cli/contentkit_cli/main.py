import typer
from pathlib import Path
from typing import List
from contentkit_core import TransformConfig, generate, save_text, load_markdown

app = typer.Typer(help="contentkit CLI — transform a single markdown into platform drafts.")

@app.command()
def transform(
    input_md: Path = typer.Argument(..., exists=True, readable=True, help="Input markdown file"),
    platforms: List[str] = typer.Option(["blog","linkedin","x","devto"], help="Platforms to generate"),
    out_dir: Path = typer.Option(Path("./out"), help="Output directory"),
    tone: str = typer.Option("practical", help="Tone (meta, practical, inspiring...)"),
    persona: str = typer.Option("action-oriented", help="Persona label"),
    word_target: int = typer.Option(600, help="Target word count (hint)")
):
    raw = load_markdown(input_md)
    cfg = TransformConfig(tone=tone, persona=persona, word_target=word_target)
    outputs = generate(raw, platforms, cfg)
    for k, v in outputs.items():
        ext = ".md" if k.endswith("_md") else ".txt"
        path = out_dir / f"{input_md.stem}.{k}{ext}"
        save_text(path, v)
        typer.echo(f"Wrote {path}")

if __name__ == "__main__":
    app()

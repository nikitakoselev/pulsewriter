from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import yaml

TEMPLATES_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml", "md"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

@dataclass
class TransformConfig:
    tone: str = "practical"
    persona: str = "action-oriented"
    word_target: int = 600

def load_markdown(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")

def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _render(template_name: str, context: Dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

def _summarize(text: str, max_lines: int = 5) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[:max_lines])

def generate(
    base_markdown: str,
    platforms: List[str],
    config: Optional[TransformConfig] = None
) -> Dict[str, str]:
    cfg = config or TransformConfig()
    summary = _summarize(base_markdown, max_lines=5)

    outputs: Dict[str, str] = {}
    context = {
        "summary": summary,
        "body": base_markdown,
        "tone": cfg.tone,
        "persona": cfg.persona,
        "word_target": cfg.word_target,
    }

    for p in platforms:
        if p == "blog":
            outputs["blog_md"] = _render("blog.md.j2", context)
        elif p == "linkedin":
            outputs["linkedin_md"] = _render("linkedin.md.j2", context)
        elif p == "x":
            outputs["x_thread"] = _render("x_thread.txt.j2", context)
        elif p == "devto":
            outputs["devto_md"] = _render("devto.md.j2", context)
        else:
            raise ValueError(f"Unknown platform: {p}")
    return outputs

def revise(drafts: Dict[str, str], instructions: str) -> Dict[str, str]:
    # Extremely simple revision: append a note and tighten intro length
    revised = {}
    for k, v in drafts.items():
        if k.endswith("_md") or k.endswith("_thread"):
            lines = v.splitlines()
            if lines:
                lines[0] = lines[0][:120]
            revised[k] = "\n".join(lines) + f"\n\n<!-- Revised: {instructions} -->"
    return revised

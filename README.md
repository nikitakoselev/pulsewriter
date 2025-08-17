# PulseWriter (MVP)

**Goal:** Write once → generate platform-ready drafts (blog, LinkedIn, X, Dev.to).  
Architecture: **open core** (transforms & templates) + **CLI** + **HTTP API**.  
This MVP intentionally keeps logic simple (template-based) so you can ship fast; you can later plug in LLM calls inside the core.

## Quick start

### 1. Create and activate a virtual environment

**macOS / Linux (bash or zsh)**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
python -m venv .venv
\.venv\Scripts\activate.bat
```

### 2. Install dependencies

**macOS / Linux**

```bash
pip install -e .[dev]
```

**Windows PowerShell**

```powershell
pip install -e ".[dev]"
```

**Windows CMD**

```cmd
pip install -e .[dev]
```

### 3. Run the CLI

```bash
pulsewriter --help
pulsewriter examples/input.md --platforms linkedin --platforms x --platforms devto --out-dir ./out
```

### 4. Run the API

```bash
uvicorn pulsewriter_api.main:app --reload
# POST /generate with JSON: {"topic":"Impact to Cashflow","platforms":["blog","linkedin","x"]}
```

## Project layout

```
src/
  pulsewriter_core/         # Open core: transforms, templates, validators
  pulsewriter_cli/          # Typer CLI (calls core)
  pulsewriter_api/          # FastAPI (calls core)
examples/                       # Sample input & config
recipes/n8n/                    # (Optional) n8n workflow stubs
tests/                          # Test suite
connectors/                     # Optional helper modules
```

## License

Source-available under **BUSL-1.1 (Business Source License)**. See `LICENSE` and `COMMERCIAL_LICENSE.md` for terms.  
You may run, modify, and use non-production internally. **Production/commercial use** requires a commercial license from the author.

## Roadmap
- v0.1: template transforms (this MVP)
- v0.2: add optional LLM augment in core (behind a flag)
- v0.3: connectors (Buffer/Notion/GitHub PR helper)
- v0.4: n8n nodes + Telegram bot adapter


---
## Blog strategy
- Primary hub: **https://nikitakoselev.github.io/**
- All free materials should point back to the blog for full versions.
- Use `config/blog.yaml` to target the GitHub Pages repo and posts directory.

## Feature-driven development
See **FEATURES.md** for a prioritized backlog, status, and Copilot-ready tasks.

---
PulseWriter is part of Nikita Koselev's open-core journey. For full articles, see [nikitakoselev.github.io](https://nikitakoselev.github.io/).

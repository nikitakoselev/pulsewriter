# Feature Backlog & Status

Status: 🟢 Ready · 🟡 In Progress · 🔴 Blocked · ✅ Done

| ID | Feature | Status | Notes / Acceptance Criteria | Owner |
|----|---------|--------|-----------------------------|-------|
| F-001 | CLI: transform markdown → blog/LinkedIn/X/Dev.to | ✅ | `pulsewriter` writes files to /out | core |
| F-002 | API: `/generate` + `/revise` | ✅ | Accepts `topic` or `body_markdown`, returns drafts | api |
| F-003 | Templates: tone/persona system | ✅ | Jinja templates parametrize `{tone, persona, word_target}` | core |
| F-004 | GitHub PR helper (blog repo) | 🟢 | Function: create branch, commit file, open PR to `nikitakoselev/nikitakoselev.github.io` | connectors |
| F-005 | n8n recipe: Cron → /generate → PR → Telegram approve | 🟢 | JSON export + README steps | recipes |
| F-006 | Buffer/Typefully draft push | 🟢 | Post generated LinkedIn/X drafts to scheduler (no publish) | connectors |
| F-007 | Config-driven “recipe” YAML | 🟢 | Single `recipe.yaml` defines sources, platforms, outputs | core |
| F-008 | Quality gates | 🟡 | Min length, section check, basic anti-hallucination guard | core |
| F-009 | Awareness agent (alerts) | 🟢 | Separate package `packages/awareness` with /watch endpoints | awareness |
| F-010 | Telegram approve loop | 🟢 | Callback handler + n8n wiring, human-in-the-loop | adapters |

## Copilot-Ready Tasks

### F-004 GitHub PR helper
- [ ] Create module `packages/connectors/github_pr.py`
- [ ] Read `GH_TOKEN` from env
- [ ] Function `open_pr(repo, branch, path, content, pr_title, pr_body)`:
  - Create branch from default
  - Add/commit `path` with `content`
  - Push branch
  - Open PR
- [ ] Return PR URL

### F-008 Quality gates
- [ ] Implement `core/validators.py`:
  - `require_sections(body, ["Why", "What", "How"])`
  - `min_words(body, 300)`
- [ ] Call validators in `generate()`; if fail, return `needs_review=true`

### F-010 Telegram approve loop
- [ ] Add `/finalize` endpoint in API
- [ ] Draft `adapters/telegram/README.md` with bot token + webhook setup
- [ ] n8n: on callback `approve:{draft_id}` → call connectors.github_pr to open PR

### F-009 Awareness agent (new package)
- [ ] Create `packages/awareness/` with `watch.py`
- [ ] `/watch` endpoint accepts keywords/sources and returns new items
- [ ] n8n recipe: daily watch → Telegram digest


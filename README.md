# aicc — AI Coding Companion

A **minimal** desktop agent for the repository on your machine: chat, an approval-gated tool loop, git, and just enough UI to work in the tree—not a full IDE.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)

## Quick start

```bash
git clone https://github.com/nadav-yo/aicc
cd aicc
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Keys can also be set in **Settings → Models**. Requires Python 3.11+, PyQt6, `anthropic`, `openai`, `markdown`, `pygments`.

## What it does

Open a workspace folder, pick a model, and work in one window:

- **Chat** — streaming Markdown, vision, `@file` mentions, edit/resend, branch, queue while busy
- **Agent** — `read_file`, `edit_file`, `bash`, `search_files`; parallel reads; you approve edits (once per chat) and each shell command
- **Repo** — file tree, syntax-highlighted tabs, git status/diffs, `AGENTS.md` in the system prompt
- **Context** — usage ring, breakdown, auto-compaction
- **Extras** — `/` skills, `Cmd+K` palette, themes, export/pin/search history

Paths stay inside the workspace for read/search. Shell runs as your user—not a sandbox.

## Documentation

| Topic | |
|---|---|
| Custom providers (Gemini, Ollama, …) | [docs/custom-models.md](docs/custom-models.md) |
| Slash-command skills | [docs/skills.md](docs/skills.md) |
| Settings file | [docs/configuration.md](docs/configuration.md) |
| Feature backlog | [features.md](features.md) |

## License

Copyright © 2026 AI Coding Companion. [MIT License](https://opensource.org/licenses/MIT).

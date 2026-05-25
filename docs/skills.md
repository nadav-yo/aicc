# Skills (slash commands)

aicc skills follow the ideas behind **[Agent Skills](https://agentskills.io/)** — an open format for giving agents specialized instructions ([overview](https://agentskills.io/home), [specification](https://agentskills.io/specification)). Here each skill is a single Markdown file with YAML frontmatter (not a `SKILL.md` folder), loaded from `~/.aicc/skills/` and `.aicc/skills/`.

Type `/` in the composer to pick a skill. It replaces the base system prompt for that turn. You can optionally restrict which tools the model may call.

## Locations

| Path | Scope |
|---|---|
| `~/.aicc/skills/*.md` | User-global |
| `.aicc/skills/*.md` | Project-local (same name overrides global) |

## File format

```markdown
---
name: review
description: Code review focused on correctness and security
tools: [read_file, search_files]
---
You are a senior reviewer. Read the relevant files, then give a concise report:
bugs, edge cases, and one concrete fix per issue. Do not edit files unless asked.
```

| Frontmatter key | Required | Description |
|---|---|---|
| `name` | no | Slash-command name (defaults to filename without `.md`) |
| `description` | no | Shown in the skill picker |
| `tools` | no | Allowlist of tool names; omit to allow all tools |

Valid tool names: `read_file`, `edit_file`, `bash`, `search_files`.

The body (after the closing `---`) is the skill system prompt for the selected turn.

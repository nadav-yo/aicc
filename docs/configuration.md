# Configuration

Settings are stored in `~/.aicc/settings.json` (written by **Settings** in the app).

| Key | Description |
|---|---|
| `anthropic_api_key` | Fallback if `ANTHROPIC_API_KEY` is unset |
| `openai_api_key` | Fallback if `OPENAI_API_KEY` is unset |
| `provider_api_keys` | Per-provider keys for built-in and custom providers |
| `system_prompt` | Overrides the default system prompt |
| `default_models` | Default model per provider |
| `theme` | `"dark"`, `"modern"`, or `"light"` |
| `font_size` | Chat font size (pt) |

API keys can also be set via environment variables or **Settings → Models** before launch.

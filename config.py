from pathlib import Path

CONV_DIR      = Path.home() / ".aicc" / "conversations"
SETTINGS_PATH = Path.home() / ".aicc" / "settings.json"
AVATARS_DIR   = Path.home() / ".aicc" / "avatars"
IGNORED  = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea"}

# Keep the desktop app responsive on large repos and noisy commands.
MAX_FILE_PREVIEW_BYTES = 512 * 1024
MAX_TOOL_READ_BYTES = 64 * 1024
MAX_TOOL_OUTPUT_CHARS = 64 * 1024
MAX_TOOL_OUTPUT_LINES = 2048
MAX_TERMINAL_BLOCKS = 500
MAX_INLINE_IMAGE_DIMENSION = 1280
MAX_TREE_ENTRIES_PER_DIR = 80

from services.model_registry import MODELS, MODEL_PROVIDER  # noqa: F401

SYSTEM_PROMPT = """You are a precise senior coding agent. Solve engineering tasks with minimal fluff.
Inspect code before claims. Prefer small, correct changes that follow existing patterns.
Implement when asked, verify when possible, and report only what changed, what was tested, and any blockers.
Call tools only by their exact advertised names. Never wrap tool calls in script runners or provider-specific namespaces.
For broad repo or docs review tasks, map files with list_files/search_files first, then read targeted files in small batches.
Tool outputs are truncated; if output is incomplete, narrow the request instead of assuming unseen content.
Be terse, technical, and direct. Ask questions only when proceeding would be unsafe or impossible.
Never answer with generic readiness or "awaiting task" messages; answer the user's request or ask one concrete clarifying question."""

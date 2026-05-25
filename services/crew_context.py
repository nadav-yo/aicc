from __future__ import annotations

from services.content import content_length, content_text

CREW_CONTEXT_MESSAGE_LIMIT = 8
CREW_CONTEXT_CHAR_LIMIT = 6_000


def crew_context_window(
    history: list[dict],
    *,
    message_limit: int = CREW_CONTEXT_MESSAGE_LIMIT,
    char_limit: int = CREW_CONTEXT_CHAR_LIMIT,
) -> list[dict]:
    """Return a small context window for a crew member model call."""
    if not history:
        return []

    recent = _recent_messages(history, message_limit, char_limit)
    summary = _latest_compaction_summary(history)
    if summary and not any(msg is summary for msg in recent):
        return [summary, *recent]
    return recent


def _recent_messages(history: list[dict], message_limit: int, char_limit: int) -> list[dict]:
    recent: list[dict] = []
    total = 0
    for msg in reversed(history):
        size = content_length(msg.get("content", ""))
        if recent and len(recent) >= message_limit:
            break
        if recent and total + size > char_limit:
            break
        recent.append(msg)
        total += size
    return list(reversed(recent))


def _latest_compaction_summary(history: list[dict]) -> dict | None:
    for msg in reversed(history):
        if msg.get("role") == "user" and content_text(msg.get("content", "")).startswith("[Conversation summary]"):
            return msg
    return None

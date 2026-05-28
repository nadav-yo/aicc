from __future__ import annotations

import json
import re

AICHS_MESSAGE_COPY_MIME = "application/x-aichs-message-copy"
MAX_CLIPBOARD_FILE_REFS = 20

_PATH_RE = re.compile(
    r"(?<![\w@./\\-])"
    r"(?P<path>[\w./\\-]+\."
    r"(?:py|md|json|yaml|yml|toml|sh|js|ts|tsx|jsx|css|html|txt|rs|go|java|c|cpp|h|hpp|cs|php|rb|swift|kt|sql|xml|ini))"
    r"(?![\w/\\-]|\.[A-Za-z0-9])",
    re.IGNORECASE,
)


def file_refs_payload(text: str) -> bytes:
    refs = file_ref_candidates(text)
    return json.dumps(
        {"kind": "aichs-copy", "file_refs": refs},
        separators=(",", ":"),
    ).encode("utf-8")


def file_ref_candidates(text: str) -> list[str]:
    return [ref for _start, _end, ref in file_ref_spans(text)]


def file_ref_spans(text: str) -> list[tuple[int, int, str]]:
    seen: set[str] = set()
    spans: list[tuple[int, int, str]] = []
    for match in _PATH_RE.finditer(str(text or "")):
        ref = _clean_ref(match.group("path"))
        if not ref or ref in seen:
            continue
        seen.add(ref)
        spans.append((match.start("path"), match.end("path"), ref))
        if len(spans) >= MAX_CLIPBOARD_FILE_REFS:
            break
    return spans


def parse_file_refs_payload(raw: bytes | bytearray | memoryview) -> list[str]:
    try:
        data = json.loads(bytes(raw).decode("utf-8"))
    except Exception:
        return []
    if not isinstance(data, dict) or data.get("kind") != "aichs-copy":
        return []
    refs = data.get("file_refs")
    if not isinstance(refs, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        cleaned = _clean_ref(str(ref or ""))
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            out.append(cleaned)
            if len(out) >= MAX_CLIPBOARD_FILE_REFS:
                break
    return out


def _clean_ref(ref: str) -> str:
    ref = str(ref or "").strip().strip("`'\"")
    ref = ref.rstrip(".,:;)]}")
    while ref.startswith("./"):
        ref = ref[2:]
    return ref

"""Render unified diff text as themed HTML for QTextEdit."""

from __future__ import annotations

import html

from ui.theme import ACCENT, MONO_FONT_CSS, current_theme, mono_font_pt, palette


def diff_to_html(unified_diff: str, theme: str | None = None) -> str:
    p = palette(theme)
    fs = mono_font_pt()
    bg = p["BG3"]
    add_bg = p["SUCCESS_BG"]
    add_fg = p["SUCCESS"]
    del_bg = "#2a1518" if current_theme() != "light" else "#fef2f2"
    del_fg = "#f87171"
    meta = p["TEXT_DIM"]

    rows: list[str] = []
    for line in unified_diff.splitlines():
        esc = html.escape(line)
        if line.startswith("+++") or line.startswith("---"):
            style = f"color:{meta};"
        elif line.startswith("@@"):
            style = f"color:{ACCENT};"
        elif line.startswith("+"):
            style = f"background:{add_bg}; color:{add_fg};"
        elif line.startswith("-"):
            style = f"background:{del_bg}; color:{del_fg};"
        else:
            style = f"color:{p['TEXT']};"
        rows.append(f'<div style="{style} white-space:pre;">{esc}</div>')

    body = "\n".join(rows) if rows else f'<div style="color:{meta};">(no differences)</div>'
    return (
        f'<pre style="font-family:{MONO_FONT_CSS}; font-size:{fs}px; line-height:1.5;'
        f'margin:0; padding:12px; background:{bg};">{body}</pre>'
    )

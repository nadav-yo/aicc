from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.tool_registry import (
    ExtensionFileSummary,
    ExtensionOverview,
    extension_overview,
    set_extension_enabled,
)
from ui.theme import palette, chat_font_pt, meta_font_pt, icon_button_style


class ExtensionsDialog(QDialog):
    def __init__(
        self,
        overview_or_cwd: ExtensionOverview | str,
        parent=None,
        on_reload=None,
    ):
        super().__init__(parent)
        self._cwd = overview_or_cwd if isinstance(overview_or_cwd, str) else ""
        self._overview = (
            extension_overview(self._cwd)
            if isinstance(overview_or_cwd, str)
            else overview_or_cwd
        )
        self._on_reload = on_reload
        self._selected_path = ""
        self._detail_mode = "placeholder"
        self.setWindowTitle("Extensions")
        self.resize(900, 620)

        p = palette()
        self.setStyleSheet(
            f"QDialog {{ background:{p['BG2']}; color:{p['TEXT']}; }}"
            f"QScrollArea {{ background:{p['BG2']}; border:none; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        title = QLabel("Extensions")
        title.setStyleSheet(
            f"font-size:{chat_font_pt() + 2}px; font-weight:600; color:{p['TEXT']};"
        )
        title_row.addWidget(title)
        title_row.addStretch()

        api_btn = QPushButton("API Reference")
        api_btn.setToolTip("Inspect the extension API reference")
        api_btn.setStyleSheet(_secondary_button_style())
        api_btn.clicked.connect(self._show_api_reference)
        title_row.addWidget(api_btn)

        reload_btn = QPushButton("↻")
        reload_btn.setToolTip("Reload extensions")
        reload_btn.setFixedSize(30, 30)
        reload_btn.setStyleSheet(icon_button_style(30))
        reload_btn.clicked.connect(self._reload)
        title_row.addWidget(reload_btn)
        root.addLayout(title_row)

        self._summary = QLabel()
        self._summary.setStyleSheet(f"color:{p['TEXT_DIM']}; font-size:{meta_font_pt()}px;")
        root.addWidget(self._summary)

        content = QHBoxLayout()
        content.setContentsMargins(0, 2, 0, 0)
        content.setSpacing(14)
        root.addLayout(content, 1)

        self._list_scroll = QScrollArea()
        self._list_scroll.setWidgetResizable(True)
        self._list_scroll.setFixedWidth(330)
        self._list_scroll.setStyleSheet(_list_scroll_style())
        self._list_body = QWidget()
        self._list_layout = QVBoxLayout(self._list_body)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(1)
        self._list_scroll.setWidget(self._list_body)
        content.addWidget(self._list_scroll)

        self._detail_scroll = QScrollArea()
        self._detail_scroll.setWidgetResizable(True)
        self._detail_scroll.setStyleSheet(_detail_scroll_style())
        content.addWidget(self._detail_scroll, 1)

        self._render()

    def _reload(self):
        if self._cwd:
            self._overview = extension_overview(self._cwd)
        if self._on_reload:
            self._on_reload()
        self._render()

    def _set_enabled(self, path: str, enabled: bool):
        set_extension_enabled(path, enabled, self._cwd or None)
        self._reload()

    def _render(self):
        overview = self._overview
        self._summary.setText(_summary_text(overview))
        _clear_layout(self._list_layout)
        if overview.files:
            selected = _find_file(overview, self._selected_path) if self._selected_path else None
            if self._selected_path and selected is None:
                self._selected_path = ""
                if self._detail_mode != "api":
                    self._detail_mode = "placeholder"
            if not self._selected_path and self._detail_mode != "api":
                selected = overview.files[0]
                self._selected_path = selected.path
                self._detail_mode = "detail"
            for file in overview.files:
                row = _ExtensionListRow(
                    file,
                    selected=file.path == self._selected_path,
                    on_toggle=self._set_enabled,
                    on_select=self._show_file_detail,
                )
                self._list_layout.addWidget(row)
            if self._detail_mode == "api":
                self._detail_scroll.setWidget(_ApiReferencePane())
            elif selected:
                self._detail_scroll.setWidget(_ExtensionDetailPane(selected, on_toggle=self._set_enabled))
            else:
                self._show_placeholder()
        else:
            self._list_layout.addWidget(_EmptyList())
            self._show_placeholder()
        self._list_layout.addStretch()

    def _show_file_detail(
        self,
        file: ExtensionFileSummary,
        *,
        rerender_list: bool = True,
    ) -> None:
        self._selected_path = file.path
        self._detail_mode = "detail"
        self._detail_scroll.setWidget(_ExtensionDetailPane(file, on_toggle=self._set_enabled))
        if rerender_list:
            self._render()

    def _show_api_reference(self) -> None:
        self._selected_path = ""
        self._detail_mode = "api"
        self._render()

    def _show_placeholder(self) -> None:
        self._detail_mode = "placeholder"
        self._detail_scroll.setWidget(_PlaceholderPane())


class _ExtensionListRow(QFrame):
    def __init__(
        self,
        file: ExtensionFileSummary,
        *,
        selected: bool,
        parent=None,
        on_toggle=None,
        on_select=None,
    ):
        super().__init__(parent)
        self._file = file
        self._on_select = on_select
        self.setObjectName("extensionListRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(_list_row_style(selected, _status_tone(file)))
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(3)

        name = QLabel(_extension_name(file))
        name.setWordWrap(True)
        name.setStyleSheet(_list_name_style())
        layout.addWidget(name, 0, 0)

        status = QLabel(_list_status_text(file))
        status.setStyleSheet(_list_meta_style(_status_tone(file)))
        layout.addWidget(status, 0, 1, Qt.AlignmentFlag.AlignRight)

        meta = QLabel(_list_subtitle(file))
        meta.setWordWrap(True)
        meta.setStyleSheet(_list_path_style())
        layout.addWidget(meta, 1, 0, 1, 2)

        enabled = file.status != "Disabled"
        checkbox = QCheckBox("Enabled")
        checkbox.setChecked(enabled)
        checkbox.setToolTip(
            "Extension is enabled" if enabled else "Extension is disabled"
        )
        checkbox.setStyleSheet(_enabled_checkbox_style())
        checkbox.toggled.connect(
            lambda checked, path=file.path:
                on_toggle and on_toggle(path, bool(checked))
        )
        layout.addWidget(checkbox, 2, 0, Qt.AlignmentFlag.AlignLeft)

    def mousePressEvent(self, event):
        if self._on_select:
            self._on_select(self._file)
        super().mousePressEvent(event)


class _ExtensionDetailPane(QWidget):
    def __init__(self, file: ExtensionFileSummary, parent=None, on_toggle=None):
        super().__init__(parent)
        self._on_toggle = on_toggle
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._add_header(root, file)
        self._add_description(root, file)
        _add_detail_section(
            root,
            "Tools",
            [
                (
                    tool.name,
                    _join_details(
                        tool.description,
                        "parallel safe" if tool.parallel_safe else "",
                        f"approval: {tool.approval}" if tool.approval else "",
                    ),
                )
                for tool in file.tools
            ],
        )
        _add_detail_section(
            root,
            "Slash Commands",
            [
                (
                    f"/{command.name}",
                    _join_details(
                        command.description,
                        "executable" if command.executable else "prompt mode",
                        f"capabilities: {', '.join(command.capabilities)}" if command.capabilities else "",
                        f"tools: {', '.join(command.tools)}" if command.tools else "tools: all",
                    ),
                )
                for command in file.commands
            ],
        )
        _add_detail_section(
            root,
            "Context",
            [(name, "Injected into workspace context") for name in file.contexts],
        )
        _add_detail_section(
            root,
            "Hooks",
            [(name, "Lifecycle hook") for name in file.hooks],
        )
        ui_rows = [(badge.name, "Status badge") for badge in file.badges]
        ui_rows += [(panel.name, f"Panel: {panel.title}") for panel in file.panels]
        _add_detail_section(root, "UI Contributions", ui_rows)
        _add_detail_section(
            root,
            "Errors",
            [(error, "") for error in file.errors],
            tone="danger",
        )
        root.addStretch()

    def _add_header(self, root: QVBoxLayout, file: ExtensionFileSummary) -> None:
        p = palette()
        header = QFrame()
        header.setObjectName("extensionHeader")
        header.setStyleSheet(_header_style())
        layout = QGridLayout(header)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)

        title = QLabel(_extension_name(file))
        title.setWordWrap(True)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        title.setStyleSheet(
            f"font-size:{chat_font_pt() + 4}px; font-weight:650; color:{p['TEXT']};"
        )
        layout.addWidget(title, 0, 0)

        status = QLabel(file.status)
        status.setStyleSheet(_status_label_style(_status_tone(file)))
        layout.addWidget(status, 0, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        path = QLabel(file.path)
        path.setWordWrap(True)
        path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path.setStyleSheet(f"color:{p['TEXT_DIM']}; font-size:{meta_font_pt()}px;")
        layout.addWidget(path, 1, 0, 1, 2)

        enabled = file.status != "Disabled"
        checkbox = QCheckBox("Enabled")
        checkbox.setChecked(enabled)
        checkbox.setStyleSheet(_enabled_checkbox_style())
        checkbox.toggled.connect(
            lambda checked, path=file.path:
                self._on_toggle and self._on_toggle(path, bool(checked))
        )
        layout.addWidget(checkbox, 2, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        root.addWidget(header)

    def _add_description(self, root: QVBoxLayout, file: ExtensionFileSummary) -> None:
        if not file.description:
            return
        p = palette()
        label = QLabel(file.description)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet(
            f"color:{p['TEXT']}; background:transparent;"
            f"border-left:2px solid {p['BORDER']}; padding:0 0 0 10px;"
        )
        root.addWidget(label)


class _EmptyList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p = palette()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel("No extension files found.")
        label.setStyleSheet(f"color:{p['TEXT_DIM']};")
        layout.addWidget(label)
        layout.addStretch()


class _PlaceholderPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p = palette()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        label = QLabel("No extension selected.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color:{p['TEXT_DIM']};")
        layout.addWidget(label)
        layout.addStretch()


class _ApiReferencePane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel("API Reference")
        title.setStyleSheet(_pane_title_style())
        layout.addWidget(title)

        intro = QLabel(
            "Extensions return structured data. aichs owns the widgets, layout, "
            "and styling, so extension UI stays predictable."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(_intro_style())
        layout.addWidget(intro)

        _add_api_section(layout, "What UI Extensions Can Do", [
            (
                "metadata",
                "Adds a short extension description shown near status in the Extensions dialog.",
            ),
            (
                "status_badge",
                "Adds a small top-bar badge. The badge can open a registered panel.",
            ),
            (
                "panel",
                "Adds a structured read-only dialog rendered by aichs.",
            ),
            (
                "Extensions view",
                "Shows loaded extension files and their registered contributions.",
            ),
        ])
        _add_api_section(layout, "Provider Context", [
            ("ctx.cwd", "Current workspace path."),
            ("ctx.model", "Currently selected model id."),
            ("ctx.history", "Current conversation history visible to the chat panel."),
            ("ctx.extension_id", "Safe id derived from the extension filename."),
            ("ctx.storage.load_config(scope)", "Load project/global extension JSON config."),
            ("ctx.storage.save_config(data, scope)", "Save project/global extension JSON config."),
            ("ctx.storage.load_state(name)", "Load project-scoped extension JSON state."),
            ("ctx.storage.save_state(data, name)", "Save project-scoped extension JSON state."),
            ("ctx.processes", "Managed process API when available to UI providers."),
        ])
        _add_api_section(layout, "Tool Context", [
            ("ctx.cwd", "Current workspace path."),
            ("ctx.on_line", "Optional callback for streaming command-like output."),
            ("ctx.cancel", "Cancellation event."),
            ("ctx.is_cancelled()", "Convenience cancellation check."),
            ("ctx.extension_id", "Safe id derived from the extension filename."),
            ("ctx.storage.load_config(scope)", "Load project/global extension JSON config."),
            ("ctx.storage.save_config(data, scope)", "Save project/global extension JSON config."),
            ("ctx.storage.load_state(name)", "Load project-scoped extension JSON state."),
            ("ctx.storage.save_state(data, name)", "Save project-scoped extension JSON state."),
        ])
        _add_api_section(layout, "Executable Command Context", [
            ("ctx.cwd", "Current workspace path."),
            ("ctx.model", "Selected model id."),
            ("ctx.history", "Current visible conversation history."),
            ("ctx.conversation_id", "Current conversation id, when available."),
            ("ctx.command", "Command name being executed."),
            ("ctx.extension_id", "Safe id derived from the extension filename."),
            ("ctx.storage.load_config(scope)", "Load project/global extension JSON config."),
            ("ctx.storage.save_config(data, scope)", "Save project/global extension JSON config."),
            ("ctx.storage.load_state(name)", "Load project conversation-scoped JSON state."),
            ("ctx.storage.save_state(data, name)", "Save project conversation-scoped JSON state."),
            ("ctx.runtime.notice(text)", "Show a center notice."),
            ("ctx.runtime.send(text)", "Send now, or queue if a run is active."),
            ("ctx.runtime.enqueue(text)", "Queue a normal chat message."),
            ("ctx.runtime.compact(force=True)", "Request normal compaction."),
            ("ctx.runtime.continue_after_compact(prompt, force=True)", "Queue a synthetic resume after compaction."),
            ("ctx.runtime.processes.start(name, command, ...)", "Start a managed long-running process."),
            ("ctx.runtime.processes.status(name)", "Inspect managed process state."),
            ("ctx.runtime.processes.tail(name, lines)", "Read recent process output."),
            ("ctx.runtime.processes.write(name, text)", "Write to process stdin when enabled."),
            ("ctx.runtime.processes.stop(name)", "Stop a managed process."),
        ])
        _add_api_section(layout, "Extension Metadata", [
            (
                "registry.metadata(description=...)",
                "Sets the description after the extension loads.",
            ),
            (
                "EXTENSION_DESCRIPTION",
                "Static fallback used even while the extension is disabled.",
            ),
            (
                "EXTENSION = {'description': ...}",
                "Alternative static fallback.",
            ),
            ("module docstring", "Last-resort static fallback."),
        ])
        _add_api_section(layout, "Runtime Hook Directives", [
            ("show_notice", "Show a notice in the active chat."),
            ("enqueue_message", "Queue a normal user message."),
            ("compact_now", "Request app-owned compaction at a safe boundary."),
            ("compact_and_resume", "Compact and queue a synthetic continuation prompt."),
            ("ledger", "Optional directive flag requiring continuation-ledger validation."),
            ("ctx.process", "Process event payload for process_started and process_exited hooks."),
        ])
        _add_api_section(layout, "Status Badge Schema", [
            (
                "registry.status_badge(name, provider)",
                "Registers a top-bar badge provider.",
            ),
            ("label", "Required button text."),
            ("tooltip", "Optional hover text."),
            (
                "tone",
                "Optional: success, danger, warning, accent.",
            ),
            ("panel", "Optional panel name to open. Defaults to the badge name."),
            ("visible", "Set to False to hide the badge."),
        ])
        _add_api_section(layout, "Panel Provider Schema", [
            ("registry.panel(name, title, provider)", "Registers a structured panel."),
            ("title", "Optional panel heading."),
            ("body", "Optional text before sections."),
            ("sections", "Optional list of section objects or strings."),
        ])
        _add_api_section(layout, "Section Schema", [
            ("heading", "Optional section heading."),
            ("body", "Optional text before section items."),
            ("items", "Optional list of item objects or strings."),
        ])
        _add_api_section(layout, "Item Schema", [
            ("title", "Primary row text. Defaults to Item."),
            ("subtitle", "Optional secondary text."),
            ("body", "Optional detail text."),
            ("action", "Optional single action object."),
            ("actions", "Optional list of action objects."),
        ])
        _add_api_section(layout, "Action Schema", [
            ("label", "Button text. Defaults to the action type."),
            ("type", "Supported: open_file, copy, refresh_panel, send_message, run_extension_command."),
            ("path", "For open_file: workspace-relative path."),
            ("text", "For copy or send_message."),
            ("command", "For run_extension_command: executable extension command name."),
            ("args", "For run_extension_command: command arguments."),
            ("refresh", "If true, refreshes the panel after the action runs."),
            ("refresh_panel", "Re-runs the provider and redraws the current panel."),
            ("send_message", "Sends or queues text like a normal user message."),
            ("run_extension_command", "Runs an executable extension command without adding a chat message."),
        ])
        _add_api_section(layout, "String Shortcuts", [
            ("panel returns a string", "Rendered as body text."),
            ("section is a string", "Rendered as body text."),
            ("item is a string", "Rendered as a single card title."),
        ])
        _add_api_section(layout, "Currently Unsupported", [
            ("tool-running buttons", ""),
            ("file links inside text", ""),
            ("custom row colors or icons", ""),
            ("arbitrary PyQt widgets", ""),
            ("HTML or Markdown rendering", ""),
        ])
        layout.addStretch()


def _add_api_section(layout: QVBoxLayout, heading: str, rows: list[tuple[str, str]]) -> None:
    _add_detail_section(layout, heading, rows)


def _add_detail_section(
    layout: QVBoxLayout,
    heading: str,
    rows: list[tuple[str, str]],
    *,
    tone: str = "",
) -> None:
    if not rows:
        return
    label = QLabel(heading)
    label.setStyleSheet(_heading_style(tone))
    layout.addWidget(label)

    table = QFrame()
    table.setObjectName("extensionDetailTable")
    table.setStyleSheet(_detail_table_style(tone))
    grid = QGridLayout(table)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(18)
    grid.setVerticalSpacing(0)

    for row, (name, description) in enumerate(rows):
        name_label = QLabel(name)
        name_label.setWordWrap(True)
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        name_label.setStyleSheet(_detail_name_style(tone))
        name_label.setContentsMargins(0, 8 if row else 0, 0, 8)
        grid.addWidget(name_label, row, 0, Qt.AlignmentFlag.AlignTop)

        desc_label = QLabel(description or "-")
        desc_label.setWordWrap(True)
        desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        desc_label.setStyleSheet(_detail_value_style(tone))
        desc_label.setContentsMargins(0, 8 if row else 0, 0, 8)
        grid.addWidget(desc_label, row, 1)

    grid.setColumnStretch(1, 1)
    layout.addWidget(table)


def _summary_text(overview: ExtensionOverview) -> str:
    count = len(overview.files)
    noun = "file" if count == 1 else "files"
    errors = overview.error_count
    disabled = sum(1 for file in overview.files if file.status == "Disabled")
    parts = [f"{count} extension {noun}"]
    parts.append(f"{errors} error(s)" if errors else "no errors")
    if disabled:
        parts.append(f"{disabled} disabled")
    return " · ".join(parts)


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def _find_file(
    overview: ExtensionOverview,
    path: str,
) -> ExtensionFileSummary | None:
    return next((file for file in overview.files if file.path == path), None)


def _extension_name(file: ExtensionFileSummary) -> str:
    return Path(file.path).name


def _list_status_text(file: ExtensionFileSummary) -> str:
    if file.errors:
        return f"{file.status} · {len(file.errors)} error(s)"
    return file.status


def _list_subtitle(file: ExtensionFileSummary) -> str:
    counts = [
        (len(file.tools), "tool"),
        (len(file.commands), "command"),
        (len(file.contexts), "context"),
        (len(file.hooks), "hook"),
        (len(file.badges) + len(file.panels), "UI"),
    ]
    parts = [
        f"{count} {label}{'' if count == 1 or label == 'UI' else 's'}"
        for count, label in counts
        if count
    ]
    if not parts:
        parts.append("No registered contributions")
    if file.description:
        parts.append(file.description)
    return " · ".join(parts)


def _tab_title(file: ExtensionFileSummary) -> str:
    name = Path(file.path).name
    if file.status == "Disabled":
        return f"Disabled · {name}"
    return f"! {name}" if file.errors else name


def _tab_tooltip(file: ExtensionFileSummary) -> str:
    suffix = f"\n\n{file.description}" if file.description else ""
    if file.status == "Disabled":
        return (
            "Disabled. This extension is visible here but does not register contributions."
            f"{suffix}"
        )
    if file.errors:
        return f"Failed to load. Open this tab to inspect errors.{suffix}"
    return f"Loaded.{suffix}"


def _tab_text_color(file: ExtensionFileSummary) -> str:
    p = palette()
    if file.status == "Disabled":
        return p["TEXT_DIM"]
    if file.errors:
        return "#f87171"
    return p["TEXT"]


def _join_details(*parts: str) -> str:
    return " | ".join(part for part in parts if part)


def _heading_style(tone: str = "") -> str:
    p = palette()
    color = "#f87171" if tone == "danger" else p["TEXT_DIM"]
    return (
        f"color:{color}; font-size:{meta_font_pt()}px;"
        "font-weight:600;"
    )


def _pane_title_style() -> str:
    p = palette()
    return f"font-size:{chat_font_pt() + 4}px; font-weight:650; color:{p['TEXT']};"


def _intro_style() -> str:
    p = palette()
    return (
        f"color:{p['TEXT']}; background:transparent;"
        f"border-left:2px solid {p['BORDER']}; padding:0 0 0 10px;"
    )


def _list_scroll_style() -> str:
    p = palette()
    return (
        f"QScrollArea {{ background:{p['BG2']}; border-right:1px solid {p['BORDER_SUBTLE']}; }}"
    )


def _detail_scroll_style() -> str:
    p = palette()
    return (
        f"QScrollArea {{ background:{p['BG2']}; border:none; }}"
        f"QScrollArea QWidget {{ background:{p['BG2']}; }}"
    )


def _list_row_style(selected: bool, tone: str) -> str:
    p = palette()
    bg = p["SELECTION"] if selected else p["BG2"]
    hover = p["SELECTION"] if selected else p["BG3"]
    border = {
        "danger": "#5f252d",
        "disabled": p["BORDER_SUBTLE"],
    }.get(tone, p["BORDER_SUBTLE"])
    return (
        f"QFrame#extensionListRow {{ background:{bg};"
        f"border-bottom:1px solid {border}; border-radius:0; }}"
        f"QFrame#extensionListRow:hover {{ background:{hover}; }}"
    )


def _list_name_style() -> str:
    p = palette()
    return f"color:{p['TEXT']}; font-weight:600;"


def _list_meta_style(tone: str) -> str:
    p = palette()
    color = {
        "danger": "#f87171",
        "disabled": p["TEXT_DIM"],
        "success": p["SUCCESS"],
    }.get(tone, p["TEXT_DIM"])
    return f"color:{color}; font-size:{meta_font_pt()}px; font-weight:600;"


def _list_path_style() -> str:
    p = palette()
    return f"color:{p['TEXT_DIM']}; font-size:{meta_font_pt()}px;"


def _secondary_button_style(*, compact: bool = False) -> str:
    p = palette()
    pad = "4px 9px" if compact else "5px 12px"
    fs = meta_font_pt() if compact else max(meta_font_pt(), 11)
    return (
        f"QPushButton {{ background:{p['BG3']}; color:{p['TEXT']};"
        f"border:1px solid {p['BORDER']}; border-radius:6px;"
        f"padding:{pad}; font-size:{fs}px; font-weight:500; }}"
        f"QPushButton:hover {{ background:{p['BORDER']}; }}"
        f"QPushButton:pressed {{ background:{p['BG2']}; }}"
    )


def _header_style() -> str:
    p = palette()
    return (
        f"QFrame#extensionHeader {{ background:transparent;"
        f"border-bottom:1px solid {p['BORDER_SUBTLE']}; border-radius:0; }}"
    )


def _detail_table_style(tone: str = "") -> str:
    p = palette()
    border = "#5f252d" if tone == "danger" else p["BORDER_SUBTLE"]
    return (
        f"QFrame#extensionDetailTable {{ background:transparent;"
        f"border-top:1px solid {border}; border-radius:0; }}"
    )


def _detail_name_style(tone: str = "") -> str:
    p = palette()
    color = "#f87171" if tone == "danger" else p["TEXT"]
    return f"color:{color}; font-weight:600;"


def _detail_value_style(tone: str = "") -> str:
    p = palette()
    color = "#fca5a5" if tone == "danger" else p["TEXT_DIM"]
    return f"color:{color}; font-size:{meta_font_pt()}px;"


def _status_label_style(tone: str) -> str:
    p = palette()
    if tone == "danger":
        bg, fg, border = "#35191d", "#f87171", "#5f252d"
    elif tone == "disabled":
        bg, fg, border = p["BG3"], p["TEXT_DIM"], p["BORDER"]
    else:
        bg, fg, border = p["SUCCESS_BG"], p["SUCCESS"], p["SUCCESS_BORDER"]
    return (
        f"background-color:{bg}; color:{fg}; border:1px solid {border};"
        "border-radius:8px; padding-left:8px; padding-right:8px;"
        f"font-size:{meta_font_pt()}px;"
    )


def _status_tone(file: ExtensionFileSummary) -> str:
    if file.status == "Disabled":
        return "disabled"
    if file.errors:
        return "danger"
    return "success"


def _enabled_checkbox_style() -> str:
    p = palette()
    return (
        f"QCheckBox {{ color:{p['TEXT']}; font-size:{meta_font_pt()}px; }}"
        "QCheckBox::indicator { width:15px; height:15px; }"
    )

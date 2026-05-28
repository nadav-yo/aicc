from PyQt6.QtWidgets import QLabel, QPushButton

from services.tool_registry import ExtensionFileSummary, ExtensionOverview
from ui.widgets.extensions_dialog import (
    ExtensionsDialog,
    _ApiReferencePane,
    _ExtensionDetailPane,
    _list_subtitle,
    _status_tone,
    _summary_text,
    _tab_text_color,
    _tab_title,
    _tab_tooltip,
)


def _summary(path="ext.py", status="Loaded", errors=None, description=""):
    return ExtensionFileSummary(
        path=path,
        status=status,
        tools=[],
        commands=[],
        contexts=[],
        hooks=[],
        badges=[],
        panels=[],
        errors=list(errors or []),
        description=description,
    )


def test_extensions_summary_includes_disabled_count():
    overview = ExtensionOverview(files=[
        _summary("loaded.py"),
        _summary("disabled.py", status="Disabled"),
    ])

    assert _summary_text(overview) == "2 extension files · no errors · 1 disabled"


def test_extensions_dialog_status_helpers():
    assert _status_tone(_summary()) == "success"
    assert _status_tone(_summary(status="Disabled")) == "disabled"
    assert _status_tone(_summary(status="Failed", errors=["boom"])) == "danger"
    assert _tab_title(_summary("disabled.py", status="Disabled")) == "Disabled · disabled.py"
    assert "Disabled" in _tab_tooltip(_summary(status="Disabled"))
    assert _tab_text_color(_summary(status="Failed", errors=["boom"])) == "#f87171"


def test_extensions_dialog_tab_tooltip_includes_description():
    tooltip = _tab_tooltip(_summary(description="Adds runtime guardrails."))

    assert "Loaded." in tooltip
    assert "Adds runtime guardrails." in tooltip


def test_extensions_dialog_keeps_api_reference_outside_extension_list(qapp):
    overview = ExtensionOverview(files=[
        _summary("runtime.py", description="Runtime controls"),
        _summary("guard.py", description="Guardrails"),
    ])
    dialog = ExtensionsDialog(overview)

    assert dialog._selected_path == "runtime.py"
    assert isinstance(dialog._detail_scroll.widget(), _ExtensionDetailPane)
    assert "Inspect" not in [button.text() for button in dialog.findChildren(QPushButton)]

    dialog._show_api_reference()

    assert dialog._selected_path == ""
    assert isinstance(dialog._detail_scroll.widget(), _ApiReferencePane)

    dialog._show_file_detail(overview.files[1])

    assert dialog._selected_path == "guard.py"
    assert isinstance(dialog._detail_scroll.widget(), _ExtensionDetailPane)


def test_extensions_dialog_list_subtitle_summarizes_contributions():
    file = _summary("runtime.py", description="Runtime controls")

    assert _list_subtitle(file) == "No registered contributions · Runtime controls"


def test_extensions_api_reference_includes_recent_runtime_apis(qapp):
    dialog = ExtensionsDialog(ExtensionOverview(files=[_summary("runtime.py")]))

    dialog._show_api_reference()

    labels = "\n".join(label.text() for label in dialog.findChildren(QLabel))
    assert "ctx.storage.load_config(scope)" in labels
    assert "ctx.runtime.processes.start(name, command, ...)" in labels
    assert "run_extension_command" in labels
    assert "compact_and_resume" in labels

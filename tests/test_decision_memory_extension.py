import shutil
from pathlib import Path

from services.tool_registry import extension_context_snippets, load_extensions, ToolRegistry
from services.tools import execute


def _install_decision_memory(workspace: Path) -> None:
    source = Path(__file__).parents[1] / ".aichs" / "extensions" / "decision_memory.py"
    target_dir = workspace / ".aichs" / "extensions"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_dir / "decision_memory.py")


def test_remember_recall_and_list_decisions(workspace):
    _install_decision_memory(workspace)
    cwd = str(workspace)

    remembered = execute(
        "remember_decision",
        {
            "topic": "Compaction",
            "decision": "Decision memory should be an opt-in extension.",
        },
        cwd,
    )
    duplicate = execute(
        "remember_decision",
        {
            "topic": "compaction",
            "decision": "Decision memory should be an opt-in extension.",
        },
        cwd,
    )
    recalled = execute("recall_decisions", {"topic": "compaction"}, cwd)
    topics = execute("list_decision_topics", {}, cwd)

    assert remembered == "Remembered decision under 'compaction'."
    assert duplicate == "Decision already remembered under 'compaction'."
    assert recalled == (
        "Decisions for 'compaction':\n"
        "- Decision memory should be an opt-in extension."
    )
    assert topics == "Decision topics:\n- compaction"
    state_path = workspace / ".aichs" / "state" / "decision_memory" / "decisions.json"
    assert "Decision memory should be an opt-in extension." in state_path.read_text(encoding="utf-8")


def test_decision_memory_context_includes_known_topics(workspace):
    _install_decision_memory(workspace)
    cwd = str(workspace)
    execute(
        "remember_decision",
        {"topic": "extensions", "decision": "Use narrow extension tools for decision memory."},
        cwd,
    )

    snippets, errors = extension_context_snippets(cwd)

    assert errors == []
    assert len(snippets) == 1
    name, text = snippets[0]
    assert name == "Decision memory"
    assert "Decision memory is enabled" in text
    assert "Known decision topics: extensions" in text
    assert "remember_decision only when the user clearly makes or confirms" in text


def test_decision_memory_registers_narrow_tools(workspace):
    _install_decision_memory(workspace)
    registry = ToolRegistry()
    load_extensions(registry, str(workspace))

    remember = registry.get("remember_decision")
    recall = registry.get("recall_decisions")
    list_topics = registry.get("list_decision_topics")

    assert remember is not None
    assert remember.approval == "once"
    assert remember.extension_id == "decision_memory"
    assert recall is not None
    assert recall.parallel_safe is True
    assert list_topics is not None
    assert list_topics.parallel_safe is True


def test_remember_decision_rejects_empty_or_long_values(workspace):
    _install_decision_memory(workspace)
    cwd = str(workspace)

    empty = execute("remember_decision", {"topic": "", "decision": "Use JWT."}, cwd)
    long_decision = execute(
        "remember_decision",
        {"topic": "auth", "decision": "x" * 301},
        cwd,
    )

    assert "requires a non-empty topic" in empty
    assert "decision is too long" in long_decision

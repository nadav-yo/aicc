import importlib.util
from pathlib import Path

from services.processes import RuntimeProcessApi, get_process_manager
from services.tool_registry import CommandContext, ExtensionContext, RuntimeCommandApi, ToolRegistry


def _load_process_module():
    path = Path(__file__).parents[1] / ".aichs" / "extensions" / "process_sessions.py"
    spec = importlib.util.spec_from_file_location("process_sessions_ext", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_process_extension_registers_tools_command_and_ui():
    module = _load_process_module()
    registry = ToolRegistry()

    module.register(registry)

    assert registry.command_by_name("process") is not None
    assert {
        "process_status",
        "process_logs",
        "process_start",
        "process_stop",
    }.issubset(set(registry.names()))
    assert registry.panels()[0].name == "process_sessions"


def test_process_config_command_creates_workspace_config(workspace):
    module = _load_process_module()
    ctx = CommandContext(cwd=str(workspace), extension_id="process_sessions")

    text = module.process_command(ctx, "config")

    config_path = workspace / ".aichs" / "extensions" / "process_sessions.json"
    assert ".aichs/extensions/process_sessions.json" in text
    assert config_path.exists()
    assert "demo" in text


def test_process_panel_uses_send_message_actions(workspace):
    module = _load_process_module()
    ctx = ExtensionContext(
        cwd=str(workspace),
        extension_id="process_sessions",
        processes=RuntimeProcessApi(get_process_manager(), workspace=str(workspace)),
    )

    data = module.process_panel(ctx)

    item = data["sections"][0]["items"][0]
    action_types = {action["type"] for action in item["actions"]}
    assert {"refresh_panel", "run_extension_command"}.issubset(action_types)
    assert any(
        action.get("args") == "start demo" and action.get("refresh") is True
        for action in item["actions"]
    )


def test_process_logs_missing_file_is_friendly(workspace):
    module = _load_process_module()
    processes = RuntimeProcessApi(get_process_manager(), workspace=str(workspace))

    assert module._logs_text(processes, "demo", 20) == "[process error] process not found: demo"


def test_process_command_uses_runtime_process_api(workspace):
    module = _load_process_module()
    calls = []

    class Processes:
        def start(self, name, command, **kwargs):
            calls.append((name, command, kwargs))
            return type("Info", (), {"pid": 123})()

    ctx = CommandContext(
        cwd=str(workspace),
        extension_id="process_sessions",
        runtime=RuntimeCommandApi(processes=Processes()),
    )

    text = module.process_command(ctx, "start demo")

    assert "pid 123" in text
    assert calls[0][0] == "demo"

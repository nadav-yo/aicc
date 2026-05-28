from pathlib import Path

from main import _parse_args
from ui.main_window import _startup_workspace


def test_plain_launch_uses_current_directory_even_with_saved_workspace(tmp_path):
    launch = tmp_path / "launch"
    saved = tmp_path / "saved"
    launch.mkdir()
    saved.mkdir()

    workspace = _startup_workspace(
        {"workspace_path": str(saved)},
        launch_cwd=str(launch),
    )

    assert Path(workspace) == launch.resolve()


def test_last_workspace_opt_in_uses_saved_workspace(tmp_path):
    launch = tmp_path / "launch"
    saved = tmp_path / "saved"
    launch.mkdir()
    saved.mkdir()

    workspace = _startup_workspace(
        {"workspace_path": str(saved)},
        prefer_saved_workspace=True,
        launch_cwd=str(launch),
    )

    assert Path(workspace) == saved.resolve()


def test_explicit_workspace_wins_over_saved_workspace(tmp_path):
    explicit = tmp_path / "explicit"
    saved = tmp_path / "saved"
    explicit.mkdir()
    saved.mkdir()

    workspace = _startup_workspace(
        {"workspace_path": str(saved)},
        startup_workspace=str(explicit),
        prefer_saved_workspace=True,
    )

    assert Path(workspace) == explicit.resolve()


def test_parse_workspace_argument():
    workspace, last_workspace, qt_args = _parse_args(["C:\\repo", "--platform", "windows"])

    assert workspace == "C:\\repo"
    assert last_workspace is False
    assert qt_args == ["--platform", "windows"]


def test_parse_workspace_option_and_last_workspace():
    workspace, last_workspace, qt_args = _parse_args(
        ["--workspace", "C:\\repo", "--last-workspace"],
    )

    assert workspace == "C:\\repo"
    assert last_workspace is True
    assert qt_args == []

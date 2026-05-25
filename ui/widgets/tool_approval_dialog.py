from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QDialogButtonBox, QTextEdit,
)
from PyQt6.QtGui import QFont

from services.tool_policy import PendingApproval, repo_root


def handle_pending_approval(parent, bus, pending: PendingApproval) -> None:
    if pending.kind == "edit":
        _show_edit(parent, bus, pending)
    elif pending.kind == "bash":
        _show_bash(parent, bus, pending)


def _show_edit(parent, bus, pending: PendingApproval) -> None:
    root = repo_root(pending.cwd)
    dlg = QDialog(parent)
    dlg.setWindowTitle("Allow file edits?")
    layout = QVBoxLayout(dlg)

    layout.addWidget(QLabel(
        f"Allows the <b>edit_file</b> tool under:<br><code>{root}</code>"
    ))
    note = QLabel(
        "This is not a sandbox. Shell commands can still change files "
        "outside this tool."
    )
    note.setWordWrap(True)
    note.setStyleSheet("color: #888;")
    layout.addWidget(note)

    buttons = QDialogButtonBox()
    allow = buttons.addButton("Allow", QDialogButtonBox.ButtonRole.AcceptRole)
    cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
    allow.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)
    layout.addWidget(buttons)

    if dlg.exec() == QDialog.DialogCode.Accepted:
        bus.complete(pending, approved=True, grant_edit=True)
    else:
        bus.complete(
            pending,
            approved=False,
            message="[tool error] User denied edit_file for this conversation.",
        )


def _show_bash(parent, bus, pending: PendingApproval) -> None:
    command = pending.inputs.get("command", "")
    policy = pending.policy
    dlg = QDialog(parent)
    dlg.setWindowTitle("Run command?")
    layout = QVBoxLayout(dlg)

    if not policy.bash_warning_shown:
        warn = QLabel(
            "Runs as <b>you</b> on this machine — not limited to the project folder. "
            "Confirmations reduce mistakes; they do not isolate the agent."
        )
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #aaa;")
        layout.addWidget(warn)
        policy.bash_warning_shown = True

    cmd_box = QTextEdit()
    cmd_box.setPlainText(command)
    cmd_box.setReadOnly(True)
    cmd_box.setMaximumHeight(120)
    cmd_font = QFont("Consolas")
    if not cmd_font.exactMatch():
        cmd_font = QFont("Courier New")
    cmd_box.setFont(cmd_font)
    layout.addWidget(cmd_box)

    row = QHBoxLayout()
    run_btn = QPushButton("Run")
    skip_btn = QPushButton("Don't ask again")
    skip_hint = QLabel("Rest of this conversation only")
    skip_hint.setStyleSheet("color: #888; font-size: 11px;")
    cancel_btn = QPushButton("Cancel")
    run_btn.clicked.connect(dlg.accept)
    skip_btn.clicked.connect(lambda: dlg.done(2))
    cancel_btn.clicked.connect(dlg.reject)
    row.addWidget(run_btn)
    row.addWidget(skip_btn)
    row.addWidget(skip_hint)
    row.addStretch()
    row.addWidget(cancel_btn)
    layout.addLayout(row)

    code = dlg.exec()
    if code == QDialog.DialogCode.Accepted:
        bus.complete(pending, approved=True)
    elif code == 2:
        bus.complete(pending, approved=True, grant_bash_skip=True)
    else:
        bus.complete(
            pending,
            approved=False,
            message="[tool error] User denied bash command.",
        )

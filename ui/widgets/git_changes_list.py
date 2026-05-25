"""Uncommitted-changes list — same look/behavior as the Git tab."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

from services.git_status import is_git_repo, list_file_changes
from ui.theme import (
    palette, meta_font_pt, mono_font_pt, mono_font,
    git_status_color, git_changes_list_style, sidebar_section_label_style,
)


class GitChangesList(QWidget):
    file_open = pyqtSignal(str)

    def __init__(self, repo_path: str, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._label = QLabel("Uncommitted changes")
        layout.addWidget(self._label)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._on_open)
        layout.addWidget(self.list)

        self.apply_appearance()
        self.refresh()

        timer = QTimer(self)
        timer.timeout.connect(self.refresh)
        timer.start(5000)

    def apply_appearance(self):
        self._label.setStyleSheet(sidebar_section_label_style())
        font = mono_font(mono_font_pt())
        self.list.setFont(font)
        self.list.setStyleSheet(git_changes_list_style())

    def _on_open(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.file_open.emit(path)

    def refresh(self):
        self.list.clear()
        if not is_git_repo(self.repo_path):
            self._label.setText("Uncommitted changes")
            item = QListWidgetItem("(not a git repository)")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list.addItem(item)
            return

        changes = list_file_changes(self.repo_path)
        if not changes:
            self._label.setText("Uncommitted changes — clean")
            return

        for ch in changes:
            item = QListWidgetItem(ch.rel_path)
            item.setToolTip(f"{ch.label} — {ch.rel_path}")
            item.setData(Qt.ItemDataRole.UserRole, ch.abs_path)
            item.setForeground(QColor(git_status_color(ch.code)))
            self.list.addItem(item)
        self._label.setText(f"Uncommitted changes ({len(changes)})")

    def set_repo_path(self, path: str):
        self.repo_path = path
        self.refresh()

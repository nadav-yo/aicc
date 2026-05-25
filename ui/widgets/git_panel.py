import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QListWidget, QLabel,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from services.git_status import run_git
from ui.theme import palette, meta_font_pt, mono_font_pt, mono_font, git_changes_list_style, sidebar_section_label_style
from ui.widgets.git_changes_list import GitChangesList


class GitPanel(QWidget):
    file_open = pyqtSignal(str)

    def __init__(self, repo_path: str, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self._changes = GitChangesList(repo_path)
        self._changes.file_open.connect(self.file_open.emit)

        log_wrap = QWidget()
        ll = QVBoxLayout(log_wrap)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(2)
        self._log_lbl = QLabel("Git log")
        ll.addWidget(self._log_lbl)
        self.log = QListWidget()
        ll.addWidget(self.log)

        splitter.addWidget(self._changes)
        splitter.addWidget(log_wrap)
        splitter.setSizes([180, 320])
        root.addWidget(splitter, 1)

        self.apply_appearance()
        self._refresh_log()
        timer = QTimer(self)
        timer.timeout.connect(self.refresh)
        timer.start(5000)

    def apply_appearance(self):
        p = palette()
        meta = meta_font_pt()
        mono = mono_font_pt()
        font = mono_font(mono)

        self._log_lbl.setStyleSheet(sidebar_section_label_style())
        list_style = git_changes_list_style()
        self.log.setFont(font)
        self.log.setStyleSheet(list_style)
        self._changes.apply_appearance()

    def refresh(self):
        self._changes.refresh()
        self._refresh_log()

    def _refresh_log(self):
        self.log.clear()
        for line in run_git(["git", "log", "--oneline", "-40"], self.repo_path).splitlines():
            self.log.addItem(line)

    def set_repo_path(self, path: str):
        self.repo_path = path
        self._changes.set_repo_path(path)
        self.refresh()

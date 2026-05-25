import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QFrame, QTabWidget,
    QScrollArea, QLabel, QSizePolicy, QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

from config import MAX_FILE_PREVIEW_BYTES
from services.diff_html import diff_to_html
from services.git_diff import can_diff_against_head, diff_against_head
from services.highlight import for_path, for_language
from ui.theme import palette, mono_font, meta_font_pt

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".ico"}


class _ImageViewer(QScrollArea):
    """Scrollable image tab; scales down large images to fit the viewport."""

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._path = path
        self._original: QPixmap | None = None

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding,
        )
        self.setWidget(self._label)

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._label.setText(f"Could not load image:\n{os.path.basename(path)}")
        else:
            self._original = pixmap

        self.apply_appearance()
        self._update_scale()

    def apply_appearance(self):
        p = palette()
        self.setStyleSheet(f"QScrollArea {{ background:{p['BG']}; border:none; }}")
        if self._original is None:
            self._label.setStyleSheet(
                f"color:{p['TEXT_DIM']}; padding:24px; background:transparent;"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scale()

    def _update_scale(self):
        if not self._original:
            return
        vp = self.viewport().size()
        if self._original.width() <= vp.width() and self._original.height() <= vp.height():
            self._label.setPixmap(self._original)
            return
        scaled = self._original.scaled(
            vp,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)


class _TextFileTab(QWidget):
    """Syntax-highlighted file view with optional git diff vs HEAD."""

    def __init__(
        self,
        path: str,
        content: str,
        repo_root: str,
        diff_text: str | None,
        parent=None,
    ):
        super().__init__(parent)
        self._path = path
        self._content = content
        self._lang_hint = path
        self._diff_text = diff_text

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 4, 8, 4)
        self._diff_toggle = QCheckBox("Show diff")
        self._diff_toggle.setChecked(bool(diff_text))
        self._diff_toggle.setVisible(diff_text is not None)
        self._diff_toggle.toggled.connect(self._on_diff_toggled)
        bar.addWidget(self._diff_toggle)
        bar.addStretch(1)
        root.addLayout(bar)

        self._editor = QTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setFrameShape(QFrame.Shape.NoFrame)
        self._editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        root.addWidget(self._editor, 1)

        self.apply_appearance()
        self._render()

    def apply_appearance(self):
        p = palette()
        meta = meta_font_pt()
        self._diff_toggle.setStyleSheet(
            f"QCheckBox {{ color:{p['TEXT_DIM']}; font-size:{meta}px; spacing:6px; }}"
            f"QCheckBox::indicator {{ width:14px; height:14px; }}"
        )
        self._editor.setFont(mono_font())
        self._editor.setStyleSheet(
            f"QTextEdit {{ background:{p['BG3']}; color:{p['TEXT']}; border:none; }}"
        )
        self._render()

    def _on_diff_toggled(self, _checked: bool):
        self._render()

    def _render(self):
        if self._diff_toggle.isChecked() and self._diff_text:
            self._editor.setHtml(diff_to_html(self._diff_text))
        else:
            self._editor.setHtml(
                for_path(self._content, self._lang_hint)
                if self._lang_hint
                else for_language(self._content, "")
            )


class FileViewerPanel(QWidget):
    all_closed = pyqtSignal()

    def __init__(self, repo_root: str = "", parent=None):
        super().__init__(parent)
        self._repo_root = repo_root or os.getcwd()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setTabsClosable(True)
        tab_bar = self._tabs.tabBar()
        tab_bar.setUsesScrollButtons(True)
        tab_bar.setElideMode(Qt.TextElideMode.ElideRight)
        tab_bar.setExpanding(False)
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)

        root.addWidget(self._tabs)

    def set_repo_root(self, path: str):
        self._repo_root = path

    def apply_appearance(self):
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, _TextFileTab):
                widget.apply_appearance()
            elif isinstance(widget, _ImageViewer):
                widget.apply_appearance()

    def _find_tab(self, key: str) -> int:
        tab_bar = self._tabs.tabBar()
        for i in range(self._tabs.count()):
            if tab_bar.tabData(i) == key:
                return i
        return -1

    def _add_tab_widget(self, key: str, title: str, widget: QWidget):
        idx = self._tabs.addTab(widget, title)
        self._tabs.tabBar().setTabData(idx, key)
        self._tabs.setCurrentIndex(idx)

    def _add_text_tab(self, key: str, title: str, content: str):
        tab = _TextFileTab(key, content, self._repo_root, diff_text=None)
        self._add_tab_widget(key, title, tab)

    def open_file(self, path: str, repo_root: str | None = None):
        if repo_root:
            self._repo_root = repo_root
        path = os.path.abspath(path)
        idx = self._find_tab(path)
        if idx >= 0:
            self._tabs.setCurrentIndex(idx)
            return

        ext = os.path.splitext(path)[1].lower()
        if ext in _IMAGE_EXTS:
            self._add_tab_widget(path, os.path.basename(path), _ImageViewer(path))
            return

        try:
            content = _read_text_preview(path)
        except OSError as e:
            content = f"[Could not read file: {e}]"

        diff_text = None
        if can_diff_against_head(self._repo_root, path):
            diff_text = diff_against_head(self._repo_root, path)

        tab = _TextFileTab(path, content, self._repo_root, diff_text=diff_text)
        self._add_tab_widget(path, os.path.basename(path), tab)

    def open_content(self, content: str, title: str):
        key = f"\0{title}"
        idx = self._find_tab(key)
        if idx >= 0:
            self._tabs.setCurrentIndex(idx)
            return
        self._add_text_tab(key, title, content)

    def _on_tab_close_requested(self, index: int):
        self._tabs.removeTab(index)
        if self._tabs.count() == 0:
            self.all_closed.emit()

    def close_current_tab(self) -> bool:
        if self._tabs.count() == 0:
            return False
        self._tabs.removeTab(self._tabs.currentIndex())
        if self._tabs.count() == 0:
            self.all_closed.emit()
        return True


def _read_text_preview(path: str) -> str:
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        raw = f.read(MAX_FILE_PREVIEW_BYTES + 1)
    truncated = len(raw) > MAX_FILE_PREVIEW_BYTES
    text = raw[:MAX_FILE_PREVIEW_BYTES].decode("utf-8", errors="replace")
    if truncated:
        text += f"\n\n[Preview truncated: showing {MAX_FILE_PREVIEW_BYTES} of {size} bytes]"
    return text

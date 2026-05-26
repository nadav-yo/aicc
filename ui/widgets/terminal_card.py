from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QSizePolicy
from PyQt6.QtCore import Qt

from config import MAX_TERMINAL_BLOCKS
from ui.theme import palette, card_frame_style, meta_font_pt, mono_font_pt, mono_font


class TerminalCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(680)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._exit_code: int | None = None
        self._line_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFrameShape(QFrame.Shape.NoFrame)
        self._output.setMinimumHeight(30)
        self._output.setMaximumHeight(38)
        self._output.setFixedHeight(38)
        self._output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._output.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._output.document().setMaximumBlockCount(MAX_TERMINAL_BLOCKS)

        self._footer = QFrame()
        footer_row = QHBoxLayout(self._footer)
        footer_row.setContentsMargins(10, 0, 10, 5)

        self._status = QLabel("Running…")
        footer_row.addStretch()
        footer_row.addWidget(self._status)

        root.addWidget(self._output, 0)
        root.addWidget(self._footer)

        self.apply_appearance()

    def apply_appearance(self):
        p = palette()
        mono = mono_font_pt()
        meta = meta_font_pt()
        self._output.setFont(mono_font(mono))
        self.setStyleSheet(card_frame_style())
        self._output.setStyleSheet(
            f"QTextEdit {{ background:transparent; color:{p['TEXT']}; border:none; padding:6px 10px; }}"
        )
        self._footer.setStyleSheet(
            "QFrame { background:transparent; border:none; }"
        )
        if self._exit_code is None:
            self._status.setStyleSheet(
                f"color:{p['TEXT_DIM']}; font-size:{meta}px; background:transparent; border:none;"
            )
        elif self._exit_code == 0:
            self._status.setStyleSheet(
                f"color:{p['SUCCESS']}; font-size:{max(9, meta - 1)}px; background:transparent; border:none;"
            )
        else:
            self._status.setStyleSheet(
                f"color:#f87171; font-size:{meta}px; background:transparent; border:none;"
            )

    def append_line(self, line: str):
        self._line_count += 1
        height = min(150, max(38, self._line_count * 20 + 20))
        self._output.setFixedHeight(height)
        if height >= 150:
            self._output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._output.append(line)
        self._output.verticalScrollBar().setValue(
            self._output.verticalScrollBar().maximum()
        )

    def finish(self, exit_code: int = 0):
        self._exit_code = exit_code
        if exit_code == 0:
            self._status.setText("done")
        else:
            self._status.setText(f"exit {exit_code}")
        self.apply_appearance()

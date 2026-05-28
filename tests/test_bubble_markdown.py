from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtGui import QGuiApplication, QKeyEvent

from services.file_ref_clipboard import AICHS_MESSAGE_COPY_MIME, parse_file_refs_payload
from ui.widgets.bubble import MessageBubble, _to_html


def test_streamed_assistant_text_finalizes_to_rich_text(qapp):
    bubble = MessageBubble("", is_user=False, typing=True)
    bubble.append("## Title\n\n**bold**")
    bubble.finalize(bubble._copy_text)
    assert bubble._md_source is not None
    assert bubble.label.textFormat() == Qt.TextFormat.RichText
    assert "Title" in bubble.label.text()
    assert "bold" in bubble.label.text()


def test_assistant_markdown_linkifies_plain_file_paths(qapp):
    bubble = MessageBubble(
        "The coverage gap in services\\git_diff.py comes from branches.",
        is_user=False,
    )

    html = bubble.label.text()

    assert 'href="aichs-file:services\\git_diff.py"' in html
    assert ">services\\git_diff.py</a>" in html


def test_assistant_markdown_linkifies_file_paths_in_lists():
    html = _to_html(
        "- services\\chat.py: 79%\n"
        "- services\\git_diff.py: 77%\n"
        "- storage\\repository.py: 88%"
    )

    assert 'href="aichs-file:services\\chat.py"' in html
    assert 'href="aichs-file:services\\git_diff.py"' in html
    assert 'href="aichs-file:storage\\repository.py"' in html


def test_assistant_markdown_does_not_relink_existing_links():
    html = _to_html("[services/chat.py](aichs-file:services/chat.py)")

    assert html.count("aichs-file:services/chat.py") == 1


def test_bubble_copy_adds_aichs_file_ref_metadata(qapp):
    bubble = MessageBubble(
        "Coverage mentions services\\git_diff.py: 77%",
        is_user=False,
    )

    bubble._copy_to_clipboard()

    mime = QGuiApplication.clipboard().mimeData()
    assert mime.text() == "Coverage mentions services\\git_diff.py: 77%"
    assert parse_file_refs_payload(mime.data(AICHS_MESSAGE_COPY_MIME)) == [
        "services\\git_diff.py"
    ]


def test_bubble_keyboard_copy_adds_aichs_file_ref_metadata(qapp):
    bubble = MessageBubble(
        "The file you just provided is services/chat.py.",
        is_user=False,
    )

    event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_C,
        Qt.KeyboardModifier.ControlModifier,
    )
    QCoreApplication.sendEvent(bubble.label, event)

    mime = QGuiApplication.clipboard().mimeData()
    assert event.isAccepted()
    assert mime.text() == "The file you just provided is services/chat.py."
    assert parse_file_refs_payload(mime.data(AICHS_MESSAGE_COPY_MIME)) == [
        "services/chat.py"
    ]

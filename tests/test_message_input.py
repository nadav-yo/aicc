from pathlib import Path

from PyQt6.QtCore import QPointF, QMimeData, QUrl, Qt
from PyQt6.QtGui import QDropEvent, QImage

from ui.widgets.message_input import ComposerWidget, _images_from_mime


def _drop_event(mime: QMimeData) -> QDropEvent:
    return QDropEvent(
        QPointF(8, 8),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_images_from_mime_local_png(qapp, tmp_path):
    png = tmp_path / "sprite.png"
    QImage(8, 8, QImage.Format.Format_RGB32).save(str(png))

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(png))])

    images = _images_from_mime(mime)
    assert len(images) == 1
    assert images[0].width() == 8


def test_drop_image_url_does_not_insert_text(qapp, tmp_path):
    png = tmp_path / "food-sprites.png"
    QImage(12, 12, QImage.Format.Format_RGB32).save(str(png))

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(png))])

    composer = ComposerWidget()
    pasted: list[QImage] = []
    composer.input.image_pasted.connect(pasted.append)

    composer.input.dropEvent(_drop_event(mime))

    assert composer.input.toPlainText() == ""
    assert len(pasted) == 1
    assert composer.strip.has_images()


def test_drop_non_image_url_does_not_insert_text(qapp, tmp_path):
    doc = tmp_path / "notes.txt"
    doc.write_text("hello", encoding="utf-8")

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(doc))])

    composer = ComposerWidget()
    composer.input.dropEvent(_drop_event(mime))

    assert composer.input.toPlainText() == ""
    assert not composer.strip.has_images()

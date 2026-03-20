from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent


class Titlebar(QWidget):
    """Barra de título customizada (drag + botões de janela)."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("Titlebar")
        self._drag_pos: QPoint | None = None
        self._main_window = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        self._title = QLabel("VANTAGE")
        self._title.setObjectName("TitlebarLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        for name, symbol, slot in [
            ("WinBtn", "─", self._minimize),
            ("WinBtn", "□", self._maximize),
            ("WinBtnClose", "✕", self._close),
        ]:
            btn = QPushButton(symbol)
            btn.setObjectName(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

    # ── drag ──────────────────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._main_window.move(self._main_window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    # ── botões ────────────────────────────────────────────────────────────

    def _minimize(self) -> None:
        self._main_window.showMinimized()

    def _maximize(self) -> None:
        if self._main_window.isMaximized():
            self._main_window.showNormal()
        else:
            self._main_window.showMaximized()

    def _close(self) -> None:
        self._main_window.close()

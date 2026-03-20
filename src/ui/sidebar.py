from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


NAV_ITEMS = [
    ("🎲  Rolagem de Dados", "dice"),
    ("🧙  Personagens", "characters"),
    ("🗺️  Mapas", "maps"),
    ("📖  Canto do Lore", "lore"),
]


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)  # emite o id da página selecionada

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._buttons: dict[str, QPushButton] = {}
        self._active: str = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 16)
        layout.setSpacing(2)

        title = QLabel("VANTAGE")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        subtitle = QLabel("Mesa do Mestre")
        subtitle.setObjectName("SidebarSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        for label, page_id in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, pid=page_id: self._select(pid))
            self._buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def _select(self, page_id: str) -> None:
        # Remove estado ativo do botão anterior
        if self._active and self._active in self._buttons:
            self._buttons[self._active].setProperty("active", False)
            self._buttons[self._active].style().unpolish(self._buttons[self._active])
            self._buttons[self._active].style().polish(self._buttons[self._active])

        self._active = page_id
        self._buttons[page_id].setProperty("active", True)
        self._buttons[page_id].style().unpolish(self._buttons[page_id])
        self._buttons[page_id].style().polish(self._buttons[page_id])

        self.page_changed.emit(page_id)

    def set_active(self, page_id: str) -> None:
        self._select(page_id)

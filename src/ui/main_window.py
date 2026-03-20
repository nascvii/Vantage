from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from src.ui.titlebar import Titlebar
from src.ui.sidebar import Sidebar
from src.ui.pages.dice_roller import DiceRollerPage
from src.ui.pages.characters import CharactersPage
from src.ui.pages.map_editor import MapEditorPage
from src.ui.pages.lore import LorePage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1024, 680)
        self.resize(1280, 800)

        self._pages: dict[str, QWidget] = {}
        self._build_ui()
        self._sidebar.set_active("dice")

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("ContentArea")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._titlebar = Titlebar(self)
        root.addWidget(self._titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._navigate)

        self._stack = QStackedWidget()

        body.addWidget(self._sidebar)
        body.addWidget(self._stack)
        root.addLayout(body)

        # Páginas
        self._register("dice", DiceRollerPage())
        self._register("characters", CharactersPage())
        self._register("maps", MapEditorPage())
        self._register("lore", LorePage())

    def _register(self, page_id: str, widget: QWidget) -> None:
        self._pages[page_id] = widget
        self._stack.addWidget(widget)

    def _navigate(self, page_id: str) -> None:
        if page_id in self._pages:
            self._stack.setCurrentWidget(self._pages[page_id])

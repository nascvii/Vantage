"""Página genérica de placeholder para funcionalidades futuras."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class PlaceholderPage(QWidget):
    def __init__(self, icon: str, title: str, description: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        lbl_icon = QLabel(icon)
        lbl_icon.setObjectName("PlaceholderIcon")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("PlaceholderTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_desc = QLabel(description)
        lbl_desc.setObjectName("PlaceholderText")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)

"""Canto do Lore — anotações de mundo organizadas por categoria."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QFrame, QScrollArea,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from datetime import datetime

from src.core.lore import LoreEntry, DEFAULT_CATEGORIES
from src.core.storage import save_json, load_json


class LoreCard(QFrame):
    """Card resumido de uma entrada de lore na lista."""

    def __init__(self, entry: LoreEntry, parent=None):
        super().__init__(parent)
        self.setObjectName("LoreCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.entry = entry

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        title = QLabel(entry.title or "Sem título")
        title.setObjectName("CardName")

        cat = QLabel(entry.category)
        cat.setObjectName("CardInfo")

        preview = entry.content[:60].replace("\n", " ")
        if len(entry.content) > 60:
            preview += "…"
        prev_lbl = QLabel(preview)
        prev_lbl.setObjectName("CardPreview")

        layout.addWidget(title)
        layout.addWidget(cat)
        if preview:
            layout.addWidget(prev_lbl)


class LorePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: list[LoreEntry] = []
        self._selected: LoreEntry | None = None
        self._build_ui()
        self._load()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_list_panel(), stretch=1)

        sep = QFrame()
        sep.setObjectName("VSeparator")
        sep.setFixedWidth(1)
        root.addWidget(sep)

        root.addWidget(self._build_editor_panel(), stretch=2)

    # ── lista lateral ─────────────────────────────────────────────────────

    def _build_list_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("ListPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("ListHeader")
        hlayout = QVBoxLayout(header)
        hlayout.setContentsMargins(12, 12, 12, 12)
        hlayout.setSpacing(8)

        title = QLabel("Canto do Lore")
        title.setObjectName("PageTitle")
        hlayout.addWidget(title)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar...")
        self._search.setObjectName("SearchInput")
        self._search.textChanged.connect(self._filter_list)
        hlayout.addWidget(self._search)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)

        self._cat_filter = QComboBox()
        self._cat_filter.addItem("Todas")
        self._cat_filter.addItems(DEFAULT_CATEGORIES)
        self._cat_filter.currentIndexChanged.connect(self._filter_list)
        filter_row.addWidget(self._cat_filter, stretch=1)

        btn_new = QPushButton("+ Nova Entrada")
        btn_new.setObjectName("PrimaryButton")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._new_entry)
        filter_row.addWidget(btn_new)

        hlayout.addLayout(filter_row)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(8, 8, 8, 8)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll)
        return panel

    # ── editor ────────────────────────────────────────────────────────────

    def _build_editor_panel(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # placeholder
        self._placeholder = QLabel("Selecione ou crie uma entrada")
        self._placeholder.setObjectName("PlaceholderTitle")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._placeholder)

        # form
        self._form = QWidget()
        self._form.hide()
        form = QVBoxLayout(self._form)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(12)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Título da entrada")
        self._title_input.setObjectName("FormInput")

        self._cat_combo = QComboBox()
        self._cat_combo.addItems(DEFAULT_CATEGORIES)

        row.addWidget(self._title_input, stretch=3)
        row.addWidget(QLabel("Categoria:"))
        row.addWidget(self._cat_combo, stretch=1)
        form.addLayout(row)

        self._content_edit = QTextEdit()
        self._content_edit.setObjectName("LoreEditor")
        self._content_edit.setPlaceholderText("Escreva suas anotações aqui...")
        form.addWidget(self._content_edit, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_current)

        btn_del = QPushButton("Excluir")
        btn_del.setObjectName("DangerButton")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self._delete_current)

        actions.addWidget(btn_save)
        actions.addWidget(btn_del)
        actions.addStretch()
        form.addLayout(actions)

        layout.addWidget(self._form)
        layout.addStretch()
        return wrapper

    # ── dados ─────────────────────────────────────────────────────────────

    def _load(self):
        data = load_json("lore.json", [])
        self._entries = [LoreEntry.from_dict(d) for d in data]
        self._refresh_list()

    def _persist(self):
        save_json("lore.json", [e.to_dict() for e in self._entries])

    # ── lista ─────────────────────────────────────────────────────────────

    def _refresh_list(self):
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search = self._search.text().lower()
        cat = self._cat_filter.currentText()

        for entry in self._entries:
            if search and search not in entry.title.lower() and search not in entry.content.lower():
                continue
            if cat != "Todas" and entry.category != cat:
                continue

            card = LoreCard(entry)
            card.mousePressEvent = lambda e, en=entry: self._select(en)
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)

    def _filter_list(self):
        self._refresh_list()

    def _select(self, entry: LoreEntry):
        self._selected = entry
        self._placeholder.hide()
        self._form.show()
        self._title_input.setText(entry.title)
        self._cat_combo.setCurrentText(entry.category)
        self._content_edit.setPlainText(entry.content)

    # ── ações ─────────────────────────────────────────────────────────────

    def _new_entry(self):
        entry = LoreEntry(title="Nova Entrada")
        self._entries.insert(0, entry)
        self._persist()
        self._refresh_list()
        self._select(entry)

    def _save_current(self):
        if not self._selected:
            return
        self._selected.title = self._title_input.text()
        self._selected.category = self._cat_combo.currentText()
        self._selected.content = self._content_edit.toPlainText()
        self._selected.updated_at = datetime.now().isoformat()
        self._persist()
        self._refresh_list()

    def _delete_current(self):
        if not self._selected:
            return
        reply = QMessageBox.question(
            self, "Excluir",
            f"Excluir \"{self._selected.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._entries = [e for e in self._entries if e.id != self._selected.id]
            self._selected = None
            self._form.hide()
            self._placeholder.show()
            self._persist()
            self._refresh_list()

"""Página de gestão de personagens com ficha completa e gerador de NPC."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QScrollArea,
    QFrame, QGridLayout, QCheckBox, QMessageBox,
)
from PyQt6.QtCore import Qt

from src.core.character import (
    Character, generate_npc, modifier_str,
    RACES, CLASSES, ATTRIBUTES, ATTR_NAMES, SKILLS,
)
from src.core.storage import save_json, load_json


class CharacterCard(QFrame):
    """Card resumido de um personagem na lista lateral."""

    def __init__(self, char: Character, parent=None):
        super().__init__(parent)
        self.setObjectName("CharacterCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.char = char

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        name = QLabel(char.name or "Sem nome")
        name.setObjectName("CardName")

        info = QLabel(f"{char.race} • {char.char_class} • Nv {char.level}")
        info.setObjectName("CardInfo")

        tag = QLabel("NPC" if char.is_npc else "JOGADOR")
        tag.setObjectName("CardTag")
        tag.setProperty("npc", char.is_npc)

        row = QHBoxLayout()
        row.addWidget(name)
        row.addStretch()
        row.addWidget(tag)

        layout.addLayout(row)
        layout.addWidget(info)


class CharactersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._characters: list[Character] = []
        self._selected: Character | None = None
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

        root.addWidget(self._build_detail_panel(), stretch=2)

    # ── lista lateral ─────────────────────────────────────────────────────

    def _build_list_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("ListPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # cabeçalho
        header = QWidget()
        header.setObjectName("ListHeader")
        hlayout = QVBoxLayout(header)
        hlayout.setContentsMargins(12, 12, 12, 12)
        hlayout.setSpacing(8)

        title = QLabel("Personagens")
        title.setObjectName("PageTitle")
        hlayout.addWidget(title)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar...")
        self._search.setObjectName("SearchInput")
        self._search.textChanged.connect(self._filter_list)
        hlayout.addWidget(self._search)

        btns = QHBoxLayout()
        btns.setSpacing(6)

        btn_new = QPushButton("+ Novo")
        btn_new.setObjectName("PrimaryButton")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._new_character)

        btn_npc = QPushButton("⚡ Gerar NPC")
        btn_npc.setObjectName("SecondaryButton")
        btn_npc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_npc.clicked.connect(self._generate_npc)

        btns.addWidget(btn_new)
        btns.addWidget(btn_npc)
        hlayout.addLayout(btns)

        layout.addWidget(header)

        # lista com scroll
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

    # ── painel de detalhe ─────────────────────────────────────────────────

    def _build_detail_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("DetailScroll")

        self._detail = QWidget()
        self._detail_layout = QVBoxLayout(self._detail)
        self._detail_layout.setContentsMargins(20, 20, 20, 20)
        self._detail_layout.setSpacing(12)

        # placeholder inicial
        self._placeholder = QLabel("Selecione ou crie um personagem")
        self._placeholder.setObjectName("PlaceholderTitle")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_layout.addWidget(self._placeholder)
        self._detail_layout.addStretch()

        # form (inicialmente escondido)
        self._form = QWidget()
        self._form.hide()
        form = QVBoxLayout(self._form)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(14)

        # ── identidade ──
        id_label = QLabel("IDENTIDADE")
        id_label.setObjectName("SectionLabel")
        form.addWidget(id_label)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Nome do personagem")
        self._name_input.setObjectName("FormInput")

        self._level_spin = QSpinBox()
        self._level_spin.setRange(1, 30)
        self._level_spin.setPrefix("Nível ")

        row1.addWidget(self._name_input, stretch=3)
        row1.addWidget(self._level_spin, stretch=1)
        form.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self._race_combo = QComboBox()
        self._race_combo.addItems(RACES)

        self._class_combo = QComboBox()
        self._class_combo.addItems(CLASSES)

        self._npc_check = QCheckBox("NPC")

        row2.addWidget(QLabel("Raça:"))
        row2.addWidget(self._race_combo, stretch=1)
        row2.addWidget(QLabel("Classe:"))
        row2.addWidget(self._class_combo, stretch=1)
        row2.addWidget(self._npc_check)
        form.addLayout(row2)

        # ── atributos ──
        attr_label = QLabel("ATRIBUTOS")
        attr_label.setObjectName("SectionLabel")
        form.addWidget(attr_label)

        attr_grid = QGridLayout()
        attr_grid.setSpacing(8)
        self._attr_spins: dict[str, QSpinBox] = {}
        self._attr_mod_labels: dict[str, QLabel] = {}

        for i, attr in enumerate(ATTRIBUTES):
            row_idx = i // 3
            col_idx = (i % 3) * 3

            lbl = QLabel(ATTR_NAMES[attr])
            lbl.setObjectName("AttrName")

            spin = QSpinBox()
            spin.setRange(1, 30)
            spin.setValue(10)
            spin.valueChanged.connect(self._update_modifiers)
            self._attr_spins[attr] = spin

            mod_lbl = QLabel("(+0)")
            mod_lbl.setObjectName("AttrMod")
            self._attr_mod_labels[attr] = mod_lbl

            attr_grid.addWidget(lbl, row_idx, col_idx)
            attr_grid.addWidget(spin, row_idx, col_idx + 1)
            attr_grid.addWidget(mod_lbl, row_idx, col_idx + 2)

        form.addLayout(attr_grid)

        # ── combate ──
        combat_label = QLabel("COMBATE")
        combat_label.setObjectName("SectionLabel")
        form.addWidget(combat_label)

        combat_row = QHBoxLayout()
        combat_row.setSpacing(12)

        self._hp_spin = QSpinBox()
        self._hp_spin.setRange(0, 9999)
        self._hp_spin.setPrefix("HP: ")

        self._max_hp_spin = QSpinBox()
        self._max_hp_spin.setRange(1, 9999)
        self._max_hp_spin.setPrefix("Max: ")

        self._ac_spin = QSpinBox()
        self._ac_spin.setRange(0, 99)
        self._ac_spin.setPrefix("CA: ")

        combat_row.addWidget(self._hp_spin)
        combat_row.addWidget(self._max_hp_spin)
        combat_row.addWidget(self._ac_spin)
        combat_row.addStretch()
        form.addLayout(combat_row)

        # ── perícias ──
        skills_label = QLabel("PERÍCIAS")
        skills_label.setObjectName("SectionLabel")
        form.addWidget(skills_label)

        skills_grid = QGridLayout()
        skills_grid.setSpacing(4)
        self._skill_checks: dict[str, QCheckBox] = {}

        for i, skill in enumerate(SKILLS):
            cb = QCheckBox(skill)
            cb.setObjectName("SkillCheck")
            self._skill_checks[skill] = cb
            skills_grid.addWidget(cb, i // 3, i % 3)

        form.addLayout(skills_grid)

        # ── anotações ──
        notes_label = QLabel("ANOTAÇÕES")
        notes_label.setObjectName("SectionLabel")
        form.addWidget(notes_label)

        self._notes_edit = QTextEdit()
        self._notes_edit.setObjectName("NotesEdit")
        self._notes_edit.setPlaceholderText("Anotações sobre o personagem...")
        self._notes_edit.setMinimumHeight(100)
        self._notes_edit.setMaximumHeight(160)
        form.addWidget(self._notes_edit)

        # ── ações ──
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

        self._detail_layout.insertWidget(0, self._form)
        scroll.setWidget(self._detail)
        return scroll

    # ── dados ─────────────────────────────────────────────────────────────

    def _load(self):
        data = load_json("characters.json", [])
        self._characters = [Character.from_dict(d) for d in data]
        self._refresh_list()

    def _persist(self):
        save_json("characters.json", [c.to_dict() for c in self._characters])

    # ── lista ─────────────────────────────────────────────────────────────

    def _refresh_list(self):
        # limpa
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search = self._search.text().lower()
        for char in self._characters:
            if search and search not in char.name.lower():
                continue
            card = CharacterCard(char)
            card.mousePressEvent = lambda e, c=char: self._select(c)
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)

    def _filter_list(self):
        self._refresh_list()

    def _select(self, char: Character):
        self._selected = char
        self._placeholder.hide()
        self._form.show()

        self._name_input.setText(char.name)
        self._level_spin.setValue(char.level)
        self._race_combo.setCurrentText(char.race)
        self._class_combo.setCurrentText(char.char_class)
        self._npc_check.setChecked(char.is_npc)

        for attr, spin in self._attr_spins.items():
            spin.setValue(char.attributes.get(attr, 10))

        self._hp_spin.setValue(char.hp)
        self._max_hp_spin.setValue(char.max_hp)
        self._ac_spin.setValue(char.ac)

        for skill, cb in self._skill_checks.items():
            cb.setChecked(skill in char.skills)

        self._notes_edit.setPlainText(char.notes)
        self._update_modifiers()

    def _update_modifiers(self):
        for attr, spin in self._attr_spins.items():
            self._attr_mod_labels[attr].setText(f"({modifier_str(spin.value())})")

    # ── ações ─────────────────────────────────────────────────────────────

    def _new_character(self):
        char = Character(name="Novo Personagem")
        self._characters.insert(0, char)
        self._persist()
        self._refresh_list()
        self._select(char)

    def _generate_npc(self):
        char = generate_npc()
        self._characters.insert(0, char)
        self._persist()
        self._refresh_list()
        self._select(char)

    def _save_current(self):
        if not self._selected:
            return
        c = self._selected
        c.name = self._name_input.text()
        c.level = self._level_spin.value()
        c.race = self._race_combo.currentText()
        c.char_class = self._class_combo.currentText()
        c.is_npc = self._npc_check.isChecked()
        c.attributes = {a: s.value() for a, s in self._attr_spins.items()}
        c.hp = self._hp_spin.value()
        c.max_hp = self._max_hp_spin.value()
        c.ac = self._ac_spin.value()
        c.skills = [s for s, cb in self._skill_checks.items() if cb.isChecked()]
        c.notes = self._notes_edit.toPlainText()
        self._persist()
        self._refresh_list()

    def _delete_current(self):
        if not self._selected:
            return
        reply = QMessageBox.question(
            self, "Excluir",
            f"Excluir \"{self._selected.name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._characters = [c for c in self._characters if c.id != self._selected.id]
            self._selected = None
            self._form.hide()
            self._placeholder.show()
            self._persist()
            self._refresh_list()

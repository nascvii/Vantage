from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt
from src.core.dice import roll, VALID_DICE, RollResult


class DiceRollerPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._history: list[RollResult] = []
        self._selected_dice: int | None = None
        self._build_ui()

    # ── construção da UI ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(16)

        title = QLabel("Rolagem de Dados")
        title.setObjectName("PageTitle")
        left.addWidget(title)

        left.addWidget(self._build_dice_grid())
        left.addWidget(self._build_controls())
        left.addWidget(self._build_result_display())
        left.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left)

        root.addWidget(left_widget, stretch=3)
        root.addWidget(self._build_history_panel(), stretch=1)

    def _build_dice_grid(self) -> QWidget:
        label = QLabel("1. ESCOLHA O DADO")
        label.setObjectName("SectionLabel")

        grid = QHBoxLayout()
        grid.setSpacing(8)
        self._dice_buttons: dict[int, QPushButton] = {}

        for sides in VALID_DICE:
            btn = QPushButton(f"d{sides}")
            btn.setObjectName("DiceButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, s=sides: self._select_dice(s))
            self._dice_buttons[sides] = btn
            grid.addWidget(btn)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(label)
        layout.addLayout(grid)
        return widget

    def _build_controls(self) -> QWidget:
        """Quantidade, modificador e botão Rolar."""
        widget = QWidget()

        step_label = QLabel("2. CONFIGURE E ROLE")
        step_label.setObjectName("SectionLabel")

        spins_row = QHBoxLayout()
        spins_row.setSpacing(16)

        for attr, label_text, minimum, default in [
            ("_qty_spin", "Quantidade", 1, 1),
            ("_mod_spin", "Modificador", -99, 0),
        ]:
            lbl = QLabel(label_text.upper())
            lbl.setObjectName("SectionLabel")
            spin = QSpinBox()
            spin.setMinimum(minimum)
            spin.setMaximum(99)
            spin.setValue(default)
            setattr(self, attr, spin)

            col = QVBoxLayout()
            col.setSpacing(4)
            col.addWidget(lbl)
            col.addWidget(spin)
            spins_row.addLayout(col)

        self._roll_btn = QPushButton("🎲  Rolar")
        self._roll_btn.setObjectName("PrimaryButton")
        self._roll_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._roll_btn.setEnabled(False)  # desabilitado até selecionar um dado
        self._roll_btn.clicked.connect(self._roll)

        col_btn = QVBoxLayout()
        col_btn.setSpacing(4)
        col_btn.addStretch()
        col_btn.addWidget(self._roll_btn)

        spins_row.addLayout(col_btn)
        spins_row.addStretch()

        outer = QVBoxLayout(widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)
        outer.addWidget(step_label)
        outer.addLayout(spins_row)
        return widget

    def _build_result_display(self) -> QWidget:
        widget = QFrame()
        widget.setObjectName("ResultDisplay")

        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        self._result_label = QLabel("Selecione um dado para começar")
        self._result_label.setObjectName("ResultLabel")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._result_total = QLabel("—")
        self._result_total.setObjectName("ResultTotal")
        self._result_total.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._result_breakdown = QLabel("")
        self._result_breakdown.setObjectName("ResultBreakdown")
        self._result_breakdown.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self._result_label)
        layout.addWidget(self._result_total)
        layout.addWidget(self._result_breakdown)
        return widget

    def _build_history_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("HistoryPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("HISTÓRICO")
        header.setObjectName("SectionLabel")
        header.setContentsMargins(12, 10, 12, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._history_container = QWidget()
        self._history_layout = QVBoxLayout(self._history_container)
        self._history_layout.setContentsMargins(0, 0, 0, 0)
        self._history_layout.setSpacing(0)
        self._history_layout.addStretch()

        scroll.setWidget(self._history_container)

        layout.addWidget(header)
        layout.addWidget(scroll)
        return panel

    # ── lógica ────────────────────────────────────────────────────────────

    def _select_dice(self, sides: int) -> None:
        """Destaca o dado selecionado e habilita o botão Rolar."""
        # Remove seleção anterior
        if self._selected_dice is not None:
            prev = self._dice_buttons[self._selected_dice]
            prev.setProperty("selected", False)
            prev.style().unpolish(prev)
            prev.style().polish(prev)

        self._selected_dice = sides
        btn = self._dice_buttons[sides]
        btn.setProperty("selected", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)

        self._roll_btn.setEnabled(True)
        self._result_label.setText(f"d{sides} selecionado — clique em Rolar")
        self._result_total.setText("—")
        self._result_breakdown.setText("")

    def _roll(self) -> None:
        if self._selected_dice is None:
            return

        qty = self._qty_spin.value()
        mod = self._mod_spin.value()

        result = roll(self._selected_dice, qty, mod)
        self._history.insert(0, result)

        self._result_label.setText(result.label)
        self._result_total.setText(str(result.total))

        breakdown = result.rolls_str
        if mod != 0:
            sign = "+" if mod > 0 else ""
            breakdown += f"  {sign}{mod}"
        self._result_breakdown.setText(breakdown)

        self._add_history_item(result)

    def _add_history_item(self, result: RollResult) -> None:
        item = QWidget()
        item.setObjectName("HistoryItem")

        layout = QHBoxLayout(item)
        layout.setContentsMargins(12, 8, 12, 8)

        lbl_label = QLabel(result.label)
        lbl_total = QLabel(str(result.total))
        lbl_total.setStyleSheet("color: #c9a84c; font-weight: 600;")
        time_str = result.timestamp.strftime("%H:%M:%S")
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("color: #a7a9be; font-size: 11px;")

        layout.addWidget(lbl_label)
        layout.addStretch()
        layout.addWidget(lbl_total)
        layout.addWidget(lbl_time)

        self._history_layout.insertWidget(0, item)

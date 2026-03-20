"""Editor de mapas 2D com pintura de terreno, tokens e zoom."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QLineEdit, QInputDialog,
    QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QWheelEvent, QFont

from src.core.map_data import MapData, Token, TERRAINS, TERRAIN_IDS, TOKEN_COLORS
from src.core.storage import save_json, load_json


# ── Canvas do mapa ────────────────────────────────────────────────────────

class MapCanvas(QWidget):
    """Widget de desenho do mapa 2D com pintura, tokens, pan e zoom."""

    CELL = 32  # tamanho base da célula em pixels

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._map: MapData | None = None
        self._zoom = 1.0
        self._offset = QPoint(0, 0)
        self._drag_start: QPoint | None = None
        self._drag_offset_start: QPoint | None = None

        self._tool = "paint"           # paint | erase | token
        self._terrain = "grama"
        self._token_name = ""
        self._token_color = TOKEN_COLORS[0]
        self._painting = False

    def set_map(self, m: MapData | None):
        self._map = m
        self._zoom = 1.0
        self._offset = QPoint(0, 0)
        self.update()

    def set_tool(self, tool: str):
        self._tool = tool

    def set_terrain(self, terrain: str):
        self._terrain = terrain

    def set_token_config(self, name: str, color: str):
        self._token_name = name
        self._token_color = color

    # ── coordenadas ───────────────────────────────────────────────────────

    def _screen_to_grid(self, pos: QPoint) -> tuple[int, int]:
        x = (pos.x() - self._offset.x()) / self._zoom
        y = (pos.y() - self._offset.y()) / self._zoom
        col = int(x // self.CELL)
        row = int(y // self.CELL)
        return row, col

    def _in_bounds(self, row: int, col: int) -> bool:
        if not self._map:
            return False
        return 0 <= row < self._map.height and 0 <= col < self._map.width

    # ── pintura ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        if not self._map:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self._offset)
        p.scale(self._zoom, self._zoom)

        cell = self.CELL
        m = self._map

        # terreno
        for r in range(m.height):
            for c in range(m.width):
                terrain_id = m.grid[r][c]
                color = TERRAINS.get(terrain_id, TERRAINS["vazio"])["color"]
                p.fillRect(c * cell, r * cell, cell, cell, QColor(color))

        # grade
        pen = QPen(QColor("#2d2b3d"), 1)
        p.setPen(pen)
        for r in range(m.height + 1):
            p.drawLine(0, r * cell, m.width * cell, r * cell)
        for c in range(m.width + 1):
            p.drawLine(c * cell, 0, c * cell, m.height * cell)

        # tokens
        p.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        for token in m.tokens:
            cx = token.col * cell + cell // 2
            cy = token.row * cell + cell // 2
            radius = cell // 2 - 3
            p.setBrush(QColor(token.color))
            p.setPen(QPen(QColor("#fffffe"), 2))
            p.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

            p.setPen(QColor("#fffffe"))
            label = token.name[0].upper() if token.name else "?"
            p.drawText(QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
                       Qt.AlignmentFlag.AlignCenter, label)

        p.end()

    # ── mouse ─────────────────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._drag_start = event.globalPosition().toPoint()
            self._drag_offset_start = QPoint(self._offset)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            row, col = self._screen_to_grid(event.pos())
            if self._tool == "token":
                self._place_token(row, col)
            elif self._tool in ("paint", "erase"):
                self._painting = True
                self._apply_brush(row, col)

        if event.button() == Qt.MouseButton.RightButton:
            row, col = self._screen_to_grid(event.pos())
            self._remove_token(row, col)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_start and self._drag_offset_start:
            delta = event.globalPosition().toPoint() - self._drag_start
            self._offset = self._drag_offset_start + delta
            self.update()
            return

        if self._painting:
            row, col = self._screen_to_grid(event.pos())
            self._apply_brush(row, col)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_start = None
        self._drag_offset_start = None
        self._painting = False

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom = max(0.2, min(5.0, self._zoom * factor))
        self.update()

    # ── ações ─────────────────────────────────────────────────────────────

    def _apply_brush(self, row: int, col: int):
        if not self._in_bounds(row, col):
            return
        if self._tool == "paint":
            self._map.grid[row][col] = self._terrain
        elif self._tool == "erase":
            self._map.grid[row][col] = "vazio"
        self.update()

    def _place_token(self, row: int, col: int):
        if not self._in_bounds(row, col) or not self._token_name:
            return
        # remove token existente na mesma posição
        self._map.tokens = [t for t in self._map.tokens if not (t.row == row and t.col == col)]
        self._map.tokens.append(Token(self._token_name, row, col, self._token_color))
        self.update()

    def _remove_token(self, row: int, col: int):
        if not self._map:
            return
        self._map.tokens = [t for t in self._map.tokens if not (t.row == row and t.col == col)]
        self.update()


# ── Página do editor ──────────────────────────────────────────────────────

class MapEditorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._maps: list[MapData] = []
        self._current: MapData | None = None
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_toolbar())

        self._canvas = MapCanvas()
        root.addWidget(self._canvas, stretch=1)

    def _build_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("MapToolbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # ── mapa ──
        layout.addWidget(QLabel("Mapa:"))
        self._map_combo = QComboBox()
        self._map_combo.setMinimumWidth(140)
        self._map_combo.currentIndexChanged.connect(self._on_map_changed)
        layout.addWidget(self._map_combo)

        btn_new = QPushButton("Novo")
        btn_new.setObjectName("SecondaryButton")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._new_map)
        layout.addWidget(btn_new)

        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save)
        layout.addWidget(btn_save)

        btn_del = QPushButton("Excluir")
        btn_del.setObjectName("DangerButton")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self._delete_map)
        layout.addWidget(btn_del)

        self._add_separator(layout)

        # ── ferramentas ──
        layout.addWidget(QLabel("Ferramenta:"))
        self._tool_buttons: dict[str, QPushButton] = {}
        for tool_id, label in [("paint", "🖌️ Pintar"), ("erase", "🧹 Apagar"), ("token", "📍 Token")]:
            btn = QPushButton(label)
            btn.setObjectName("ToolButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, t=tool_id: self._set_tool(t))
            self._tool_buttons[tool_id] = btn
            layout.addWidget(btn)

        self._tool_buttons["paint"].setChecked(True)

        self._add_separator(layout)

        # ── terreno ──
        layout.addWidget(QLabel("Terreno:"))
        self._terrain_combo = QComboBox()
        for tid, info in TERRAINS.items():
            self._terrain_combo.addItem(info["label"], tid)
        self._terrain_combo.setCurrentIndex(1)  # grama
        self._terrain_combo.currentIndexChanged.connect(self._on_terrain_changed)
        layout.addWidget(self._terrain_combo)

        self._terrain_preview = QFrame()
        self._terrain_preview.setFixedSize(20, 20)
        self._terrain_preview.setStyleSheet(f"background-color: {TERRAINS['grama']['color']}; border-radius: 3px;")
        layout.addWidget(self._terrain_preview)

        self._add_separator(layout)

        # ── config de token ──
        self._token_name_input = QLineEdit()
        self._token_name_input.setPlaceholderText("Nome do token")
        self._token_name_input.setObjectName("TokenNameInput")
        self._token_name_input.setMaximumWidth(120)
        self._token_name_input.textChanged.connect(self._on_token_config_changed)
        layout.addWidget(self._token_name_input)

        self._token_color_combo = QComboBox()
        for color in TOKEN_COLORS:
            self._token_color_combo.addItem("⬤", color)
        self._token_color_combo.currentIndexChanged.connect(self._on_token_config_changed)
        layout.addWidget(self._token_color_combo)

        layout.addStretch()
        return bar

    def _add_separator(self, layout: QHBoxLayout):
        sep = QFrame()
        sep.setObjectName("ToolSep")
        sep.setFixedWidth(1)
        sep.setFixedHeight(24)
        layout.addWidget(sep)

    # ── dados ─────────────────────────────────────────────────────────────

    def _load(self):
        data = load_json("maps.json", [])
        self._maps = [MapData.from_dict(d) for d in data]
        self._refresh_combo()
        if self._maps:
            self._map_combo.setCurrentIndex(0)

    def _persist(self):
        save_json("maps.json", [m.to_dict() for m in self._maps])

    def _refresh_combo(self):
        self._map_combo.blockSignals(True)
        self._map_combo.clear()
        for m in self._maps:
            self._map_combo.addItem(m.name, m.id)
        self._map_combo.blockSignals(False)

    # ── eventos ───────────────────────────────────────────────────────────

    def _on_map_changed(self, idx: int):
        if 0 <= idx < len(self._maps):
            self._current = self._maps[idx]
            self._canvas.set_map(self._current)

    def _on_terrain_changed(self):
        tid = self._terrain_combo.currentData()
        self._canvas.set_terrain(tid)
        color = TERRAINS[tid]["color"]
        self._terrain_preview.setStyleSheet(f"background-color: {color}; border-radius: 3px;")

    def _on_token_config_changed(self):
        name = self._token_name_input.text()
        color = self._token_color_combo.currentData() or TOKEN_COLORS[0]
        self._canvas.set_token_config(name, color)

    def _set_tool(self, tool: str):
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool)
        self._canvas.set_tool(tool)

    # ── ações ─────────────────────────────────────────────────────────────

    def _new_map(self):
        name, ok = QInputDialog.getText(self, "Novo Mapa", "Nome do mapa:")
        if not ok or not name.strip():
            return

        w, ok_w = QInputDialog.getInt(self, "Largura", "Largura (colunas):", 30, 5, 200)
        if not ok_w:
            return
        h, ok_h = QInputDialog.getInt(self, "Altura", "Altura (linhas):", 20, 5, 200)
        if not ok_h:
            return

        m = MapData(name=name.strip(), width=w, height=h)
        self._maps.append(m)
        self._persist()
        self._refresh_combo()
        self._map_combo.setCurrentIndex(len(self._maps) - 1)

    def _save(self):
        if self._current:
            self._persist()

    def _delete_map(self):
        if not self._current:
            return
        reply = QMessageBox.question(
            self, "Excluir mapa",
            f"Excluir \"{self._current.name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._maps = [m for m in self._maps if m.id != self._current.id]
            self._current = None
            self._canvas.set_map(None)
            self._persist()
            self._refresh_combo()

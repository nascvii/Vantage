"""Modelo de dados para mapas 2D."""
import uuid
from dataclasses import dataclass, field, asdict


TERRAINS: dict[str, dict] = {
    "vazio":          {"color": "#1a1826", "label": "Vazio"},
    "grama":          {"color": "#2d6a27", "label": "Grama"},
    "floresta":       {"color": "#1a4a15", "label": "Floresta"},
    "agua":           {"color": "#1a5a8a", "label": "Água"},
    "agua_profunda":  {"color": "#0f2a5a", "label": "Água Profunda"},
    "pedra":          {"color": "#6a6a6a", "label": "Pedra"},
    "areia":          {"color": "#c4a35a", "label": "Areia"},
    "lava":           {"color": "#9b3500", "label": "Lava"},
    "estrada":        {"color": "#6b5b3a", "label": "Estrada"},
    "madeira":        {"color": "#5a3a1a", "label": "Madeira"},
}

TERRAIN_IDS = list(TERRAINS.keys())

TOKEN_COLORS = ["#c9a84c", "#8b2635", "#2a7a4a", "#4a6ac9", "#c94a8b", "#c97a4a", "#7a4ac9", "#4ac9a8"]


@dataclass
class Token:
    name: str
    row: int
    col: int
    color: str = "#c9a84c"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Token":
        return cls(**d)


@dataclass
class MapData:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Novo Mapa"
    width: int = 30
    height: int = 20
    grid: list[list[str]] = field(default=None)
    tokens: list[Token] = field(default_factory=list)

    def __post_init__(self):
        if self.grid is None:
            self.grid = [["vazio"] * self.width for _ in range(self.height)]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "grid": self.grid,
            "tokens": [t.to_dict() for t in self.tokens],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MapData":
        tokens = [Token.from_dict(t) for t in d.get("tokens", [])]
        return cls(
            id=d["id"], name=d["name"],
            width=d["width"], height=d["height"],
            grid=d["grid"], tokens=tokens,
        )

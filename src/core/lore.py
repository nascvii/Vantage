"""Modelo de dados para anotações de lore."""
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime


DEFAULT_CATEGORIES = ["Locais", "NPCs", "Eventos", "Itens", "Facções", "Notas"]


@dataclass
class LoreEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    category: str = "Notas"
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LoreEntry":
        return cls(**d)

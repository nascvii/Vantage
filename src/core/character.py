"""Modelo de personagem e gerador de NPC."""
import random
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime


RACES = [
    "Humano", "Elfo", "Anão", "Halfling", "Meio-Elfo",
    "Meio-Orc", "Gnomo", "Tiefling", "Draconato",
]

CLASSES = [
    "Guerreiro", "Mago", "Ladino", "Clérigo", "Paladino",
    "Ranger", "Bárbaro", "Bardo", "Druida", "Feiticeiro",
    "Bruxo", "Monge",
]

ATTRIBUTES = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]

ATTR_NAMES = {
    "FOR": "Força", "DES": "Destreza", "CON": "Constituição",
    "INT": "Inteligência", "SAB": "Sabedoria", "CAR": "Carisma",
}

SKILLS = [
    "Acrobacia", "Arcanismo", "Atletismo", "Atuação", "Enganação",
    "Furtividade", "História", "Intimidação", "Intuição", "Investigação",
    "Lidar com Animais", "Medicina", "Natureza", "Percepção", "Persuasão",
    "Prestidigitação", "Religião", "Sobrevivência",
]

FIRST_NAMES = [
    "Aldric", "Bram", "Cedric", "Dorian", "Elric", "Fenris", "Gareth",
    "Hadrian", "Jareth", "Kael", "Lothar", "Merric", "Theron", "Silas",
    "Orin", "Rolf", "Varn", "Wulf", "Aria", "Brynn", "Celeste", "Dara",
    "Elara", "Freya", "Gwen", "Helena", "Iris", "Kira", "Lyra", "Mira",
    "Nova", "Sera", "Thalia", "Vera", "Wren", "Petra", "Yara", "Rhea",
]

LAST_NAMES = [
    "Ferrolume", "Sombravento", "Pedrafogo", "Luanegra", "Raioprateado",
    "Trovãobranco", "Escurâmbar", "Solnascente", "Estrelamorta",
    "Sangreverde", "Cinzaflor", "Ventogélido", "Cristalrubro", "Neblina",
    "Clareira", "Corvonix", "Flamejante", "Tormentoso", "Auroreal",
]


@dataclass
class Character:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    race: str = "Humano"
    char_class: str = "Guerreiro"
    level: int = 1
    hp: int = 10
    max_hp: int = 10
    ac: int = 10
    attributes: dict[str, int] = field(default_factory=lambda: {a: 10 for a in ATTRIBUTES})
    skills: list[str] = field(default_factory=list)
    notes: str = ""
    is_npc: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        return cls(**data)


def modifier(score: int) -> int:
    return (score - 10) // 2


def modifier_str(score: int) -> str:
    m = modifier(score)
    return f"+{m}" if m >= 0 else str(m)


def _roll_4d6_drop_lowest() -> int:
    rolls = sorted(random.randint(1, 6) for _ in range(4))
    return sum(rolls[1:])


def generate_npc() -> Character:
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    race = random.choice(RACES)
    char_class = random.choice(CLASSES)
    level = random.randint(1, 10)
    attrs = {a: _roll_4d6_drop_lowest() for a in ATTRIBUTES}
    con_mod = modifier(attrs["CON"])
    max_hp = max(1, (8 + con_mod) * level)

    return Character(
        name=name,
        race=race,
        char_class=char_class,
        level=level,
        hp=max_hp,
        max_hp=max_hp,
        ac=10 + modifier(attrs["DES"]),
        attributes=attrs,
        skills=random.sample(SKILLS, random.randint(2, 5)),
        is_npc=True,
    )

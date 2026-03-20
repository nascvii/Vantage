"""Lógica pura de rolagem de dados — sem dependências de UI."""
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


DiceType = Literal[4, 6, 8, 10, 12, 20, 100]
VALID_DICE: list[DiceType] = [4, 6, 8, 10, 12, 20, 100]


@dataclass
class RollResult:
    dice_type: int          # ex: 20
    quantity: int           # ex: 2
    modifier: int           # ex: +3
    rolls: list[int]        # resultados individuais
    total: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def label(self) -> str:
        sign = "+" if self.modifier >= 0 else ""
        mod_str = f" {sign}{self.modifier}" if self.modifier != 0 else ""
        return f"{self.quantity}d{self.dice_type}{mod_str}"

    @property
    def rolls_str(self) -> str:
        return " + ".join(str(r) for r in self.rolls)


def roll(dice_type: int, quantity: int = 1, modifier: int = 0) -> RollResult:
    """Rola `quantity` dados de `dice_type` lados e aplica `modifier`."""
    if quantity < 1:
        raise ValueError("Quantidade deve ser >= 1")
    if dice_type not in VALID_DICE:
        raise ValueError(f"Tipo de dado inválido: d{dice_type}")

    rolls = [random.randint(1, dice_type) for _ in range(quantity)]
    total = sum(rolls) + modifier
    return RollResult(
        dice_type=dice_type,
        quantity=quantity,
        modifier=modifier,
        rolls=rolls,
        total=total,
    )

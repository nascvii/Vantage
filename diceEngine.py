from random import randint, choice

def rollXdY(x, y):
    return list(randint(1, y) for _ in range(x))

# Dado explosivo, role dados adicionais até parar de critar
def rollXdYexp(x, y):
    roll = rollXdY(x, y)
    soma = sum(roll)
    if roll[0] == y:
        soma += rollXdYexp(x, y)
    return soma

# 1d10 roll do The Witcher. Explode no 10 e soma, e explode no 1 e reduz
def skillCheck(base: int = 0):
    roll = rollXdY(1, 10)[0]
    if roll == 10:
        roll += rollXdYexp(1, 10)
    elif roll == 1:
        roll -= rollXdYexp(1, 10)
    return roll+base


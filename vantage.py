import random


def rolar_d10():
    return random.randint(1, 10)


def rolagem_especial():
    primeiro = rolar_d10()
    rolls = [primeiro]

    # Dice boom positive : if the result is 10, keep rolling and adding until you get a result differet from 10. the total will be positive.
    if primeiro == 10:
        total = primeiro
        while True:
            novo = rolar_d10()
            rolls.append(novo)
            total += novo
            if novo != 10:
                break
        return {"rolls": rolls, "total": total}

    # Dice boom negative : if the result is 1, keep rolling and adding until you get a result differet from 1. The total will be negative.
    elif primeiro == 1:
        total = primeiro
        while True:
            novo = rolar_d10()
            rolls.append(novo)
            total += novo
            if novo != 10:
                break
        return {"rolls": rolls, "total": -total}  # resultado negativo

    # Normal dice roll : the result is equal to the value of the first roll, without any additional rolls.
    else:
        return {"rolls": rolls, "total": primeiro}


# Exemplo de uso
resultado = rolagem_especial()
print(f"Rolls: {resultado['rolls']}")
print(f"Total: {resultado['total']}")

def ife(value: bool, a: int = 1, b: int = -1) -> int:
    """
    Si la valeur est True, renvoie a, sinon renvoie b

    :param value: booléen
    :type value: bool
    :param a: La valeur à renvoyer si la valeur est True, defaults to 1
    :type a: int (optional)
    :param b: La valeur à renvoyer si la condition est fausse
    :type b: int (optional)
    :return: a si value est vraie sinon b
    """
    return a if value else b


def deepcopy2d(x: list) -> list:
    """
    Retourne une copie d'une liste 2D

    :param x: la 2d liste à copier
    :return: La copie de la liste.
    """
    return [row[:] for row in x]

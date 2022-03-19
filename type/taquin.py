from a_star import AStarNode, AStarResult, def_node_attr, wrap_search
from utils import ife, deepcopy2d


class TaquinState(AStarNode):

    def __init__(self, rows: list[list[int]]):
        self.rows = rows
        self.col_count = len(rows[0])
        self.row_count = len(rows)
        self.size = self.row_count * self.col_count
        self.cache_index: {int: int} = {}

        self.update_indexes()

    def __repr__(self):
        return f"TaquinState(rows={self.rows})"

    def __str__(self):
        return f"TaquinState(rows={self.rows})"

    def __eq__(self, other):
        for row in self.rows:
            for value in row:
                if self.get_index(value) != other.get_index(value):
                    return False

        return True

    def __hash__(self):
        r = 0
        for row in self.rows:
            for v in row:
                r += hash(v)

        return hash(r)

    def update_indexes(self) -> None:
        for y, row in enumerate(self.rows):
            for index, v in enumerate(row):
                self.cache_index[v] = index + (y * self.col_count)

    def get_index(self, value: int) -> int:
        if value in self.cache_index:
            return self.cache_index[value]
        return -1

    def children(self) -> list:
        """
        Construit la liste des nœuds fils du nœud actuel

        :return: Une liste d'états.
        """

        children = []

        empty_index = self.get_index(0)
        x = empty_index % self.col_count
        y = empty_index // self.row_count

        # Échange droit
        if x != self.col_count - 1:
            new_rows = deepcopy2d(self.rows)

            prev = new_rows[y][x + 1]
            new_rows[y][x + 1] = new_rows[y][x]
            new_rows[y][x] = prev

            children.append(TaquinState(new_rows))

        # Échange haut
        if y != 0:
            new_rows = deepcopy2d(self.rows)

            prev = new_rows[y - 1][x]
            new_rows[y - 1][x] = new_rows[y][x]
            new_rows[y][x] = prev

            children.append(TaquinState(new_rows))

        # Échange gauche
        if x != 0:
            new_rows = deepcopy2d(self.rows)

            prev = new_rows[y][x - 1]
            new_rows[y][x - 1] = new_rows[y][x]
            new_rows[y][x] = prev

            children.append(TaquinState(new_rows))

        # Échange bas
        if y != self.row_count - 1:
            new_rows = deepcopy2d(self.rows)

            prev = new_rows[y + 1][x]
            new_rows[y + 1][x] = new_rows[y][x]
            new_rows[y][x] = prev

            children.append(TaquinState(new_rows))

        return children


def render_node(node: TaquinState, result: AStarResult) -> str:
    lines = []

    lines.append(f"#{result.step[node]}")
    lines.append("")
    try:
        h = result.h_score[node]
        g = result.g_score[node]
        lines.append(f"f(n) = {h} + {g} = {h + g}")
    except Exception as e:
        print(type(e))

    lines.append("")

    for row in node.rows:
        lines.append("|".join(map(lambda x: f"{x:2d}", row)))
        lines.append("---" * len(row))

    return "\n".join(lines)


def hamming(state: TaquinState, _: TaquinState) -> float:
    # Nombre de pièces qui ne sont pas à leur position (distance Hamming)
    state.update_indexes()
    res = 0
    for i in range(state.size - 1):
        res += ife(state.get_index(i + 1) == i, a=0, b=1)
    return res


def manhattan(state: TaquinState, final_state: TaquinState) -> float:
    state.update_indexes()
    res = 0
    # Pour chaque point, on calcule la distance entre le point actuel et le point final
    # La somme donne la distance de manhattan.
    for i in range(state.size):
        from_index = state.get_index(i)
        to_index = final_state.get_index(i)

        y = (from_index // state.row_count) - (to_index // state.row_count)
        x = (from_index % state.col_count) - (to_index % state.col_count)

        res += abs(y) + abs(x)
    return res


def _3x3():
    def heuristic_2(state: TaquinState) -> float:
        state.update_indexes()
        return (ife(state.get_index(1) == 0, a=0, b=1)) + \
               (ife(state.get_index(2) == 1, a=0, b=1)) + \
               (ife(state.get_index(3) == 2, a=0, b=1)) + \
               (ife(state.get_index(7) == 3, a=0, b=1)) + \
               (ife(state.get_index(0) == 4, a=0, b=1)) + \
               (ife(state.get_index(4) == 5, a=0, b=1)) + \
               (ife(state.get_index(8) == 6, a=0, b=1)) + \
               (ife(state.get_index(6) == 7, a=0, b=1)) + \
               (ife(state.get_index(5) == 8, a=0, b=1))

    from_state = TaquinState([
        [1, 4, 2],
        [7, 6, 3],
        [8, 0, 5]
    ])

    to_state = TaquinState([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ])

    wrap_search(from_state, to_state, hamming, 1, render_node, def_node_attr, "out/taquin-3x3-hamming.png")
    wrap_search(from_state, to_state, manhattan, 1, render_node, def_node_attr, "out/taquin-3x3-manhattan.png")


def _4x4():
    from_state = TaquinState([
        [12, 1, 3, 4],
        [2, 13, 14, 5],
        [11, 10, 8, 6],
        [9, 15, 7, 0]
    ])

    to_state = TaquinState([
        [2, 12, 3, 4],
        [1, 13, 0, 5],
        [11, 14, 7, 8],
        [10, 9, 15, 6]
    ])

    wrap_search(from_state, to_state, manhattan, 1, render_node, def_node_attr, "out/taquin-4x4-manhattan.png")
    # wrap_search(from_state, to_state, hamming,1, render_node, def_node_attr, "out/taquin-4x4-hamming.png")  # Trop long !


def main():
    _3x3()
    _4x4()


if __name__ == '__main__':
    main()

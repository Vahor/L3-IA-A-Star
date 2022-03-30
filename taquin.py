from dataclasses import dataclass, field

from a_star import AStarNode, AStarResult, def_node_attr, wrap_search
from utils import ife, deepcopy2d


@dataclass(frozen=True, order=True)  # Le nombre d'étapes change aussi selon l'ordre.
class TaquinState(AStarNode):
    rows: list[list[int]] = field(hash=False)
    cache_index: {int: int} = field(default_factory=dict, hash=False)

    def __post_init__(self):
        self.update_indexes()

    @property
    def col_count(self):
        return len(self.rows[0])

    @property
    def row_count(self):
        return len(self.rows)

    @property
    def size(self):
        return self.row_count * self.col_count

    def __eq__(self, other):
        for row in self.rows:
            for value in row:
                if self.get_index(value) != other.get_index(value):
                    return False

        return True

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

    # On affiche l'ordre de parcours du nœud
    if node in result.visited:
        lines.append(f"#{result.visited[node]}")
    else:
        lines.append("")
    lines.append("")

    # Ajout du score dans l'affichage
    try:
        h = result.h_score[node]
        g = result.g_score[node]
        lines.append(f"f(n) = {h} + {g:.1f} = {h + g}")
    except KeyError:
        pass

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

    wrap_search(from_state, to_state, hamming, 1, render_node, def_node_attr, "out/taquin/taquin-3x3-hamming.png")
    wrap_search(from_state, to_state, manhattan, 1, render_node, def_node_attr, "out/taquin/taquin-3x3-manhattan.png")


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

    wrap_search(from_state, to_state, manhattan, 1, render_node, def_node_attr, "out/taquin/taquin-4x4-manhattan.png", False)
    # wrap_search(from_state, to_state, manhattan, 0.1, render_node, def_node_attr, "out/taquin/taquin-4x4-manhattan-g-s.png", False) # 60s environ 1800 noeuds
    # wrap_search(from_state, to_state, manhattan, 2, render_node, def_node_attr, "out/taquin/taquin-4x4-manhattan-g-b.png", False) # [17-50]s environ 1100-3600 noeuds
    # wrap_search(from_state, to_state, hamming,1, render_node, def_node_attr, "out/taquin/taquin-4x4-hamming.png")  # Trop long !


def main():
    _3x3()
    _4x4()


if __name__ == '__main__':
    main()

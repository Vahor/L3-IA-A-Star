from dataclasses import dataclass, field

from a_star import AStarNode, AStarResult, def_node_attr, wrap_search
from utils import ife, deepcopy2d


@dataclass(frozen=True)  # Le nombre d'étapes change aussi selon l'ordre.
class MachineState(AStarNode):
    arm: str or None
    stacks: list[list[str]] = field(hash=False)
    max_stacks: int

    def __post_init__(self):
        # On remplit les piles avec des listes vides au besoin
        for i in range(self.max_stacks - len(self.stacks)):
            self.stacks.append([])

    @property
    def size(self):
        return sum(len(stack) for stack in self.stacks) + (0 if self.arm is None else 1)

    def get_free_blocks(self) -> list[str]:
        """
        Renvoie la liste des premiers éléments de chaque pile non vide
        :return: La liste des blocs en tête de file.
        """
        free_blocks = []

        for stack in self.stacks:
            if stack:
                free_blocks.append(stack[0])

        return free_blocks

    def __eq__(self, other):
        if self.arm != other.arm:
            return False

        for stack in self.stacks:
            if stack not in other.stacks:
                return False

        return True

    def is_above(self, first: str, second: str or None) -> bool:
        """
        :param first: La lettre que nous cherchons
        :type first: str
        :param second: La lettre qui doit être en dessous de {first}
        :type second: str or None
        :return: Vrai ou faux
        """

        # On cherche où est {first}
        # Et on regarde si {second} est en dessous
        for stack in self.stacks:
            for (i, letter) in enumerate(stack):
                if letter == first:
                    if i + 1 >= len(stack):
                        return second is None
                    return stack[i + 1] == second
        return False

    def is_free(self, letter: str) -> bool:
        """
        :param letter: la lettre dont on veut savoir l'état
        :type letter: str
        :return: Vrai si la lettre est libre, Faux sinon.
        """

        # Si le bloc est dans le bras, il n'est pas libre
        if self.arm == letter:
            return False

        # Si le bloc n'est pas le premier element de la pile, c'est qu'il a quelque chose au-dessus de lui
        for stack in self.stacks:
            if stack and stack[0] == letter:
                return True

        return False

    def on_table(self, letter: str) -> bool:
        """
        :param letter: la lettre dont on veut savoir l'état
        :type letter: str
        :return: Vrai si la lettre est sur la table, Faux sinon.
        """

        # Si le bloc est dans le bras, il n'est pas sur la table
        if self.arm == letter:
            return False

        # Si le bloc est le dernier element de la pile, il est sur la table
        for stack in self.stacks:
            if stack and stack[-1] == letter:
                return True

        return False

    def children(self) -> list:
        """
        Construit la liste des nœuds fils du nœud actuel

        :return: Une liste d'états.
        """

        children = []

        # Si le bras est libre, on essaie de porter un element en tête de file
        if self.arm is None:

            # Pour tous les blocs libres, on créé un état qui porte ce bloc
            for free_block in self.get_free_blocks():
                new_stacks = deepcopy2d(self.stacks)

                for stack in new_stacks:  # On retire le bloc concerné dans nos listes
                    if free_block in stack:
                        stack.remove(free_block)
                        break

                state = MachineState(free_block, new_stacks, self.max_stacks)

                children.append(state)

        else:  # Sinon, on essaie de poser sur une tête de file, ou dans une nouvelle file
            for i in range(self.max_stacks):
                new_stacks = deepcopy2d(self.stacks)
                # On ajoute le bloc qu'on porte à la tête de la i-ème file
                # Si la file est vide cela correspondra à un bloc posé sur la table

                new_stacks[i].insert(0, self.arm)

                state = MachineState(None, new_stacks, self.max_stacks)

                children.append(state)

        return children


def render_node(node: MachineState, result: AStarResult) -> str:
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
        lines.append(f"f(n) = {h} + {g:.1f} = {(h + g):.1f}")
    except KeyError:
        pass

    lines.append("")
    lines.append(f"Bras : {node.arm}")

    # On affiche les piles sous la forme : ABC.
    # On complète avec des underscores si la pile n'est pas complète
    for i, stack in enumerate(node.stacks):
        lines.append(f"Pile #{i} : " + " ".join(stack[::-1]) + " _" * (node.size - len(stack)))

    return "\n".join(lines)


def td_3():
    def heuristic_1(state: MachineState, _) -> float:
        return 6 - \
               (ife(state.is_above('A', 'B')) * 1) - \
               (ife(state.is_above('B', 'C')) * 2) - \
               (ife(state.is_above('C', None)) * 3)

    def heuristic_2(state: MachineState, _) -> float:
        return 3 - \
               (ife(state.is_above('A', 'B'))) - \
               (ife(state.is_above('B', 'C'))) - \
               (ife(state.is_above('C', None)))

    from_state = MachineState(None, [['A'], ['B'], ['C']], 3)
    to_state = MachineState(None, [['A', 'B', 'C']], 3)

    wrap_search(from_state, to_state, heuristic_1, 1, render_node, def_node_attr, "out/machine/machine-3-heuristic_1")
    wrap_search(from_state, to_state, heuristic_2, 1, render_node, def_node_attr, "out/machine/machine-3-heuristic_2")
    wrap_search(from_state, to_state, heuristic_2, 0.1, render_node, def_node_attr,
                "out/machine/machine-3-heuristic_2-g-b")


def _5():
    def heuristic_1(state: MachineState, _) -> float:
        return 10 - \
               (ife(state.is_above('A', 'B')) * 1) - \
               (ife(state.is_above('B', 'C')) * 2) - \
               (ife(state.is_above('C', 'D')) * 3) - \
               (ife(state.is_above('E', None)) * 4)

    def heuristic_2(state: MachineState, _) -> float:
        return 4 - \
               (ife(state.is_above('A', 'B'))) - \
               (ife(state.is_above('B', 'C'))) - \
               (ife(state.is_above('C', 'D'))) - \
               (ife(state.is_above('E', None)))

    from_state = MachineState('E', [['C', 'A'], ['B'], ['D']], 3)
    to_state = MachineState(None, [['A', 'B', 'C', 'D', 'E']], 3)

    wrap_search(from_state, to_state, heuristic_1, 1, render_node, def_node_attr, "out/machine/machine-5-heuristic_1")
    wrap_search(from_state, to_state, heuristic_1, 0.1, render_node, def_node_attr,
                "out/machine/machine-5-heuristic_1-g-s",
                False)
    wrap_search(from_state, to_state, heuristic_1, 2, render_node, def_node_attr,
                "out/machine/machine-5-heuristic_1-g-b",
                False)

    wrap_search(from_state, to_state, heuristic_2, 1, render_node, def_node_attr, "out/machine/machine-5-heuristic_2",
                False)


def main():
    td_3()
    _5()


if __name__ == '__main__':
    main()

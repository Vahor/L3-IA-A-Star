from a_star import AStarNode, AStarResult, def_node_attr, wrap_search
from utils import ife, deepcopy2d


class MachineState(AStarNode):

    def __init__(self, arm: str or None, stacks: list[list[str]], max_stacks: int = 3):
        self.arm = arm
        self.stacks = stacks
        self.max_stacks = max_stacks
        self.size = sum(len(stack) for stack in stacks) + (0 if arm is None else 1)

        # On remplit les piles avec des listes vides au besoin
        for i in range(max_stacks - len(stacks)):
            stacks.append([])

        pass

    def __repr__(self):
        return f"MachineState(arm={self.arm}, stacks={self.stacks}, max_stacks={self.max_stacks})"

    def __str__(self):
        return f"MachineState(arm={self.arm}, stacks={self.stacks})"

    def __eq__(self, other):
        if self.arm != other.arm:
            return False

        for stack in self.stacks:
            if stack not in other.stacks:
                return False

        return True

    def __hash__(self):
        r = 0
        for stack in self.stacks:
            for v in stack:
                r += hash(v)

        return hash((self.arm, self.max_stacks, r))

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

    def children(self) -> list:
        """
        Construit la liste des nœuds fils du nœud actuel

        :return: Une liste d'états.
        """

        children = []

        # Si le bras est libre, on essaie de porter un element en tête de file
        if self.arm is None:

            for free_block in self.get_free_blocks():
                new_stacks = deepcopy2d(self.stacks)

                for stack in new_stacks:  # On retire le bloc concerné dans nos listes
                    if free_block in stack:
                        stack.remove(free_block)
                        break

                state = MachineState(free_block, new_stacks)

                children.append(state)

        else:  # Sinon, on essaie de poser sur une tête de file, ou dans une nouvelle file
            for i in range(self.max_stacks):
                new_stacks = deepcopy2d(self.stacks)
                # On ajoute le bloc qu'on porte, dans la i-ème file
                new_stacks[i].insert(0, self.arm)

                state = MachineState(None, new_stacks)

                children.append(state)

        return children


def render_node(node: MachineState, result: AStarResult) -> str:
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
    lines.append(f"Bras : {node.arm}")

    for i, stack in enumerate(node.stacks):
        lines.append(f"Pile #{i} : " + " ".join(stack[::-1]) + " _" * (node.size - len(stack)))

    return "\n".join(lines)


def td():
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

    from_state = MachineState(None, [['C', 'A'], ['B']])
    to_state = MachineState(None, [['A', 'B', 'C']])

    wrap_search(from_state, to_state, heuristic_1, 1, render_node, def_node_attr, "out/machine-td-heuristic_1.png")
    wrap_search(from_state, to_state, heuristic_2, 1, render_node, def_node_attr, "out/machine-td-heuristic_2.png")


def random():
    from_state = MachineState('E', [['C', 'A'], ['B'], ['D']])
    to_state = MachineState(None, [['A', 'B', 'C', 'D', 'E']])

    def heuristic_1(state: MachineState, _) -> float:
        return 10 - \
               (ife(state.is_above('A', 'B')) * 1) - \
               (ife(state.is_above('B', 'C')) * 2) - \
               (ife(state.is_above('C', 'D')) * 3) - \
               (ife(state.is_above('E', None)) * 4)

    wrap_search(from_state, to_state, heuristic_1, 1, render_node, def_node_attr, "out/machine-random-heuristic_1.png")


def main():
    td()
    random()


if __name__ == '__main__':
    main()

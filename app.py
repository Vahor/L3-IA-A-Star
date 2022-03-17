from copy import deepcopy

from a_star import a_star_search
from render import render_tree
from state import State


class MachineState(State):

    def __init__(self, arm: str or None, stacks: list[list[str]], max_stacks: int = 3):
        self.arm = arm
        self.stacks = stacks
        self.max_stacks = max_stacks

        # On remplit les piles avec des listes vides au besoin
        for i in range(max_stacks - len(stacks)):
            stacks.append([])

        pass

    def __repr__(self):
        return f"MachineState(arm={self.arm}, stacks={self.stacks}, max_stacks={self.max_stacks})"

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        if self.arm != other.arm:
            return False

        for stack in self.stacks:
            if stack not in other.stacks:
                return False

        return True

    def __hash__(self):
        return id(self)

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
        children = []

        # Si le bras est libre, on essaie de porter un element en tête de file
        if self.arm is None:

            for free_block in self.get_free_blocks():
                new_stacks = deepcopy(self.stacks)

                for stack in new_stacks:  # On retire le bloc concerné dans nos listes
                    if free_block in stack:
                        stack.remove(free_block)
                        break

                state = MachineState(free_block, new_stacks)

                children.append(state)

        else:  # Sinon, on essaie de poser sur une tête de file, ou dans une nouvelle file
            for i in range(self.max_stacks):
                new_stacks = deepcopy(self.stacks)
                # On ajoute le bloc qu'on porte, dans la i-ème file
                new_stacks[i].insert(0, self.arm)

                state = MachineState(None, new_stacks)

                children.append(state)

        return children


def b(value: bool) -> int:
    return 1 if value else -1


def heuristic_1(state: MachineState) -> float:
    return 6 - \
           (b(state.is_above('A', 'B')) * 1) - \
           (b(state.is_above('B', 'C')) * 2) - \
           (b(state.is_above('C', None)) * 3)


def main():
    from_state = MachineState(None, [['C', 'A'], ['B']])
    to_state = MachineState(None, [['A', 'B', 'C']])

    path = a_star_search(from_state, to_state, heuristic_1)

    render_tree(path)


if __name__ == '__main__':
    main()

from queue import PriorityQueue

from render import Path
from state import State


class AStarResult(Path):
    path: list[State]

    def __init__(self):
        pass

    def get_path(self):
        return self.path


def build_path(parent: {State: State}, current: State) -> list[State]:
    path = [current]
    while current in parent.keys():
        current = parent[current]
        path.insert(0, current)
    return path


def a_star_search(from_state: State, to_state: State, h) -> AStarResult:
    result = AStarResult()

    to_check = [from_state]
    visited = []

    g_score = {from_state: 0}

    from_state_g = 0
    from_state_h = h(from_state)
    from_state_f = from_state_g + from_state_h  # f = g + h

    parent = {}  # Liste des parents pour pouvoir faire le chemin inverse à la fin

    f_score = PriorityQueue()

    # Tuple = (f, g, h, value). Seuls f et value sont utiles, mais on garde toutes les valeurs pour le debug
    f_score.put((from_state_f, from_state_g, from_state_h, from_state))

    # Tant qu'on a des états à essayer
    while to_check:
        current = f_score.get()  # On récupère l'état avec le plus petit heuristic
        current_state = current[3]

        if current_state == to_state:  # Si c'est l'état cible, on s'arrête là
            result.path = build_path(parent, current_state)
            return result

        visited.append(current_state)  # Et on le marque comme visité
        to_check.remove(current_state)  # On le retire de la liste des nœuds à visiter

        g_current = g_score[current_state]
        # Sinon on essaie tous les fils de l'état actuel dans notre liste
        for children in current_state.children():
            h_child = h(children)
            g_child = g_current + 1  # Chaque avancement dans une branche coûte 1
            f_child = h_child + g_child

            # Si le score actuel est meilleur que le score précédent (ou qu'il n'y en a pas)
            if children not in g_score or f_child < g_score[children]:
                g_score[children] = g_child
                f_score.put((f_child, g_child, h_child, children))
                parent[children] = current_state  # On met à jour le parent

                if children not in visited:  # On n'ajoute à la file que si l'état n'a pas déjà été testé précédemment
                    to_check.append(children)

    return result

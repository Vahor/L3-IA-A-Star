from abc import ABC
from queue import PriorityQueue
from random import random

from anytree import Node
from anytree.exporter import DotExporter

from state import State


class AStarNode(State, ABC):

    def __lt__(self, other):
        return False


# AStarResult est une classe qui contient le résultat de l'algorithme A*
class AStarResult:
    root: AStarNode
    path: list[AStarNode]
    visited: list[AStarNode]
    g_score: {AStarNode: float}
    h_score: {AStarNode: float}
    steps: int = 0
    step: {AStarNode: int}

    def __init__(self):
        pass


def build_path(parent: {State: State}, current: State) -> list[State]:
    """
    Construit le chemin inverse depuis un point jusqu'a la racine à l'aide de la liste des parents

    :param parent: Un dictionnaire qui mappe l'objet actuel à son parent
    :type parent: {State: State}
    :param current: l'état actuel
    :type current: State
    :return: Une liste d'états.
    """
    path = [current]
    while current in parent.keys():
        current = parent[current]
        path.insert(0, current)
    return path


def a_star_search(from_state: AStarNode, to_state: AStarNode, h) -> AStarResult or None:
    """
    Réalise une recherche A* pour trouver le chemin le plus court entre deux point.
    La fonction heuristique est utilisée pour estimer la distance entre le nœud actuel et le nœud cible.

    :param from_state: L'état initial à partir duquel commencer la recherche
    :type from_state: AStarNode
    :param to_state: L'état du but
    :type to_state: AStarNode
    :param h: la fonction heuristique
    :return: AStarResult est un tuple nommé avec les champs suivants:
        - root : le nœud racine de l'arbre de recherche
        - path: le chemin de la racine au nœud de but
        - visited : la liste des nœuds visités
        - g_score: le score g du nœud de but
        - h_score: le score h du nœud de but
        - steps: le nombre d'étapes
        - step: l'ordre de passage d'un nœud
    """

    result = AStarResult()
    result.root = from_state

    to_check = [from_state]
    visited = []

    from_state_g = 0
    from_state_h = h(from_state)
    from_state_f = from_state_g + from_state_h  # f = g + h

    parent = {}  # Liste des parents pour pouvoir faire le chemin inverse à la fin

    g_score = {from_state: from_state_g}
    h_score = {from_state: from_state_h}
    step = {from_state: 0}

    f_score = PriorityQueue()

    # Tuple = (f, g, h, value). Seuls f et value sont utiles, mais on garde toutes les valeurs pour le debug
    f_score.put((from_state_f, from_state))

    # Tant qu'on a des états à essayer
    while to_check:
        current = f_score.get()  # On récupère l'état avec le plus petit heuristic
        current_state: State = current[1]
        step[current_state] = result.steps

        visited.append(current_state)  # Et on le marque comme visité

        if current_state == to_state:  # Si c'est l'état cible, on s'arrête là
            # On ajoute les informations au résultat et on le retourne
            result.path = build_path(parent, current_state)
            result.visited = visited
            result.g_score = g_score
            result.h_score = h_score
            result.step = step
            return result

        result.steps += 1  # On augmente le nombre d'étapes

        if current_state in to_check:
            to_check.remove(current_state)  # On le retire de la liste des nœuds à visiter

        g_current = g_score[current_state]
        # Sinon on essaie tous les fils de l'état actuel dans notre liste
        for children in current_state.children():

            if children in h_score:
                h_child = h_score[children]
            else:
                h_child = h(children)

            g_child = g_current + 1  # Chaque avancement dans une branche coûte 1
            f_child = h_child + g_child

            # Si le score actuel est meilleur que le score précédent (ou qu'il n'y en a pas)
            if children not in g_score or f_child < g_score[children]:
                h_score[children] = h_child
                g_score[children] = g_child
                parent[children] = current_state  # On met à jour le parent

                if children not in visited:  # On n'ajoute à la file que si l'état n'a pas déjà été testé précédemment
                    to_check.append(children)
                    f_score.put((f_child, children))

    return None


def render_tree(result: AStarResult, node_content, node_attr, file_name: str) -> None:
    """
    Génère une image à partir d'un résultat A*

    :param result: AStarRésultat
    :type result: AStarResult
    :param node_content: Une fonction qui renvoie le contenu du nœud
    :param node_attr: Une fonction qui prend un nœud et un résultat A* et renvoie une chaîne d'attributs HTML pour le nœud
    :param file_name: Nom du fichier dans lequel enregistrer l'image
    :type file_name: str
    """

    if result is None:
        print("Aucun chemin")
        return
    print(f"Recherche terminée en {result.steps} étapes ({file_name})")

    root = add_node(result.root, result, [])

    DotExporter(root,
                nodenamefunc=lambda n: node_content(n.node, result),
                nodeattrfunc=lambda n: node_attr(n.node, result)
                ).to_picture(file_name)


def def_node_attr(node, result: AStarResult) -> str:
    """
    Renvoie la chaîne d'attribut d'un nœud

    :param node: MachineState
    :type node: MachineState
    :param result: AStarRésultat
    :type result: AStarResult
    :return: Chaîne utilisée pour spécifier les attributs d'un nœud dans le graphique.
    """

    # Les attributs de styles sont utilisées avec graphviz, on les retrouves sur :
    #   https://www.graphviz.org/doc/info/shapes.html#styles-for-nodes

    if node in result.path:
        return "color=red"
    return ""


def add_node(node: AStarNode, result: AStarResult, already: list[AStarNode], parent: Node or None = None) -> Node:
    """
    Ajouter un nœud au résultat ainsi que ses fils s'ils ne sont pas déjà dans l'arbre

    :param node: Le nœud à ajouter à l'arborescence
    :type node: AStarNode
    :param result: Le résultat de la recherche A*
    :type result: AStarResult
    :param already: La liste des nœuds qui ont déjà été visités
    :type already: list[AStarNode]
    :param parent: Le nœud parent
    :type parent: Node or None
    :return: Un objet Node.
    """
    already.append(node)
    n = Node(random(), node=node, parent=parent)
    for child in node.children():
        if child in result.visited and child not in already:
            add_node(child, result, already, parent=n)

    return n

from dataclasses import dataclass
from queue import PriorityQueue
from time import perf_counter

from anytree import AnyNode
from anytree.exporter import DotExporter
from typing import Callable


# AStarNode est une classe qui représente un nœud dans l'algorithme de recherche A*
class AStarNode:

    def __lt__(self, other):
        return False

    def children(self) -> list:
        """
        :return: Une liste des enfants du nœud.
        """
        return []


# AStarResult est une classe qui contient le résultat de l'algorithme A*
@dataclass(frozen=True)
class AStarResult:
    root: AStarNode
    path: list[AStarNode]
    g_score: {AStarNode: float}
    h_score: {AStarNode: float}
    parent: {AStarNode: AStarNode}
    visited: {AStarNode: int}
    steps: int = 0


def build_path(parent: {AStarNode: AStarNode}, current: AStarNode) -> list:
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
        path.append(current)
    path.reverse()
    return path


def a_star_search(from_state: AStarNode,
                  to_state: AStarNode,
                  h: Callable[[any, any], float],
                  cost: float = 1) -> AStarResult or None:
    """
    Réalise une recherche A* pour trouver le chemin le plus court entre deux point.
    La fonction heuristique est utilisée pour estimer la distance entre le nœud actuel et le nœud cible.

    :param from_state: L'état initial à partir duquel commencer la recherche
    :type from_state: AStarNode
    :param to_state: L'état du but
    :type to_state: AStarNode
    :param h: la fonction heuristique
    :param cost: coût d'avancement dans une branche
    :return: AStarResult est un tuple nommé avec les champs suivants:
        - root : le nœud racine de l'arbre de recherche
        - path: le chemin de la racine au nœud de but
        - g_score: le score g du nœud de but
        - h_score: le score h du nœud de but
        - steps: le nombre d'étapes
        - visited: l'ordre de passage d'un nœud
    """

    from_state_g = 0
    from_state_h = h(from_state, to_state)
    from_state_f = from_state_g + from_state_h  # f = g + h

    parent = {}  # Liste des parents pour pouvoir faire le chemin inverse à la fin

    g_score: {AStarNode: float} = {from_state: from_state_g}
    h_score: {AStarNode: float} = {from_state: from_state_h}
    visited: {AStarNode: int} = {}  # Peut correspondre à une liste de nœuds fermés

    f_score = PriorityQueue()  # Peut correspondre à une liste de nœuds ouverts

    # Tuple = (f, g, h, value). Seuls f et value sont utiles, mais on garde toutes les valeurs pour le debug
    f_score.put((from_state_f, from_state))

    steps = 0

    # Tant qu'on a des états à essayer
    while f_score:
        _, current = f_score.get()  # On récupère l'état avec le plus petit heuristic

        visited[current] = len(visited)

        if current == to_state:  # Si c'est l'état cible, on s'arrête là
            # On ajoute les informations au résultat et on le retourne
            return AStarResult(
                from_state,
                build_path(parent, current),
                g_score,
                h_score,
                parent,
                visited,
                steps
            )

        g_current = g_score[current]
        # Sinon on essaie tous les fils de l'état actuel dans notre liste
        for children in current.children():
            if children == current:
                continue

            steps += 1

            g_child = g_current + cost  # Chaque avancement dans une branche a un coût

            # Si le score actuel est meilleur que le score précédent (ou qu'il n'y en a pas)
            # ça veut dire qu'on a atteint le nœud plus haut que précédemment
            if children not in g_score or g_child < g_score[children]:

                h_child = h(children, to_state)
                f_child = h_child + g_child

                h_score[children] = h_child
                g_score[children] = g_child

                parent[
                    children] = current  # On change le lien de parenté avec l'ancien nœud, comme ce chemin est plus court

                if children not in visited:  # On n'ajoute à la file que si l'état n'a pas déjà été testé précédemment
                    f_score.put((f_child, children))

    return None


def render_tree(result: AStarResult,
                node_content: Callable[[AStarNode, AStarResult], str],
                node_attr: Callable[[AStarNode, AStarResult], str],
                file_name: str,
                unvisited_nodes) -> None:
    """
    Génère une image à partir d'un résultat A*

    :param result: AStarRésultat
    :type result: AStarResult
    :param node_content: Une fonction qui renvoie le contenu du nœud
    :param node_attr: Une fonction qui prend un nœud et un résultat A* et renvoie une chaîne d'attributs HTML pour le nœud
    :param file_name: Nom du fichier dans lequel enregistrer l'image
    :type file_name: str
    :param unvisited_nodes: Est-ce qu'on affiche les nœuds non visités
    :type unvisited_nodes: True or False
    """

    root = add_node(result.root, result, [], unvisited_nodes)

    DotExporter(root,
                nodenamefunc=lambda n: node_content(n.node, result),
                nodeattrfunc=lambda n: node_attr(n.node, result)
                ).to_picture(file_name)


def def_node_attr(node: AStarNode, result: AStarResult) -> str:
    """
    Renvoie la chaîne d'attribut d'un nœud

    :param node: AStarNode
    :type node: AStarNode
    :param result: AStarRésultat
    :type result: AStarResult
    :return: Chaîne utilisée pour spécifier les attributs d'un nœud dans le graphique.
    """

    # Les attributs de styles sont utilisées avec graphviz, on les retrouves sur :
    #   https://www.graphviz.org/doc/info/shapes.html#styles-for-nodes

    if node not in result.visited:
        return "style=\"dotted\""

    if node in result.path:
        return "color=red,style=filled, fillcolor=\"#0000000f\""

    return ""


def add_node(node: AStarNode,
             result: AStarResult,
             already: list[AStarNode],
             show_unvisited_nodes: bool,
             parent: AnyNode or None = None) -> AnyNode:
    """
    Ajouter un nœud au résultat ainsi que ses fils s'ils ne sont pas déjà dans l'arbre

    :param node: Le nœud à ajouter à l'arborescence
    :type node: AStarNode
    :param result: Le résultat de la recherche A*
    :type result: AStarResult
    :param already: La liste des nœuds qui ont déjà été visités
    :type already: list[AStarNode]
    :param show_unvisited_nodes: Est-ce qu'on affiche les nœuds non visités
    :type show_unvisited_nodes: True or False
    :param parent: Le nœud parent
    :type parent: AnyNode or None
    :return: Un objet AnyNode.
    """
    already.append(node)
    n = AnyNode(node=node, parent=parent)
    for child in node.children():
        if child == node:
            continue
        if show_unvisited_nodes and child not in result.visited:
            already.append(node)
            AnyNode(node=child, parent=n)
            continue
        if child in result.visited and child not in already:
            add_node(child, result, already, show_unvisited_nodes, parent=n)

    return n


def wrap_search(from_state: AStarNode,
                to_state: AStarNode,
                h: Callable[[any, any], float],
                cost: float,
                render_node: Callable[[any, any], str],
                render_attr: Callable[[any, any], str],
                file_name: str,
                unvisited_nodes: bool = True):
    t_start = perf_counter()

    print("----")
    print(f"Début de la recherche {file_name}")
    path = a_star_search(from_state, to_state, h, cost)
    t_delta = perf_counter() - t_start
    print(f"Temps d'execution : {t_delta:.5f} secondes")
    print(f"Temps par noeud : {t_delta / path.steps:.5f} secondes")
    print(f"Nombre de noeuds visités : {path.steps}")
    print(f"Nombre de noeuds parcourus : {len(path.visited)}")

    if path is None:
        print("Aucun chemin trouvé")
    else:
        print(f"Écriture du fichier {file_name}")
        render_tree(path, render_node, render_attr, file_name, unvisited_nodes)
        print("Écriture terminée")

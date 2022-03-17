from abc import abstractmethod, ABC

from state import State


class Path(ABC):

    @abstractmethod
    def get_path(self) -> list[State]:
        pass


def render_tree(result: Path):
    print(result.get_path())

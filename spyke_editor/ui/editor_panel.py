import abc
import typing as t


class EditorPanel(abc.ABC):
    @abc.abstractmethod
    def render(self) -> None: ...

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

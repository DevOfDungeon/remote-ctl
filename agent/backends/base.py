from abc import ABC, abstractmethod


class InputBackend(ABC):
    """One implementation per OS. The rest of the app only sees this."""

    @abstractmethod
    def move(self, dx: int, dy: int) -> None: ...

    @abstractmethod
    def scroll(self, dx: int, dy: int) -> None: ...

    @abstractmethod
    def click(self, button: str) -> None: ...

    def close(self) -> None:
        pass
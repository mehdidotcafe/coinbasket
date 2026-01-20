from abc import ABC, abstractmethod


class DateTime(ABC):
    """
    Abstract base class for time-related operations.
    """

    @abstractmethod
    def now(self) -> int:
        """
        Get the current time as a timestamp.

        Returns:
            str: The current time as a timestamp.
        """
        raise NotImplementedError

    @abstractmethod
    def now_str(self) -> str:
        """
        Get the current time as a string.

        Returns:
            str: The current time as a string.
        """
        raise NotImplementedError

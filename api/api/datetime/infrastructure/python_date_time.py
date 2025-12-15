from datetime import datetime
import time

from api.datetime.date_time import DateTime


class PythonDateTime(DateTime):
    """
    PythonTime is a class that provides a method to get the current time in UTC.
    """

    def now(self) -> int:
        """
        Get the current time as timestamp.

        Returns:
            int: The current time as a timestamp.
        """

        return int(time.time())

    def now_str(self) -> str:
        """
        Get the current time as a string.

        Returns:
            str: The current time as a string.
        """

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

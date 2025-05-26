import datetime as dt

from .._base import Ten8tBaseSchedule
from .._base import Ten8tException


class Ten8tTTLSchedule(Ten8tBaseSchedule):
    """
    A derived schedule class that allows a time-to-live or debounce mechanism.

    Tasks are executed immediately on the first call using `run_now`. Subsequent calls are blocked
    until a configured debounce duration (TTL in seconds or minutes) has passed relative to the
    last execution time.
    """

    def __init__(self, name="debounce_schedule", ttl_sec: int | None = None, ttl_min: int | None = None) -> None:
        """
        Initializes the debounce schedule with a name and a TTL (Time-To-Live) duration.

        Args:
            name (str): The name of the debounce schedule. Defaults to "debounce_schedule".
            ttl_sec (int, optional): The TTL (Time-To-Live) duration in seconds.
            ttl_min (int, optional): The TTL duration in minutes. Defaults to None.

        Raises:
            Ten8tException: If neither ttl_sec nor ttl_min is provided, or both are negative.
        """
        super().__init__(name=name, granularity="second")  # Default granularity: 'second'

        # Validate and compute total TTL in seconds
        if ttl_sec is not None and ttl_sec < 0:
            raise Ten8tException("TTL in seconds must be greater than zero.")
        if ttl_min is not None and ttl_min < 0:
            raise Ten8tException("TTL in minutes must be greater than zero.")
        if ttl_sec is None and ttl_min is None:
            raise Ten8tException("You must provide either ttl_sec or ttl_min.")

        self.ttl_sec = ttl_sec if ttl_sec is not None else ttl_min * 60  # Always store TTL in seconds

    def mark_executed(self, execution_time: dt.datetime | None = None) -> bool:
        """
        Executes the task if it's not within the debounce duration.

        Args:
            execution_time (datetime, optional): The current execution time.
                Defaults to `datetime.now()`.

        Returns:
            bool: True if the task is run now, False if it's within the debounce duration.
        """
        execution_time = execution_time or dt.datetime.now()

        # If no last execution time, allow immediate run
        if self.last_execution_time is None:
            self.last_execution_time = execution_time
            return True

        # Calculate the earliest available time for the next execution
        next_allowed_time = self.last_execution_time + dt.timedelta(seconds=self.ttl_sec)

        # Check if the current time has surpassed the allowable time
        if execution_time >= next_allowed_time:
            self.last_execution_time = execution_time
            return True  # Task is executed now

        return False  # Task execution is debounced

    def __repr__(self) -> str:
        """Representation for debugging or logs."""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"last_execution_time={self.last_execution_time}, "
            f"ttl_sec={self.ttl_sec})"
        )

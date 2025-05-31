import datetime as dt
from contextlib import contextmanager

from ..ten8t_exception import Ten8tException
from ..ten8t_types import DateTimeOrNone


class Ten8tBaseSchedule:
    """
    A base schedule class that always allows tasks to run at any time.
    This class can be used as-is or extended for custom scheduling logic.

    Class-level constants:
        ALL_DAYS_OF_MONTH (set[int]): Represents all days of the month (1-31).
        ALL_DAYS_OF_WEEK (set[int]): Represents all days of the week (Sunday=0 through Saturday=6).
    """

    GRANULARITY_MAP = {
        "day": {"day", "days", "d"},
        "hour": {"hour", "hours", "hr", "h"},
        "minute": {"minute", "minutes", "min", "mn", "m"},
        "second": {"second", "seconds", "sec", "s"},
    }

    # Define replacement parameters for each granularity
    GRANULARITY_REPLACEMENTS = {
        "day": {"hour": 0, "minute": 0, "second": 0, "microsecond": 0},
        "hour": {"minute": 0, "second": 0, "microsecond": 0},
        "minute": {"second": 0, "microsecond": 0},
        "second": {"microsecond": 0}
    }


    # Class-level constants for days
    ALL_DAYS_OF_MONTH = set(range(1, 32))  # Represents all days of the month (1-31)
    ALL_DAYS_OF_WEEK = set(range(0, 7))  # Represents all days of the week (0=Sunday, ... 6=Saturday)

    def __init__(self, name="base", granularity: str = "minute") -> None:
        """
        Initializes the schedule with an optional name and granularity level.

        Granularity is what allows you to say things happen at the same time and thus
        allowing you to skip repeated checks.  The system currently supports day, hour minute
        and second granularity.   Each one of these "zeros out" values in the datetime object
        so if you set granularity to hours, the minute and second values will be zeroed out.


        Args:
            name (str): The name of the schedule. Defaults to "base".
            granularity (str): The time granularity to use ("minute" or "second").
                               Defaults to "minute".
        """
        if name:
            name = name.strip()

        if not name:
            raise Ten8tException(f"Name must be provided for schedule by {self.__class__.__name__})")

        self.last_execution_time: DateTimeOrNone = None
        self.name = name or "unknown"
        self.granularity = self._normalize_granularity(granularity)

    def _normalize_granularity(self, granularity: str) -> str:
        """
        Normalizes the provided granularity to a standard format (e.g., 'minute').

        This allows users to use anyting value specified in the map, like
        minute, minutes, min, or m for minutes.  This is ONLY provided to simplify
        the user experience for data read from config files.

        Args:
            granularity (str): The user-provided granularity input.

        Returns:
            str: The normalized granularity (e.g., "hour", "minute").

        Raises:
            ValueError: If the granularity is invalid.
        """
        granularity = granularity.lower().strip()  # case-insensitive, remove whitespace
        for standard, aliases in self.GRANULARITY_MAP.items():
            if granularity in aliases:
                return standard
        raise Ten8tException(
            f"Invalid granularity: '{granularity}'. "
            f"Supported values are: {', '.join(self.GRANULARITY_MAP.keys())}."
        )

    def _normalize_time(self, time: dt.datetime) -> dt.datetime:
        """
        Normalizes a datetime according to the schedule's granularity.

        This method handles applying the appropriate replacements to zero out
        smaller time units based on the configured granularity.

        Args:
            time (dt.datetime): The time to normalize.

        Returns:
            dt.datetime: The normalized time with appropriate values zeroed out.

        Raises:
            Ten8tException: If an unsupported granularity is specified.
        """
        if self.granularity not in self.GRANULARITY_REPLACEMENTS:  # pragma no cover
            raise Ten8tException(
                f"Granularity must be one of {', '.join(self.GRANULARITY_REPLACEMENTS.keys())}, "
                f"not {self.granularity}"
            )

        # Get the specific kwargs for the current granularity
        replace_kwargs = self.GRANULARITY_REPLACEMENTS[self.granularity]

        # Apply the appropriate replacements based on granularity
        return time.replace(**replace_kwargs)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"last_execution_time={self.last_execution_time})"
        )

    def is_due(self, time: dt.datetime) -> bool:
        """
        Always returns True, allowing tasks to run at any time.
        """
        return True

    def can_execute(self, execution_time: DateTimeOrNone = None) -> bool:
        """
        Checks if execution is allowed at the current time based on schedule and
        previous execution history, without modifying state.

        Args:
            execution_time (dt.datetime, optional): The time to check. Defaults to datetime.now().

        Returns:
            bool: True if execution is allowed, False otherwise.
        """
        execution_time = execution_time or dt.datetime.now()
        normalized_time = self._normalize_time(execution_time)

        # First check if the time is in the schedule
        if not self.is_due(execution_time):
            return False

        # Then check if we've already executed at this time unit
        return self.last_execution_time != normalized_time

    def record_execution(self, execution_time: DateTimeOrNone = None) -> bool:
        """
        Updates the last execution state and prevents duplicate runs
        based on the specified granularity.

        Args:
            execution_time (dt.datetime, optional): The current execution time.
                                                  Defaults to `datetime.now()`.

        Returns:
            bool: True if the task was recorded to run now, False if it's a duplicate.
        """
        execution_time = execution_time or dt.datetime.now()
        normalized_time = self._normalize_time(execution_time)

        # Compare and update the last execution time
        if self.last_execution_time != normalized_time:
            self.last_execution_time = normalized_time
            return True  # Task is scheduled to run
        return False  # Task execution is a duplicate

    @contextmanager
    def execute_once(self, execution_time: DateTimeOrNone = None):
        """
        Context manager that tracks execution at most once per time interval.

        Yields whether this is the first execution in this interval (True)
        or a duplicate (False). Only marks as executed if yielded True and
        the with block completes successfully.

        Args:
            execution_time: Time to check, defaults to current time

        Example:

            # Create a schedule with minute granularity
            schedule = Ten8tBaseSchedule(name="my_task", granularity="minute")

            # Use the context manager to prevent duplicate executions
            with schedule.run_once_in_period() as should_execute:
                if should_execute:
                    # This code will run at most once per minute
                    print("Performing task...")
                    process_data()
                else:
                    print("Skipping duplicate execution in this time interval")

            # If an exception occurs inside the with block, the interval
            # won't be marked as executed
            try:
                with schedule.run_once_in_period() as should_execute:
                    if should_execute:
                        risky_operation()  # If this fails, won't mark as executed
            except Exception as e:
                log_error(e)

    """

        execution_time = execution_time or dt.datetime.now()
        should_execute = self.can_execute(execution_time)

        try:
            # Yield whether this execution should be tracked
            yield should_execute
            # Only mark as executed if it should have executed
            if should_execute:
                self.record_execution(execution_time)
        except Exception:
            # Don't mark as executed if an exception occurs
            raise

    def __or__(self, other: "Ten8tBaseSchedule") -> "Ten8tCompositeSchedule":
        """
        Combines this schedule with another using the logical OR operator (`|`).

        This creates a composite schedule that allows tasks to run if the time
        is valid in either one of the combined schedules.

        Args:
            other (Ten8tBaseSchedule): Another schedule to combine with.

        Returns:
            Ten8tCompositeSchedule: A new schedule representing the union of the two schedules.

        Raises:
            TypeError: If the other object is not a Ten8tBaseSchedule.
        """

        # Break circular import
        from ._composite import Ten8tCompositeSchedule

        if not isinstance(other, Ten8tBaseSchedule):
            raise Ten8tException("Can only combine schedules with another Ten8tBaseSchedule")
        return Ten8tCompositeSchedule(schedules=[self, other])

    def __and__(self, other: "Ten8tBaseSchedule") -> "Ten8tIntersectionSchedule":
        """
        Combines this schedule with another using the logical AND operator (`&`).

        This creates a schedule that only runs a task if the time is valid in all combined schedules.

        Args:
            other (Ten8tBaseSchedule): Another schedule to combine with.

        Returns:
            Ten8tIntersectionSchedule: A new schedule representing the intersection.

        Raises:
            TypeError: If the other object is not a Ten8tBaseSchedule.
        """

        # Break circular import
        from ._intersect import Ten8tIntersectionSchedule

        if not isinstance(other, Ten8tBaseSchedule):
            raise Ten8tException(f"Can only combine schedules with another Ten8tBaseSchedule")
        return Ten8tIntersectionSchedule(schedules=[self, other])

    def __invert__(self) -> "Ten8tInverseSchedule":
        """
        Returns a schedule that represents the inverse of this schedule.

        This creates an "inverse" schedule that allows tasks to run only when the original schedule would not.

        Returns:
            Ten8tInverseSchedule: A new schedule representing the inverse logic.
        """

        # Break circular import
        from ._inverse import Ten8tInverseSchedule

        return Ten8tInverseSchedule(schedule=self)


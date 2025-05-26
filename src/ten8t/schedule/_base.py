import datetime as dt
from contextlib import contextmanager

from ..ten8t_exception import Ten8tException


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
        "minute": {"minute", "minutes", "min", "m"},
        "second": {"second", "seconds", "sec", "s"},
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

        self.last_execution_time: dt.datetime | None = None
        self.name = name or "unknown"

        self.granularity = self._normalize_granularity(granularity)

    def _normalize_granularity(self, granularity: str) -> str:
        """
        Normalizes the provided granularity to a standard format (e.g., 'minute').

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


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"last_execution_time={self.last_execution_time})"
        )

    def is_time_in_schedule(self, time: dt.datetime) -> bool:
        """
        Always returns True, allowing tasks to run at any time.
        """
        return True

    def mark_executed(self, execution_time: dt.datetime | None = None) -> bool:
        """
        Updates the last execution state and prevents duplicate runs
        based on a specified granularity (hour, minute, or second).

        Supported granularities:
            - "day": Ensures tasks run only once per day.
            - "hour": Ensures tasks run only once per hour.
            - "minute": Ensures tasks run only once per minute (default).
            - "second": Ensures tasks run only once per second.

        Args:
            execution_time (datetime, optional): The current execution time.
                                                Defaults to `datetime.now()`.

        Returns:
            bool: True if the task was recorded to run now, False if it's a duplicate.

        Raises:
            Ten8tException: If an unsupported granularity is specified.
        """
        execution_time = execution_time or dt.datetime.now()

        # Define replacement parameters for each granularity
        replacement_params = {
            "day": {"hour": 0, "minute": 0, "second": 0, "microsecond": 0},
            "hour": {"minute": 0, "second": 0, "microsecond": 0},
            "minute": {"second": 0, "microsecond": 0},
            "second": {"microsecond": 0}
        }

        if self.granularity not in replacement_params:
            raise Ten8tException(
                f"Granularity must be one of {', '.join(replacement_params.keys())}, "
                f"not {self.granularity}"
            )

        # Get the specific kwargs for the current granularity
        replace_kwargs = replacement_params[self.granularity]

        # Apply the appropriate replacements based on granularity
        current_time_value = execution_time.replace(**replace_kwargs)

        # Compare and update the last execution time
        if self.last_execution_time != current_time_value:
            self.last_execution_time = current_time_value
            return True  # Task is scheduled to run
        return False  # Task execution is a duplicate

    @contextmanager
    def execution_context(self, execution_time: dt.datetime | None = None):
        """
        A context manager that checks if execution should proceed and automatically
        marks it as executed upon successful completion.

        Args:
            execution_time (datetime, optional): The time to check. Defaults to datetime.now().

        Yields:
            bool: True if execution should proceed, False otherwise.

        Example:
            with schedule.execution_context() as should_run:
                if should_run:
                    # Do the actual work
                    do_something()
                    # No need to call mark_executed - happens automatically
        """
        execution_time = execution_time or dt.datetime.now()
        should_execute = self.can_execute(execution_time)

        try:
            # Yield whether execution should proceed
            yield should_execute

            # Only mark as executed if execution was allowed and completed successfully
            if should_execute:
                self.mark_executed(execution_time)
        except Exception:
            # If an exception occurs, don't mark as executed
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
        return Ten8tInverseSchedule(schedule=self)


class Ten8tCompositeSchedule(Ten8tBaseSchedule):
    """
    A composite schedule that evaluates multiple schedules and allows a time
    if it matches any of the constituent schedules (logical OR).
    """

    def __init__(self, schedules: list[Ten8tBaseSchedule], name="or_composite") -> None:
        super().__init__(name=name)
        self.schedules = schedules

    def __repr__(self) -> str:
        # Include the list of schedules in the representation
        return f"{self.__class__.__name__}(schedules={self.schedules!r}, name={self.name!r}, last_execution_time={self.last_execution_time!r})"

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        """
        Returns True if the given time matches any schedule in the list.
        """
        return any(schedule.is_time_in_schedule(time_) for schedule in self.schedules)


class Ten8tIntersectionSchedule(Ten8tBaseSchedule):
    def __init__(self, schedules: list[Ten8tBaseSchedule], name="and_composite"):
        """Combine multiple schedules with logical AND."""
        super().__init__(name=name)
        self.schedules = schedules

    def __repr__(self):
        return f"{self.__class__.__name__}(schedules={self.schedules!r}, name={self.name!r}, last_execution_time={self.last_execution_time!r})"

    def is_time_in_schedule(self, dt):
        """Check if all the schedules include the given time."""
        return all(schedule.is_time_in_schedule(dt) for schedule in self.schedules)


class Ten8tInverseSchedule(Ten8tBaseSchedule):
    """
    Represents an inverse schedule that returns True only when the original schedule returns False.
    """

    def __init__(self, schedule: Ten8tBaseSchedule):
        super().__init__(name=f"not({schedule.name})")
        self.schedule = schedule

    def is_time_in_schedule(self, time: dt.datetime) -> bool:
        """
        Inverts the result of the original schedule's `is_time_in_schedule` method.

        Args:
            time (datetime): The time to check against the schedule.

        Returns:
            bool: True if the original schedule is False, otherwise False.
        """
        return not self.schedule.is_time_in_schedule(time)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(original_schedule={self.schedule!r})"

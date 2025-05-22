import datetime as dt

from ..ten8t_exception import Ten8tException


class Ten8tBaseSchedule:
    """
    A base schedule class that always allows tasks to run at any time.
    This class can be used as-is or extended for custom scheduling logic.

    Class-level constants:
        ALL_DAYS_OF_MONTH (set[int]): Represents all days of the month (1-31).
        ALL_DAYS_OF_WEEK (set[int]): Represents all days of the week (Sunday=0 through Saturday=6).
    """

    # Class-level constants for days
    ALL_DAYS_OF_MONTH = set(range(1, 32))  # Represents all days of the month (1-31)
    ALL_DAYS_OF_WEEK = set(range(0, 7))  # Represents all days of the week (0=Sunday, ... 6=Saturday)

    def __init__(self, name='base') -> None:
        if not name:
            raise Ten8tException(f"Name must be provided for schedule by {self.__class__.__name__})")

        self.last_execution_time: dt.datetime | None = None
        self.name = name or 'unknown'

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, last_execution_time={self.last_execution_time!r})"

    def is_time_in_schedule(self, time: dt.datetime) -> bool:
        """
        Always returns True, allowing tasks to run at any time.
        """
        return True

    def run_now(self, execution_time: dt.datetime | None = None) -> bool:
        """
        Updates the last execution state and prevents duplicate runs within the same minute.

        Args:
            execution_time (datetime, optional): The current execution time. Defaults to `datetime.now()`.

        Returns:
            bool: True if the task was recorded to run now, False if it's a duplicate.
        """
        execution_time = execution_time or dt.datetime.now()

        if self.last_execution_time is None or self.last_execution_time != execution_time:
            self.last_execution_time = execution_time
            return True  # Task is scheduled to run
        return False  # Duplicate execution

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
            raise TypeError("Can only combine schedules with another Ten8tBaseSchedule")
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
            raise TypeError(f"Can only combine schedules with another Ten8tBaseSchedule")
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
    def __init__(self, schedules):
        """Combine multiple schedules with logical AND."""
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

import datetime as dt
from typing import Set

from .ten8t_exception import Ten8tException
from .ten8t_util import StrListOrNone, any_to_str_list


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


class Ten8tCronSchedule(Ten8tBaseSchedule):
    """
    A cron-like schedule implementation.

    The `Ten8tCronSchedule` class represents a schedule defined using cron-like
    expressions for minute, hour, day of the month, month, and day of the week.
    It evaluates whether a specific datetime matches the defined schedule rules.

    Attributes:
        minute (set[int]): Set of valid minutes, parsed from a cron-like expression
            (e.g., "*", "*/15", "15,30,45").
        hour (set[int]): Set of valid hours, parsed from a cron-like expression
            (e.g., "*", "9-17", "6,12,18").
        day_of_month (set[int]): Set of valid days of the month, parsed from a cron-like
            expression (e.g., "*", "1-10", "5,15,25").
        month (set[int]): Set of valid months, parsed from a cron-like expression
            (e.g., "*", "1-6", "1,3,7").
        day_of_week (set[int]): Set of valid days of the week, parsed from a cron-like
            expression (e.g., "*", "0-4", "0,3,6"). In this context, Sunday is represented
            as 0 (following cron convention).

    Methods:
        is_time_in_schedule(time):
            Checks whether a given datetime matches the cron schedule.

    Raises:
        Ten8tException: If both `day_of_month` and `day_of_week` are explicitly specified
            (representing a conflict), or if an invalid value is provided in the cron-like fields.

    Example:
        >>> from datetime import datetime
        >>> cron_schedule = Ten8tCronSchedule(minute="*/15", hour="9-17", day_of_week="1-5")
        >>> cron_schedule.is_time_in_schedule(datetime(2023, 11, 7, 9, 15))  # Tuesday, 9:15 AM
        True
        >>> cron_schedule.is_time_in_schedule(datetime(2023, 11, 7, 9, 10))  # Tuesday, 9:10 AM
        False
    """

    def __init__(
            self,
            minute: str | None = None,
            hour: str | None = None,
            day_of_month: str | None = None,
            month: str | None = None,
            day_of_week: str | None = None,
            cfg: dict[str, str] | None = None,
            name: str = 'cron',
    ) -> None:
        super().__init__(name=name)
        cfg = cfg or {}

        # Parse schedule fields, using "*" as the default if no value is given
        self.minute: set[int] = self._parse_field(minute or cfg.get("minute", "*"), 0, 59, "minute")
        self.hour: set[int] = self._parse_field(hour or cfg.get("hour", "*"), 0, 23, "hour")
        self.day_of_month: set[int] = self._parse_field(
            day_of_month or cfg.get("day_of_month", "*"), 1, 31, "day_of_month"
        )
        self.month: set[int] = self._parse_field(month or cfg.get("month", "*"), 1, 12, "month")
        self.day_of_week: set[int] = self._parse_field(
            day_of_week or cfg.get("day_of_week", "*"), 0, 6, "day_of_week"
        )

        # Validate that day_of_week and day_of_month are not set at the same time.  Strictly speaking this
        # could be valid if you wanted to do things where the nth day of the month was the mth day
        # of the week was what you wanted.  I find this a VERY unlikely use case.
        if self.day_of_month != self.ALL_DAYS_OF_MONTH and self.day_of_week != self.ALL_DAYS_OF_WEEK:
            raise Ten8tException(
                "Invalid schedule: `day_of_month` and `day_of_week` cannot both be defined at the same time."
            )

    @staticmethod
    def _parse_field(field: str, min_val: int, max_val: int, field_name: str) -> Set[int]:
        """
        Parses a cron-like scheduling field into a set of valid values.

        Args:
            field (str): The cron-like field (e.g., '*', '*/5', '1,2,3').
            min_val (int): The minimum valid value for the field.
            max_val (int): The maximum valid value for the field.
            field_name (str): The name of the field (used for error reporting).

        Returns:
            Set[int]: A set of integers representing the valid values.

        Raises:
            ValueError: If the field contains invalid data or if parsing fails.
        """
        try:
            if field == "*":
                # All possible values for the field
                return set(range(min_val, max_val + 1))
            elif field.startswith("*/"):
                # Step values (e.g., "*/5")
                step = int(field[2:])
                if step <= 0:
                    raise Ten8tException(f"Step value in '{field_name}' must be greater than zero")
                return set(range(min_val, max_val + 1, step))
            elif "," in field:
                # Specific values (e.g., "1,2,3")
                values = {int(value) for value in field.split(",")}
                if not all(min_val <= value <= max_val for value in values):
                    raise Ten8tException(f"Values in '{field}' are out of range ({min_val}-{max_val})")
                return values
            elif "-" in field:
                # Range of values (e.g., "1-5")
                start, end = map(int, field.split("-"))
                if start > end or start < min_val or end > max_val:
                    raise Ten8tException(f"Invalid range in '{field_name}'")
                return set(range(start, end + 1))
            else:
                # Single value (e.g., "5")
                value = int(field)
                if value < min_val or value > max_val:
                    raise Ten8tException(f"'{field_name}' value out of range ({min_val}-{max_val})")
                return {value}
        except (ValueError, TypeError) as e:
            raise Ten8tException(f"Invalid data for {field_name}: {field}. Error: {e}")

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        """
        Determines whether the given datetime matches the defined schedule.

        Args:
            time_ (datetime): The datetime to check.

        Returns:
            bool: True if the time matches the schedule, False otherwise.
        """
        # Convert Python weekday to cron's Sunday=0 format
        day_of_week_cron = (time_.weekday() + 1) % 7

        # Check individual conditions
        minute_matches = time_.minute in self.minute
        hour_matches = time_.hour in self.hour
        day_of_month_matches = time_.day in self.day_of_month
        month_matches = time_.month in self.month
        day_of_week_matches = day_of_week_cron in self.day_of_week

        # Logic for day matching
        if self.day_of_month == self.ALL_DAYS_OF_MONTH and self.day_of_week == self.ALL_DAYS_OF_WEEK:
            # Both day_of_month and day_of_week are wildcards (*)
            day_matches = True
        elif self.day_of_month != self.ALL_DAYS_OF_MONTH and self.day_of_week == self.ALL_DAYS_OF_WEEK:
            # day_of_month is explicitly set, and day_of_week is a wildcard
            day_matches = day_of_month_matches
        elif self.day_of_month == self.ALL_DAYS_OF_MONTH and self.day_of_week != self.ALL_DAYS_OF_WEEK:
            # day_of_month is a wildcard, and day_of_week is explicitly set
            day_matches = day_of_week_matches
        else:
            # Both day_of_month and day_of_week are explicitly set
            day_matches = day_of_month_matches or day_of_week_matches

        return minute_matches and hour_matches and month_matches and day_matches


class Ten8tNonHolidaySchedule(Ten8tBaseSchedule):
    """A schedule that excludes specific holidays.

    For example if you set holidays for xmas and new years, this schedule will have
    every day of the year EXCEPT those two returning true from is_time_in_schedule(dt)

    Attributes:
        holidays (list[datetime.date]): A list of `datetime.date` objects representing holidays to exclude.
    """

    def __init__(self, name="holiday_schedule", holidays: list[dt.datetime] = None, config=None):
        """Initializes the holiday-excluding schedule.

        If no holidays are explicitly provided, the schedule defaults to no holidays (all dates included).
        Optionally, a configuration dictionary can be passed containing holidays as a string (comma-separated dates).

        Args:
            name (str, optional): The name of the schedule. Defaults to "holiday_schedule".
            holidays (list[datetime.date], optional): A list of holidays as `datetime.date` objects to exclude. Defaults to None.
            config (dict, optional): A configuration dictionary where holidays can be defined as a
                comma-separated string under the key `'holidays'`. Defaults to None.
        """
        super().__init__(name=name)

        # Parse holidays
        if holidays and config:
            raise Ten8tException("Cannot set holidays and provide config file at the same time.")
        elif holidays is not None:
            self.holidays = holidays
        elif config and 'holidays' in config:
            self.holidays = self._parse_holidays_from_config(config['holidays'])
        else:
            self.holidays = []

    def _parse_holidays_from_config(self, holidays: StrListOrNone = None) -> list[dt.date]:
        """Parses holiday dates from a given string or list.

        Args:
            holidays (str or list, optional): A comma-separated string or list of dates
                in the `YYYY-MM-DD` format. Dates are parsed into `datetime.date` objects.

        Returns:
            list[datetime.date]: A list of `datetime.date` objects representing the parsed holidays.

        Raises:
            Ten8tException: If any date in the string is invalid or cannot be parsed.
        """

        try:
            holidays = any_to_str_list(holidays)
            return [dt.datetime.strptime(holiday.strip(), '%Y-%m-%d').date() for holiday in holidays]
        except ValueError:
            raise Ten8tException(f"Invalid holiday date format: {holidays}")

    def is_time_in_schedule(self, time: dt.datetime) -> bool:
        """Checks whether the given datetime falls within the schedule.

        Args:
            time (datetime.datetime): The datetime object to check.

        Returns:
            bool: Returns `True` if the date is not in the holiday list, otherwise `False`.
        """
        return time.date() not in self.holidays

import datetime as dt
from typing import Set

from .._base import Ten8tBaseSchedule
from ...ten8t_exception import Ten8tException


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
        >>> cron_schedule.is_due(datetime(2023, 11, 7, 9, 15))  # Tuesday, 9:15 AM
        True
        >>> cron_schedule.is_due(datetime(2023, 11, 7, 9, 10))  # Tuesday, 9:10 AM
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

    def is_due(self, time_: dt.datetime) -> bool:
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

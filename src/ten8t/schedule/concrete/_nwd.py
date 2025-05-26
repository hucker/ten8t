import datetime as dt

from .._base import Ten8tBaseSchedule
from .._base import Ten8tException


class Ten8tNthWeekdaySchedule(Ten8tBaseSchedule):
    """
    A schedule that allows tasks to run on a specific occurrence of a weekday in a month.
    For example, the 3rd Wednesday of every month.

    Weekdays are represented as integers:
    0 = Monday
    1 = Tuesday
    2 = Wednesday
    3 = Thursday
    4 = Friday
    5 = Saturday
    6 = Sunday
    """

    _WEEKDAY_NAMES = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]

    def __init__(
            self,
            n: int,
            weekday: int,
            name: str | None = None
    ):
        """
        Initialize the schedule.

        Args:
            n: Which occurrence of the weekday (1 for first, 2 for second, etc.)
               Use negative numbers to count from the end of the month (-1 for last).
            weekday: The weekday to schedule (0=Monday through 6=Sunday)
            name: The name of the schedule. Defaults to "{nth}_{weekday}_of_month".
        """
        if n == 0:
            raise Ten8tException("n must be non-zero (positive for nth from start, negative for nth from end)")

        if weekday < 0 or weekday > 6:
            raise Ten8tException("weekday must be an integer between 0 and 6 (Monday to Sunday)")

        self.n = n
        self.weekday = weekday

        # Generate a default name if none provided
        if name is None:
            ordinal = self._get_ordinal(abs(n))
            direction = "" if n > 0 else "last "
            weekday_name = self._WEEKDAY_NAMES[weekday]
            name = f"{direction}{ordinal}_{weekday_name}_of_month"

        super().__init__(name=name)

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        """
        Check if the given time is on the nth occurrence of the specified weekday in its month.

        Args:
            time_: The time to check.

        Returns:
            bool: True if the time is on the nth occurrence of the specified weekday, False otherwise.
        """
        # First, check if it's the right weekday
        if time_.weekday() != self.weekday:
            return False

        if self.n > 0:
            # Count from beginning of month
            # Get the day of month for the first occurrence of this weekday
            first_day = 1 + (self.weekday - dt.datetime(time_.year, time_.month, 1).weekday()) % 7
            # Calculate the day for the nth occurrence
            target_day = first_day + (self.n - 1) * 7
            return time_.day == target_day
        else:
            # Count from end of month
            # Get the last day of the month
            if time_.month == 12:
                next_month = dt.datetime(time_.year + 1, 1, 1)
            else:
                next_month = dt.datetime(time_.year, time_.month + 1, 1)
            last_day = (next_month - dt.timedelta(days=1)).day

            # Get the day of month for the last occurrence of this weekday
            last_occurrence = last_day - (
                    (dt.datetime(time_.year, time_.month, last_day).weekday() - self.weekday) % 7)
            # Calculate the day for the nth-from-last occurrence
            target_day = last_occurrence + (self.n + 1) * 7
            # Make sure we don't go below 1
            target_day = max(target_day, 1)
            return time_.day == target_day

    @staticmethod
    def _get_ordinal(n: int) -> str:
        """
        Convert a number to its ordinal representation.

        Args:
            n: The number to convert

        Returns:
            str: The ordinal representation (1st, 2nd, 3rd, etc.)
        """
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

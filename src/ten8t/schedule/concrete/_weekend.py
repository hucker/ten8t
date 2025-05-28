import datetime as dt

from .._base import Ten8tBaseSchedule


class Ten8tWeekendSchedule(Ten8tBaseSchedule):
    """
    A schedule that allows tasks to run on weekends
    """

    def __init__(self, name: str = "weekend_schedule"):
        """
        Initialize the schedule.

        Args:
            _inverse (bool): If True, the schedule is inverted (matches weekends instead of weekdays).
            name (str): The name of the schedule.
        """
        super().__init__(name=name)

    def is_due(self, time_: dt.datetime) -> bool:
        """
        Check if the given time is during a weekday.

        Args:
            time (datetime): The time to check.

        Returns:
            bool: True if the time is on a weekday, False otherwise.
        """
        # Weekends (Sat=5,Sun=6)
        return time_.weekday() in {5, 6}

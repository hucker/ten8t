import datetime as dt

from .._base import Ten8tBaseSchedule


class Ten8tWeekdaySchedule(Ten8tBaseSchedule):
    """
    A schedule that allows tasks to run on weekdays (Monday through Friday).
    """

    def __init__(self, name: str = "weekday_schedule"):
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
        # Weekdays (Monday=0, ..., Friday=4)
        return time_.weekday() in {0, 1, 2, 3, 4}

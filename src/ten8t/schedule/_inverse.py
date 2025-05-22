import datetime as dt

from ._base import Ten8tBaseSchedule


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

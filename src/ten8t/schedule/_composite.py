import datetime as dt

from ._base import Ten8tBaseSchedule


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

    def is_due(self, time_: dt.datetime) -> bool:
        """
        Returns True if the given time matches any schedule in the list.
        """
        return any(schedule.is_due(time_) for schedule in self.schedules)

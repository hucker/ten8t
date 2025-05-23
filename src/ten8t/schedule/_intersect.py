from ._base import Ten8tBaseSchedule


class Ten8tIntersectionSchedule(Ten8tBaseSchedule):
    def __init__(self, schedules):
        """Combine multiple schedules with logical AND."""
        super().__init__(name="and composite")
        self.schedules = schedules

    def __repr__(self):
        return f"{self.__class__.__name__}(schedules={self.schedules!r}, name={self.name!r}, last_execution_time={self.last_execution_time!r})"

    def is_time_in_schedule(self, dt):
        """Check if all the schedules include the given time."""
        return all(schedule.is_time_in_schedule(dt) for schedule in self.schedules)

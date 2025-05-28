import datetime as dt

from .._base import Ten8tBaseSchedule
from ...ten8t_exception import Ten8tException
from ...ten8t_util import StrListOrNone, any_to_str_list


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

    def is_due(self, time: dt.datetime) -> bool:
        """Checks whether the given datetime falls within the schedule.

        Args:
            time (datetime.datetime): The datetime object to check.

        Returns:
            bool: Returns `True` if the date is not in the holiday list, otherwise `False`.
        """
        return time.date() not in self.holidays

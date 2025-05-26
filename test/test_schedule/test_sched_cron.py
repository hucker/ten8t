import datetime as dt

import pytest

from ten8t import Ten8tException
from ten8t.schedule import Ten8tCronSchedule


# =======================
# Tests for Ten8tCronSchedule
# =======================
@pytest.mark.parametrize(
    "minute, hour, day_of_month, month, day_of_week, test_time, expected",
    [
        # Match exact times
        ("0", "9", "*", "*", "1", dt.datetime(2023, 10, 9, 9, 0), True),  # Monday, 9:00
        ("*/15", "*", "*", "*", "*", dt.datetime(2023, 10, 1, 15, 15), True),  # Every 15 minutes
        ("10-20", "*", "*", "*", "*", dt.datetime(2023, 10, 1, 15, 15), True),  # Minute range
        ("*", "*", "*", "10", "*", dt.datetime(2023, 10, 1, 12, 30), True),  # October only

        # No match conditions
        ("0", "9", "*", "*", "1", dt.datetime(2023, 10, 9, 10, 0), False),  # Wrong hour
        ("*/15", "*", "*", "*", "*", dt.datetime(2023, 10, 1, 15, 16), False),  # Minute mismatch
        ("*", "*", "*", "9", "*", dt.datetime(2023, 10, 1, 12, 30), False),  # Wrong month (September)
        ("0", "9", "15", "*", "*", dt.datetime(2023, 10, 16, 9, 0), False),  # Wrong day of month

    ],
)
def test_cron_schedule(minute, hour, day_of_month, month, day_of_week, test_time, expected):
    """
    Test Ten8tCronSchedule with a variety of cases.
    """
    schedule = Ten8tCronSchedule(minute=minute, hour=hour, day_of_month=day_of_month, month=month,
                                 day_of_week=day_of_week)
    assert schedule.is_time_in_schedule(test_time) == expected


def test_cron_schedule_execution_tracking():
    """
    Ensure Ten8tCronSchedule tracks last execution times correctly.
    """
    schedule = Ten8tCronSchedule(minute="0-1", hour="9", day_of_week="1")  # Mondays at 9:00
    test_time = dt.datetime(2023, 10, 9, 9, 0)  # Monday, 9:00

    # First execution should succeed
    assert schedule.is_time_in_schedule(test_time) is True
    assert schedule.mark_executed(test_time) is True  # First run
    assert schedule.mark_executed(test_time) is False  # Duplicate should not run again

    # A different valid time should allow execution
    new_time = dt.datetime(2023, 10, 9, 9, 1)  # One minute later
    assert schedule.is_time_in_schedule(new_time) is True
    assert schedule.mark_executed(new_time) is True  # This is a valid new execution
    assert schedule.mark_executed(new_time) is False  # This is a valid new execution

    # A different valid time should allow execution
    new_time = dt.datetime(2023, 10, 9, 9, 2)  # One minute later
    assert schedule.is_time_in_schedule(new_time) is False


def test_invalid_cron_schedules():
    """
    Ensure invalid configuration in Ten8tCronSchedule raises appropriate errors.
    """
    # Invalid minute range
    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(minute="abc")

    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(minute="61")  # Out of range

    # Invalid hour range
    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(hour="25")  # Out of range

    # Invalid day_of_month range
    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(day_of_month="32")  # Out of range

    # Invalid month range
    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(month="13")  # Out of range

    # Invalid day_of_week range
    with pytest.raises(Ten8tException):
        Ten8tCronSchedule(day_of_week="7")  # Out of range


def test_cron_schedule_no_day_of_week_and_day_of_month():
    """
    Test that `day_of_week` and `day_of_month` cannot both be set.
    """
    # Both `day_of_month` and `day_of_week` defined
    with pytest.raises(Ten8tException,
                       match="Invalid schedule: `day_of_month` and `day_of_week` cannot both be defined"):
        Ten8tCronSchedule(minute="0", hour="9", day_of_month="15", day_of_week="1")

    # Only `day_of_month` defined
    schedule = Ten8tCronSchedule(minute="0", hour="9", day_of_month="15")
    test_time = dt.datetime(2023, 10, 15, 9, 0)
    assert schedule.is_time_in_schedule(test_time) is True

    # Only `day_of_week` defined
    schedule = Ten8tCronSchedule(minute="0", hour="9", day_of_week="1")
    test_time = dt.datetime(2023, 10, 16, 9, 0)  # A Monday
    assert schedule.is_time_in_schedule(test_time) is True


def test_ten8t_cron_schedule_repr1():
    # Case 1: Default cron schedule
    cron_schedule = Ten8tCronSchedule()
    assert repr(cron_schedule) == (
        "Ten8tCronSchedule(name='cron', last_execution_time=None)"
    )


def test_ten8t_cron_schedule_repr2():
    # Case 2: Specific schedule and name
    cron_schedule = Ten8tCronSchedule(
        minute="*/15",
        hour="8-18",
        day_of_month="1,15",
        month="1-6",
        name="weekday_mornings",
    )
    cron_schedule.last_execution_time = dt.datetime(2023, 10, 2, 9, 0, 0)
    assert repr(cron_schedule) == (
        "Ten8tCronSchedule(name='weekday_mornings', last_execution_time=2023-10-02 09:00:00)"
    )

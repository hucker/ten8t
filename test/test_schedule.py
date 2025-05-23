"""
Module: _base.py

This module provides the core classes for schedule composition in the Ten8t framework. These classes allow
schedules to be combined, intersected, or inverted, enabling the creation of complex scheduling logic.

### Classes
1. **Ten8tBaseSchedule**: The foundation for all schedules, supporting logical operations like union (`|`),
   intersection (`&`), and inversion (`~`).
2. **Ten8tCompositeSchedule**: Combines multiple schedules into a single schedule (union).
3. **Ten8tIntersectionSchedule**: Evaluates the intersection of multiple schedules.
4. **Ten8tInverseSchedule**: Represents the inverse of a given schedule, matching times outside it.

This design ensures that these classes work together cohesively while avoiding circular import issues.
"""

import datetime as dt
import random

import pytest

from ten8t.schedule import Ten8tBaseSchedule, Ten8tCronSchedule, Ten8tNonHolidaySchedule
from ten8t.schedule import Ten8tCompositeSchedule, Ten8tIntersectionSchedule, Ten8tInverseSchedule
from ten8t.schedule import Ten8tTTLSchedule, Ten8tWeekdaySchedule, Ten8tWeekendSchedule
from ten8t.ten8t_exception import Ten8tException


# =======================
# Tests for Ten8tBaseSchedule
# =======================
def generate_random_time():
    """
    Generate a random time for a datetime object.
    """
    hour = random.randint(0, 23)  # Random hour (24-hour format)
    minute = random.randint(0, 59)  # Random minute
    second = random.randint(0, 59)  # Random second
    return hour, minute, second


def test_base_schedule_fuzzing():
    """
    Fuzz test Ten8tBaseSchedule with all days of a year and random times to
    overkill test this
    """
    schedule = Ten8tBaseSchedule()

    # Define a year (with adjustments for leap years if needed)
    year = 2023  # You can change the year or make this random too
    days_in_year = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365

    for day_of_year in range(1, days_in_year + 1):
        # Generate a date from the day of the year
        base_date = dt.datetime(year, 1, 1) + dt.timedelta(days=day_of_year - 1)

        # Test with multiple random times for each day
        for _ in range(24):  # 24 random times per day
            hour, minute, second = generate_random_time()
            random_datetime = base_date.replace(hour=hour, minute=minute, second=second)

            # Assert that the schedule always "runs" (returns True)
            assert schedule.is_time_in_schedule(random_datetime) is True, f"Failed for {random_datetime}"


def test_base_schedule_no_duplicate_runs():
    """
    Ensure duplicate runs for the same time in Ten8tBaseSchedule are not recorded.
    """
    schedule = Ten8tBaseSchedule()
    now = dt.datetime.now()

    # First run should succeed
    assert schedule.run_now(now) is True

    # Same time should result in no new run
    assert schedule.run_now(now) is False

    # Future time should allow a new run
    future_time = now + dt.timedelta(minutes=1)
    assert schedule.run_now(future_time) is True


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
    assert schedule.run_now(test_time) is True  # First run
    assert schedule.run_now(test_time) is False  # Duplicate should not run again

    # A different valid time should allow execution
    new_time = dt.datetime(2023, 10, 9, 9, 1)  # One minute later
    assert schedule.is_time_in_schedule(new_time) is True
    assert schedule.run_now(new_time) is True  # This is a valid new execution
    assert schedule.run_now(new_time) is False  # This is a valid new execution

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


def test_ten8t_base_schedule_repr():
    # Case 1: Default initialization
    base_schedule = Ten8tBaseSchedule()
    assert repr(base_schedule) == "Ten8tBaseSchedule(name='base', last_execution_time=None)"

    # Case 2: Custom name and no execution time
    base_schedule = Ten8tBaseSchedule(name="custom_schedule")
    assert repr(base_schedule) == "Ten8tBaseSchedule(name='custom_schedule', last_execution_time=None)"

    # Case 3: Custom name and a specific last execution time
    last_exec_time = dt.datetime(2023, 10, 1, 12, 0, 0)
    base_schedule.last_execution_time = last_exec_time
    assert repr(base_schedule) == (
        "Ten8tBaseSchedule(name='custom_schedule', last_execution_time=2023-10-01 12:00:00)"
    )



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



@pytest.fixture
def always_true_schedule():
    """A schedule that always returns True."""

    class AlwaysTrueSchedule(Ten8tBaseSchedule):
        def is_time_in_schedule(self, time: dt.datetime) -> bool:
            return True

    return AlwaysTrueSchedule(name="always_true")


@pytest.fixture
def always_false_schedule():
    """A schedule that always returns False."""

    class AlwaysFalseSchedule(Ten8tBaseSchedule):
        def is_time_in_schedule(self, time: dt.datetime) -> bool:
            return False

    return AlwaysFalseSchedule(name="always_false")


@pytest.fixture
def specific_time_schedule():
    """A schedule that matches only a specific time."""

    class SpecificTimeSchedule(Ten8tBaseSchedule):
        def is_time_in_schedule(self, time: dt.datetime) -> bool:
            # Returns True only for 12:30
            return time.hour == 12 and time.minute == 30

    return SpecificTimeSchedule(name="specific_time")


@pytest.fixture
def divisible_by_15_schedule():
    """A schedule allowing times when the minute is divisible by 15."""

    class DivisibleBy15Schedule(Ten8tBaseSchedule):
        def is_time_in_schedule(self, time: dt.datetime) -> bool:
            return time.minute % 15 == 0

    return DivisibleBy15Schedule(name="divisible_by_15")


def test_inverse_repr(divisible_by_15_schedule):
    ndiv_15 = ~divisible_by_15_schedule
    assert repr(ndiv_15).startswith("Ten8tInverseSchedule")


def test_or_repr(specific_time_schedule, divisible_by_15_schedule):
    or_sched = specific_time_schedule | divisible_by_15_schedule
    assert repr(or_sched).startswith("Ten8tCompositeSchedule")


def test_and_repr(specific_time_schedule, divisible_by_15_schedule):
    and_sched = specific_time_schedule & divisible_by_15_schedule
    assert repr(and_sched).startswith("Ten8tIntersectionSchedule")

def test_or_logic_with_always_true_and_false(
        always_true_schedule, always_false_schedule
):
    """Test OR operation between always-true and always-false schedules."""
    composite_schedule = always_true_schedule | always_false_schedule

    # Test with arbitrary times - always_true should dominate the OR logic
    test_time = dt.datetime(2023, 10, 20, 14, 0)
    assert composite_schedule.is_time_in_schedule(test_time)

    test_time2 = dt.datetime(2023, 10, 20, 14, 30)
    assert composite_schedule.is_time_in_schedule(test_time2)


def test_or_logic_with_specific_and_false(
        specific_time_schedule, always_false_schedule
):
    """Test OR operation between a specific-time schedule and always-false."""
    composite_schedule = specific_time_schedule | always_false_schedule

    # Test time that matches specific_time_schedule
    matching_time = dt.datetime(2023, 10, 20, 12, 30)
    assert composite_schedule.is_time_in_schedule(matching_time)

    # Test arbitrary time (does not match specific_time_schedule)
    non_matching_time = dt.datetime(2023, 10, 20, 14, 0)
    assert not composite_schedule.is_time_in_schedule(non_matching_time)


def test_exhaustive_or_logic_with_two_schedules(specific_time_schedule, divisible_by_15_schedule):
    """
    Exhaustive test: Validate OR logic between two schedules by testing all 60 minutes of a specific hour.
    """
    composite_schedule = specific_time_schedule | divisible_by_15_schedule

    # Test all 60 minutes in a specific hour (2023-10-20, 12:00 to 12:59)
    hour_to_test = dt.datetime(2023, 10, 20, 12, 0)
    for minute in range(60):
        current_time = hour_to_test.replace(minute=minute)

        # Check the expected result
        is_in_specific_schedule = (minute == 30)  # specific_time_schedule matches 12:30 only
        is_in_divisible_schedule = (minute % 15 == 0)  # divisible_by_15_schedule matches every 15th minute
        expected_result = is_in_specific_schedule or is_in_divisible_schedule

        # Assert that the composite schedule matches the expected result
        assert composite_schedule.is_time_in_schedule(current_time) == expected_result


def test_chained_or_logic(
        always_true_schedule, specific_time_schedule, divisible_by_15_schedule
):
    """Test chaining OR operations between multiple schedules."""
    composite_schedule = (
            always_true_schedule | specific_time_schedule | divisible_by_15_schedule
    )

    # Test an arbitrary time - always_true should dominate
    random_time = dt.datetime(2023, 10, 20, 8, 45)
    assert composite_schedule.is_time_in_schedule(random_time)

    # Test time matching the specific_time_schedule
    specific_time = dt.datetime(2023, 10, 20, 12, 30)
    assert composite_schedule.is_time_in_schedule(specific_time)

    # Test time matching the divisible_by_15_schedule
    divisible_time = dt.datetime(2023, 10, 20, 9, 15)
    assert composite_schedule.is_time_in_schedule(divisible_time)


def test_flatten_nested_or_composites(specific_time_schedule, divisible_by_15_schedule):
    """Test nested OR operations are flattened and logic remains valid."""
    composite1 = specific_time_schedule | divisible_by_15_schedule
    composite2 = composite1 | divisible_by_15_schedule  # Nesting composite schedules

    # Test time that DOES match specific_time_schedule
    specific_time = dt.datetime(2023, 10, 20, 12, 30)
    assert composite2.is_time_in_schedule(specific_time)

    # Test time that DOES match divisible_by_15_schedule
    divisible_time = dt.datetime(2023, 10, 20, 11, 45)
    assert composite2.is_time_in_schedule(divisible_time)

    # Test time that matches NEITHER schedule
    non_matching_time = dt.datetime(2023, 10, 20, 8, 13)
    assert not composite2.is_time_in_schedule(non_matching_time)


def test_all_days_in_year_with_holidays():
    """Test `Ten8tNonHolidaySchedule` for all days in a year."""

    # Define holidays for the year
    holidays = [
        dt.date(2023, 1, 1),  # New Year's Day
        dt.date(2023, 7, 4),  # Independence Day
        dt.date(2023, 12, 25)  # Christmas Day
    ]

    # Initialize the schedule
    schedule = Ten8tNonHolidaySchedule(holidays=holidays)

    # Start testing from January 1, 2023
    jan1 = dt.date(2023, 1, 1)

    # Loop over 365 days of the year
    for day_offset in range(365):
        current_date = jan1 + dt.timedelta(days=day_offset)

        # Check if the current date is a holiday
        if current_date in holidays:
            assert not schedule.is_time_in_schedule(
                dt.datetime.combine(current_date, dt.time(12, 0))
            ), f"Failed for holiday {current_date}"
        else:
            assert schedule.is_time_in_schedule(
                dt.datetime.combine(current_date, dt.time(12, 0))
            ), f"Failed for non-holiday {current_date}"


def test_holidays_parsed_from_config():
    """Test that holidays are correctly parsed from a config dictionary."""

    # Define configuration with holidays as a comma-separated string
    config = {'holidays': '2023-01-01 2023-07-04 2023-12-25'}

    # Initialize the schedule
    schedule = Ten8tNonHolidaySchedule(config=config)

    # List of expected holiday dates
    expected_holidays = [
        dt.date(2023, 1, 1),  # New Year's Day
        dt.date(2023, 7, 4),  # Independence Day
        dt.date(2023, 12, 25)  # Christmas Day
    ]

    # Check if each expected holiday is actually excluded
    for holiday in expected_holidays:
        assert not schedule.is_time_in_schedule(
            dt.datetime.combine(holiday, dt.time(12, 0))
        ), f"Failed to exclude holiday {holiday}"

    # Check a non-holiday date to ensure it's included
    non_holiday = dt.date(2023, 1, 2)  # Day after New Year's Day
    assert schedule.is_time_in_schedule(
        dt.datetime.combine(non_holiday, dt.time(12, 0))
    ), f"Incorrectly excluded non-holiday {non_holiday}"


class AlwaysTrueSchedule(Ten8tBaseSchedule):
    def is_time_in_schedule(self, time: dt.datetime) -> bool:
        return True  # Always valid for any time


class SpecificHourSchedule(Ten8tBaseSchedule):
    def __init__(self, valid_hour: int, name="specific_hour"):
        super().__init__(name)
        self.valid_hour = valid_hour

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        return time_.hour == self.valid_hour and time_.minute == 0


class SpecificMinuteSchedule(Ten8tBaseSchedule):
    def __init__(self, valid_minute: int, name="specific_minute"):
        super().__init__(name)
        self.valid_minute = valid_minute

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        return time_.minute == self.valid_minute


class SpecificWeekdaySchedule(Ten8tBaseSchedule):
    def __init__(self, valid_weekday, name="specific_weekday"):
        super().__init__(name=name)
        self.valid_weekday = valid_weekday  # Python weekday: 0=Monday, ..., 6=Sunday

    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        return time_.weekday() == self.valid_weekday


def test_and_operator_with_mixed_schedules():
    """
    Test intersecting schedules where one is always valid and the
    other restricts to a specific minute.
    """
    schedule1 = AlwaysTrueSchedule(name="always_true")
    schedule2 = SpecificMinuteSchedule(valid_minute=15, name="only_minute_15")
    combined_schedule = schedule1 & schedule2

    # Verify the type of the combined schedule
    assert isinstance(combined_schedule, Ten8tIntersectionSchedule)

    # Test valid and invalid times
    valid_time = dt.datetime(2023, 12, 25, 10, 15)  # 10:15 is valid for both
    invalid_time = dt.datetime(2023, 12, 25, 10, 30)  # 10:30 is invalid for schedule2

    assert combined_schedule.is_time_in_schedule(valid_time) is True
    assert combined_schedule.is_time_in_schedule(invalid_time) is False


def test_and_operator_with_all_invalid():
    """
    Test intersecting schedules where no time is allowed in both schedules.
    """
    schedule1 = SpecificHourSchedule(valid_hour=10, name="only_10")
    schedule2 = SpecificHourSchedule(valid_hour=11, name="only_11")
    combined_schedule = schedule1 & schedule2

    test_time = dt.datetime(2023, 12, 25, 10, 0)  # 10:00 is only valid in schedule1
    assert combined_schedule.is_time_in_schedule(test_time) is False


def test_and_operator_with_all_valid():
    """
    Test intersecting schedules where the same time satisfies all conditions.
    """

    # Create two schedules with overlapping constraints
    schedule1 = SpecificHourSchedule(valid_hour=12, name="noon_schedule")
    schedule2 = SpecificHourSchedule(valid_hour=12, name="midday_schedule")

    # Combine the schedules using the AND operator
    combined_schedule = schedule1 & schedule2

    # Test a valid time that matches both schedule conditions
    valid_time = dt.datetime(2023, 12, 25, 12, 0, 0)
    assert combined_schedule.is_time_in_schedule(valid_time) is True

    # Test an invalid time that does not match the conditions
    invalid_time = dt.datetime(2023, 12, 25, 13, 0, 0)
    assert combined_schedule.is_time_in_schedule(invalid_time) is False


# Define parameterized test cases
test_cases = [
    (dt.datetime(2023, 12, 20, 15, 0, 0), True),  # Wednesday at 3 PM (matches weekday & hour)
    (dt.datetime(2023, 12, 20, 10, 0, 0), False),  # Wednesday at 10 AM (fails hour condition)
    (dt.datetime(2023, 12, 19, 15, 0, 0), True),  # Tuesday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 19, 10, 0, 0), True),  # Tuesday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 21, 15, 0, 0), True),  # Thursday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 21, 10, 0, 0), True),  # Thursday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 20, 20, 0, 0), False),  # Wednesday at 8 PM (fails hour condition)
    (dt.datetime(2023, 12, 18, 15, 0, 0), True),  # Monday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 18, 10, 0, 0), True),  # Monday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 22, 15, 0, 0), True),  # Friday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 22, 10, 0, 0), True),  # Friday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 23, 15, 0, 0), True),  # Saturday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 23, 10, 0, 0), True),  # Saturday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 24, 15, 0, 0), True),  # Sunday at 3 PM (matches ~weekday)
    (dt.datetime(2023, 12, 24, 10, 0, 0), True),  # Sunday at 10 AM (matches ~weekday)
    (dt.datetime(2023, 12, 20, 15, 15, 0), False),
    # Wednesday at 3:15 PM (fails hour condition since not exactly 3:00 PM)
    (dt.datetime(2023, 12, 20, 15, 59, 0), False),  # Wednesday at 3:59 PM (fails hour condition just before 4 PM)
]


@pytest.mark.parametrize("test_time, expected", test_cases)
def test_complex_combination_of_operators(test_time, expected):
    """
    Parameterized test for a complex combination of |, & and ~ operators.
    Assumes SpecificHourSchedule and SpecificWeekdaySchedule exist.
    """

    # Create specific schedules
    weekday_schedule = SpecificWeekdaySchedule(valid_weekday=2, name="wednesday_schedule")  # Restricts to Wednesday
    hour_schedule = SpecificHourSchedule(valid_hour=15, name="afternoon_schedule")  # Restricts to 3 PM

    # Create a combined schedule with |, & and ~ operators
    combined_schedule = ~weekday_schedule | (weekday_schedule & hour_schedule)

    # Evaluate if the test_time matches the combined_schedule
    assert combined_schedule.is_time_in_schedule(test_time) == expected, (
        f"Failed for time: {test_time}, expected: {expected}"
    )


def test_invalid_granularity():
    """Test initialization raises error for negative TTL minutes."""
    with pytest.raises(Ten8tException, match="Invalid granularity"):
        Ten8tBaseSchedule(name="test_schedule", granularity='foo')


def test_invalid_name():
    """Test initialization raises error for negative TTL minutes."""
    for name_ in ['', ' ', None]:
        with pytest.raises(Ten8tException, match="Name must be provided"):
            Ten8tBaseSchedule(name=name_)


def test_day_granularity():
    # Test schedule with "day" granularity
    schedule = Ten8tBaseSchedule(name="day_schedule", granularity="day")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.run_now(time_now) is True

    # Second execution within the same day: should fail
    same_day = time_now + dt.timedelta(hours=5)
    assert schedule.run_now(same_day) is False

    # Execution on the next day: should succeed
    next_day = time_now + dt.timedelta(days=1)
    assert schedule.run_now(next_day) is True


def test_hour_granularity():
    # Test schedule with "hour" granularity
    schedule = Ten8tBaseSchedule(name="hour_schedule", granularity="hour")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.run_now(time_now) is True

    # Second execution within the same hour: should fail
    same_hour = time_now + dt.timedelta(minutes=30)
    assert schedule.run_now(same_hour) is False

    # Execution in the next hour: should succeed
    next_hour = time_now + dt.timedelta(hours=1)
    assert schedule.run_now(next_hour) is True


def test_minute_granularity():
    # Test schedule with "minute" granularity
    schedule = Ten8tBaseSchedule(name="minute_schedule", granularity="minute")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.run_now(time_now) is True

    # Second execution within the same minute: should fail
    same_minute = time_now + dt.timedelta(seconds=30)
    assert schedule.run_now(same_minute) is False

    # Execution in the next minute: should succeed
    next_minute = time_now + dt.timedelta(minutes=1)
    assert schedule.run_now(next_minute) is True


def test_second_granularity():
    # Test schedule with "second" granularity
    schedule = Ten8tBaseSchedule(name="second_schedule", granularity="second")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.run_now(time_now) is True

    # Second execution within the same second: should fail
    same_second = time_now + dt.timedelta(milliseconds=500)
    assert schedule.run_now(same_second) is False

    # Execution in the next second: should succeed
    next_second = time_now + dt.timedelta(seconds=1)
    assert schedule.run_now(next_second) is True


def test_initialize_with_seconds():
    """Test initialization with a valid TTL in seconds."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    assert schedule.ttl_sec == 30
    assert schedule.name == "test_schedule"


def test_initialize_with_minutes():
    """Test initialization with a valid TTL in minutes."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_min=1)
    assert schedule.ttl_sec == 60  # Should convert minutes to seconds


def test_initialize_with_no_ttl():
    """Test initialization raises error if no TTL is provided."""
    with pytest.raises(Ten8tException, match="You must provide either ttl_sec or ttl_min."):
        Ten8tTTLSchedule(name="test_schedule")


def test_initialize_with_negative_ttl_seconds():
    """Test initialization raises error for negative TTL seconds."""
    with pytest.raises(Ten8tException, match="TTL in seconds must be greater than zero."):
        Ten8tTTLSchedule(name="test_schedule", ttl_sec=-10)


def test_initialize_with_negative_ttl_minutes():
    """Test initialization raises error for negative TTL minutes."""
    with pytest.raises(Ten8tException, match="TTL in minutes must be greater than zero."):
        Ten8tTTLSchedule(name="test_schedule", ttl_min=-5)


def test_first_execution_runs_immediately():
    """Test that the first execution always runs immediately."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    result = schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))
    assert result is True
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 0)


def test_execution_blocks_within_ttl():
    """Test that executions block if within TTL threshold."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 15))
    assert result is False  # Should block since only 15s have passed
    # Last execution time should remain unchanged
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 0)


def test_execution_allows_after_ttl():
    """Test that executions allow after TTL threshold."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 31))
    assert result is True  # Should allow since 31s have passed
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 31)


def test_execution_at_exact_ttl_boundary():
    """Test behavior exactly at the TTL boundary."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.run_now(execution_time=dt.datetime(2023, 1, 1, 12, 0, 30))
    assert result is True  # Should allow at exactly 30s
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 30)


def test_ttl_default_execution_time():
    """Test that run_now uses current time when no execution_time is provided."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=0)  # Zero TTL for testing
    result = schedule.run_now()  # No execution_time provided
    assert result is True
    assert schedule.last_execution_time is not None  # Should have set a timestamp


def test_ttl_repr():
    """Test the string representation (repr) for debugging."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=60)
    execution_time = dt.datetime(2023, 1, 1, 12, 0, 0)
    schedule.run_now(execution_time=execution_time)

    expected_repr = (
        f"Ten8tTTLSchedule(name='test_schedule', "
        f"last_execution_time={execution_time}, "
        f"ttl_sec=60)"
    )
    assert repr(schedule) == expected_repr


def test_multiple_invalid_operations():
    """Test a combination of invalid operations."""
    schedule = Ten8tBaseSchedule()

    # Test that operations with non-schedule objects raise exceptions
    with pytest.raises(Ten8tException):
        schedule | "not a schedule"

    with pytest.raises(Ten8tException):
        schedule & 42

    with pytest.raises(Ten8tException):
        schedule | None

    with pytest.raises(Ten8tException):
        schedule & {}


def test_weekday_schedule_initialization():
    """Test initialization of the weekday schedule."""
    # Test default name
    schedule = Ten8tWeekdaySchedule()
    assert schedule.name == "weekday_schedule"

    # Test custom name
    custom_schedule = Ten8tWeekdaySchedule(name="custom_weekday")
    assert custom_schedule.name == "custom_weekday"

    # Test empty name should raise an exception
    with pytest.raises(Ten8tException):
        Ten8tWeekdaySchedule(name="")


def test_weekday_schedule_is_time_in_schedule():
    """Test the is_time_in_schedule method for weekdays."""
    schedule = Ten8tWeekdaySchedule()

    # Test weekdays (Monday through Friday)
    monday = dt.datetime(2023, 7, 3)  # A Monday
    assert monday.weekday() == 0
    assert schedule.is_time_in_schedule(monday)

    wednesday = dt.datetime(2023, 7, 5)  # A Wednesday
    assert wednesday.weekday() == 2
    assert schedule.is_time_in_schedule(wednesday)

    friday = dt.datetime(2023, 7, 7)  # A Friday
    assert friday.weekday() == 4
    assert schedule.is_time_in_schedule(friday)

    # Test weekends (should return False)
    saturday = dt.datetime(2023, 7, 8)  # A Saturday
    assert saturday.weekday() == 5
    assert not schedule.is_time_in_schedule(saturday)

    sunday = dt.datetime(2023, 7, 9)  # A Sunday
    assert sunday.weekday() == 6
    assert not schedule.is_time_in_schedule(sunday)


def test_weekend_schedule_initialization():
    """Test initialization of the weekend schedule."""
    # Test default name
    schedule = Ten8tWeekendSchedule()
    assert schedule.name == "weekend_schedule"

    # Test custom name
    custom_schedule = Ten8tWeekendSchedule(name="weekend_only")
    assert custom_schedule.name == "weekend_only"

    # Test empty name should raise an exception
    with pytest.raises(Ten8tException):
        Ten8tWeekendSchedule(name="")


def test_weekend_schedule_is_time_in_schedule():
    """Test the is_time_in_schedule method for weekends."""
    schedule = Ten8tWeekendSchedule()

    # Test weekdays (Monday through Friday) - should return False
    monday = dt.datetime(2023, 7, 3)  # A Monday
    assert monday.weekday() == 0
    assert not schedule.is_time_in_schedule(monday)

    wednesday = dt.datetime(2023, 7, 5)  # A Wednesday
    assert wednesday.weekday() == 2
    assert not schedule.is_time_in_schedule(wednesday)

    friday = dt.datetime(2023, 7, 7)  # A Friday
    assert friday.weekday() == 4
    assert not schedule.is_time_in_schedule(friday)

    # Test weekends (should return True)
    saturday = dt.datetime(2023, 7, 8)  # A Saturday
    assert saturday.weekday() == 5
    assert schedule.is_time_in_schedule(saturday)

    sunday = dt.datetime(2023, 7, 9)  # A Sunday
    assert sunday.weekday() == 6
    assert schedule.is_time_in_schedule(sunday)


def test_weekday_and_weekend_schedules_are_complementary():
    """Test that weekday and weekend schedules are complementary."""
    weekday_schedule = Ten8tWeekdaySchedule()
    weekend_schedule = Ten8tWeekendSchedule()

    # Test for a full week that the schedules are complementary
    start_date = dt.datetime(2023, 7, 3)  # A Monday
    for days in range(7):
        test_date = start_date + dt.timedelta(days=days)
        # For any given day, exactly one of these schedules should return True
        assert weekday_schedule.is_time_in_schedule(test_date) != weekend_schedule.is_time_in_schedule(test_date)
        # Both schedules together should cover every day
        assert weekday_schedule.is_time_in_schedule(test_date) or weekend_schedule.is_time_in_schedule(test_date)


def test_operator_classes_coverage():
    """Test to ensure coverage of the operator overloading classes."""
    # Create two base schedules
    schedule1 = Ten8tBaseSchedule(name="schedule1")
    schedule2 = Ten8tBaseSchedule(name="schedule2")

    # Get a specific time for consistent testing
    test_time = dt.datetime(2023, 7, 10, 12, 0, 0)

    # Test OR operator (__or__) directly
    result_or = schedule1.__or__(schedule2)
    assert isinstance(result_or, Ten8tCompositeSchedule)
    assert result_or.is_time_in_schedule(test_time) == True  # Base schedule always returns True
    assert (schedule1 | schedule2).is_time_in_schedule(test_time) == result_or.is_time_in_schedule(test_time)

    # Test AND operator (__and__) directly
    result_and = schedule1.__and__(schedule2)
    assert isinstance(result_and, Ten8tIntersectionSchedule)
    assert result_and.is_time_in_schedule(test_time) == True  # Base schedule always returns True
    assert (schedule1 & schedule2).is_time_in_schedule(test_time) == result_and.is_time_in_schedule(test_time)

    # Test NOT operator (__invert__) directly
    result_invert = schedule1.__invert__()
    assert isinstance(result_invert, Ten8tInverseSchedule)
    assert result_invert.is_time_in_schedule(test_time) == False  # Inverse of True is False
    assert (~schedule1).is_time_in_schedule(test_time) == result_invert.is_time_in_schedule(test_time)

    # Additional tests to exercise methods within each class

    # Test composite schedule with multiple inputs
    composite = Ten8tCompositeSchedule(schedules=[schedule1, schedule2], name="composite_test")
    assert composite.is_time_in_schedule(test_time) == True

    # Test intersection schedule with multiple inputs
    intersection = Ten8tIntersectionSchedule(schedules=[schedule1, schedule2], name="intersection_test")
    assert intersection.is_time_in_schedule(test_time) == True

    # Test inverse schedule
    inverse = Ten8tInverseSchedule(schedule=schedule1)
    assert inverse.is_time_in_schedule(test_time) == False

    # Test repr methods for coverage
    assert "Ten8tCompositeSchedule" in repr(composite)
    assert "Ten8tIntersectionSchedule" in repr(intersection)
    assert "Ten8tInverseSchedule" in repr(inverse)

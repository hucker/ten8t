import datetime as dt
import random

import pytest

from ten8t.schedule import Ten8tBaseSchedule, Ten8tCronSchedule, Ten8tNonHolidaySchedule
from ten8t.schedule import Ten8tIntersectionSchedule
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
    assert repr(
        base_schedule) == f"Ten8tBaseSchedule(name='custom_schedule', last_execution_time={repr(last_exec_time)})"


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
        f"Ten8tCronSchedule(name='weekday_mornings', "
        f"last_execution_time={cron_schedule.last_execution_time!r})"
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
    """A schedule allowing times where the minute is divisible by 15."""

    class DivisibleBy15Schedule(Ten8tBaseSchedule):
        def is_time_in_schedule(self, time: dt.datetime) -> bool:
            return time.minute % 15 == 0

    return DivisibleBy15Schedule(name="divisible_by_15")


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


class MidnightSchedule(Ten8tBaseSchedule):
    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        return time_.hour == 0 and time_.minute == 0


class EndOfDaySchedule(Ten8tBaseSchedule):
    def is_time_in_schedule(self, time_: dt.datetime) -> bool:
        return time_.hour == 23 and time_.minute == 59 and time_.second == 59


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

import datetime as dt
import random

import pytest

from ten8t import Ten8tBaseSchedule, Ten8tCompositeSchedule, Ten8tIntersectionSchedule, Ten8tInverseSchedule
from ten8t import Ten8tException


@pytest.fixture
def schedule():
    """Create a fresh schedule instance for each test."""
    return Ten8tBaseSchedule(name="test_schedule", granularity="minute")


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
    assert schedule.mark_executed(now) is True

    # Same time should result in no new run
    assert schedule.mark_executed(now) is False

    # Future time should allow a new run
    future_time = now + dt.timedelta(minutes=1)
    assert schedule.mark_executed(future_time) is True


def test_normalize_time(schedule):
    """Test that time normalization works correctly with different granularities."""
    test_time = dt.datetime(2023, 1, 1, 12, 34, 56, 789)

    # Test minute granularity (default)
    normalized = schedule._normalize_time(test_time)
    assert normalized == dt.datetime(2023, 1, 1, 12, 34, 0, 0)

    # Test hour granularity
    schedule.granularity = "hour"
    normalized = schedule._normalize_time(test_time)
    assert normalized == dt.datetime(2023, 1, 1, 12, 0, 0, 0)

    # Test day granularity
    schedule.granularity = "day"
    normalized = schedule._normalize_time(test_time)
    assert normalized == dt.datetime(2023, 1, 1, 0, 0, 0, 0)

    # Test second granularity
    schedule.granularity = "second"
    normalized = schedule._normalize_time(test_time)
    assert normalized == dt.datetime(2023, 1, 1, 12, 34, 56, 0)


def test_execution_context_success_flow(schedule):
    """Test that the context manager correctly yields True and marks execution when successful."""
    test_time = dt.datetime(2023, 1, 1, 12, 34, 56)

    # Ensure it's a fresh execution
    assert schedule.last_execution_time is None

    # Use the context manager with explicit time
    with schedule.once_per_interval(execution_time=test_time) as first_time:
        assert first_time

    # Verify execution was marked (with granularity of minute)
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 34, 0)


def test_execution_context_duplicate_execution(schedule):
    """Test that the context manager correctly skips duplicate executions."""

    test_time = dt.datetime(2023, 1, 1, 12, 34, 10)
    with schedule.once_per_interval(execution_time=test_time) as first_time:
        pass
    assert first_time

    # Second execution at the same minute should be skipped, even with different seconds
    different_seconds = dt.datetime(2023, 1, 1, 12, 34, 20)
    with schedule.once_per_interval(execution_time=different_seconds) as first_time:
        assert not first_time

    # Execution at a different minute should run
    different_minute = dt.datetime(2023, 1, 1, 12, 35, 0)
    with schedule.once_per_interval(execution_time=different_minute) as first_time:
        assert first_time

    # Verify the latest execution time is recorded
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 35, 0)


def test_different_granularities():
    """Test the behavior with different granularity settings."""

    # Test with hour granularity
    hour_schedule = Ten8tBaseSchedule(name="hour_schedule", granularity="hour")
    test_time = dt.datetime(2023, 1, 1, 12, 30, 45)

    with hour_schedule.once_per_interval(execution_time=test_time) as first_time:
        assert first_time

    # Last execution time should have minutes and seconds zeroed out
    assert hour_schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 0)

    # Test with day granularity
    day_schedule = Ten8tBaseSchedule(name="day_schedule", granularity="day")
    with day_schedule.once_per_interval(execution_time=test_time) as first_time:
        assert first_time

    # Last execution time should have hours, minutes and seconds zeroed out
    assert day_schedule.last_execution_time == dt.datetime(2023, 1, 1, 0, 0, 0)


def test_consecutive_days(schedule):
    """Test execution on consecutive days."""
    # Set granularity to day
    schedule.granularity = "day"

    # Execution on first day
    day1 = dt.datetime(2023, 1, 1, 15, 30, 0)
    assert schedule.can_execute(execution_time=day1) is True
    schedule.mark_executed(execution_time=day1)

    # Check that another execution on the same day is rejected
    same_day_later = dt.datetime(2023, 1, 1, 18, 45, 0)
    assert schedule.can_execute(execution_time=same_day_later) is False

    # Check that execution on the next day is allowed
    next_day = dt.datetime(2023, 1, 2, 10, 15, 0)
    assert schedule.can_execute(execution_time=next_day) is True


def test_rollover_at_midnight(schedule):
    """Test that execution rolls over correctly at midnight."""
    # Set granularity to hour to make testing easier
    schedule.granularity = "hour"

    # Execution before midnight
    before_midnight = dt.datetime(2023, 1, 1, 23, 45, 0)
    schedule.mark_executed(execution_time=before_midnight)

    # Last execution time should be at the hour boundary
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 23, 0, 0)

    # Execution after midnight should be allowed (new hour)
    after_midnight = dt.datetime(2023, 1, 2, 0, 15, 0)
    assert schedule.can_execute(execution_time=after_midnight) is True


def test_can_execute_without_prior_execution(schedule):
    """Test that can_execute returns True when no prior execution exists."""
    test_time = dt.datetime(2023, 1, 1, 12, 0, 0)
    assert schedule.last_execution_time is None
    assert schedule.can_execute(execution_time=test_time) is True


def test_manual_execution_tracking(schedule):
    """Test the manual pattern of checking can_execute followed by mark_executed."""
    test_time = dt.datetime(2023, 1, 1, 12, 30, 0)

    # Check if execution is allowed
    can_run = schedule.can_execute(execution_time=test_time)
    assert can_run is True

    # Mark as executed
    result = schedule.mark_executed(execution_time=test_time)
    assert result is True
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 30, 0, 0)

    # Check again - should not be allowed now
    can_run_again = schedule.can_execute(execution_time=test_time)
    assert can_run_again is False


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
    intersection = Ten8tIntersectionSchedule(schedules=[schedule1, schedule2])
    assert intersection.is_time_in_schedule(test_time) == True

    # Test inverse schedule
    inverse = Ten8tInverseSchedule(schedule=schedule1)
    assert inverse.is_time_in_schedule(test_time) == False

    # Test repr methods for coverage
    assert "Ten8tCompositeSchedule" in repr(composite)
    assert "Ten8tIntersectionSchedule" in repr(intersection)
    assert "Ten8tInverseSchedule" in repr(inverse)


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
    assert schedule.mark_executed(time_now) is True

    # Second execution within the same day: should fail
    same_day = time_now + dt.timedelta(hours=5)
    assert schedule.mark_executed(same_day) is False

    # Execution on the next day: should succeed
    next_day = time_now + dt.timedelta(days=1)
    assert schedule.mark_executed(next_day) is True


def test_hour_granularity():
    # Test schedule with "hour" granularity
    schedule = Ten8tBaseSchedule(name="hour_schedule", granularity="hour")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.mark_executed(time_now) is True

    # Second execution within the same hour: should fail
    same_hour = time_now + dt.timedelta(minutes=30)
    assert schedule.mark_executed(same_hour) is False

    # Execution in the next hour: should succeed
    next_hour = time_now + dt.timedelta(hours=1)
    assert schedule.mark_executed(next_hour) is True


def test_minute_granularity():
    # Test schedule with "minute" granularity
    schedule = Ten8tBaseSchedule(name="minute_schedule", granularity="minute")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.mark_executed(time_now) is True

    # Second execution within the same minute: should fail
    same_minute = time_now + dt.timedelta(seconds=30)
    assert schedule.mark_executed(same_minute) is False

    # Execution in the next minute: should succeed
    next_minute = time_now + dt.timedelta(minutes=1)
    assert schedule.mark_executed(next_minute) is True


def test_second_granularity():
    # Test schedule with "second" granularity
    schedule = Ten8tBaseSchedule(name="second_schedule", granularity="second")
    time_now = dt.datetime(2023, 10, 1, 10, 0, 0)

    # First execution: should succeed
    assert schedule.mark_executed(time_now) is True

    # Second execution within the same second: should fail
    same_second = time_now + dt.timedelta(milliseconds=500)
    assert schedule.mark_executed(same_second) is False

    # Execution in the next second: should succeed
    next_second = time_now + dt.timedelta(seconds=1)
    assert schedule.mark_executed(next_second) is True


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

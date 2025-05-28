import datetime as dt

import pytest

from ten8t import Ten8tException, Ten8tWeekdaySchedule, Ten8tWeekendSchedule


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
    assert schedule.is_due(monday)

    wednesday = dt.datetime(2023, 7, 5)  # A Wednesday
    assert wednesday.weekday() == 2
    assert schedule.is_due(wednesday)

    friday = dt.datetime(2023, 7, 7)  # A Friday
    assert friday.weekday() == 4
    assert schedule.is_due(friday)

    # Test weekends (should return False)
    saturday = dt.datetime(2023, 7, 8)  # A Saturday
    assert saturday.weekday() == 5
    assert not schedule.is_due(saturday)

    sunday = dt.datetime(2023, 7, 9)  # A Sunday
    assert sunday.weekday() == 6
    assert not schedule.is_due(sunday)


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
    assert not schedule.is_due(monday)

    wednesday = dt.datetime(2023, 7, 5)  # A Wednesday
    assert wednesday.weekday() == 2
    assert not schedule.is_due(wednesday)

    friday = dt.datetime(2023, 7, 7)  # A Friday
    assert friday.weekday() == 4
    assert not schedule.is_due(friday)

    # Test weekends (should return True)
    saturday = dt.datetime(2023, 7, 8)  # A Saturday
    assert saturday.weekday() == 5
    assert schedule.is_due(saturday)

    sunday = dt.datetime(2023, 7, 9)  # A Sunday
    assert sunday.weekday() == 6
    assert schedule.is_due(sunday)


def test_weekday_and_weekend_schedules_are_complementary():
    """Test that weekday and weekend schedules are complementary."""
    weekday_schedule = Ten8tWeekdaySchedule()
    weekend_schedule = Ten8tWeekendSchedule()

    # Test for a full week that the schedules are complementary
    start_date = dt.datetime(2023, 7, 3)  # A Monday
    for days in range(7):
        test_date = start_date + dt.timedelta(days=days)
        # For any given day, exactly one of these schedules should return True
        assert weekday_schedule.is_due(test_date) != weekend_schedule.is_due(test_date)
        # Both schedules together should cover every day
        assert weekday_schedule.is_due(test_date) or weekend_schedule.is_due(test_date)

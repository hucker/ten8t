import datetime as dt

import pytest

from ten8t.schedule import Ten8tNthWeekdaySchedule
from ten8t.ten8t_exception import Ten8tException


def test_init_with_valid_parameters():
    """Test initialization with valid parameters."""
    # Test with positive n
    schedule = Ten8tNthWeekdaySchedule(3, 2)  # 3rd Wednesday
    assert schedule.n == 3
    assert schedule.weekday == 2
    assert schedule.name == "3rd_wednesday_of_month"

    # Test with negative n
    schedule = Ten8tNthWeekdaySchedule(-1, 4, name='last_friday_of_month')  # Last Friday
    assert schedule.n == -1
    assert schedule.weekday == 4
    assert schedule.name == "last_friday_of_month"

    # Test with custom name
    schedule = Ten8tNthWeekdaySchedule(2, 0, name="custom_name")  # 2nd Monday
    assert schedule.name == "custom_name"


def test_init_with_invalid_parameters():
    """Test initialization with invalid parameters."""
    # Test with n = 0
    with pytest.raises(Ten8tException):
        Ten8tNthWeekdaySchedule(0, 0)

    # Test with invalid weekday values
    with pytest.raises(Ten8tException):
        Ten8tNthWeekdaySchedule(1, -1)  # Too low

    with pytest.raises(Ten8tException):
        Ten8tNthWeekdaySchedule(1, 7)  # Too high


@pytest.mark.parametrize(
    "test_name,n,weekday,year,month,expected_day",
    [
        # Positive indexes - First of each weekday
        ("FirstMonday", 1, 0, 2023, 5, 1),  # May 1, 2023
        ("FirstTuesday", 1, 1, 2023, 5, 2),  # May 2, 2023
        ("FirstWednesday", 1, 2, 2023, 5, 3),  # May 3, 2023
        ("FirstThursday", 1, 3, 2023, 5, 4),  # May 4, 2023
        ("FirstFriday", 1, 4, 2023, 5, 5),  # May 5, 2023
        ("FirstSaturday", 1, 5, 2023, 5, 6),  # May 6, 2023
        ("FirstSunday", 1, 6, 2023, 5, 7),  # May 7, 2023

        # Positive indexes - Second of each weekday
        ("SecondMonday", 2, 0, 2023, 5, 8),  # May 8, 2023
        ("SecondTuesday", 2, 1, 2023, 5, 9),  # May 9, 2023

        # Positive indexes - Third, Fourth, Fifth
        ("ThirdWednesday", 3, 2, 2023, 5, 17),  # May 17, 2023
        ("FourthThursday", 4, 3, 2023, 5, 25),  # May 25, 2023
        ("FifthMonday", 5, 0, 2023, 1, 30),  # Jan 30, 2023 (January has 5 Mondays)

        # Negative indexes - Last of each weekday
        ("LastMonday", -1, 0, 2023, 5, 29),  # May 29, 2023
        ("LastTuesday", -1, 1, 2023, 5, 30),  # May 30, 2023
        ("LastWednesday", -1, 2, 2023, 5, 31),  # May 31, 2023
        ("LastThursday", -1, 3, 2023, 5, 25),  # May 25, 2023
        ("LastFriday", -1, 4, 2023, 5, 26),  # May 26, 2023
        ("LastSaturday", -1, 5, 2023, 5, 27),  # May 27, 2023
        ("LastSunday", -1, 6, 2023, 5, 28),  # May 28, 2023

        # Negative indexes - Second-to-last, Third-to-last, Fourth-to-last
        ("SecondToLastMonday", -2, 0, 2023, 5, 22),  # May 22, 2023
        ("ThirdToLastTuesday", -3, 1, 2023, 5, 16),  # May 16, 2023

        # Edge cases
        # Leap year vs non-leap year (February)
        ("LastWednesdayFeb2023", -1, 2, 2023, 2, 22),  # Feb 22, 2023 (non-leap)
        ("LastWednesdayFeb2024", -1, 2, 2024, 2, 28),  # Feb 28, 2024 (leap)

        # Month with exactly 4 occurrences of a weekday
        ("FourthMondayFeb2023", 4, 0, 2023, 2, 27),  # Feb 27, 2023 (4 Mondays)

        # Special cases - 5th occurrence from start
        ("FifthSundayJuly2023", 5, 6, 2023, 7, 30),  # July 30, 2023

        # Special cases - 5th occurrence from end (when month has 5 occurrences)
        ("FifthToLastMondayJan2023", -5, 0, 2023, 1, 2),  # Jan 2, 2023 (January has 5 Mondays)

        # Month transition cases
        ("LastFridayDec2023", -1, 4, 2023, 12, 29),  # Dec 29, 2023
        ("FirstFridayJan2024", 1, 4, 2024, 1, 5),  # Jan 5, 2024

        ("LastMondayMay2025", -1, 0, 2025, 5, 26),  # May 26 20204
    ]
)
def test_nth_weekday_schedule(test_name, n, weekday, year, month, expected_day):
    """
    Parameterized test for Ten8tNthWeekdaySchedule.

    For each test case:
    1. Tests that the expected date passes
    2. Tests that a day before the expected date fails
    3. Tests that a day after the expected date fails
    """
    schedule = Ten8tNthWeekdaySchedule(n, weekday)

    # Create datetime objects for expected date, day before, and day after
    expected_date = dt.datetime(year, month, expected_day)
    day_before = expected_date - dt.timedelta(days=1)
    day_after = expected_date + dt.timedelta(days=1)

    # Assert that the expected date is in schedule
    assert schedule.is_due(expected_date), f"Failed: {test_name} should be in schedule on {expected_date}"

    # Assert that day before and after are not in schedule
    assert not schedule.is_due(
        day_before), f"Failed: {test_name} should not be in schedule on {day_before}"
    assert not schedule.is_due(day_after), f"Failed: {test_name} should not be in schedule on {day_after}"

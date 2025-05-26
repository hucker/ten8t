import datetime as dt

from ten8t.schedule import Ten8tNonHolidaySchedule


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

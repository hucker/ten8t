import datetime as dt

import pytest

from ten8t import Ten8tException, Ten8tTTLSchedule


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
    result = schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))
    assert result is True
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 0)


def test_execution_blocks_within_ttl():
    """Test that executions block if within TTL threshold."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 15))
    assert result is False  # Should block since only 15s have passed
    # Last execution time should remain unchanged
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 0)


def test_execution_allows_after_ttl():
    """Test that executions allow after TTL threshold."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 31))
    assert result is True  # Should allow since 31s have passed
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 31)


def test_execution_at_exact_ttl_boundary():
    """Test behavior exactly at the TTL boundary."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=30)
    schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 0))  # Initial execution
    result = schedule.mark_executed(execution_time=dt.datetime(2023, 1, 1, 12, 0, 30))
    assert result is True  # Should allow at exactly 30s
    assert schedule.last_execution_time == dt.datetime(2023, 1, 1, 12, 0, 30)


def test_ttl_default_execution_time():
    """Test that run_now uses current time when no execution_time is provided."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=0)  # Zero TTL for testing
    result = schedule.mark_executed()  # No execution_time provided
    assert result is True
    assert schedule.last_execution_time is not None  # Should have set a timestamp


def test_ttl_repr():
    """Test the string representation (repr) for debugging."""
    schedule = Ten8tTTLSchedule(name="test_schedule", ttl_sec=60)
    execution_time = dt.datetime(2023, 1, 1, 12, 0, 0)
    schedule.mark_executed(execution_time=execution_time)

    expected_repr = (
        f"Ten8tTTLSchedule(name='test_schedule', "
        f"last_execution_time={execution_time}, "
        f"ttl_sec=60)"
    )
    assert repr(schedule) == expected_repr

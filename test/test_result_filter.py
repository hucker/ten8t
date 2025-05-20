import pytest

import ten8t as t8


# Define the results data as a pytest fixture
@pytest.fixture
def results():
    """
    These are the possible result fields that we can filter on, so these 3
    results simulate result dictionaries.
    Returns:

    """
    return {
        "results": [
            {"ruid": "r1", "tag": "tag1", "phase": "phase1", 'func_name': 'func1', 'summary_result': True},
            {"ruid": "r2", "tag": "tag2", "phase": "phase2", 'func_name': 'func2', 'summary_result': False},
            {"ruid": "r3", "tag": "tag3", "phase": "phase3", 'func_name': 'func3', 'summary_result': False},
        ]
    }


def test_filter_by_func_name(results):
    """Test filtering by func_name patterns only."""
    filter_instance = t8.Ten8tResultDictFilter(func_name_patterns="func1 func3")
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r1", "tag": "tag1", "phase": "phase1", "func_name": "func1", "summary_result": True},
        {"ruid": "r3", "tag": "tag3", "phase": "phase3", "func_name": "func3", "summary_result": False}
    ], "Filter should return results with func_name 'func1' and 'func3'."


def test_filter_by_summary_result(results):
    """Test filtering by summary_result field only."""
    filter_instance = t8.Ten8tResultDictFilter(summary_results=True)
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r1", "tag": "tag1", "phase": "phase1", "func_name": "func1", "summary_result": True}
    ], "Filter should return results where summary_result is True."


def test_filter_by_func_name_and_summary_result(results):
    """Test filtering by both func_name and summary_result fields."""
    filter_instance = t8.Ten8tResultDictFilter(func_name_patterns="func1 func2", summary_results=False)
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r2", "tag": "tag2", "phase": "phase2", "func_name": "func2", "summary_result": False}
    ], "Filter should return results matching func_name 'func2' and summary_result False."


def test_filter_with_all_patterns(results):
    """Test filtering with all field patterns (ruid, tag, phase, func_name, summary_result)."""
    filter_instance = t8.Ten8tResultDictFilter(
        ruid_patterns="r3",
        tag_patterns="tag3",
        phase_patterns="phase3",
        func_name_patterns="func3",
        summary_results=False
    )
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r3", "tag": "tag3", "phase": "phase3", "func_name": "func3", "summary_result": False}
    ], "Filter should return results matching all specified fields."


def test_filter_with_no_func_name_pattern(results):
    """Test filtering without specifying func_name patterns (all func_name values pass)."""
    filter_instance = t8.Ten8tResultDictFilter(ruid_patterns="r1", phase_patterns="phase1",
                                               summary_results=True)
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r1", "tag": "tag1", "phase": "phase1", "func_name": "func1", "summary_result": True}
    ], "Filter should allow all func_name values to pass if no func_name patterns are specified."


def test_filter_with_no_summary_result_filter(results):
    """Test filtering without specifying summary_result filter (all summary_result values pass)."""
    filter_instance = t8.Ten8tResultDictFilter(ruid_patterns="r2", func_name_patterns="func2")
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r2", "tag": "tag2", "phase": "phase2", "func_name": "func2", "summary_result": False}
    ], "Filter should allow all summary_result values to pass if no summary_result filter is specified."


def test_filter_with_no_patterns_including_new_fields(results):
    """Test filtering with no patterns for any field, including new fields (all results pass)."""
    filter_instance = t8.Ten8tResultDictFilter()
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == results[
        "results"], "Filter should return all results if no patterns are specified."


def test_filter_with_regex_including_new_fields(results):
    """Test filtering with regex patterns for new fields."""
    filter_instance = t8.Ten8tResultDictFilter(
        ruid_patterns="r[1-3]",
        tag_patterns="tag[1-3]",
        func_name_patterns="func[1-2]"
    )
    filtered_results = filter_instance.filter(results.copy())
    assert filtered_results["results"] == [
        {"ruid": "r1", "tag": "tag1", "phase": "phase1", "func_name": "func1", "summary_result": True},
        {"ruid": "r2", "tag": "tag2", "phase": "phase2", "func_name": "func2", "summary_result": False}
    ], "Filter should match regex patterns on ruid, tag, and func_name."


def test_filter_with_no_parameters(results):
    """Test that a filter with no parameters lets everything through."""
    # Create a filter with no parameters
    filter_instance = t8.Ten8tResultDictFilter()

    # Apply the filter to the results
    filtered_results = filter_instance.filter(results.copy())

    # Assert that all results are returned unchanged
    assert filtered_results["results"] == results[
        "results"], "Filter with no parameters should return all results unaltered."


@pytest.mark.parametrize(
    "filter_args",  # Parameterized sets of filter arguments
    [
        {},  # No values at all (default behavior)
        {"func_name_patterns": None},  # None for filter
        {"func_name_patterns": ""},  # Empty string for filter
        {"ruid_patterns": None},  # None in another field
        {"ruid_patterns": ""},  # Empty string in another field
        {"tag_patterns": None},  # Another field with None
        {"tag_patterns": ""},  # Another field with empty string
        {"phase_patterns": None},  # Another field with None
        {"phase_patterns": ""},  # Another field with empty string
    ],
)
def test_filter_treats_empty_and_none_as_unfiltered(results, filter_args):
    """Test that None or empty string values behave the same as no filter."""
    # Create a filter instance with the parameterized arguments
    filter_instance = t8.Ten8tResultDictFilter(**filter_args)

    # Apply the filter to the results
    filtered_results = filter_instance.filter(results.copy())

    # Assert that all original results pass through
    assert filtered_results["results"] == results["results"], (
        f"Filter with arguments {filter_args} should return all results unaltered."
    )


@pytest.mark.parametrize("tag_pattern", ["tag1", "tag2", "tag3"])
def test_rule_ten8t_json_file_tags(tag_pattern):
    """
    Parameterized test to verify that all results returned match the specified tag.
    """

    def check_func():
        filter_instance = t8.Ten8tResultDictFilter(tag_patterns=tag_pattern)
        yield from t8.rule_ten8t_json_file(
            file_name="rule_ten8t_results/result1.json",
            filter=filter_instance,
            pass_if_missing=False,
        )

    checker = t8.Ten8tChecker(check_functions=[check_func])
    checker.run_all()

    result_dict = checker.as_dict()
    results = result_dict["results"]

    # Validate that every result matches the tag pattern
    for result in results:
        assert result['tag'] == tag_pattern


@pytest.mark.parametrize("ruid_pattern", ["m1_f1", "m1_f2", "m1_f3", "m2_f1", "m2_f2", "m2_f3", "m2_f4"])
def test_rule_ten8t_json_file_ruids(ruid_pattern):
    """
    Parameterized test to verify that all results returned match the specified RUID.
    """

    def check_func():
        filter_instance = t8.Ten8tResultDictFilter(ruid_patterns=ruid_pattern)
        yield from t8.rule_ten8t_json_file(
            file_name="rule_ten8t_results/result1.json",
            filter=filter_instance,
            pass_if_missing=False,
        )

    checker = t8.Ten8tChecker(check_functions=[check_func])
    checker.run_all()

    result_dict = checker.as_dict()
    results = result_dict["results"]

    # Validate that every result matches the RUID pattern
    for result in results:
        assert result['ruid'] == ruid_pattern


@pytest.mark.parametrize("phase_pattern", ["production", "proto"])
def test_rule_ten8t_json_file_phases(phase_pattern):
    """
    Parameterized test to verify that all results returned match the specified phase.
    """

    def check_func():
        filter_instance = t8.Ten8tResultDictFilter(phase_patterns=phase_pattern)
        yield from t8.rule_ten8t_json_file(
            file_name="rule_ten8t_results/result1.json",
            filter=filter_instance,
            pass_if_missing=False,
        )

    checker = t8.Ten8tChecker(check_functions=[check_func])
    checker.run_all()

    result_dict = checker.as_dict()
    results = result_dict["results"]

    # Validate that every result matches the phase pattern
    for result in results:
        assert result['phase'] == phase_pattern

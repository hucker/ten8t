import pytest

from ten8t.overview import Ten8tMarkdownOverview, Ten8tStreamlitOverview, Ten8tTextOverview
from ten8t.ten8t_attribute import attributes
from ten8t.ten8t_checker import Ten8tChecker
from ten8t.ten8t_result import TR


def test_text_overview(tmp_path):
    """
    Tests the `generate` and `get_text` methods of the `Ten8tTextOverview` class
    to ensure that the expected content is correctly written to a text file.

    This test verifies that the text overview of checks, including metadata, is
    accurately generated and contains all the required fields such as tag, phase,
    level, RUID, description, and more. The temporary file is used to simulate a
    real-world use case without affecting the permanent filesystem.

    Args:
        tmp_path: A pathlib.Path object provided by pytest, representing a temporary
            directory that is unique for each test function.

    Attributes:
        tag: The tag category associated with the check (`check_overview`), providing
            a label for organizational purposes.
        phase: The operational phase where the check is relevant.
        level: The severity or descriptive level of the check.
        ruid: A unique identifier for the check, aiding in tracking and reference.
    """

    @attributes(tag="tag", phase="phase", level=1, ruid='r1')
    def check_overview():
        """
        This is a simple over test.

        This test does many useful things.
        """
        return TR(status=True, msg="Result check_overview")

    checker = Ten8tChecker(check_functions=[check_overview])

    # Use tmp_path to generate a temporary file
    temp_file = tmp_path / "temp_file.txt"

    ov = Ten8tTextOverview(checker)
    ov_contents = ov.generate(file_name=temp_file)
    contents = ov.get_text()

    # These asserts verify that the correct items end up in the text file
    assert ov_contents == contents
    assert "No environment data provided" in contents
    assert "Check Functions for" in contents
    assert "Checker Overview Generated on" in contents
    assert "Tag: tag" in contents
    assert "Phase: phase" in contents
    assert "Level: 1" in contents
    assert "RUID: r1" in contents
    assert "Attempts: 1" in contents
    assert "Description:" in contents
    assert "This is a simple over test." in contents
    assert "This test does many useful things." in contents
    assert "check_overview" in contents


def test_text_overview_with_env(tmp_path):
    """
    Tests the text generation of an overview with an active environment.

    This test ensures that the `Ten8tTextOverview` class correctly generates
    a text overview file that accurately reflects the current environment,
    check function configurations, and their execution results. It uses
    assertions to validate the content of the generated text file.

    Args:
        tmp_path (Path): A temporary file path fixture provided by the
            testing framework.

    """

    @attributes(tag="tag", phase="phase", level=1, ruid='r1')
    def check_overview_env(foo, fum):
        """
        This is a simple overview test.

        This test does many useful things.
        """
        return TR(status=foo > fum, msg="Result check_overview")

    env = {"foo": 2, "fum": 1}
    checker = Ten8tChecker(check_functions=[check_overview_env], env=env)

    # Use tmp_path to generate a temporary file
    temp_file = tmp_path / "temp_file.txt"

    ov = Ten8tTextOverview(checker)
    gen_contents = ov.generate(file_name=temp_file)
    contents = ov.get_text()
    # Verify that the generate method does return the text.
    assert contents == gen_contents

    # These asserts verify that the correct items end up in the text file
    assert "Check Functions for" in contents
    assert "Checker Overview Generated on" in contents
    assert "check_overview_env" in contents
    assert "Tag: tag" in contents
    assert "Phase: phase" in contents
    assert "Level: 1" in contents
    assert "RUID: r1" in contents
    assert "Attempts: 1" in contents
    assert "Description:\n" in contents
    assert "Environment:\n" in contents
    assert "foo: 2" in contents
    assert "fum: 1" in contents
    assert "foo fum" in contents
    assert "This is a simple overview test." in contents
    assert "This test does many useful things." in contents


@pytest.mark.parametrize("OverviewClass", [Ten8tMarkdownOverview, Ten8tStreamlitOverview])
def test_md_overview(tmp_path, OverviewClass):
    """
    Parameterized test for `generate` and `get_text` methods of `Ten8tMarkdownOverview`
    and `Ten8tStreamlitOverview` classes to ensure consistency in output.

    This test verifies that both classes can correctly generate and fetch text output
    related to the checks, and that the output contains all required metadata.

    Args:
        tmp_path: A pathlib.Path object representing a temporary directory unique to the test.
        OverviewClass: The class being tested, either `Ten8tMarkdownOverview` or
                       `Ten8tStreamlitOverview` (passed using pytest parameterization).

    Attributes:
        tag: The tag category associated with the check (`check_overview`), providing
            a label for organizational purposes.
        phase: The operational phase where the check is relevant.
        level: The severity or descriptive level of the check.
        ruid: A unique identifier for the check, aiding in tracking and reference.
    """

    @attributes(tag="tag", phase="phase", level=1, ruid='r1')
    def check_overview():
        """
        This is a simple overview test.

        This test does many useful things.
        """
        return TR(status=True, msg="Result check_overview")

    checker = Ten8tChecker(check_functions=[check_overview])

    # Use tmp_path to generate a temporary file
    temp_file = tmp_path / "temp_file.txt"

    # Instantiate the class dynamically using the parameterized class
    ov = OverviewClass(checker)
    gen_contents = ov.generate(file_name=temp_file)
    contents = ov.get_text()

    # Verify that the generate method does return the text.
    assert contents == gen_contents

    # Redundant repeated duplicate test.
    for txt in [contents, gen_contents]:
        # These asserts verify that the correct items end up in the text file
        assert "### Check Functions for checker" in txt
        assert "Checker Overview Generated on" in txt
        assert "| RUID | r1 |" in txt
        assert "| Phase | phase |" in txt
        assert "| Level | 1 |" in txt
        assert "| RUID | r1 |" in txt
        assert "| Attempts | 1 |" in txt

import xml.etree.ElementTree as ET


def parse_test_results(file_path: str):
    """
    Parses the test results XML file and returns the number of failures and total tests.
    :param file_path: Path to the `results.xml` file
    :return: A tuple (failures, total_tests)
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find the first <testsuite> element
        testsuite = root.find('testsuite')
        if testsuite is not None:
            failures = int(testsuite.attrib.get('failures', 0))
            total_tests = int(testsuite.attrib.get('tests', 0))
            return failures, total_tests
        else:
            raise ValueError("No <testsuite> element found in the XML file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML file: {e}")


def extract_line_rate(xml_file: str) -> float:
    """
    Extracts the line coverage rate from the coverage XML file.
    :param xml_file: Path to the coverage XML file
    :return: Line coverage rate as a float (e.g., 0.85 for 85% coverage)
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        line_rate = float(root.attrib.get('line-rate', 0))
        return line_rate
    except FileNotFoundError:
        raise FileNotFoundError(f"Coverage XML file not found: {xml_file}")
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML file: {e}")


def make_shieldio_badge(label: str, value: str, color: str) -> str:
    """
    Generates a Shield.io badge URL.
    :param label: Label for the badge (e.g., "Pytest" or "Coverage")
    :param value: Value to display on the badge (e.g., "865/865" or "85%")
    :param color: Color of the badge (e.g., "brightgreen", "red", "yellow")
    :return: A Markdown string for the Shield.io badge
    """
    value = value.replace('%', '%25')
    badge_url = f"https://img.shields.io/badge/{label}-{value}-{color}.svg"
    return f"![Ten8t {label} Status]({badge_url})"


def determine_badge_color(value: float, thresholds: dict) -> str:
    """
    Determines the badge color based on the value and defined thresholds.
    :param value: Numeric value to evaluate (e.g., failure percentage, coverage rate)
    :param thresholds: Dictionary with 'green', 'yellow', and 'red' keys and their respective thresholds
    :return: Color for the badge ("brightgreen", "yellow", "red")
    """
    if value >= thresholds['green']:
        return "brightgreen"
    elif value >= thresholds['yellow']:
        return "yellow"
    elif value >= thresholds['orange']:
        return "orange"
    else:
        return "red"


def update_readme_with_badge(readme_file: str, badge_label: str, badge_markdown: str):
    """
    Updates the README.md file with the specified badge, replacing the relevant line.
    :param readme_file: Path to the README.md file.
    :param badge_label: The label to look for in the README line (e.g., "[Ten8t PyTest Status]")
    :param badge_markdown: The new Markdown badge to replace in the README file.
    """
    try:
        with open(readme_file, 'r') as file:
            lines = file.readlines()

        # Replace matching line with the new badge
        with open(readme_file, 'w') as file:
            for line in lines:
                if badge_label in line:
                    file.write(badge_markdown + '\n')
                else:
                    file.write(line)

        print(f"README.md updated successfully with the badge for {badge_label}.")
    except FileNotFoundError:
        raise FileNotFoundError(f"README file not found: {readme_file}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while updating the README: {e}")


def update_test_badge(readme_file: str, results_file: str):
    """
    Parses test results and updates the README.md file with the test status badge.
    :param readme_file: Path to the README.md file
    :param results_file: Path to the test results XML file
    """
    failures, total_tests = parse_test_results(results_file)
    passes = total_tests - failures
    color = "brightgreen" if failures == 0 else "red"
    badge_markdown = make_shieldio_badge("PyTest", f"{passes}/{total_tests}", color)
    update_readme_with_badge(readme_file, "[Ten8t PyTest Status]", badge_markdown)


def update_coverage_badge(readme_file: str, coverage_file: str):
    """
    Parses coverage results and updates the README.md file with the coverage badge.
    :param readme_file: Path to the README.md file
    :param coverage_file: Path to the coverage XML file
    """
    line_rate = extract_line_rate(coverage_file)
    percentage = int(line_rate * 100)
    thresholds = {"green": 90, "yellow": 80, "orange": 70, "red": 0}
    color = determine_badge_color(percentage, thresholds)
    badge_markdown = make_shieldio_badge("Coverage", f"{percentage}%", color)
    update_readme_with_badge(readme_file, "[Ten8t Coverage Status]", badge_markdown)


# Example usage:
update_test_badge('../README.md', '../test/test/results.xml')
update_coverage_badge('../README.md', '/Users/chuck/Library/Caches/JetBrains/PyCharm2024.3/coverage/ten8t$.xml')

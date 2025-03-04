"""
Read the coverage XML file and update the readme as needed.
"""

# Path to the XML file
xml_file = "/Users/chuck/Library/Caches/JetBrains/PyCharm2024.3/coverage/ten8t$.xml"
# Path to your README.md file
readme_file = "../README.md"

# The base URL for the image service
# Use a service like shields.io to create a dynamic badge
image_base_url = "https://img.shields.io/badge/coverage-{}%25-brightgreen"


def extract_line_rate(xml_path):
    """Extract the line-rate (coverage percentage) from the coverage XML file.

    The function searches the specified XML file for the <package> tag and retrieves
    the `line-rate` attribute value. This attribute indicates the test coverage as
    a fraction, e.g., `0.8743`.

    Args:
        xml_path (str): Path to the coverage XML file.

    Returns:
        float: The coverage percentage (0.0–100.0). Returns 0.0 if the file cannot
               be read or no valid `line-rate` is found.
    """
    try:
        with open(xml_path, "r") as file:
            for line in file.readlines():
                if line.strip().startswith('<package name=".Users.chuck.Projects.ten8t.src.ten8t" line-rate='):
                    params = line.split('line-rate="')
                    return 100.0 * float(params[1].split('"')[0])
    except Exception as e:
        print(f"Error reading coverage XML file: {e}")

    return 0.0  # Return 0% if the file cannot be read or the line is not found


def badge_color(coverage):
    """Determine the color of the badge based on the coverage percentage.

    Uses a list of ranges to map coverage values to colors.

    Args:
        coverage (float): The coverage percentage (0–100).

    Returns:
        str: The corresponding color for the badge.
    """
    # Define coverage ranges and their associated colors
    ranges_to_colors = [
        (100, "brightgreen"),  # 90–100%
        (90, "green"),  # 90–99.999%
        (80, "yellow"),  # 80–89%
        (70, "orange"),  # 70–79%
    ]

    # Find the first range that the coverage matches
    for threshold, color in ranges_to_colors:
        if coverage >= threshold:
            return color
    return 'red'


def create_shields_io_link(coverage):
    """Generate a Markdown link using Shields.io for the test coverage badge.

    Args:
        coverage (float): The coverage percentage.

    Returns:
        str: A valid Markdown link for the Shields.io coverage badge.
    """
    color = badge_color(coverage)
    badge_url = image_base_url.format(int(coverage))
    return f"![Ten8t Package Test Coverage]({badge_url})"


def update_readme_with_badge(readme_path, coverage):
    """Update the README file to replace the coverage badge link.

    The function looks for an existing line starting with
    `[![Ten8t Package Test Coverage]` in the README file and replaces it
    with a dynamically generated badge Markdown link that reflects the
    provided test coverage. If no such line is found, no changes are made.

    Args:
        readme_path (str): Path to the README.md file.
        coverage (float): The test coverage percentage to reflect in the badge.

    Returns:
        None
    """
    try:
        # Generate Markdown for the badge using the extracted coverage
        badge_markdown = create_shields_io_link(coverage) + "\n"

        # Read the existing README.md content
        with open(readme_path, "r") as file:
            lines = file.readlines()

        # Search for the line to replace
        updated_lines = []
        replaced = False
        for line in lines:
            if line.strip().startswith("![Ten8t Package Test Coverage]"):
                updated_lines.append(badge_markdown)
                replaced = True
            else:
                updated_lines.append(line)

        # Only write changes if the line was replaced
        if replaced:
            with open(readme_path, "w") as file:
                file.writelines(updated_lines)
            print("Coverage badge updated successfully in README.md")
        else:
            print("Coverage badge line not found. No changes made.")

    except Exception as e:
        print(f"Error updating README.md file: {e}")


if __name__ == "__main__":
    # Step 1: Extract line-rate from the XML file
    coverage = extract_line_rate(xml_file)

    if coverage is not None:
        print(f"Extracted Coverage: {int(coverage)}%")
        # Step 2: Replace or update the badge line in the README.md
        update_readme_with_badge(readme_file, coverage)

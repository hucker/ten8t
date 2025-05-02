import sys
from pathlib import Path

import ten8t as t8
from ten8t import Ten8tResult


def main():
    """
    Ten8t Checker Command-Line Interface.

    This script provides a basic command-line interface to validate and run Ten8t checks on a Python file or a folder.

    It performs the following:
    - Validates the provided file path or folder path to ensure it exists.
    - If the path is a Python file:
        Runs Ten8t checks on the specified file (module).
    - If the path is a folder:
        Runs Ten8t checks on all valid modules within the folder (package).
    - Displays the results of each check including pass/fail status, messages, and a final score.

    Usage:
        python script_name.py <path_to_python_file_or_folder>

    Arguments:
        <path_to_python_file_or_folder>  Path to a Python file or folder containing Ten8t check definitions.

    Example:
        python script_name.py check_example.py
        python script_name.py /path/to/package

    Output:
        - Displays error messages if the file/folder doesn't exist or is invalid.
        - Provides detailed results for each Ten8t check, including status and messages.
        - Displays the final Ten8t score percentage.

    Dependencies:
        - The `ten8t` module must be installed in your environment.
        - Ensure the specified Python file or folder contains valid Ten8t check definitions.

    Exit Codes:
        - 1: Invalid file or folder path provided.
        - 0: Script executed successfully.
    """

    if len(sys.argv) < 2:
        print("Error: Please enter the path to a Python file or folder containing Ten8t check definitions.")
        sys.exit(1)

    # Get the first command-line argument
    target_path = sys.argv[1]

    # Use pathlib to handle the file path
    path = Path(target_path)

    # Check if the path exists
    if not path.exists():
        print(f"Error: The path '{target_path}' does not exist.")
        sys.exit(1)

    # Check if the path is a Python file
    if path.is_file():
        if path.suffix != '.py':
            print(f"Error: The file '{target_path}' is not a Python (.py) file.")
            sys.exit(1)

        print(f"Running Ten8t checks on the Python file: {path}")
        # Run Ten8t module checker
        ch = t8.Ten8tChecker(modules=path)
        ch.run_all()
        print_results(ch)

    # Check if the path is a folder
    elif path.is_dir():
        print(f"Running Ten8t checks on the package (folder): {path}")
        # Run Ten8t package checker
        ch = t8.Ten8tChecker(packages=[path])
        ch.run_all()
        print_results(ch)

    else:
        # If the path is neither a file nor a folder
        print(f"Error: The provided path '{target_path}' is neither a file nor a folder.")
        sys.exit(1)

    sys.exit(0)


def print_results(checker):
    """
    Helper function to print Ten8t checks results.

    Args:
        checker (Ten8tChecker): An instance of `Ten8tChecker` containing the results to print.
    """
    # Iterate over results and print the status and message
    for r in checker.results:
        result: Ten8tResult = r
        print(f"Status:{result.status} Tag:{result.tag} Msg:{result.msg_text}")

    # Print final score
    print(f"Score = {checker.score:0.1f}%")


if __name__ == "__main__":
    main()

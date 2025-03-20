"""
Sample app for running ten8t with rich.
Demonstrates checks with progress bars and a styled results table.
"""

import logging
import time

from rich import print as rprint
from rich.box import HEAVY
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

import ten8t as t8

# Styles / Constants for display
PASS = "[green]PASS[/green]"
FAIL = "[red]FAIL[/red]"

DEMO_DELAY = 0.5

console = Console(force_terminal=True, color_system="256")


# Define your checks with attributes
@t8.attributes(tag='tag1', ruid='ruid1')
def check1():
    """Demo check function 1"""
    time.sleep(DEMO_DELAY)
    yield t8.TR(status=True, msg="Test 1 passed")


@t8.attributes(tag='tag2', ruid='ruid2')
def check2():
    """Demo check function 2"""
    time.sleep(DEMO_DELAY)
    yield t8.TR(status=False, msg="Test 2 failed")


@t8.attributes(tag='tag3', ruid='ruid3')
def check3():
    """Demo check function 3"""
    time.sleep(DEMO_DELAY)
    yield t8.TR(status=True, msg="Test 3 passed")
    yield t8.TR(status=True, msg="Test 4 passed")


@t8.attributes(tag='tag3', ruid='ruid4')
def check4():
    """Demo check function 4"""
    time.sleep(DEMO_DELAY)
    yield t8.TR(status=True, msg="Test 5 passed")
    yield t8.TR(status=True, msg="Test 6 passed")


# Custom CLI Progress class using Rich
class Ten8tRichProgressBar(t8.Ten8tProgress):
    """
    Progress bar to integrate with rich's progress bar.

    The rich progress bar is quite sophisticated and supports multiple progress bars
    and allows.  It needs to know a size ahead of time so it can manage 1 of N progress
    bar.  It also allows short messages to be displayed on the projgress bar.
    """

    def __init__(self):
        # Create a rich_ten8t friendly progress bar.
        self.rich_progress: Progress = Progress(
            TextColumn("[bold blue]{task.description}"),  # Task description
            BarColumn(),  # Progress bar
            TextColumn("[bold green]{task.completed}/{task.total}"),  # Counter
            console=console,
        )
        self.task_id = None

    def initialize_task(self, total: int):
        """
            Set up a progress task in the Rich progress bar.

            Args:
                total (int): Total number of items to complete the task.
            """
        self.task_id = self.rich_progress.add_task("Running Checks", total=total)

    def message(self, msg: str):
        """ Display a generic message, these are unrelated to results """
        if self.task_id is not None:
            self.rich_progress.update(self.task_id,
                                      description=msg)  # Only update description dynamically

    def result_msg(self,
                   current_iteration: int,
                   max_iteration: int,
                   msg: str = "",
                   result: t8.Ten8tResult | None = None
                   ) -> None:
        """Display a result message."""
        if self.task_id is not None:
            self.rich_progress.update(self.task_id,
                                      total=max_iteration,
                                      completed=current_iteration,
                                      description=msg or result.msg)


def display_results_table(results: list[t8.Ten8tResult]) -> None:
    """
    Format and render the results as a styled Rich table.

    Args:
        results (list[Ten8tResult]): Results to display in the table.
    """

    table = Table(
        title="Test Results",
        show_header=True,
        header_style="magenta",
        box=HEAVY,  # Use heavy borders for styling
    )
    table.add_column("Tag", style="cyan", justify="center")
    table.add_column("RUID", style="green", justify="center")
    table.add_column("Function Name", style="blue", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Message", style="yellow")

    for result in results:
        table.add_row(
            result.tag,
            str(result.ruid),
            result.func_name,
            PASS if result.status else FAIL,  # Use consistent PASS/FAIL styling
            result.msg,
        )
    console.print(table)


def show_raw_data(checker: t8.Ten8tChecker) -> None:
    """
    Prompt the user to display raw data and handle the output.

    Args:
        checker (Ten8tChecker): The Ten8tChecker instance containing results.
    """
    console.print("[bold red]Press Enter For Raw Data[/bold red]")
    rprint(checker.as_dict())


def main():
    """Main application logic to run checks and display results."""

    # Set up progress bars for CLI and logging
    cli_progress = Ten8tRichProgressBar()
    log_progress = t8.Ten8tLogProgress(result_level=logging.INFO, msg_level=logging.INFO)

    # Build the checker with checks and progress hooks
    checker = t8.Ten8tChecker(
        check_functions=[check1, check2, check3, check4],
        progress_object=[cli_progress, log_progress],
    )

    # Initialize CLI progress bar with the total number of functions
    cli_progress.initialize_task(total=checker.function_count)

    # Run checks and collect results
    with cli_progress.rich_progress:
        results = checker.run_all()

    # Display results in a table if any exist
    if results:
        display_results_table(results)
        show_raw_data(checker)


if __name__ == "__main__":
    try:
        t8.ten8t_setup_logging(logging.DEBUG, file_name="rich_demo.log")
    except PermissionError as e:
        console.print(f"[red]Error setting up logging: {e}. Ensure you have write access to the directory.[/red]")


    main()

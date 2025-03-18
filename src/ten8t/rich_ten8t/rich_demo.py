"""
Sample app for running ten8t with rich
"""

import logging
import time

from rich import print as rprint
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

import ten8t as t8

console = Console(force_terminal=True, color_system="256")


# Define your checks with attributes
@t8.attributes(tag='tag1', ruid='ruid1')
def check1():
    """Demo check function 1"""
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 1 passed")


@t8.attributes(tag='tag2', ruid='ruid2')
def check2():
    """Demo check function 2"""
    time.sleep(.5)
    yield t8.TR(status=False, msg="Test 2 failed")


@t8.attributes(tag='tag3', ruid='ruid3')
def check3():
    """Demo check function 3"""
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 3 passed")
    yield t8.TR(status=True, msg="Test 4 passed")


@t8.attributes(tag='tag3', ruid='ruid4')
def check4():
    """Demo check function 4"""
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 5 passed")
    yield t8.TR(status=True, msg="Test 6 passed")


# Custom CLI Progress class using Rich
class Ten8tRichProgressBar(t8.Ten8tProgress):
    """Progress bar to integrate with rich's progress bar."""
    def __init__(self):
        # Create a rich_ten8t friendly progress bar.
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),  # Task description
            BarColumn(),  # Progress bar
            TextColumn("[bold green]{task.completed}/{task.total}"),  # Counter
            console=console,
        )
        self.task_id = None

    def __call__(self, current_iteration, max_iteration, msg: str = "", result: t8.Ten8tResult = None):
        if self.task_id is None:
            self.task_id = self.progress.add_task("Running Checks", total=max_iteration)

        # Update progress with current iteration
        self.progress.update(self.task_id, completed=current_iteration)

    def start_progress(self):
        """Required for rich integration """
        self.progress.start()

    def stop_progress(self):
        """Required for rich integration """
        self.progress.stop()


def main():
    # Set up and run checks as usual

    # This gives a very simple example of using an RC 'file'.  In this case
    # it is filtering for ruids and the regex lets everything through, you could
    # make this more complex or use a config file.
    rc = t8.ten8t_rc_factory({'ruids': 'ruid.*'})  # Configure with regex pattern

    # An example or running multiple loggers
    cli_progress = Ten8tRichProgressBar()
    log_progress = t8.Ten8tLogProgress(result_level=logging.INFO, msg_level=logging.INFO)

    cli_progress.start_progress()

    ch = t8.Ten8tChecker(
        check_functions=[check1, check2, check3, check4],
        rc=rc,
        progress_object=[cli_progress, log_progress],  # some magic here, two progress objects
        auto_ruid=True,
    )
    results = ch.run_all()
    cli_progress.stop_progress()

    # Format the final results using a Rich Table
    if results:
        table = Table(title="Test Results", show_header=True, header_style="bold magenta")
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
                ":white_check_mark:" if result.status else ":x:",
                result.msg
            )
        console.print(table)
        console.print(f"Score={ch.score:0.1f}%")
        console.print(f"Raw Results")
        rprint(ch.as_dict())


if __name__ == "__main__":
    t8.ten8t_setup_logging(logging.DEBUG, file_name="rich_demo.log")

    main()

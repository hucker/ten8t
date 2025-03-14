import time

from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

import ten8t as t8

console = Console(force_terminal=True, color_system="256")


# Define your checks with attributes
@t8.attributes(tag='tag1', ruid='ruid1')
def check1():
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 1 passed")


@t8.attributes(tag='tag2', ruid='ruid2')
def check2():
    time.sleep(.5)
    yield t8.TR(status=False, msg="Test 2 failed")


@t8.attributes(tag='tag3', ruid='ruid3')
def check3():
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 3 passed")
    yield t8.TR(status=True, msg="Test 4 passed")


@t8.attributes(tag='tag3', ruid='ruid4')
def check4():
    time.sleep(.5)
    yield t8.TR(status=True, msg="Test 5 passed")
    yield t8.TR(status=True, msg="Test 6 passed")


# Custom CLI Progress class using Rich
class Ten8tCLIProgress(t8.Ten8tProgress):
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
            self.task_id = self.progress.add_task("Processing Checks", total=max_iteration)

        # Update progress with current iteration
        self.progress.update(self.task_id, completed=current_iteration)

    def start_progress(self):
        self.progress.start()

    def stop_progress(self):
        self.progress.stop()


# Set up and run checks
rc = t8.ten8t_rc_factory({'ruids': '.*'})

progress_object = Ten8tCLIProgress()
progress_object.start_progress()

ch = t8.Ten8tChecker(
    check_functions=[check1, check2, check3, check4],
    auto_setup=True,
    rc=rc,
    progress_object=progress_object,
    auto_ruid=True,
)
results = ch.run_all()
progress_object.stop_progress()

# Format the final results using a Rich Table
if results:
    table = Table(title="Test Results", show_header=True, header_style="bold magenta")
    table.add_column("Tag", style="cyan")
    table.add_column("RUID", style="green")
    table.add_column("Function Name", style="blue")
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

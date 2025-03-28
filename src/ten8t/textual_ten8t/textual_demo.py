"""
Ten8t Textual Demo Application

This demonstration app showcases the integration between Ten8t (a Python infra
checking framework) and Textual (a rich text user interface framework).

The application provides a directory browser that filters for Python files
starting with 'check_', allowing users to select and run Ten8t checkers on
individual files or directories. Results are displayed in a DataTable with
color-coded status indicators.

Features:
- Directory navigation with custom filtering
- Running Ten8t checks on selected files or folders
- Detailed results display with rich formatting
- Command-line parameter for specifying the starting folder
- Detailed logging to a log file.

Usage:
    python ten8t_textual_demo.py --folder /path/to/start/folder

The app can be controlled via:
- Mouse interaction with the directory tree and buttons
- Keyboard shortcuts: 'q' to quit, 'r' to run selected checker
"""

import logging
import pathlib
from typing import Iterable

import click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, DirectoryTree, Footer, Header
from textual.widgets import DataTable

import ten8t as t8
from ten8t import Ten8tChecker, ten8t_logger


class FilteredDirectoryTree(DirectoryTree):
    """
    FilteredDirectoryTree extends Textual's DirectoryTree to display only specific files and directories.

    This component filters the directory tree to show:
    - Python files (.py) that start with 'check_' prefix
    - Directories that don't start with underscores ('_') or dots ('.')

    This specialized view helps users focus on Ten8t checker files and folders
    while ignoring other files and directories..

    """

    def filter_paths(self, paths: Iterable[pathlib.Path]) -> Iterable[pathlib.Path]:
        def valid_path(p):
            # The prefix is changeable, but for now check_ is good for demos.
            if p.is_file() and p.suffix == '.py' and p.name.startswith('check_'):
                return True
            if not p.is_dir():
                return False
            if p.name.startswith('_'):
                return False
            if p.name.startswith('.'):
                return False

            return True

        return [p for p in paths if valid_path(p)]


class FileProcessorApp(App):
    """A Textual app with directory selection, run button, and results display."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 5;
        grid-rows: 1fr;
        padding: 1;
    }

    #sidebar {
        width: 100%;
        height: 100%;
        border: solid green;
        padding: 1;
        column_span: 1;  /* 20% */
        layout: grid;
        grid-size: 1;
        grid-rows: 1fr 3 3;  /* 1fr for tree (takes remaining space), 3 for each button */
    }

    #content {
        width: 100%;
        height: 100%;
        border: solid blue;
        padding: 1;
        column_span: 4;  /* 80% */
    }

    #directory-tree {
        /* Remove the fixed height: 80% */
        border: solid grey;
        margin-bottom: 1;
    }

    #run-button {
        width: 1fr;  
        height: 3;
    }
    
    #exit-button {
        width: 1fr; 
        height: 3;
        background: darkred;
    }

    #exit-button:hover {
        background: red;
    }

    #results-table {
        height: 100%;
        width:100%;
    }

    Button:hover {
        background: green;
    }
    
   .textual-tooltip {
        max-width: 100;  /* Set maximum width to 30 cells */
        min-width: 10;  /* Set minimum width to 10 cells */
        width: auto;    /* Allow automatic width between min and max */
        /* Basic border around the tooltip */
        border: solid $accent;
        
        /* Add some padding so text isn't right against the border */
        padding: 1;
        
        /* Control background and text colors */
        background: $surface;
        color: $text;
}

    """

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the application"),
        Binding(key="r", action="run_process", description="Run the selected checker"),
    ]

    def __init__(self, start_folder: str = ".", *args, **kwargs):
        """Enable the start folder to be set at startup"""
        super().__init__(*args, **kwargs)
        self.start_folder = start_folder

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="sidebar"):
            # Use Path.home() instead of os.path.expanduser
            yield FilteredDirectoryTree(pathlib.Path(self.start_folder), id="directory-tree")

            yield Button("Run", id="run-button", variant="primary")
            yield Button("Exit", id="exit-button")

        with Container(id="content"):
            # Create an empty results table that will be updated later
            yield DataTable(id="results_table")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = ("Ten8t Runner")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when any button is pressed."""
        if event.button.id == "run-button":
            try:
                self.run_process()
            except Exception as e:
                print(f"Error running process: {e}")
        if event.button.id == "exit-button":
            self.exit()

    def run_process(self) -> None:
        """Process the selected directory and display results."""
        tree = self.query_one(DirectoryTree)
        selected_node = tree.cursor_node

        if selected_node is None:
            self.notify("No directory selected or valid file was selected.")
            return
        selected_path = pathlib.Path(selected_node.data.path)

        # Get rid of old data
        self.query_one("#results_table", DataTable).clear(columns=True)

        # This allows users to run a file or a folder
        module, package = None, None
        if selected_path.is_file():
            module = t8.Ten8tModule(module_file=str(selected_path))

        if selected_path.is_dir():
            package = t8.Ten8tPackage(folder=selected_path)

        # Create a progress object that logs ten8t actions to the log file
        progress = t8.Ten8tLogProgress(ten8t_logger)

        checker = t8.Ten8tChecker(modules=module,
                                  packages=package,
                                  renderer=t8.Ten8tBasicRichRenderer(),
                                  progress_object=progress)

        ten8t_logger.info(msg=f"Start run = {checker.function_count} functions.")
        self.update_results_table(checker, selected_path)
        ten8t_logger.info(msg=f"Run complete.")

    def textual_status(self, checker: Ten8tChecker) -> None:
        """Toast messages for status."""
        score = f"Score={checker.score:.2f}%"
        if checker.result_count == 0:
            self.notify(message="No results were collected.",
                        title="No Results!",
                        severity="error")
        elif not checker.perfect_run:
            self.notify(message=f"There were {checker.fail_count} errors out of {checker.result_count} checks. {score}",
                        title="Imperfect Run!",
                        severity="warning")
        elif checker.perfect_run:
            self.notify(message=f"There were no errors! out of {checker.result_count} checks. {score}",
                        title="SUCCESS",
                        severity="information")
        else:
            self.notify(message=f"There were {checker.fail_count} errors out of {checker.result_count} checks. {score}",
                        title="Warning",
                        severity="warning")

    def make_result_status(self, status):
        """Formate that pass/fail status nicely."""
        if status:
            return "[green]PASS[/green]"
        if status is False:
            return "[red]FAIL[/red]"
        else:
            return "N/A"

    def make_skipped(self, skipped):
        if skipped:
            return "[purple]Skipped[/purple]"
        else:
            return ""

    def make_tooltip(self, checker: Ten8tChecker) -> str:
        """
        Create a textual friendly tool tip.

        The tool tip is for the whole table, so this just extracts a bunch of info from the checker as
        a sort of poor mans summary or header.
        """
        c = checker
        ruids = '' if not c.ruids else "ruids=" + ",".join(c.ruids) + '\n'
        tags = '' if not c.tags else "tags=" + ",".join(c.tags) + '\n'
        phases = '' if not c.phases else "phases=" + ",".join(c.phases) + '\n'
        score = f"{c.score:.1f}%" if c.score else "N/A"
        pass_count = c.pass_count
        fail_count = c.fail_count
        skip_count = c.skip_count
        tt = f"Checker Run Summary:\n{score=}\n{pass_count=}\n{fail_count=}\n{skip_count=}\n{ruids}{tags}{phases}".strip()
        return tt

    def update_results_table(self, checker: Ten8tChecker, path) -> None:
        """Update the results table with new data."""
        data_table = self.query_one("#results_table", DataTable)
        # Clear any existing data
        data_table.clear(columns=True)
        # Add columns with appropriate styles
        data_table.add_columns(
            "Status", "Skipped", "Message", "RUID", "Tag", "Phase", "Function", "Module", "Runtime"
        )

        # Add rows for each result
        for result in checker.yield_all():
            status = self.make_result_status(result.status)
            skipped = self.make_skipped(result.skipped)
            message = result.msg_rendered if hasattr(result, 'msg_rendered') else str(result)
            ruid = result.ruid if hasattr(result, 'ruid') else "N/A"
            tag = result.tag if hasattr(result, 'tag') else "N/A"
            phase = str(result.phase) if hasattr(result, 'phase') else "N/A"
            function = str(result.func_name) if hasattr(result, 'func_name') else "N/A"
            module = str(result.module_name) if hasattr(result, 'module_name') else "N/A"
            runtime = f"{result.runtime_sec:.06f}s" if hasattr(result, 'runtime_sec') else "N/A"

            # Style the status column based on the value
            status_style = ""
            if status == "PASS":
                status_style = "green"
            elif status == "FAIL":
                status_style = "red"
            elif status == "WARNING":
                status_style = "yellow"

            data_table.add_row(
                f"[{status_style}]{status}[/{status_style}]" if status_style else status,
                skipped,
                message,
                ruid,
                tag,
                phase,
                function,
                module,
                runtime,
            )
            data_table.refresh(repaint=True, recompose=True, layout=True)

        data_table.tooltip = self.make_tooltip(checker)
        self.textual_status(checker)


@click.command()
@click.option("--folder", "-f", default=".", help="Starting folder path")
def main(folder: str):
    t8.ten8t_logging.ten8t_setup_logging(level=logging.INFO, file_name="./textual_demo.log")
    ten8t_logger.info(msg=f"Startup package folder = {folder}")

    app = FileProcessorApp(start_folder=folder)
    app.run()


if __name__ == "__main__":
    main()

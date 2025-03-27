import pathlib
from typing import Iterable

from rich import box
from rich.table import Table
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, DirectoryTree, Footer, Header, Label, Static

import ten8t as t8


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[pathlib.Path]) -> Iterable[pathlib.Path]:
        def valid_path(p):
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
    }
    
    #content {
        width: 100%;
        height: 100%;
        border: solid blue;
        padding: 1;
        column_span: 4;  /* 80% */
    }

    #directory-tree {
        height: 80%;
        border: solid grey;
        margin-bottom: 1;
    }

    #run-button {
        width: 1fr;  /* Take 50% of the container width */
        height: 3;
    }
    
    #exit-button {
        width: 1fr;  /* Take 50% of the container width */
        height: 3;
        background: darkred;
    }

    #exit-button:hover {
        background: red;
    }

    #results-list {
        height: 100%;
        border: solid grey;
        overflow-y: auto;
    }

    /* Button container for side-by-side buttons */
    #button-container {
        width: 100%;
        height:10;
    }



    Button:hover {
        background: green;
    }
    """

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the application"),
        Binding(key="r", action="run_process", description="Run the selected checker"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="sidebar"):
            # Add a title for the directory section
            yield Label("Select a folder", id="directory-title")
            # Use Path.home() instead of os.path.expanduser
            yield FilteredDirectoryTree(pathlib.Path.cwd().parent / "Examples", id="directory-tree")

            with Container(id="button_container"):
                yield Button("Run", id="run-button", variant="primary")
                yield Button("Exit", id="exit-button")

        # Create an empty results table that will be updated later
        yield Static("", id="results_table")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = ("Ten8t Runner")
        # Initialize with placeholder items

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""
        if event.button.id == "run-button":
            self.run_process()
        if event.button.id == "exit-button":
            self.exit()

    def action_run_process(self) -> None:
        """Run process on the selected directory."""
        self.run_process()

    def run_process(self) -> None:
        """Process the selected directory and display results."""
        tree = self.query_one(DirectoryTree)
        selected_node = tree.cursor_node

        if selected_node is None:
            self.add_result("No directory selected")
            return

        selected_path = pathlib.Path(selected_node.data.path)
        package = t8.Ten8tPackage(folder=selected_path)
        checker = t8.Ten8tChecker(packages=[package], renderer=t8.Ten8tBasicRichRenderer())
        checker.run_all()
        self.update_results_table(checker.results, selected_path)

    def make_status(self, status):
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

    def update_results_table(self, results, path) -> None:
        """Update the results table with new data."""
        # Create a table to display results
        table = Table(
            title=f"Processing directory: {path}",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            expand=True
        )

        # Add columns
        table.add_column("Status", style="cyan")
        table.add_column("Skipped", style="yellow")
        table.add_column("Message", style="white", max_width=60)
        table.add_column("RUID", style="dim")
        table.add_column("Tag", style="green")

        # Add rows for each result
        for result in results:
            status = self.make_status(result.status)
            skipped = self.make_skipped(result.skipped)
            message = result.msg_rendered if hasattr(result, 'msg_rendered') else str(result)
            ruid = result.ruid if hasattr(result, 'ruid') else "N/A"
            tag = result.tag if hasattr(result, 'tag') else "N/A"

            # Style the status column based on the value
            status_style = ""
            if status == "PASS":
                status_style = "green"
            elif status == "FAIL":
                status_style = "red"
            elif status == "WARNING":
                status_style = "yellow"

            table.add_row(
                f"[{status_style}]{status}[/{status_style}]" if status_style else status,
                skipped,
                message,
                ruid,
                tag
            )

        # Update the Static widget with the new table
        results_table = self.query_one("#results_table", Static)
        results_table.update(table)


    def clear_results(self) -> None:
        """Clear the results table."""
        try:
            results_table = self.query_one("#results-table", Static)
            results_table.update("Results cleared.")
        except Exception as e:
            print(f"Error clearing results: {e}")


if __name__ == "__main__":
    app = FileProcessorApp()
    app.run()

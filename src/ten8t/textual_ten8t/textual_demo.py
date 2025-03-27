import os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, DirectoryTree, Footer, Header, Label, ListItem, ListView


class FileProcessorApp(App):
    """A Textual app with directory selection, run button, and results display."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-rows: 1fr;
        padding: 1;
    }

    #sidebar {
        width: 30%;
        height: 100%;
        border: solid green;
        padding: 1;
    }

    #content {
        width: 70%;
        height: 100%;
        border: solid blue;
        padding: 1;
    }

    #directory-tree {
        height: 80%;
        border: solid grey;
        margin-bottom: 1;
    }

    #run-button {
        width: 100%;
        height: 3;
        margin-top: 1;
    }

    #results-list {
        height: 100%;
        border: solid grey;
        overflow-y: auto;
    }

    Button:hover {
        background: green;
    }
    """

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the application"),
        Binding(key="r", action="run_process", description="Run the process"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="sidebar"):
            yield DirectoryTree(os.path.expanduser("~"), id="directory-tree")
            yield Button("Run", id="run-button", variant="primary")

        with Container(id="content"):
            yield ListView(id="results-list")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = "File Processor App"
        # Initialize with placeholder items
        self.add_placeholder_results()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""
        if event.button.id == "run-button":
            self.run_process()

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

        selected_path = selected_node.data.path
        self.clear_results()
        self.add_result(f"Processing directory: {selected_path}")

        # Here you would add your actual processing logic
        # For this example, we'll just list files in the directory
        try:
            files = os.listdir(selected_path)
            for file in files[:10]:  # Limit to first 10 files
                file_path = os.path.join(selected_path, file)
                is_dir = os.path.isdir(file_path)
                size = os.path.getsize(file_path) if not is_dir else 0
                self.add_result(f"{'[DIR]' if is_dir else '[FILE]'} {file} ({size} bytes)")

            if len(files) > 10:
                self.add_result(f"... and {len(files) - 10} more items")
        except Exception as e:
            self.add_result(f"Error: {str(e)}")

    def add_result(self, message: str) -> None:
        """Add a result message to the results list."""
        results_list = self.query_one("#results-list", ListView)
        # Create a ListItem widget with the message and append that to the ListView
        results_list.append(ListItem(Label(message)))

    def clear_results(self) -> None:
        """Clear all results from the list."""
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()

    def add_placeholder_results(self) -> None:
        """Add placeholder items to the results list."""
        self.add_result("Select a directory and click Run")
        self.add_result("or press 'r' to process")


if __name__ == "__main__":
    app = FileProcessorApp()
    app.run()

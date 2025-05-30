import csv
import datetime as dt
import json
import pathlib
import re
from abc import ABC, abstractmethod
from typing import Optional

import typer


class ToMarkdown(ABC):
    """
    Abstract base class for converting files to markdown format.

    This class provides functionality to load file content and convert it to
    markdown representation. Concrete subclasses must implement the `to_markdown()`
    method to define specific conversion logic.

    Attributes:
        file_name (str): Path to the file to be converted
        text (str): Content of the loaded file
        markdown (str): The markdown representation after conversion
        error_str (str): Error message if file loading fails
        date_stamp (bool): Whether to include timestamp in the output
    """

    def __init__(self, file_name: str, date_stamp: bool = False, **kwargs):
        self.file_name: str = file_name
        self.text: str = self.load_file()
        self.markdown: str = ""
        self.error_str: str = ""
        self.date_stamp: bool = date_stamp
        # Store remaining kwargs if needed
        self.kwargs = kwargs


    def file_time_stamp_md(self,
                           file_path:str=None,
                           tag:str='small',
                           tfmt="%H:%M:%S",
                           dfmt="%Y-%m-%d") -> str:
        """
        Generate a markdown header with filename and file's modification datetime in small text.

        Args:
            file_path (str): The path to the file

        Returns:
            str: Markdown formatted text with filename and datetime

        Example:
            '<small>data.csv &nbsp;&nbsp; 14:32:05 2023-08-21</small>'
        """
        file_path = file_path or self.file_name

        # Note that these tags ove opening and closing backticks to make fixed pitch small font
        open_tag = f"<{tag}>" if tag  else ''
        close_tag = f"</{tag}>" if tag  else ''
        # Create Path object
        path = pathlib.Path(file_path)

        try:

            # Get file's modification time
            ts = dt.datetime.fromtimestamp(path.stat().st_mtime)

            # This inserts the text in small text
            markdown = f"{open_tag}{path.name} &nbsp;&nbsp;" \
                       f" { ts.strftime(tfmt)} {ts.strftime(dfmt)}{close_tag}"

            return markdown
        except FileNotFoundError:
            # File doesn't exist
            return f"{open_tag}{path.name} WARNING:(file not found){close_tag}"

        except PermissionError:
            # No permission to access the file
            return f"{open_tag}{path.name} WARNING:(permission denied){close_tag}"

        except OSError as e:
            # Other OS-related errors
            return f"{open_tag}{path.name} (WARNING: {str(e)}){close_tag}"

    def load_file(self,file_name:str=None):
        file_name = file_name or self.file_name
        try:
            with open(file_name, 'r') as file:
                self.text = file.read()
        except (FileNotFoundError,FileExistsError,IOError,PermissionError) as e:
            self.error_str = str(e)
            self.text = ''

        return self.text

    @abstractmethod
    def to_markdown(self):
        pass

    def to_full_markdown(self):
        """
        THe full markdown includes any headers and footers that might be configured.

        Returns:
            str: The complete markdown representation
        """
        md = self.to_markdown()

        if self.date_stamp:
            md = f"{md}\n{self.file_time_stamp_md()}\n"

        return md


class MarkdownToMarkdown(ToMarkdown):
    def __init__(self, file_name: str, date_stamp: bool, **kwargs):
        super().__init__(file_name, date_stamp, **kwargs)

    def to_markdown(self):
        return f"\n{self.text}\n"


class TextToMarkdown(ToMarkdown):
    def __init__(self, file_name: str,date_stamp:bool, **kwargs):
        super().__init__(file_name,date_stamp, **kwargs)

    def to_markdown(self):
        return f"```\n{self.text}\n```"

class PyToMarkdown(ToMarkdown):
    def __init__(self, file_name: str,date_stamp:bool, **kwargs):
        super().__init__(file_name,date_stamp, **kwargs)
    def to_markdown(self):
        return f"```python\n{self.text}\n```"

class JsonToMarkdown(ToMarkdown):
    def __init__(self, file_name: str,date_stamp:bool, **kwargs):
        super().__init__(file_name,date_stamp, **kwargs)

    def to_markdown(self):
        formatted_json = json.dumps(json.loads(self.text), indent=4)
        return f"```json\n{formatted_json}\n```"

class CsvToMarkdown(ToMarkdown):
    def __init__(self, file_name: str,date_stamp:bool, **kwargs):
        # Extract CSV-specific parameters before calling super()
        self.auto_break = kwargs.pop('auto_break', True)
        self.bold_vals = kwargs.pop('bold_vals', [])

        # Pass remaining kwargs to super
        super().__init__(file_name,date_stamp, **kwargs)


    def to_markdown(self):
        try:
            with open(self.file_name, 'r') as csv_file:
                reader = csv.reader(csv_file)

                # Read all rows from the CSV
                rows = list(reader)

                if not rows:
                    return "The CSV file is empty."

                # Prepare the Markdown table header
                header = rows[0]

                # Insert line breaks
                if self.auto_break:
                    header = [h.replace(" ", "<br>").replace("_", "<br>") for h in header]

                markdown = "| " + " | ".join(header) + " |\n"
                markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

                # Add the rows
                for row in rows[1:]:
                    formatted_row = []
                    for item in row:
                        try:
                            if item in self.bold_vals:
                                item = f"-> **{item}** <-"
                            # Check if the item is numeric (can be converted to a float)
                            number = float(item)
                            # Format as a 2-significant-figure float (if it's not an integer)
                            if number.is_integer() and '.' not in str(number):
                                formatted_row.append(f"{int(number)}")  # Keeps integers as they are
                            else:
                                formatted_row.append(f"{number:.02f}")
                        except ValueError:
                            # If not numeric, keep the item as-is
                            formatted_row.append(item)

                    markdown += "| " + " | ".join(formatted_row) + " |\n"

                return markdown
        except FileNotFoundError:
            return f"Error: File '{self.file_name}' not found."
        except Exception as e:
            return f"Error: An error occurred while processing the file: {e}"


def markdown_factory(filename:str,date_time:bool, **kwargs):
    """
    Creates the appropriate markdown converter based on file extension.

    This factory function examines the provided filename's extension and instantiates
    the corresponding converter class. All keyword arguments are passed through to
    the converter's constructor, allowing each converter to use parameters relevant
    to its functionality.

    Args:
        filename (str): Path to the file that needs conversion to markdown.
        date_time (bool): Whether to include timestamp in the output.
        **kwargs: Additional keyword arguments that will be passed to the converter.
            CSV-specific parameters:
                auto_break (bool): Whether to insert line breaks in CSV headers.
                bold_vals (list): List of values to be bolded in CSV tables.

    Returns:
        ToMarkdown: An instance of the appropriate converter subclass:
            - TextToMarkdown: For .md files or unrecognized file types
            - PyToMarkdown: For .py files
            - JsonToMarkdown: For .json files
            - CsvToMarkdown: For .csv files

    """

    if filename.endswith(".md"):
        return MarkdownToMarkdown(filename, date_time, **kwargs)
    elif filename.endswith(".py"):
        return PyToMarkdown(filename,date_time,**kwargs)
    elif filename.endswith(".json"):
        return JsonToMarkdown(filename,date_time,**kwargs)
    elif filename.endswith(".csv"):
        return CsvToMarkdown(filename,date_time,**kwargs)
    else:
        return TextToMarkdown(filename,date_time,**kwargs)



def update_markdown_file(md_file: str, bold:bool, date_stamp:bool, auto_break:bool) -> None:
    """
    Parse a Markdown file and replace special placeholders with actual file contents.

    Supported placeholders:
        1. <!--file <filename>--> : Replaces with the Markdown table generated based on file extension

    Args:
        md_file (str): The path to the Markdown file to be updated.
    """
    try:
        with open(md_file, 'r') as file:
            content = file.read()

        # Regex to find CSV table blocks
        file_pattern = r'<!--file\s+(.+?)-->(.*?)<!--file end-->'
        file_matches = re.finditer(file_pattern, content, re.DOTALL)
        file_matches = list(file_matches)

        new_content = content

        # Process file insertions
        for match in file_matches:

            kwargs = {
                'bold_vals':bold.split(",") if bold else [],
                'auto_break':auto_break,
            }

            file_name = match.group(1).strip()  # Extract the CSV file name
            md_gen = markdown_factory(file_name,date_stamp, **kwargs)
            markdown_text =md_gen.to_full_markdown()

            # Replace the block with the Markdown table
            old_block = match.group(0)  # The full match (e.g., <!--file ...--> ... <!--file end-->)
            new_block = f"<!--file {file_name}-->\n{markdown_text}\n<!--file end-->"
            new_content = new_content.replace(old_block, new_block)

        # Write the updated content back to the Markdown file
        #with open(md_file, 'w') as file:
        #    file.write(new_content)

        #typer.echo(f"Updated {md_file} with file contents.",err=True)
        return new_content
    except FileNotFoundError:
        typer.echo(f"Error: File '{md_file}' not found.",err=True)
    except Exception as e:
        typer.echo(f"An error occurred: {e}",err=True)

    return None
app = typer.Typer()

@app.command()
def convert(
    file_name: str = typer.Argument("../README.md", help="The file to convert to Markdown"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file (if not specified, prints to stdout)"
    ),
    bold_values: Optional[str] = typer.Option(
        None, "--bold", "-b", help="Comma-separated values to make bold (for CSV files)"
    ),
    date_stamp: Optional[bool] = typer.Option(
        True, "--date-stamp/--no-date-stamp", "-d", help="Add datetime stamp to file output"
    ),
    auto_break: Optional[bool] = typer.Option(
        True, "--auto-break/--no-auto-break", help="Disable automatic line breaks in CSV headers"
    ),
):
    """Convert a file to Markdown based on its extension."""
    try:

        markdown_text = update_markdown_file(file_name,bold=bold_values,date_stamp=date_stamp,auto_break=auto_break)

        if output:
            with open(output, "w") as file:
                file.write(markdown_text)
            typer.echo(f"Markdown written to {output}",err=True)
        else:
            if markdown_text:
                typer.echo(markdown_text)
            else:
                typer.echo("An Error Occurred",err=True)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)



if __name__ == "__main__":
    app()
    #update_markdown_file("../README.md")

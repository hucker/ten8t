import csv
import re


def csv_to_markdown(file_name: str, bold_vals: list = None) -> str:
    """
    Convert the contents of a CSV file into a Markdown table.

    Args:
        file_name (str): The path to the CSV file.
        bold_vals (list): List of values that should be bold.

    Returns:
        str: A string representing the Markdown table.
    """

    bold_vals = bold_vals or []

    try:
        with open(file_name, 'r') as csv_file:
            reader = csv.reader(csv_file)

            # Read all rows from the CSV
            rows = list(reader)

            if not rows:
                return "The CSV file is empty."

            # Prepare the Markdown table header
            header = rows[0]
            markdown = "| " + " | ".join(header) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

            # Add the rows
            for row in rows[1:]:
                formatted_row = []
                for item in row:
                    try:
                        if item in bold_vals:
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
        return f"Error: File '{file_name}' not found."
    except Exception as e:
        return f"Error: An error occurred while processing the file: {e}"


def text_file_to_content(file_name: str) -> str:
    """
    Read and return the contents of a text file.

    Args:
        file_name (str): The path to the text file.

    Returns:
        str: The contents of the text file.
    """
    try:
        with open(file_name, 'r') as text_file:
            return text_file.read()
    except FileNotFoundError:
        return f"Error: File '{file_name}' not found."
    except Exception as e:
        return f"An error occurred while processing the file: {e}"


def update_markdown_file(md_file: str) -> None:
    """
    Parse a Markdown file and replace special placeholders with actual file contents.

    Supported placeholders:
        1. <!--csv_table <filename>--> : Replaces with the Markdown table generated from a CSV file.
        2. <!--text_file <filename>--> : Replaces with the raw contents of a text file.

    Args:
        md_file (str): The path to the Markdown file to be updated.
    """
    try:
        with open(md_file, 'r') as file:
            content = file.read()

        # Regex to find CSV table blocks
        csv_pattern = r'<!--csv_table\s+(.+?)-->(.*?)<!--csv_table end-->'
        csv_matches = re.finditer(csv_pattern, content, re.DOTALL)
        csv_matches = list(csv_matches)

        # Regex to find text file blocks
        text_pattern = r'<!--text_file\s+(.+?)-->(.*?)<!--text_file end-->'
        text_matches = re.finditer(text_pattern, content, re.DOTALL)
        text_matches = list(text_matches)

        new_content = content

        # Process CSV table placeholders
        for match in csv_matches:
            csv_file_name = match.group(1).strip()  # Extract the CSV file name
            markdown_table = csv_to_markdown(csv_file_name, ['D', 'E', 'F'])  # Generate the Markdown table
            if markdown_table.startswith("Error"):
                print(f"Skipping {csv_file_name}: {markdown_table}")
                continue

            # Replace the block with the Markdown table
            old_block = match.group(0)  # The full match (e.g., <!--csv_table ...--> ... <!--csv_table end-->)
            new_block = f"<!--csv_table {csv_file_name}-->\n{markdown_table}\n<!--csv_table end-->"
            new_content = new_content.replace(old_block, new_block)

        # Process text file placeholders
        for match in text_matches:
            text_file_name = match.group(1).strip()  # Extract the text file name
            text_content = text_file_to_content(text_file_name)  # Read the text content
            if "Error" in text_content:
                print(f"Skipping {text_file_name}: {text_content}")
                continue

            # Replace the block with the text file content
            old_block = match.group(0)  # The full match (e.g., <!--text_file ...--> ... <!--text_file end-->)
            new_block = f"<!--text_file {text_file_name}-->\n{text_content}\n<!--text_file end-->"
            new_content = new_content.replace(old_block, new_block)

        # Write the updated content back to the Markdown file
        with open(md_file, 'w') as file:
            file.write(new_content)

        print(f"Updated {md_file} with CSV tables and text file contents.")

    except FileNotFoundError:
        print(f"Error: File '{md_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


update_markdown_file("../README.md")

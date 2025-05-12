"""
This is baseline implementation of serializing checker results to an sqlite database.

It uses the serialization abstract base class from Ten8tDump.  This is an imperfect abstraction in that
we aren't really writing to a text file and I only want to write as simple JSON header and results list.

I'm assuming that to a first approximation this will mostly be used for stuff persistent caching of
previous results.

This could be dramatically improve for more generic database output by making a proper schema
where all the fields were nicely mapped as first class entities.

At this time each record is:

    datetime  string (ISO 8601)
    header    string (JSON)
    results   string (JSON)

Note that fields may be added or removed so you might want to check the __version__ string in
the header to make sure you know what you are dealing with.

"""


import datetime as dt
import json
import sqlite3
from typing import TextIO

from .._base import Ten8tDump
from ...ten8t_checker import Ten8tChecker


class Ten8tDumpSQLite(Ten8tDump):
    """
    Serialize Ten8t test results into an SQLite database.

    NOTE: This class ONLY saves all fields so any configuration that

    Schema:
        - datetime: Timestamp of when the data is saved (Primary Key)
        - header: Summary or header information (as a string)
        - results: Test results in JSON format (as a string)
    """

    def __init__(self, db_file: str, table_name: str = "ten8t_results", config=None):
        """
        Initializes the SQLiteTen8tDump class.

        Args:
            db_path (str): File path to the SQLite database.
            table_name (str): Name of the SQLite table for saving data.
            config: Optional configuration object for formatting output.
        """
        super().__init__(config=config)
        self.table_name = table_name or "ten8t_results"
        self.db_file = db_file or 'ten8t_results.db'

        # Initialize the SQLite database and table
        self._initialize_db()

    def _initialize_db(self) -> None:
        """
        Creates the database table if it does not already exist,
        and validates the schema if the table exists.
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            # Check if the table exists
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='{self.table_name}'
            """)

            if cursor.fetchone() is not None:
                # Table exists; validate schema
                self._validate_schema()
            else:
                # Table doesn't exist; create it with the expected schema
                cursor.execute(f"""
                    CREATE TABLE {self.table_name} (
                        datetime TEXT PRIMARY KEY,
                        header TEXT NOT NULL,
                        results TEXT NOT NULL
                    )
                """)
                conn.commit()

    def _validate_schema(self) -> None:
        """
        Validates that the existing SQLite table matches the expected schema.

        Raises:
            ValueError: If the table schema does not match the expected schema.
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()

        # Expected schema
        expected_columns = [
            ("datetime", "TEXT"),
            ("header", "TEXT"),
            ("results", "TEXT"),
        ]

        # Check if the number of columns matches
        if len(columns) != len(expected_columns):
            raise ValueError(f"Schema mismatch: Expected {len(expected_columns)} columns, found {len(columns)}")

        # Check each column's name and type
        for i, (expected_name, expected_type) in enumerate(expected_columns):
            actual = columns[i]
            if actual[1] != expected_name or actual[2] != expected_type:
                raise ValueError(
                    f"Schema mismatch at column {i}: Expected {expected_name} ({expected_type}), found {actual[1]} ({actual[2]})")

    def _get_output_file(self, encoding="utf8") -> TextIO:
        pass

    def get_output_file(self):
        return self.db_file

    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO, timestamp: dt.datetime = None) -> None:
        """
        Dumps the checker results into the SQLite database.

        Args:
            checker: The `Ten8tChecker` instance containing test results.
            output_file: File handle for writing (not used for database serialization).
            timestamp: Optional timestamp to use as the primary key.
        """
        # Prepare the data
        timestamp = timestamp or dt.datetime.now().isoformat()  # Use current datetime as index
        results = checker.as_dict()
        header = json.dumps(results['header'], default=str)
        results = json.dumps(results['results'], default=str)

        self._save_to_db(timestamp, header, results)

    def _save_to_db(self, timestamp: str, header: str, results: str) -> None:
        """
        Inserts data into the SQLite database.

        Args:
            timestamp: Timestamp to use as the primary key.
            header: Header information as a string.
            results: JSON-encoded string of results.
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_name} (datetime, header, results)
                VALUES (?, ?, ?)
            """, (timestamp, header, results))
            conn.commit()

    def _get_summary(self, checker: Ten8tChecker) -> str:
        results = checker.to_json()
        return results['header']

    def _get_results(self, checker: Ten8tChecker) -> str:
        results = checker.to_json()
        return results['results']

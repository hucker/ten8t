import copy
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .ten8t_checker import Ten8tChecker
from .ten8t_result import TR, Ten8tResult


def RUNNER(checker_: Ten8tChecker) -> list[Ten8tResult]:
    return checker_.run_all()


class Ten8tExecutor:
    """
    A class to manage and execute Ten8tChecker tasks in parallel using an executor.

    This class supports both ThreadPoolExecutor and ProcessPoolExecutor by allowing users
    to specify the executor type during initialization. Functions are grouped by their `thread_id`
    attribute, executed in parallel, and results are aggregated.

    Example:
        checker = Ten8tChecker(...)
        t_executor = Ten8tExecutor(checker, executor_type=ThreadPoolExecutor)
        results = t_executor.run_all(max_workers=5)

        # For processes, just pass ProcessPoolExecutor
        t_executor = Ten8tExecutor(checker, executor_type=ProcessPoolExecutor)
    """

    def __init__(self, checker: Ten8tChecker, executor_type=ThreadPoolExecutor):
        """
        Initialize the Ten8tExecutor instance with a specific Ten8tChecker.

        Args:
            checker (Ten8tChecker): An instance of Ten8tChecker containing the collected functions.
            executor_type: The type of executor to use (ThreadPoolExecutor or ProcessPoolExecutor).
        """
        self.checker = checker
        self.executor_type = executor_type  # Store the provided executor type (e.g., Thread or Process).
        self.thread_groups = self.make_thread_groups()
        self.results: list[Ten8tResult] = []

    @property
    def expected_threads(self) -> int:
        """
        Calculate the number of threads expected based on the number of unique thread groups.

        (`thread_id` values) present in `_func_groups`.

        Returns:
            int: Number of thread groups (keys) in `_func_groups`.
        """
        return len(self.thread_groups)

    def __repr__(self) -> str:
        """
        Return a string representation of the Ten8tExecutor instance.

        Includes:
            - Class name.
            - Number of thread groups (expected threads).
            - Checker's class name for context.

        Returns:
            str: A string suitable for debugging, showing the internal state of the object.
        """
        return (
            f"<{self.__class__.__name__}(expected {self.executor_type.__class__.__name__}-{self.expected_threads}, "
            f"checker={self.checker.__class__.__name__})>"
        )

    def make_thread_groups(self) -> defaultdict:
        """
        Group the functions collected by the Ten8tChecker based on their `thread_id`.

        Returns:
            defaultdict: A dictionary mapping `thread_id` values to lists of functions.
        """
        fg = defaultdict(list)
        for function_ in self.checker.collected:
            fg[function_.thread_id].append(function_)
        self.thread_groups = fg
        return fg

    def run_all(self, max_workers=5) -> list[Ten8tResult]:
        """
        Execute all groups of functions in parallel, where each group is keyed by its `thread_id`.

        Args:
            max_workers (int): The maximum number of worker threads/processes to use for execution.
                               Default is 5.

        Returns:
            list[Ten8tResult]: A list of `Ten8tResult` objects representing the execution results.
        """
        # If only one group of functions exists, execute them sequentially without parallelism.
        if len(self.thread_groups) == 1:
            return self.checker.run_all()

        # List to hold checkers, each assigned a subset of functions to process.
        checkers = []
        for name, functions in self.thread_groups.items():
            # Create a shallow copy of the Ten8tChecker instance.
            checker = copy.copy(self.checker)
            checker.collected = functions
            checkers.append(checker)

        # Helper function to execute a checker's `run_all` method.

        final_result: list[Ten8tResult] = []

        # Use the specified executor type to execute each checker in parallel.
        with self.executor_type(max_workers=max_workers) as executor:
            futures = [executor.submit(RUNNER, checker) for checker in checkers]

            # Collect results from each task as they finish.
            for future in as_completed(futures):
                try:
                    final_result.extend(future.result())
                except Exception as e:
                    final_result.append(TR(status=False, msg=f"Unexpected exception in Ten8tExecutor.run_all: {e}"))

        # Aggregate and return the results.
        self.results = final_result
        self.results.sort(key=lambda result: result.thread_id)  # Sort by thread_id for consistency
        return self.results

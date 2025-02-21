import copy
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .ten8t_checker import Ten8tChecker
from .ten8t_result import TR, Ten8tResult


class Ten8tThread:
    """
    A class to manage and execute Ten8tChecker tasks in parallel using threading.

    This class groups functions collected by a Ten8tChecker instance based on their `thread_id`
    attribute, executes each group in parallel using `ThreadPoolExecutor`, and aggregates the results.

    Example:
        checker = Ten8tChecker(...)
        t_thread = Ten8tThread(checker)
        results = t_thread.run_all(max_workers=5)
    """

    def __init__(self, checker: Ten8tChecker):
        """
        Initialize the Ten8tThread instance with a specific Ten8tChecker.

        Args:
            checker (Ten8tChecker): An instance of Ten8tChecker containing the collected functions
                                    that need to be executed.
        """
        self.checker = checker

        # Organize the collected functions into groups based on their `thread_id`.
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
        Return a string representation of the Ten8tThread instance.

        Includes:
            - Class name.
            - Number of thread groups (expected threads).
            - Checker's class name for context.

        Returns:
            str: A string suitable for debugging, showing the internal state of the object.
        """
        return (
            f"<{self.__class__.__name__}(expected_threads={self.expected_threads}, "
            f"checker={self.checker.__class__.__name__})>"
        )

    def make_thread_groups(self) -> defaultdict:
        """
        Groups the functions collected by the Ten8tChecker based on their `thread_id` attribute.
        The result of this is a dictionary where keys are `thread_id` values, and values are lists
        of functions corresponding to those thread IDs.

        Returns:
            defaultdict: A dictionary where keys are `thread_id` values, and values are lists
                         functions corresponding to those thread IDs.
        """

        fg = defaultdict(list)
        for function_ in self.checker.collected:
            fg[function_.thread_id].append(function_)
        self.thread_groups = fg
        return fg

    def run_all(self, max_workers=5) -> list[Ten8tResult]:
        """
        Execute all groups of functions in threads, where each group is in
        a dictionary keyed by its `thread_id`.

        If there is only one group, all functions are executed using the 'normal'
        checker object without threading. Otherwise, it uses a thread pool to execute
        each group concurrently.

        Args:
            max_workers (int): The maximum number of worker threads to use for parallel execution.
                               Default is 5.

        Returns:
            list[Ten8tResult]: A list of `Ten8tResult` objects representing the results of executed
                               check functions.
        """
        # If only one group of functions exists, execute them sequentially without threading.

        if len(self.thread_groups) == 1:
            return self.checker.run_all()

        # List to hold checkers, each assigned a subset of functions to process.
        checkers = []
        for name, functions in self.thread_groups.items():
            # Create a shallow copy of the Ten8tChecker instance.  This is a bit of paranoia on my part
            # but not enough to do deep copies.  Perhaps there are use cases for this?
            checker = copy.copy(self.checker)

            # Assign the subset of functions corresponding to the current group.
            checker.collected = functions

            # Add this modified checker to the list of checkers to process.
            checkers.append(checker)

        # Helper function to execute a checker's `run_all` method.
        def runner(checker_: Ten8tChecker) -> list[Ten8tResult]:
            """
            Execute the `run_all` method of the given Ten8tChecker instance.

            Args:
                checker_ (Ten8tChecker): The checker instance to execute.

            Returns:
                list[Ten8tResult]: The list of results from executing the checker.
            """

            # Assign the thread name of the checker object to the thread.
            # TODO: This is a hack.  When we run from Ten8tThread we know
            #       all thread_ids are the same so we are safe grabbing the first one
            #       this will need to be refactored.  This is ONLY done to make
            #       log messages know the thread_id.
            if len(checker_.collected) > 0:
                threading.current_thread().name = checker_.collected[0].thread_id
            else:
                threading.current_thread().name = "Checker"

            return checker_.run_all()

        final_result: list[Ten8tResult] = []  # This will collect all results from the threads.

        # Use ThreadPoolExecutor to execute each checker in parallel.
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all checkers to the thread pool for parallel execution.
            futures = [executor.submit(runner, checker) for checker in checkers]

            # Collect results from each thread as they complete.
            for future in as_completed(futures):
                try:
                    # Combine results from the completed thread into `final_result`.
                    final_result.extend(future.result())
                except Exception as e:  # pragma: no cover
                    # I don't know how to trigger this exception I have this code here to remind me what could go wrong
                    # This should be impossible, less out of memory type stuff, since the code in the checker handles
                    # all exceptions... ideally this code all goes away and this runner is trivial.
                    final_result.append(TR(status=False, msg=f"Unexpected exception in ten8t_thread.run_all {e} "))

        # Return the aggregated results from all threads.
        self.results = final_result

        # This might not be needed, but it is useful since threaded code returns the results interleaved.
        self.results.sort(key=lambda result: result.thread_id)

        return self.results

"""
This class manages running the checker against a list of functions.
There is also support for low level progress for functions/classes.
"""
import datetime as dt
import pathlib
from importlib.metadata import version
from typing import Any, Callable

from .progress import Ten8tMultiProgress, Ten8tNoProgress, Ten8tProgress
from .rc import Ten8tRC
from .render import Ten8tAbstractRenderer
from .render import Ten8tTextRenderer
from .score import ScoreByResult, ScoreStrategy
from .ten8t_exception import Ten8tException
from .ten8t_function import Ten8tFunction
from .ten8t_immutable import Ten8tEnvDict, Ten8tEnvList, Ten8tEnvSet
from .ten8t_logging import ten8t_logger
from .ten8t_module import Ten8tModule
from .ten8t_package import Ten8tPackage
from .ten8t_result import Ten8tResult
from .ten8t_ruid import empty_ruids, ruid_issues, valid_ruids
from .ten8t_util import IntList, IntListOrNone, StrList, StrListOrNone

ADHOC_MODULE_NAME = 'adhoc'
"""Name of the adhoc module"""


def _param_str_list(params: StrListOrNone,
                    disallowed=' ,!@#$%^&*(){}[]<>~`-+=\t\n\'"') -> StrList:
    """
    Allow user to specify "foo fum" instead of ["foo","fum"] or slightly more
    shady "foo" instead of ["foo"].  This is strictly for reducing friction
    for the programmer.

    Also note: the disallowed characters is just me being courteous and trying to protect
               you from yourself.  If there are other dumb characters that
               I missed please submit a PR as I have no intention of walling off
               everything in a dynamic language.

    Returns: List of Strings

    Args:
        params: "foo fum" or ["foo","fum"]

    """

    # Null case...on could argue they meant the empty string as a name
    if params is None or params == [] or isinstance(params, str) and params.strip() == '':
        return []

    if isinstance(params, str):
        params = params.split()

    for param in params:
        if not isinstance(param, str):
            raise Ten8tException(f"Invalid parameter list {param}")
        bad_chars = [c for c in disallowed if c in param]
        if bad_chars:
            raise Ten8tException(f"Parameter '{bad_chars}' is in the disallowed list.  ")

    return params


def _param_int_list(params: IntListOrNone) -> IntList:
    """
    That's a lot of options there.
    
    Allow user to specify "1 2 3" instead of [1,2,3] or slightly more
    shady 1 instead of [1].  For small numbers this is a wash but for
    symmetry with str_list it included it.

    NOTE: The separator is the default for split...whitespace

    Args:
        params: "1 2" or [1,2] or even [1,"2"]

    Returns: List of Integers

    """

    if isinstance(params, int):
        return [params]

    elif isinstance(params, str):
        params = params.split()

    params = [str(p) for p in params]

    # Make sure everything is an integer
    for param in params:
        if isinstance(param, str) and param.isdigit():
            continue
        raise Ten8tException(f"Invalid integer parameter in {param} in {params}")

    return [int(param) for param in params]






class Ten8tChecker:
    """
    A checker object is what manages running rules against a system.

    The life cycle of a checker object is

    1) Load what ever packages/modules/functions are associated with a system as
       a collection of functions that could be run.
    2) Load any environment that may be needed for the rules.
    2) Optionally filter those functions based on any of the function attributes.
    3) Check all the rules and collect the results while providing status using
       a user specified progress object.
    4) Score the results based on the scoring strategy.
    5) Return the result object as object data or json data.

    """

    def __init__(
            self,
            packages: list[Ten8tPackage] | None = None,
            modules: list[Ten8tModule] | None = None,
            check_functions: list[Ten8tFunction | Callable] | None = None,
            progress_object: Ten8tProgress | list[Ten8tProgress] | None = None,
            score_strategy: ScoreStrategy | None = None,
            rc: Ten8tRC | None = None,
            env: dict[str, Any] | None = None,
            renderer: Ten8tAbstractRenderer = None,
            abort_on_fail=False,
            abort_on_exception=False,
            auto_setup: bool = True,
            auto_ruid: bool = False,
    ):
        """

        
        Args:
            packages: List of Ten8tPackage objs to check. 
                      If not provided, default = [] .
            modules: A list of Ten8tModule objs to check. 
                     If not provided, default = [].
            check_functions: A list of Ten8tFunction objs to check. If not provided, default = [].
            progress_object: A Ten8tProgress objs for tracking progress. Multiple objects may be
                             provided.
                             If not provided, def = Ten8tNoProgress.
            score_strategy: A ScoreStrategy objs for scoring the results. 
                            If not provided, def = ScoreByResult.
            env: A dict containing additional env variables. 
                            If not provided, def = {}
            abort_on_fail: A bool flag indicating whether to abort a fail result occurs. def =False.
            abort_on_exception: A bool flag indicating whether to abort on exceptions. def=False.
            auto_setup: A bool flag automatically invoke pre_collect/prepare. def=False.
            auto_ruid: A bool flag automatically generate rule_ids if they don't exist.
        Raises:
            Ten8tException: If the provided packages, modules, or check_functions 
                             are not in the correct format.

        """

        self.packages = self._process_packages(packages)
        self.modules = self._process_modules(modules)
        self.check_functions = self._process_check_funcs(check_functions)

        # If the user has not provided a score strategy then use the simple one
        self.score_strategy = score_strategy or ScoreByResult()
        self.score = 0.0

        # Allow an RC object to be specified.
        self.rc = rc

        # In order to support rendered output a render object must be provided
        # if none are provided we create one
        self.renderer = renderer or Ten8tTextRenderer()

        # If we are provided with an environment we save it off but first wrap it in
        # a class that guards reasonably against writes to the underlying environment
        # data.
        if env:
            self.env = self._make_immutable_env(env)
        else:
            self.env = {}

        # THis dict has the environment values that are NULL
        self.env_nulls: dict[str, Any] = {}

        # If they have a progress object then set it up.
        self.set_progress(progress_object)

        # If any fail result occurs stop processing.
        self.abort_on_fail = abort_on_fail

        # If any exception occurs stop processing
        self.abort_on_exception = abort_on_exception

        # All checker functions from packages, modules, and adhoc  and of any type
        # BEFORE filtering
        self.pre_collected: list[Ten8tFunction] = []

        # Filtered list of functions from packages, modules, and adhoc
        self.check_func_list: list[Ten8tFunction] = []
        self.async_check_func_list: list[Ten8tFunction] = []
        self.coroutine_check_func_list: list[Ten8tFunction] = []

        self.start_time = dt.datetime.now()
        self.end_time = dt.datetime.now()
        self.results: list[Ten8tResult] = []
        self.auto_ruid = auto_ruid

        if not self.packages and not self.modules and not self.check_functions:
            raise Ten8tException(
                "You must provide at least one package, module or function to check."
            )

        # For some use cases there is no need for special setup so just do auto setup
        # to clean up the startup.  Real code will likely need to be sophisticated
        # with prepare...
        if auto_setup:
            self.pre_collect()
            self.prepare_functions()

    def set_progress(self, progress_object: Ten8tProgress | list[Ten8tProgress]):
        # Connect the progress output to the checker object.  The NoProgress
        # class is a dummy class that does no progress reporting.  This supports
        # a list of progress objects allowing you to send progress to a log file
        # and a UI and perhaps the terminal.  A bit overkill but it works nicely
        # if you need it with very little cost.
        if isinstance(progress_object, list):
            progress_object = Ten8tMultiProgress(progress_list=progress_object)
            progress_object = Ten8tMultiProgress(progress_list=progress_object)
        elif progress_object is None:
            progress_object = Ten8tNoProgress()

        self.progress_object: Ten8tProgress = progress_object

    @property
    def check_function_count(self) -> int:
        """
        Return the check function count.

        These are the functions passed directly in not as part of a module or package.
        """
        return len(self.check_functions) if self.check_functions else 0

    @property
    def collected_count(self) -> int:
        """Return the check function count.

        This is the could AFTER filtering
        """
        return len(self.check_func_list) if self.check_func_list else 0

    @property
    def pre_collected_count(self) -> int:
        """Return the number of "pre_collected" functions
        This is the functions BEFORE filtering
        ..."""
        return len(self.pre_collected) if self.pre_collected else 0

    @property
    def async_count(self) -> int:
        """Return the number of async functions"""
        return len(self.async_check_func_list) if self.async_check_func_list else 0

    @property
    def coroutine_count(self) -> int:
        """Return the number of coroutine functions"""
        return len(self.coroutine_check_func_list) if self.coroutine_check_func_list else 0

    @staticmethod
    def _make_immutable_env(env: dict) -> dict:
        """
        Converts mutable containers in a dictionary to immutable versions.
        """
        for key, value in env.items():

            # Detect mutable objects and convert them to immutable ones
            if isinstance(value, list):
                env[key] = Ten8tEnvList(value)
            elif isinstance(value, dict):
                env[key] = Ten8tEnvDict(value)
            elif isinstance(value, set):
                env[key] = Ten8tEnvSet(value)

        return env

    @staticmethod
    def _process_packages(packages: list[Ten8tPackage] | None) -> list[Ten8tPackage]:
        """ Allow packages to be in various forms"""
        if not packages:
            return []
        if isinstance(packages, Ten8tPackage):
            return [packages]
        if isinstance(packages, list) and all(isinstance(p, Ten8tPackage) for p in packages):
            return packages
        raise Ten8tException('Packages must be a list of Ten8tPackage objects.')

    @staticmethod
    def _process_modules(modules: list[Ten8tModule] | pathlib.Path | str | None) -> list[Ten8tModule]:
        """ Allow modules to be in various forms"""
        if not modules:
            return []
        if isinstance(modules, (pathlib.Path | str)):
            return [Ten8tModule(module_file=modules)]
        if isinstance(modules, Ten8tModule):
            return [modules]
        if isinstance(modules, list) and all(isinstance(m, Ten8tModule) for m in modules):
            return modules
        raise Ten8tException('Modules must be a list of Ten8tModule objects.')

    @staticmethod
    def _process_check_funcs(check_functions: list[Ten8tFunction | Callable] | None) -> list[Ten8tFunction]:
        """Load up an arbitrary list of Ten8t functions.
        These functions are tagged 'adhoc' for module reference.
        """
        if isinstance(check_functions, list) and len(check_functions) >= 1:
            processed_functions = []

            for count, f in enumerate(check_functions, start=1):
                if not isinstance(f, Ten8tFunction) and callable(f):
                    f = Ten8tFunction(f)

                if not isinstance(f, Ten8tFunction):
                    raise Ten8tException(
                        "Functions must be a list of Ten8tFunction objects or callable objects."
                    )

                # Set the index and module appropriately
                f.index = count
                f.module = ADHOC_MODULE_NAME

                # Add to new list
                processed_functions.append(f)

            return processed_functions

        return []

    def pre_collect(self) -> list[Ten8tFunction]:
        """
        Collect all the functions from the packages, modules and functions with no filtering.
        This list of functions is will be filtered by the checker before running checks.

        Returns:
            _type_: _description_
        """

        self.pre_collected = []

        # Worth noting that += does an 'extend' rather than an 'append'.
        for pkg in self.packages:
            self.pre_collected += [func for module in pkg.modules for func in module.check_functions]

        for module in self.modules:
            self.pre_collected += module.check_functions

        self.pre_collected += self.check_functions

        # This is a bit of a hack and is NOT required and one could argue that it is bad code.
        # I suspect that this will only be useful for testing.
        self.pre_collected = [Ten8tFunction(func) if not isinstance(func, Ten8tFunction) else func
                              for func in self.pre_collected]

        # List of all possible functions that could be run
        return self.pre_collected

    def prepare_functions(self, filter_functions=None):
        """
        Prepare the collected functions for running checks.

        Run through the collected functions to prepare the checks that will be run.
        A list of filter functions may be provided to filter the functions. Filter
        functions must return True if the function should be kept.

        Args:
            filter_functions (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        # If no filter functions are provided then use a default one allows all functions
        filter_functions = filter_functions or [lambda _: True]

        # If the user didn't provide ruids, generic ones will be created.
        self.auto_gen_ruids()

        # At this point we have all the functions in the packages, modules and functions
        # Now we need to filter out the ones that are not wanted. Filter functions return
        # True if the function should be kept
        self.check_func_list = []
        for ten8t_func in self.pre_collected:
            if all(f(ten8t_func) for f in filter_functions):
                if ten8t_func.is_asyncgen:
                    self.async_check_func_list.append(ten8t_func)
                elif ten8t_func.is_coroutine:
                    self.coroutine_check_func_list.append(ten8t_func)
                else:
                    self.check_func_list.append(ten8t_func)

        # Now use the RC file.  Note that if you are running filter functions AND
        # an RC file this can be confusing.  Ideally you use one or the other. but
        # it isn't an error to do so, you just need to know what you are doing.
        self.apply_rc(self.rc)

        # The collected list has the functions that will be run to verify operation
        # of the system.

        # If the user has provided valid ruids for all functions (or for none) then
        # we can proceed.  If not then we need to raise an exception and show the issues.
        ruids = [f.ruid for f in self.check_func_list]

        # If the user decided to set up ruids for every function OR if they didn't configure
        # any ruids then we can just run with the collected functions.
        if empty_ruids(ruids) or valid_ruids(ruids):
            return self.check_func_list

        # Otherwise there is a problem.
        raise Ten8tException(
            f"There are duplicate or missing RUIDS: {ruid_issues(ruids)}"
        )

    def auto_gen_ruids(self, template='__ruid__@id@'):
        """ Provide a mechanism for to transition from no ruids to ruids.  This way they
            can only set up the rules that need rule_ids"""
        if not self.auto_ruid:
            return
        id_ = 1
        for function in self.pre_collected:
            if function.ruid == '':
                function.ruid = template.replace("@id@", f'{id_:04d}')
                id_ += 1

    def apply_rc(self, rc=None):
        """ Apply RC file to collected functions applying includes then excludes. """
        self.rc = rc or self.rc

        # By exiting early an NOT using the RC file we don't use
        # Sets as shown below.  Sets cause order to be nondeterministic
        if not self.rc:
            return self.check_func_list

        self.check_func_list = [function for function in self.check_func_list
                                if self.rc.does_match(ruid=function.ruid,
                                                      tag=function.tag,
                                                      phase=function.phase,
                                                      level=function.level)]

        return self.check_func_list

    def exclude_by_attribute(self, tags: StrListOrNone = None,
                             ruids: StrListOrNone = None,
                             levels: IntListOrNone = None,
                             phases: StrListOrNone = None) -> list[Ten8tFunction]:
        """ Run everything except the ones that match these attributes """

        # Make everything nice lists
        tags = _param_str_list(tags)
        ruids = _param_str_list(ruids)
        phases = _param_str_list(phases)
        levels = _param_int_list(levels)

        # Exclude attributes that don't match
        self.check_func_list = [f for f in self.check_func_list if f.tag not in tags and
                                f.ruid not in ruids and
                                f.level not in levels and
                                f.phase not in phases]
        return self.check_func_list

    def include_by_attribute(self,
                             tags: StrListOrNone = None,
                             ruids: StrListOrNone = None,
                             levels: IntListOrNone = None,
                             phases: StrListOrNone = None) -> list[Ten8tFunction]:
        """ Run everything that matches these attributes """

        # Make everything nice lists
        tags_ = _param_str_list(tags)
        ruids_ = _param_str_list(ruids)
        phases_ = _param_str_list(phases)
        levels_ = _param_int_list(levels)

        # This is a special case to make including everything the default
        # if not tags and not ruids and not levels and not phases:
        #    return self.collected

        # Only include the attributes that match
        self.check_func_list = [f for f in self.check_func_list if (f.tag in tags_) or
                                (f.ruid in ruids_) or
                                (f.level in levels_) or
                                (f.phase in phases_)]

        return self.check_func_list

    def load_environments(self):
        """
        This takes the global environment and adds in the results
        from all the discovered environment functions.  The results
        are all merged into a dictionary of parameter names and their values.

        This works very much like pytest, only without the scoping Parameters
        that are needed in multiple places aren't regenerated.
        Returns:

        """

        # Prime the environment with top level config
        # This should be json-able things
        full_env = self.env.copy()

        for m in self.modules:
            for env_func in m.env_functions:
                # TODO: There should be exceptions on collisions
                full_env.update(env_func(full_env))

        # This is a concern, there should be no nulls, HOWEVER this is more complex
        # since there should be no nulls for parameters to the collected check functions.
        # for now, I'm tracking this and dumping it in the results.
        self.env_nulls = [key for key, value in full_env.items() if value is None]

        return full_env

    @property
    def ruids(self):
        """
        Return a list of all the RUIDs in the collected functions.

        Returns:
            _type_: _description_
        """
        r = sorted(set(f.ruid for f in self.check_func_list))
        return r

    @property
    def levels(self):
        """
        Return a list of all the levels in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.level for f in self.check_func_list))

    @property
    def tags(self):
        """
        Return a list of all the tags in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.tag for f in self.check_func_list))

    @property
    def phases(self):
        """
        Return a list of all the phases in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.phase for f in self.check_func_list))

    class AbortYieldException(Exception):
        """Allow breaking out of multi level loop without state variables"""

    def yield_all(self, env=None):
        """
        Yield all the results from the collected functions

        This is where the rule engine does its work.

        Args:
            env: The environment to use for the rule functions

        Yields:
            _type_: Ten8tResult
        """

        # Note that it is possible for the collected list to be
        # empty.  This is not an error condition.  It is possible
        # that the filter functions have filtered out all the
        # functions.
        count = 0
        self.progress_object.message("Start Rule Check")
        self.start_time = dt.datetime.now()

        ten8t_logger.info("Checker start with %d functions", len(self.check_func_list))

        if self.async_count:
            ten8t_logger.info("Checker has %d async functions that will be ignored.",
                              self.async_count)
        if self.coroutine_count:
            ten8t_logger.info("Checker has %d coroutine functions that will be ignored.",
                              self.coroutine_count)

        self.results = []

        # Fixes linting issue
        function_ = None
        try:
            # Magic happens here.  Each module is checked for any functions that start with
            # env_ (which is configurable).  Env is a dictionary that has values that may be
            # used as function parameters to check functions (very similar to pytest).  At this
            # time environments are global, hence there could be collisions on larger projects.
            env = self.load_environments()

            # Count here to enable progress bars
            for count, function_ in enumerate(self.check_func_list, start=1):

                # Lots of magic here
                function_.env = env

                self.progress_object.message(f"Function Start {function_.function_name}")
                for result in function_():

                    # Render the message if needed.  The render happens right before it is yielded so it "knows"
                    # as much as possible at this point.
                    result.msg_rendered = result.msg if not self.renderer else self.renderer.render(result.msg)

                    ten8t_logger.debug("%s:%s:%s", result.func_name, result.status, result.msg)

                    # TODO: Verify that we don't need to record any of the abort on data
                    self.results.append(result)

                    yield result

                    # Check early exits
                    if self.abort_on_fail and result.status is False:
                        ten8t_logger.info("Abort on fail")
                        raise self.AbortYieldException()

                    if self.abort_on_exception and result.except_:
                        ten8t_logger.info("Abort on exception")
                        raise self.AbortYieldException()

                    # Stop yielding from a function
                    if function_.finish_on_fail and result.status is False:
                        self.progress_object.message(f"Early exit. {function_.function_name} failed.")
                        break
                    self.progress_object.result_msg(count, self.function_count, result=result)
                self.progress_object.message(f"Function {function_.function_name} done.")

        except self.AbortYieldException:
            name = function_.function_name if function_ is not None else "???"

            if self.abort_on_fail:
                self.progress_object.message(f"Abort on fail: {name}")
            if self.abort_on_exception:
                self.progress_object.message(f"Abort on exception: {name}")

        self.end_time = dt.datetime.now()
        self.progress_object.message("Rule Check Complete.")
        ten8t_logger.info("Checker complete ran %s check functions", self.function_count)

        self.score = self.score_strategy(self.results)
        self.progress_object.message(f"Score = {self.score:.1f}")

    def run_all(self, env=None) -> list[Ten8tResult]:
        """
        Run through the generator.

        """

        # Just consume the generator.  Yield all saves everything for you
        for _ in self.yield_all(env=env):
            pass

        return self.results

    @property
    def clean_run(self):
        """
        Determine whether all results are free of exceptions.

        Returns:
            bool: True if none of the results contain an exception, False otherwise.
        """
        return all(not r.except_ for r in self.results)

    @property
    def perfect_run(self):
        """
        Check if all results indicate a perfect run without failures, skips, or warnings.

        Returns:
            bool: True if all results passed successfully without warnings or skips, False otherwise.
        """
        return all(r.status and not r.skipped and not r.warn_msg for r in self.results)

    @property
    def skip_count(self):
        """
        Count the number of results marked as skipped.

        Returns:
            int: The number of skipped results.
        """
        return len([r for r in self.results if r.skipped])

    @property
    def warn_count(self):
        """
        Count the number of results that contain warnings.

        Returns:
            int: The number of results with warnings.
        """
        return len([r for r in self.results if r.warn_msg])

    @property
    def pass_count(self):
        """
        Count the number of results that passed without being skipped.

        Returns:
            int: The number of passing results excluding skips.
        """
        return len([r for r in self.results if r.status and not r.skipped])

    @property
    def fail_count(self):
        """
        Count the number of results that failed but were not skipped.

        Returns:
            int: The number of failed results excluding skips.
        """
        return len([r for r in self.results if not r.status and not r.skipped])

    @property
    def summary_count(self):
        """
        Count the number of summary results that were not skipped.

        Returns:
            int: The number of summary results excluding skips.
        """
        return len([r for r in self.results if not r.summary_result and not r.skipped])

    @property
    def result_count(self):
        """
        Get the total number of results available.

        Returns:
            int: The total count of results.
        """
        return len(self.results)

    @property
    def function_count(self):
        """
        Count all collected functions.

        Note:
            This includes all functions collected, regardless of whether they were run.

        Returns:
            int: The total number of collected functions.
        """
        return len(self.check_func_list)

    @property
    def module_count(self):
        """
        Count the total number of modules across all available packages and modules.

        Returns:
            int: The total number of modules, including those in individual packages.
        """
        return len(self.modules) + sum(1 for pkg in self.packages for _ in pkg.modules)

    @property
    def module_names(self):
        """
        Retrieve a list of all module names.

        Returns:
            list: A list of all module names from standalone modules and packages.
        """
        return [module.module_name for module in self.modules] + \
            [m.module_name for pkg in self.packages for m in pkg.modules]

    @property
    def duration_seconds(self) -> float:
        """
        Calculate the duration in seconds between start_time and end_time.

        Returns:
            float: The duration in seconds. Returns 0 if start_time or end_time is not set.
        """
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def package_count(self):
        """ Count of the packages (almost always 1 or 0)"""
        return len(self.packages)

    def get_header(self) -> dict:
        """Make a header with the top level information about the checker run"""
        header = {
            "package_count": self.package_count,
            "module_count": self.module_count,
            "modules": self.module_names,
            "function_count": self.function_count,
            "tags": self.tags,
            "levels": self.levels,
            "phases": self.phases,
            "ruids": self.ruids,
            "score": self.score,
            "env_nulls": self.env_nulls,
            "__version__": version("ten8t"),
        }
        return header

    def as_dict(self):
        """
        Return a dictionary of the results.
        """
        h = self.get_header()

        r = {
            # This is the less important header stuff.
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "functions": [f.function_name for f in self.check_functions],
            "passed_count": self.pass_count,
            "warn_count": self.warn_count,
            "failed_count": self.fail_count,
            "skip_count": self.skip_count,
            "total_count": self.result_count,
            "check_count": self.function_count,
            "result_count": self.result_count,
            "clean_run": self.clean_run,
            "perfect_run": self.perfect_run,
            "abort_on_fail": self.abort_on_fail,
            "abort_on_exception": self.abort_on_exception,

            # the meat of the output lives here
            "results": [r.as_dict() for r in self.results],
        }
        return h | r

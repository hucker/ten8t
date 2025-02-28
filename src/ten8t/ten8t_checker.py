"""
This class manages running the checker against a list of functions.
There is also support for low level progress for functions/classes.
"""
import datetime as dt
from abc import ABC, abstractmethod
from typing import Any, Callable

from .ten8t_exception import Ten8tException
from .ten8t_format import Ten8tAbstractRender, Ten8tRenderText
from .ten8t_function import Ten8tFunction
from .ten8t_immutable import Ten8tEnvDict, Ten8tEnvList, Ten8tEnvSet
from .ten8t_logging import ten8t_logger
from .ten8t_module import Ten8tModule
from .ten8t_package import Ten8tPackage
from .ten8t_rc import Ten8tRC
from .ten8t_result import Ten8tResult
from .ten8t_ruid import empty_ruids, ruid_issues, valid_ruids
from .ten8t_score import ScoreByResult, ScoreStrategy
from .ten8t_util import IntList, IntListOrNone, StrList, StrListOrNone, StrOrNone


# pylint: disable=R0903
class Ten8tProgress(ABC):
    """
    Abstract base class for tracking and managing progress.

    This class serves as a base for defining progress tracking mechanisms in
    iterative processes. It is designed to be subclassed, with custom behavior
    to be implemented in the '__call__' method. Users can leverage this class
    to provide updates for operations with finite or infinite iterations, display
    status messages, and optionally handle results.

    """

    def __init__(self):
        pass

    @abstractmethod
    def __call__(self,
                 current_iteration: int,
                 max_iterations,
                 text: str,
                 result=None):  # pragma: no cover
        pass


# pylint: disable=R0903
class Ten8tNoProgress(Ten8tProgress):
    """
    Brief summary of what the class does.

    A subclass of Ten8tProgress that overrides progress functionality by
    performing no operation. This class is particularly useful for testing
    purposes when progress tracking is not required.

    """

    def __call__(self, current_iteration: int,
                 max_iterations,
                 text: str, result=None):
        """Don't do anything for progress.  This is useful for testing."""


# pylint: disable=R0903
class Ten8tDebugProgress(Ten8tProgress):
    """
    Manages and displays debug progress messages for a process.

    This class is a subclass of `Ten8tProgress` and is specifically
    designed for debugging purposes. It provides functionality to
    print debug messages alongside an optional status indicator based
    on the provided result. Typically used during iterative processes
    to notify about current progress and outcomes.

    Attributes:
        No specific attributes are defined for this subclass.
    """

    def __call__(self, current_iteration: int, max_iteration: int, msg: str,
                 result=None):  # pylint: disable=unused-argument
        """Print a debug message."""
        if msg:
            print(msg)
        if result:
            print("+" if result.status else "-", end="")


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


def exclude_ruids(ruids: list[str]):
    """Return a filter function that will exclude the ruids from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.ruid not in ruids

    return filter_func


def exclude_tags(tags: list[str]):
    """Return a filter function that will exclude the tags from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.tag not in tags

    return filter_func


def exclude_levels(levels: list[int]):
    """Return a filter function that will exclude the levels from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.level not in levels

    return filter_func


def exclude_phases(phases: list[str]):
    """Return a filter function that will exclude the phases from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.phase not in phases

    return filter_func


def keep_ruids(ruids: list[str]):
    """Return a filter function that will keep the ruids from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.ruid in ruids

    return filter_func


def keep_tags(tags: list[str]):
    """Return a filter function that will keep the tags from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.tag in tags

    return filter_func


def keep_levels(levels: list[int]):
    """Return a filter function that will keep the levels from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.level in levels

    return filter_func


def keep_phases(phases: list[str]):
    """Return a filter function that will keep the phases from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.phase in phases

    return filter_func


def debug_progress(_, msg: StrOrNone = None, result: Ten8tResult | None = None
                   ):  # pylint: disable=unused-argument
    """Print a debug message."""
    if msg:
        print(msg)
    if result:
        print("+" if result.status else "-", end="")


class Ten8tChecker:
    """
    A checker object is what manages running rules against a system.

    THe life cycle of a checker object is

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
            progress_object: Ten8tProgress | None = None,
            score_strategy: ScoreStrategy | None = None,
            rc: Ten8tRC | None = None,
            env: dict[str, Any] | None = None,
            renderer: Ten8tAbstractRender = None,
            abort_on_fail=False,
            abort_on_exception=False,
            auto_setup: bool = False,
            auto_ruid: bool = False,
    ):
        """

        
        Args:
            packages: List of Ten8tPackage objs to check. 
                      If not provided, default = [] .
            modules: A list of Ten8tModule objs to check. 
                     If not provided, default = [].
            check_functions: A list of Ten8tFunction objs to check. If not provided, default = [].
            progress_object: A Ten8tProgress objs for tracking progress. 
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
        self.renderer = renderer or Ten8tRenderText()

        # If we are provided with an environment we save it off but first wrap it in
        # a class that guards reasonably against writes to the underlying environment
        # data.
        if env:
            self.env = self._make_immutable_env(env)
        else:
            self.env = {}

        # THis dict has the environment values that are NULL
        self.env_nulls: dict[str, Any] = {}

        # Connect the progress output to the checker object.  The NoProgress
        # class is a dummy class that does no progress reporting.
        self.progress_callback: Ten8tProgress = progress_object or Ten8tNoProgress()

        # If any fail result occurs stop processing.
        self.abort_on_fail = abort_on_fail

        # If any exception occurs stop processing
        self.abort_on_exception = abort_on_exception

        # All checker functions from packages, modules, and adhoc BEFORE filtering
        self.pre_collected: list[Ten8tFunction] = []

        # Filtered list of functions from packages, modules, and adhoc
        self.collected: list[Ten8tFunction] = []

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
            self.prepare()

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
        return len(self.collected) if self.collected else 0

    @property
    def pre_collected_count(self) -> int:
        """Return the number of "pre_collected" functions
        This is the functions BEFORE filtering
        ..."""
        return len(self.pre_collected) if self.pre_collected else 0

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
    def _process_modules(modules: list[Ten8tModule] | None) -> list[Ten8tModule]:
        """ Allow modules to be in various forms"""
        if not modules:
            return []
        if isinstance(modules, Ten8tModule):
            return [modules]
        if isinstance(modules, list) and all(isinstance(m, Ten8tModule) for m in modules):
            return modules
        raise Ten8tException('Modules must be a list of Ten8tModule objects.')

    @staticmethod
    def _process_check_funcs(check_functions: list[Ten8tFunction | Callable] | None) -> list[Ten8tFunction]:
        """ Load up an arbitrary list of ten8t functions.
        These functions are tagged with adhoc for module"""
        if isinstance(check_functions, list) and len(check_functions) >= 1:
            for count, f in enumerate(check_functions, start=1):

                # It is arguable if this is a good idea or not.  This allows you to pass regular old
                # python functions to ten8t.  This code will automatically covert those callables to
                # Ten8tFunctions so they can be used by the system.  This is mostly useful for testing
                # and for easy demos
                if not isinstance(f, Ten8tFunction) and callable(f):
                    f = Ten8tFunction(f)

                if not isinstance(f, Ten8tFunction):
                    raise Ten8tException(
                        "Functions must be a list of Ten8tFunction objects."
                    )
                # Since we are building up a module from nothing we give it a generic name and
                # remember the load order.
                f.index = count
                f.module = "adhoc"
            return check_functions

        if not check_functions:
            return []

        raise Ten8tException("Functions must be a list of Ten8tFunction objects.")

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

    def prepare(self, filter_functions=None):
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

        self.auto_gen_ruids()

        # At this point we have all the functions in the packages, modules and functions
        # Now we need to filter out the ones that are not wanted. Filter functions return
        # True if the function should be kept
        self.collected = []
        for ten8t_func in self.pre_collected:
            if all(f(ten8t_func) for f in filter_functions):
                self.collected.append(ten8t_func)

        # Now use the RC file.  Note that if you are running filter functions AND
        # an RC file this can be confusing.  Ideally you use one or the other. but
        # it isn't an error to do so, you just need to know what you are doing.
        self.apply_rc(self.rc)

        # The collected list has the functions that will be run to verify operation
        # of the system.

        # If the user has provided valid ruids for all functions (or for none) then
        # we can proceed.  If not then we need to raise an exception and show the issues.
        ruids = [f.ruid for f in self.collected]

        # If the user decided to set up ruids for every function OR if they didn't configure
        # any ruids then we can just run with the collected functions.
        if empty_ruids(ruids) or valid_ruids(ruids):
            return self.collected

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
            return self.collected

        self.collected = [function for function in self.collected
                          if self.rc.does_match(ruid=function.ruid,
                                                tag=function.tag,
                                                phase=function.phase,
                                                level=function.level)]

        return self.collected

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
        self.collected = [f for f in self.collected if f.tag not in tags and
                          f.ruid not in ruids and
                          f.level not in levels and
                          f.phase not in phases]
        return self.collected

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
        self.collected = [f for f in self.collected if (f.tag in tags_) or
                          (f.ruid in ruids_) or
                          (f.level in levels_) or
                          (f.phase in phases_)]

        return self.collected

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
        r = sorted(set(f.ruid for f in self.collected))
        return r

    @property
    def levels(self):
        """
        Return a list of all the levels in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.level for f in self.collected))

    @property
    def tags(self):
        """
        Return a list of all the tags in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.tag for f in self.collected))

    @property
    def phases(self):
        """
        Return a list of all the phases in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.phase for f in self.collected))

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
        self.progress_callback(count, self.function_count, "Start Rule Check")
        self.start_time = dt.datetime.now()

        ten8t_logger.info("Checker start with %d functions", len(self.collected))
        # Fixes linting issue
        function_ = None
        try:
            # Magic happens here.  Each module is checked for any functions that start with 
            # env_ (which is configurable).  Env is a dictionary that has values that may be
            # used as function parameters to check functions (very similar to pytest).  At this
            # time environments are global, hence there could be collisions on larger projects.
            env = self.load_environments()

            # Count here to enable progress bars
            for count, function_ in enumerate(self.collected, start=1):

                # Lots of magic here
                function_.env = env

                self.progress_callback(count,
                                       self.function_count,
                                       f"Func Start {function_.function_name}")
                for result in function_():

                    # Render the message if needed.  The render happens right before it is yielded so it "knows" as 
                    # much as possible at this point.
                    result.msg_rendered = result.msg if not self.renderer else self.renderer.render(result.msg)

                    ten8t_logger.debug("%s:%s:%s", result.func_name, result.status, result.msg)

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
                        self.progress_callback(count, self.function_count,
                                               f"Early exit. {function_.function_name} failed.")
                        break
                    self.progress_callback(count, self.function_count, "", result)
                self.progress_callback(count, self.function_count, "Func done.")

        except self.AbortYieldException:
            name = function_.function_name if function_ is not None else "???"

            if self.abort_on_fail:
                self.progress_callback(count,
                                       self.function_count,
                                       f"Abort on fail: {name}")
            if self.abort_on_exception:
                self.progress_callback(count,
                                       self.function_count,
                                       f"Abort on exception: {name}")

        self.end_time = dt.datetime.now()
        self.progress_callback(count,
                               self.function_count,
                               "Rule Check Complete.")
        ten8t_logger.info("Checker complete ran %s check functions", self.function_count)

    def run_all(self, env=None) -> list[Ten8tResult]:
        """
        List version of yield all.

        """

        # A deceptively important line of code
        self.results = list(self.yield_all(env=env))

        self.score = self.score_strategy(self.results)
        self.progress_callback(self.function_count,
                               self.function_count,
                               f"Score = {self.score:.1f}")
        return self.results

    @property
    def clean_run(self):
        """ No exceptions """
        return all(not r.except_ for r in self.results)

    @property
    def perfect_run(self):
        """No fails or skips"""
        return all(r.status and not r.skipped and not r.warn_msg for r in self.results)

    @property
    def skip_count(self):
        """Number of skips"""
        return len([r for r in self.results if r.skipped])

    @property
    def warn_count(self):
        """Number of warns"""
        return len([r for r in self.results if r.warn_msg])

    @property
    def pass_count(self):
        """Number of passes"""
        return len([r for r in self.results if r.status and not r.skipped])

    @property
    def fail_count(self):
        """Number of fails"""
        return len([r for r in self.results if not r.status and not r.skipped])

    @property
    def result_count(self):
        """ Possibly redundant call to get the number of results."""
        return len(self.results)

    @property
    def function_count(self):
        """ Count all the collected functions (this is not the ones that are run)"""
        return len(self.collected)

    @property
    def module_count(self):
        """Count up all the modules in all the packages"""
        return len(self.modules) + sum(1 for pkg in self.packages for _ in pkg.modules)

    @property
    def module_names(self):
        """Get a list of module names."""
        return [module.name for module in self.modules] + \
            [m.module_name for pkg in self.packages for m in pkg.modules]

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
        }
        return header

    def as_dict(self):
        """
        Return a dictionary of the results.
        """
        h = self.get_header()

        r = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),

            "functions": [f.function_name for f in self.check_functions],
            "passed_count": self.pass_count,
            "warn_count": self.warn_count,
            "failed_count": self.fail_count,
            "skip_count": self.skip_count,
            "total_count": self.result_count,
            "package_count": self.package_count,
            "module_count": self.module_count,
            "check_count": self.function_count,
            "result_count": self.result_count,
            "clean_run": self.clean_run,
            "perfect_run": self.perfect_run,
            "abort_on_fail": self.abort_on_fail,
            "abort_on_exception": self.abort_on_exception,
            "phases": self.phases,
            "levels": self.levels,
            "tags": self.tags,
            # the meat of the output lives here
            "results": [r.as_dict() for r in self.results],
        }
        return h | r
